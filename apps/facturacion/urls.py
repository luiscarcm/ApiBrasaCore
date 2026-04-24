from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, AlertaCajeroViewSet

router = DefaultRouter()
router.register(r'alertas', AlertaCajeroViewSet, basename='alerta')
router.register(r'', FacturaViewSet, basename='factura')

urlpatterns = [path('', include(router.urls))]
