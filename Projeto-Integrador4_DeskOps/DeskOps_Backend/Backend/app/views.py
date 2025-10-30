from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets

from .permissions import ChamadoPermission
from .models import Users, Environment, Ativo, Chamado, Notificate
from .permissions import ChamadoPermission
from .serializers import (
    UserSerializer,
    EnvironmentSerializer,
    AtivoSerializer,
    ChamadoSerializer,
    NotificateSerializer,
    CustomTokenObtainPairSerializer,
    ReadWriteSerializer
)

# ============================================================
# 🔐 Autenticação (Login / Logout)
# ============================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint de login JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Realiza logout invalidando o token JWT"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Token inválido ou já expirado."}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# 👤 Cadastro e Aprovação de Usuários
# ============================================================

class RegisterView(APIView):
    """Cadastro de novos usuários (aguardando aprovação)"""
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        data["is_active"] = False
        data["is_staff"] = False
        data["cargo"] = "aguardando"

        if "password" in data:
            data["password"] = make_password(data["password"])

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuário cadastrado com sucesso! Aguarde aprovação do administrador."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def aprovar_usuario(request, pk):
    """Admin aprova e define cargo de um usuário"""
    try:
        user = Users.objects.get(pk=pk)
    except Users.DoesNotExist:
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    cargo = request.data.get("cargo")
    if cargo not in ["usuario", "tecnico"]:
        return Response({"error": "Cargo inválido. Use 'usuario' ou 'tecnico'."}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = True
    user.cargo = cargo
    user.save()

    return Response(
        {"message": f"Usuário '{user.name}' aprovado como {cargo}."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    """Retorna dados do usuário logado"""
    user = request.user
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "cargo": user.cargo,
        "cpf": user.cpf,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
    }
    return Response(data)


# ============================================================
# 📦 CRUDs — ModelViewSets
# ============================================================

class UsersView(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class EnvironmentView(ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permission_classes = [IsAuthenticated]


class AtivoView(ModelViewSet):
    queryset = Ativo.objects.all()
    serializer_class = AtivoSerializer
    permission_classes = [IsAuthenticated]


class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamado.objects.all()
    serializer_class = ChamadoSerializer
    permission_classes = [IsAuthenticated, ChamadoPermission]


class NotificateView(ModelViewSet):
    queryset = Notificate.objects.all()
    serializer_class = NotificateSerializer
    permission_classes = [IsAuthenticated]
