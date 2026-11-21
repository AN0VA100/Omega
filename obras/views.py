"""
Vistas de Obras, Presupuestos y Terreno. Incluye la Máquina de Estados de FYAG.
"""
from rest_framework import generics, status
from rest_framework.response import Response

from .models import ClienteMandante, Presupuesto, Obra, HojaServicio, HorasTrabajadas
from .serializers import (
    ClienteMandanteSerializer, PresupuestoSerializer, ObraSerializer,
    HojaServicioSerializer, HorasTrabajadasSerializer
)
from .permissions import CanAccessFinanzasObra, CanManageObras, CanManageTerreno
from core.models import Rol
from logistica.models import Cardex


class ClienteMandanteListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClienteMandante.objects.all().order_by('id')
    serializer_class = ClienteMandanteSerializer
    permission_classes = [CanAccessFinanzasObra]


class PresupuestoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Presupuesto.objects.all().order_by('id')
    serializer_class = PresupuestoSerializer
    permission_classes = [CanAccessFinanzasObra]


class ObraListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ObraSerializer
    permission_classes = [CanManageObras]

    def get_queryset(self):
        """
        Regla de Negocio: Técnicos SOLO ven las obras donde su usuario es el id_tecnico.
        Otros roles operativos ven todo.
        """
        usuario = self.request.user
        if not usuario.is_superuser and usuario.rol and usuario.rol.nombre_rol == Rol.TECNICO:
            return Obra.objects.filter(id_tecnico=usuario).order_by('-fecha_creacion')
        return Obra.objects.all().order_by('-fecha_creacion')


class ObraDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ObraSerializer
    permission_classes = [CanManageObras]

    def get_queryset(self):
        usuario = self.request.user
        if not usuario.is_superuser and usuario.rol and usuario.rol.nombre_rol == Rol.TECNICO:
            return Obra.objects.filter(id_tecnico=usuario)
        return Obra.objects.all()

    def update(self, request, *args, **kwargs):
        """
        Regla de Negocio 1: Máquina de Estados y Bloqueo Financiero.
        Si la obra intenta pasar a 'Finalizada', valida requisitos estrictos. Retorna 422 en caso de fallo.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        nuevo_estado = serializer.validated_data.get('estado')
        
        if nuevo_estado == Obra.ESTADO_FINALIZADA and instance.estado != Obra.ESTADO_FINALIZADA:
            errores = []
            
            # Validación 1: Técnico asignado
            if not instance.id_tecnico:
                errores.append("La obra no tiene un técnico asignado.")
            
            # Validación 2: Hoja de servicio firmada
            if not instance.hojas_servicio.filter(estado_firma=True).exists():
                errores.append("La obra no tiene una hoja de servicio firmada adjunta.")
            
            # Validación 3: Horas trabajadas reportadas
            if not instance.horas_trabajadas.exists():
                errores.append("La obra no tiene registro de horas trabajadas imputadas.")
                
            # Validación 4: Egresos de materiales en Cardex
            tiene_egresos = Cardex.objects.filter(id_obra=instance.id, tipo_movimiento=Cardex.TIPO_EGRESO).exists()
            if not tiene_egresos:
                errores.append("La obra carece de egresos de materiales registrados en el Cardex de Bodega.")

            # Si falla el workflow, rechazar la transacción con HTTP 422 Unprocessable Entity
            if errores:
                return Response({"errores": errores}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        self.perform_update(serializer)
        return Response(serializer.data)


class HojaServicioListCreateAPIView(generics.ListCreateAPIView):
    queryset = HojaServicio.objects.all().order_by('-fecha_servicio')
    serializer_class = HojaServicioSerializer
    permission_classes = [CanManageTerreno]


class HorasTrabajadasListCreateAPIView(generics.ListCreateAPIView):
    queryset = HorasTrabajadas.objects.all().order_by('-id')
    serializer_class = HorasTrabajadasSerializer
    permission_classes = [CanManageTerreno]