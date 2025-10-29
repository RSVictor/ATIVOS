from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsersView, EnvironmentView, AtivoView, ChamadoView, NotificateView,
    RegisterView, aprovar_usuario, CustomTokenObtainPairView 
)
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LogoutView
from .views import get_me

router = DefaultRouter()

router.register(r'users', UsersView)
router.register(r'environment', EnvironmentView)
router.register(r'ativo', AtivoView)
router.register(r'chamado', ChamadoView)
router.register(r'notificate', NotificateView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('aprovar_usuario/<int:pk>/', aprovar_usuario, name='aprovar_usuario'),

    # JWT login e refresh
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

     path('logout/', LogoutView.as_view(), name='logout'),

      # Endpoint de perfil
    path('me/', get_me, name='get_me'),

    # 👇 ESSENCIAL: adiciona todas as rotas do router (ativo, chamado, etc.)
    path('', include(router.urls)),
]
