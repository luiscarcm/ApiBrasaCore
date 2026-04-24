from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CierreCajaViewSet, ConfigCajaView

router = SimpleRouter()
router.register(r'cierres', CierreCajaViewSet, basename='caja')

urlpatterns = [
    path('config/', ConfigCajaView.as_view()),
    path('', include(router.urls)),
]
