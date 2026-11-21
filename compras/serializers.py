"""
Serializadores explícitos para el módulo de Compras.
"""
import re
from rest_framework import serializers
from .models import Proveedor, ContactoProveedor, DocumentoCompra, DetalleCompra


def validar_rut_chileno(value: str) -> str:

    """Valida el formato básico del RUT (ej: 12345678-9 o 1234567-K)."""
    if not re.match(r'^\d{7,8}-[kK0-9]$', value):
    
        raise serializers.ValidationError("Formato de RUT inválido. Utilice el formato 12345678-9.")
    
    return value

class ContactoProveedorSerializer(serializers.ModelSerializer):

    rut = serializers.CharField(max_length=12, validators=[validar_rut_chileno])

    class Meta:
        model = ContactoProveedor
        fields = ['id', 'nombre', 'rut', 'cargo', 'email', 'telefono']


class ProveedorSerializer(serializers.ModelSerializer):
    contactos = ContactoProveedorSerializer(many=True, read_only=True)

    class Meta:
        model = Proveedor
        fields = [
            'id', 'rut', 'razon_social', 'direccion', 'banco', 
            'tipo_cuenta', 'numero_cuenta', 'email_pagos', 'contactos'
        ]


class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'id_articulo', 'cantidad', 'costo_base', 
            'descuento_1', 'descuento_2', 'descuento_3', 'costo_neto_final'
        ]
        read_only_fields = ['id', 'costo_neto_final'] # Se calcula por BD (save)


class DocumentoCompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)

    class Meta:
        model = DocumentoCompra
        fields = [
            'id', 'id_proveedor', 'tipo_documento', 'folio', 'fecha_ingreso',
            'subtotal', 'descuentos_generales', 'descuento_pago_anticipado',
            'total_neto', 'iva', 'total_final', 'detalles'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Creación anidada del documento y sus detalles."""
        detalles_data = validated_data.pop('detalles')
        documento = DocumentoCompra.objects.create(**validated_data)
        
        for detalle_data in detalles_data:
            DetalleCompra.objects.create(id_documento=documento, **detalle_data)
            
        return documento