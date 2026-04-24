from decimal import Decimal
from rest_framework import serializers
from .models import CategoriaIngrediente, Ingrediente, RecetaProducto, MovimientoInventario


class CategoriaIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaIngrediente
        fields = '__all__'


class IngredienteSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    estado_stock = serializers.CharField(read_only=True)

    class Meta:
        model = Ingrediente
        fields = [
            'id', 'nombre', 'unidad_medida', 'stock_actual',
            'stock_minimo', 'stock_critico', 'categoria', 'categoria_nombre',
            'activo', 'estado_stock',
        ]


class IngredienteLiteSerializer(serializers.ModelSerializer):
    """Serializer compacto para uso en recetas y movimientos."""
    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre', 'unidad_medida', 'stock_actual', 'estado_stock']


class RecetaProductoSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)
    ingrediente_unidad = serializers.CharField(source='ingrediente.unidad_medida', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = RecetaProducto
        fields = [
            'id', 'producto', 'producto_nombre',
            'ingrediente', 'ingrediente_nombre', 'ingrediente_unidad',
            'cantidad',
        ]


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)
    ingrediente_unidad = serializers.CharField(source='ingrediente.unidad_medida', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'ingrediente', 'ingrediente_nombre', 'ingrediente_unidad',
            'tipo', 'tipo_display', 'cantidad', 'stock_resultante',
            'referencia_pedido', 'referencia_detalle',
            'usuario', 'usuario_nombre', 'notas', 'creado_en',
        ]
        read_only_fields = ['stock_resultante', 'creado_en']

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return None


class AjusteManualSerializer(serializers.Serializer):
    """Para el endpoint POST /inventario/ingredientes/{id}/ajustar/"""
    nuevo_stock = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=Decimal('0'))
    notas = serializers.CharField(required=False, allow_blank=True, default='')


class EntradaStockSerializer(serializers.Serializer):
    """Para el endpoint POST /inventario/ingredientes/{id}/entrada/"""
    cantidad = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=Decimal('0'))
    notas = serializers.CharField(required=False, allow_blank=True, default='')
