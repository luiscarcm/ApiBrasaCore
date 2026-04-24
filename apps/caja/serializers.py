from rest_framework import serializers
from .models import ConfigCaja, CierreCaja


class ConfigCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigCaja
        fields = ['id', 'base_efectivo', 'actualizado_en']
        read_only_fields = ['actualizado_en']


class CierreCajaSerializer(serializers.ModelSerializer):
    cajero_nombre = serializers.CharField(source='cajero.get_full_name', read_only=True)
    total_general = serializers.SerializerMethodField()

    class Meta:
        model = CierreCaja
        fields = [
            'id', 'cajero', 'cajero_nombre',
            'apertura_en', 'cierre_en',
            'base_efectivo',
            'total_efectivo', 'total_tarjeta', 'total_transferencia', 'total_general',
            'efectivo_contado', 'diferencia',
            'notas', 'estado',
        ]
        read_only_fields = [
            'cajero', 'apertura_en', 'cierre_en',
            'base_efectivo',
            'total_efectivo', 'total_tarjeta', 'total_transferencia',
            'efectivo_contado', 'diferencia', 'estado',
        ]

    def get_total_general(self, obj):
        return float(obj.total_efectivo + obj.total_tarjeta + obj.total_transferencia)
