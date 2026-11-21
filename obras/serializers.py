"""
Serializadores explícitos para el módulo Obras.
"""
from rest_framework import serializers
from .models import (
    ClienteMandante, ContactoCliente, Presupuesto,
    Obra, HojaServicio, HorasTrabajadas
)


class ContactoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoCliente
        fields = ['id', 'id_cliente', 'nombre', 'rut', 'cargo', 'email', 'telefono']


class ClienteMandanteSerializer(serializers.ModelSerializer):
    contactos = ContactoClienteSerializer(many=True, read_only=True)

    class Meta:
        model = ClienteMandante
        fields = ['id', 'rut', 'razon_social', 'giro', 'contactos']


class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = ['id', 'id_cliente', 'estado', 'monto_total']


class HojaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HojaServicio
        fields = ['id', 'id_obra', 'fecha_servicio', 'ruta_fotografia', 'firma_canvas_base64', 'estado_firma']
        read_only_fields = ['id', 'fecha_servicio']


class HorasTrabajadasSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorasTrabajadas
        fields = ['id', 'id_obra', 'id_tecnico', 'cantidad_horas', 'costo_hora']


class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = ['id', 'id_presupuesto', 'id_cliente', 'id_tecnico', 'tipo_servicio', 'estado', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']