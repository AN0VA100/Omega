import os
import django
import random
from decimal import Decimal
from datetime import date, timedelta

# 1. Configurar Django para ejecución autónoma
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Omega.settings')
django.setup()

from core.models import Usuario, Rol
from logistica.models import Articulo, Cardex
from obras.models import ClienteMandante, ContactoCliente, Presupuesto, Obra, HojaServicio, HorasTrabajadas
from compras.models import Proveedor, ContactoProveedor, DocumentoCompra, DetalleCompra

def run_seed():
    print("Iniciando la inserción de datos de prueba (Proyecto Omega FYAG)...")

    # 1. Obtener Roles (Deben existir gracias a tu migración RunPython)
    try:
        rol_admin = Rol.objects.get(nombre_rol=Rol.ADMIN_GENERAL)
        rol_bodega = Rol.objects.get(nombre_rol=Rol.BODEGA)
        rol_tecnico = Rol.objects.get(nombre_rol=Rol.TECNICO)
        rol_supervisor = Rol.objects.get(nombre_rol=Rol.SUPERVISOR)
        rol_finanzas = Rol.objects.get(nombre_rol=Rol.ADMINISTRACION)
    except Rol.DoesNotExist:
        print("Error: Los roles no existen. Ejecuta 'python manage.py migrate' primero.")
        return

    # 2. Crear Usuarios Operativos
    usuarios_data = [
        ('bodega1', '11111111-1', rol_bodega),
        ('tec1', '22222222-2', rol_tecnico),
        ('tec2', '33333333-3', rol_tecnico),
        ('tec3', '44444444-4', rol_tecnico),
        ('sup1', '55555555-5', rol_supervisor),
        ('finanzas1', '66666666-6', rol_finanzas)
    ]
    
    usuarios_creados = []
    for username, rut, rol in usuarios_data:
        usuario, created = Usuario.objects.get_or_create(
            username=username,
            rut=rut,
            defaults={'first_name': f'Nombre_{username}', 'last_name': 'Prueba', 'rol': rol}
        )
        if created:
            usuario.set_password('pass123')
            usuario.save()
        usuarios_creados.append(usuario)
    print(f"[{len(usuarios_creados)}] Usuarios creados.")

    # 3. Crear Catálogo de Artículos (Logística)
    articulos_data = [
        ('REF-001', 'Compresor Danfoss 1HP', 'Refrigeración', 'Unidad', 50000, 75000),
        ('REF-002', 'Válvula Expansión Termostática', 'Refrigeración', 'Unidad', 15000, 22000),
        ('REF-003', 'Gas Refrigerante R404A', 'Refrigeración', 'Kg', 12000, 18000),
        ('ELE-001', 'Contactor Trifásico 32A', 'Electricidad', 'Unidad', 25000, 35000),
        ('ELE-002', 'Cable THHN 12 AWG Rollo 100m', 'Electricidad', 'Rollo', 45000, 60000),
        ('HER-001', 'Bomba de Vacío 2 Etapas', 'Herramientas', 'Unidad', 150000, 200000),
        ('HER-002', 'Manifold Digital Testo', 'Herramientas', 'Unidad', 250000, 320000),
        ('REP-001', 'Filtro Deshidratador 3/8', 'Repuestos', 'Unidad', 8000, 12000),
        ('REP-002', 'Termostato Digital Full Gauge', 'Repuestos', 'Unidad', 30000, 45000),
        ('REP-003', 'Resistencia Deshielo 400W', 'Repuestos', 'Unidad', 12000, 18000),
        ('INS-001', 'Tubo Cobre 1/2 Pulgada', 'Ferretería', 'Tira', 20000, 28000),
        ('INS-002', 'Aislante Armaflex 1/2', 'Ferretería', 'Tira', 4000, 6000),
        ('INS-003', 'Soldadura Plata 15%', 'Ferretería', 'Varilla', 2000, 3500),
        ('INS-004', 'Cinta Teflón Industrial', 'Ferretería', 'Rollo', 1500, 2500),
        ('CLI-001', 'Equipo Split Muro 12000 BTU', 'Aire Acondicionado', 'Unidad', 180000, 250000),
        ('CLI-002', 'Soporte Unidad Exterior', 'Aire Acondicionado', 'Juego', 8000, 15000),
        ('CLI-003', 'Bomba Condensado', 'Aire Acondicionado', 'Unidad', 45000, 65000),
        ('REF-004', 'Termómetro Infrarrojo', 'Refrigeración', 'Unidad', 35000, 50000),
        ('ELE-003', 'Interruptor Termomagnético 16A', 'Electricidad', 'Unidad', 3500, 6000),
        ('REP-004', 'Ventilador Axial 300mm', 'Repuestos', 'Unidad', 40000, 55000),
    ]
    
    articulos_creados = []
    for i, (codigo, nombre, categoria, um, costo, precio) in enumerate(articulos_data):
        articulo, _ = Articulo.objects.get_or_create(
            codigo_interno=codigo,
            defaults={
                'codigo_barras': f'7801234567{i:03d}',
                'nombre': nombre,
                'categoria': categoria,
                'unidad_medida': um,
                'ubicacion': f'Pasillo {random.randint(1,5)} Estante {random.choice(["A","B","C"])}',
                'stock_disponible': Decimal(random.randint(5, 50)),
                'stock_minimo': Decimal('10.00'),
                'ultimo_costo': costo,
                'precio_lista_vigente': precio
            }
        )
        articulos_creados.append(articulo)
    print(f"[{len(articulos_creados)}] Artículos creados.")

    # 4. Crear Proveedores y sus Contactos
    proveedores_creados = []
    for i in range(1, 21):
        prov, _ = Proveedor.objects.get_or_create(
            rut=f'76{i:06d}-K',
            defaults={
                'razon_social': f'Proveedor Industrial {i} SpA',
                'direccion': f'Avenida Parque Industrial {1000+i}, Santiago',
                'banco': 'Banco de Chile',
                'tipo_cuenta': 'Corriente',
                'numero_cuenta': f'00-111-2222{i}',
                'email_pagos': f'pagos@prov{i}.cl'
            }
        )
        ContactoProveedor.objects.get_or_create(
            id_proveedor=prov,
            rut=f'15{i:06d}-2',
            defaults={
                'nombre': f'Vendedor {i}',
                'cargo': 'Ejecutivo de Ventas',
                'email': f'vendedor{i}@prov{i}.cl',
                'telefono': f'+569876543{i:02d}'
            }
        )
        proveedores_creados.append(prov)
    print(f"[{len(proveedores_creados)}] Proveedores creados.")

    # 5. Generar Facturas de Compra integradas con Cardex (Regla Cascada)
    admin_user = Usuario.objects.get(username='j00') # Usa tu superusuario para los ingresos de bodega
    hoy = date.today()
    for i in range(1, 21):
        doc, created = DocumentoCompra.objects.get_or_create(
            folio=f'F-2026-{i:04d}',
            defaults={
                'id_proveedor': random.choice(proveedores_creados),
                'tipo_documento': DocumentoCompra.TIPO_FACTURA,
                'fecha_ingreso': hoy - timedelta(days=random.randint(1, 60)),
                'subtotal': 0, 'total_neto': 0, 'iva': 0, 'total_final': 0
            }
        )
        if created:
            subtotal_doc = 0
            for _ in range(random.randint(2, 4)):
                art = random.choice(articulos_creados)
                cant = Decimal(random.randint(1, 10))
                costo_b = art.ultimo_costo
                desc1 = Decimal(random.choice(['0.00', '0.05', '0.10']))
                
                # Fórmula de cascada y valorización de inventario
                factor = (Decimal('1') - desc1)
                costo_n = int(round(Decimal(costo_b) * factor))
                
                DetalleCompra.objects.create(
                    id_documento=doc,
                    id_articulo=art,
                    cantidad=cant,
                    costo_base=costo_b,
                    descuento_1=desc1,
                    costo_neto_final=costo_n
                )
                subtotal_doc += int(round(Decimal(costo_n) * cant))
                
                # Inyección atómica al stock
                art.stock_disponible += cant
                art.ultimo_costo = costo_n
                art.save()
                
                # Integración con el Cardex inmutable
                Cardex.objects.create(
                    id_articulo=art,
                    id_usuario=admin_user,
                    tipo_movimiento=Cardex.TIPO_INGRESO,
                    cantidad=cant,
                    precio_unitario=costo_n
                )
                
            doc.subtotal = subtotal_doc
            doc.total_neto = subtotal_doc
            doc.iva = int(round(doc.total_neto * 0.19))
            doc.total_final = doc.total_neto + doc.iva
            doc.save()
    print("Facturas de Compras y Cardex integrados.")

    # 6. Clientes Mandantes y Presupuestos
    clientes_creados = []
    for i in range(1, 21):
        cli, _ = ClienteMandante.objects.get_or_create(
            rut=f'77{i:06d}-1',
            defaults={
                'razon_social': f'Exportadora Agrícola {i} S.A.',
                'giro': 'Agroindustria y Packing'
            }
        )
        ContactoCliente.objects.get_or_create(
            id_cliente=cli,
            rut=f'12{i:06d}-3',
            defaults={
                'nombre': f'Jefe Planta {i}',
                'cargo': 'Gerente de Operaciones',
                'email': f'planta{i}@agricola{i}.cl',
                'telefono': f'+569123456{i:02d}'
            }
        )
        clientes_creados.append(cli)

    presupuestos_creados = []
    for i in range(1, 21):
        pres, _ = Presupuesto.objects.get_or_create(
            id_cliente=random.choice(clientes_creados),
            monto_total=random.randint(500000, 5000000),
            defaults={
                'estado': random.choice([Presupuesto.ESTADO_PENDIENTE, Presupuesto.ESTADO_APROBADO])
            }
        )
        presupuestos_creados.append(pres)
    print(f"[{len(clientes_creados)}] Clientes y [{len(presupuestos_creados)}] Presupuestos listos.")

    # 7. Obras, Máquina de Estados, Horas y Egresos (Terreno)
    tecnicos = [u for u in usuarios_creados if u.rol.nombre_rol == Rol.TECNICO]
    for i in range(1, 21):
        pres_aprob = random.choice([p for p in presupuestos_creados if p.estado == Presupuesto.ESTADO_APROBADO] or presupuestos_creados)
        obra, created = Obra.objects.get_or_create(
            id_presupuesto=pres_aprob,
            id_cliente=pres_aprob.id_cliente,
            defaults={
                'id_tecnico': random.choice(tecnicos),
                'tipo_servicio': random.choice(['Mantención', 'Emergencia', 'Proyecto', 'Climatización']),
                'estado': random.choice([Obra.ESTADO_PROCESO, Obra.ESTADO_FINALIZADA])
            }
        )
        if created:
            # Imputar horas de terreno
            HorasTrabajadas.objects.create(
                id_obra=obra,
                id_tecnico=obra.id_tecnico,
                cantidad_horas=Decimal(random.randint(2, 12)),
                costo_hora=15000
            )
            
            # Subir Hoja de Servicio firmada (Base64)
            if obra.estado == Obra.ESTADO_FINALIZADA or random.choice([True, False]):
                HojaServicio.objects.create(
                    id_obra=obra,
                    estado_firma=True,
                    firma_canvas_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
                )
            
            # Egresos desde bodega a la obra para evitar error HTTP 422
            for _ in range(random.randint(1, 3)):
                art = random.choice(articulos_creados)
                cant = Decimal(random.randint(1, 3))
                if art.stock_disponible >= cant:
                    art.stock_disponible -= cant
                    art.save()
                    Cardex.objects.create(
                        id_articulo=art,
                        id_usuario=obra.id_tecnico,
                        tipo_movimiento=Cardex.TIPO_EGRESO,
                        id_obra=obra,
                        cantidad=cant,
                        precio_unitario=art.precio_lista_vigente
                    )
    print("Obras y operaciones de terreno generadas.")
    print("===================================================")
    print("¡Base de datos de Proyecto Omega poblada con éxito!")

if __name__ == '__main__':
    run_seed()