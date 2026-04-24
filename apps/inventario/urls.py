from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaIngredienteViewSet,
    IngredienteViewSet,
    RecetaProductoViewSet,
    MovimientoInventarioViewSet,
    AlertasViewSet,
    ReporteInventarioView,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaIngredienteViewSet, basename='cat-ingrediente')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'recetas', RecetaProductoViewSet, basename='receta')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')
router.register(r'alertas', AlertasViewSet, basename='alerta-inventario')
router.register(r'reporte', ReporteInventarioView, basename='reporte-inventario')

urlpatterns = [path('', include(router.urls))]
