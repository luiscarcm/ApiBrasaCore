from rest_framework import serializers
from decimal import Decimal
from .models import Factura, AlertaCajero
from apps.pedidos.serializers import PedidoSerializer


class FacturaSerializer(serializers.ModelSerializer):
    pedido_detalle = PedidoSerializer(source='pedido', read_only=True)
    cajero_nombre = serializers.CharField(source='cajero.get_full_name', read_only=True)

    class Meta:
        model = Factura
        fields = ['id', 'pedido', 'pedido_detalle', 'cajero', 'cajero_nombre',
                  'subtotal', 'descuento', 'propina', 'iva', 'total',
                  'metodo_pago', 'extras', 'extras_total', 'creado_en']
        read_only_fields = ['cajero', 'subtotal', 'extras_total', 'total', 'creado_en']


class FacturaCreateSerializer(serializers.ModelSerializer):
    extras = serializers.JSONField(default=list, required=False)

    class Meta:
        model = Factura
        fields = ['pedido', 'descuento', 'propina', 'iva', 'metodo_pago', 'extras']

    def validate_pedido(self, value):
        if value.estado == 'pagado':
            raise serializers.ValidationError("Este pedido ya fue facturado.")
        if value.estado == 'cancelado':
            raise serializers.ValidationError("No se puede facturar un pedido cancelado.")
        if not value.detalles.exists():
            raise serializers.ValidationError("No hay ítems en el pedido.")
        return value

    def create(self, validated_data):
        pedido = validated_data['pedido']
        descuento_pct = Decimal(str(validated_data.get('descuento', 0)))
        propina_pct = Decimal(str(validated_data.get('propina', 0)))
        iva_pct = Decimal(str(validated_data.get('iva', 19)))
        extras = validated_data.get('extras', [])

        subtotal = pedido.calcular_subtotal()
        descuento_valor = subtotal * descuento_pct / 100
        base = subtotal - descuento_valor
        iva_valor = base * iva_pct / 100
        propina_valor = base * propina_pct / 100
        extras_total = sum(
            Decimal(str(e.get('valor', 0))) * max(int(e.get('cantidad', 1)), 1)
            for e in extras
        )
        total = base + iva_valor + propina_valor + extras_total

        cajero = self.context['request'].user
        factura = Factura.objects.create(
            pedido=pedido,
            cajero=cajero,
            subtotal=subtotal,
            descuento=descuento_pct,
            propina=propina_pct,
            iva=iva_pct,
            total=total,
            metodo_pago=validated_data['metodo_pago'],
            extras=extras,
            extras_total=extras_total,
        )

        # Update pedido state and free the table
        pedido.estado = 'pagado'
        pedido.save()
        pedido.mesa.estado = 'libre'
        pedido.mesa.save()

        return factura


class AlertaCajeroSerializer(serializers.ModelSerializer):
    cajero_nombre = serializers.CharField(source='cajero.get_full_name', read_only=True)
    mesa_numero = serializers.IntegerField(source='pedido.mesa.numero', read_only=True)

    class Meta:
        model = AlertaCajero
        fields = ['id', 'pedido', 'cajero', 'cajero_nombre', 'mesa_numero',
                  'descripcion', 'items_removidos', 'leido', 'creado_en']
        read_only_fields = ['cajero', 'creado_en']
