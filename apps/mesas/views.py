from rest_framework import viewsets, permissions
from .models import Mesa
from .serializers import MesaSerializer


class IsAdminOrReadWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ['DELETE', 'POST'] and request.user.rol != 'admin':
            return False
        return True


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [permissions.IsAuthenticated]
