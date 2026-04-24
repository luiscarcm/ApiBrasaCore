from rest_framework import serializers
from .models import Pedido, DetallePedido
from apps.productos.serializers import ProductoSerializer


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    requiere_cocina = serializers.BooleanField(source='producto.requiere_cocina', read_only=True)

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'observaciones', 'entregado', 'requiere_cocina']


class DetallePedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'observaciones']

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    mesa_numero = serializers.IntegerField(source='mesa.numero', read_only=True)
    mesero_nombre = serializers.CharField(source='mesero.get_full_name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'mesa_numero', 'mesero', 'mesero_nombre', 'estado',
                  'creado_en', 'actualizado_en', 'en_preparacion_en', 'listo_en',
                  'entregado_en', 'detalles', 'subtotal']
        read_only_fields = ['mesero', 'creado_en', 'actualizado_en']

    def get_subtotal(self, obj):
        return float(obj.calcular_subtotal())


class PedidoCreateSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoCreateSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ['mesa', 'detalles']

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("El pedido debe tener al menos un ítem.")
        return value

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        mesero = self.context['request'].user
        pedido = Pedido.objects.create(mesero=mesero, **validated_data)

        # Mark table as occupied
        pedido.mesa.estado = 'ocupada'
        pedido.mesa.save()

        for detalle in detalles_data:
            producto = detalle['producto']
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=detalle['cantidad'],
                precio_unitario=producto.precio,
                observaciones=detalle.get('observaciones', '')
            )
        return pedido
