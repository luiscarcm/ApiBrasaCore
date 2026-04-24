from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, CustomTokenObtainPairView, ForgotPasswordView, ResetPasswordView

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]
