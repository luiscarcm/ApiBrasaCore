from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    disponible_en_inventario = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'categoria', 'categoria_nombre',
            'activo', 'requiere_cocina',
            'disponible_en_inventario',
        ]

    def get_disponible_en_inventario(self, obj):
        try:
            from apps.inventario.models import RecetaProducto
            receta = obj.receta.select_related('ingrediente').all()
            if not receta.exists():
                return True
            for item in receta:
                if item.ingrediente.stock_actual <= item.ingrediente.stock_critico:
                    return False
            return True
        except Exception:
            return True
