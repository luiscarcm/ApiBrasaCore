from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('apps.users.urls')),
    path('api/mesas/', include('apps.mesas.urls')),
    path('api/productos/', include('apps.productos.urls')),
    path('api/pedidos/', include('apps.pedidos.urls')),
    path('api/facturacion/', include('apps.facturacion.urls')),
    path('api/caja/', include('apps.caja.urls')),
    path('api/inventario/', include('apps.inventario.urls')),
]
