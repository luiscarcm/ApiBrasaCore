from django.contrib import admin
from .models import CategoriaIngrediente, Ingrediente, RecetaProducto, MovimientoInventario


@admin.register(CategoriaIngrediente)
class CategoriaIngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_medida', 'stock_actual', 'stock_minimo', 'stock_critico', 'categoria', 'activo']
    list_filter = ['activo', 'categoria', 'unidad_medida']
    search_fields = ['nombre']
    list_editable = ['activo']


@admin.register(RecetaProducto)
class RecetaProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ingrediente', 'cantidad']
    list_filter = ['producto', 'ingrediente']
    search_fields = ['producto__nombre', 'ingrediente__nombre']


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['creado_en', 'ingrediente', 'tipo', 'cantidad', 'stock_resultante', 'usuario']
    list_filter = ['tipo', 'creado_en']
    search_fields = ['ingrediente__nombre', 'notas']
    readonly_fields = ['creado_en', 'stock_resultante']
    date_hierarchy = 'creado_en'
