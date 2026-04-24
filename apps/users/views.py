from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Usuario, PasswordResetToken
from .serializers import (
    UsuarioSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Respuesta genérica para no revelar si el correo existe
        response = Response(
            {'detail': 'Si el correo está registrado, recibirás un enlace de recuperación.'},
            status=status.HTTP_200_OK,
        )

        try:
            user = Usuario.objects.get(email=email, is_active=True)
        except Usuario.DoesNotExist:
            return response

        # Invalidar tokens anteriores del usuario
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        reset_token = PasswordResetToken.objects.create(user=user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"

        subject = 'Recuperación de contraseña – BrasaCore'
        text_body = (
            f"Hola {user.get_full_name() or user.username},\n\n"
            f"Recibimos una solicitud para restablecer tu contraseña.\n"
            f"Usa el siguiente enlace (válido por 1 hora):\n\n{reset_url}\n\n"
            f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
            f"— Equipo BrasaCore"
        )
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
          <div style="background:#7c2d12;padding:28px 32px;text-align:center;">
            <h2 style="color:#fff;margin:0;font-size:1.4rem;letter-spacing:0.04em;">BrasaCore</h2>
            <p style="color:#fca5a5;margin:4px 0 0;font-size:0.85rem;">Sistema de Gestión para Restaurantes</p>
          </div>
          <div style="padding:32px;">
            <p style="color:#374151;margin:0 0 12px;">Hola <strong>{user.get_full_name() or user.username}</strong>,</p>
            <p style="color:#374151;margin:0 0 24px;">Recibimos una solicitud para restablecer la contraseña de tu cuenta. Haz clic en el botón a continuación. El enlace es válido por <strong>1 hora</strong>.</p>
            <div style="text-align:center;margin:24px 0;">
              <a href="{reset_url}" style="background:#ea580c;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:1rem;">Restablecer contraseña</a>
            </div>
            <p style="color:#6b7280;font-size:0.8rem;margin:24px 0 0;">Si no solicitaste este cambio, puedes ignorar este mensaje. Tu contraseña no será modificada.</p>
          </div>
          <div style="background:#f9fafb;padding:16px 32px;text-align:center;">
            <p style="color:#9ca3af;font-size:0.75rem;margin:0;">BRASACORE · MARCA UNISOFT</p>
          </div>
        </div>
        """

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)

        return response


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_token = PasswordResetToken.objects.get(token=serializer.validated_data['token'])
        user = reset_token.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        reset_token.used = True
        reset_token.save()

        return Response({'detail': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)
