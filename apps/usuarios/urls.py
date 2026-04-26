"""SICEME - URLs de Usuarios"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verificar-otp/', views.verificar_otp_view, name='verificar_otp'),
    path('reenviar-otp/', views.reenviar_otp_view, name='reenviar_otp'),
    path('crear-cuenta/', views.registro_publico_view, name='registro_publico'),

    # Gestión de usuarios (Admin)
    path('registro/', views.registro_view, name='registro'),
    path('lista/', views.lista_usuarios_view, name='lista_usuarios'),
    path('editar/<int:pk>/', views.editar_usuario_view, name='editar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario_view, name='eliminar_usuario'),
    path('desbloquear/<int:pk>/', views.desbloquear_usuario_view, name='desbloquear_usuario'),
    path('estado/<int:pk>/', views.toggle_estado_usuario_view, name='toggle_estado_usuario'),
    path('promover/<int:pk>/', views.promover_admin_usuario_view, name='promover_admin_usuario'),

    # Perfil y contraseña
    path('perfil/', views.perfil_view, name='perfil'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),

    # Bitácora
    path('bitacora/', views.bitacora_view, name='bitacora'),

    # Recuperación de contraseña por OTP (Personalizado)
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_otp_view, name='password_reset_otp'),
    path('password-reset/change/', views.password_reset_change_view, name='password_reset_change'),
]
