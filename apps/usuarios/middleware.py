"""
SICEME - Middleware de Seguridad
RBAC y Auditoría automática
"""
import logging
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import resolve
from .models import BitacoraAuditoria

logger = logging.getLogger('siceme')

# Rutas públicas que no requieren autenticación
RUTAS_PUBLICAS = [
    'login',
    'verificar_otp',
    'reenviar_otp',
    'password_reset',
    'password_reset_done',
    'password_reset_confirm',
    'password_reset_complete',
]

# Configuración RBAC: qué roles pueden acceder a qué módulos URL
RBAC_CONFIG = {
    # Módulos de administración - solo ADMIN
    'registro': ['ADMIN'],
    'lista_usuarios': ['ADMIN'],
    'editar_usuario': ['ADMIN'],
    'eliminar_usuario': ['ADMIN'],
    'desbloquear_usuario': ['ADMIN'],
    'bitacora': ['ADMIN'],
    'crud_especialidades': ['ADMIN'],
    'crear_especialidad': ['ADMIN'],
    'editar_especialidad': ['ADMIN'],
    'eliminar_especialidad': ['ADMIN'],
    'crud_especialistas': ['ADMIN'],
    'crear_especialista': ['ADMIN'],
    'editar_especialista': ['ADMIN'],
    'eliminar_especialista': ['ADMIN'],

    # Módulos operativos - ADMIN, ESPECIALISTA y PUBLICO
    'lista_emergencias': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'crear_emergencia': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'editar_emergencia': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'eliminar_emergencia': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'lista_morbilidad_especialistas': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'crear_morbilidad_especialista': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'editar_morbilidad_especialista': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'eliminar_morbilidad_especialista': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'lista_no_asistidos': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'crear_no_asistido': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'editar_no_asistido': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'eliminar_no_asistido': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'lista_ecosonogramas': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'crear_ecosonograma': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'editar_ecosonograma': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'eliminar_ecosonograma': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'lista_jornadas': ['ADMIN', 'ESPECIALISTA'],
    'registrar_entrada': ['ADMIN', 'ESPECIALISTA'],
    'registrar_salida': ['ADMIN', 'ESPECIALISTA'],
    'registrar_pausa_inicio': ['ADMIN', 'ESPECIALISTA'],
    'registrar_pausa_fin': ['ADMIN', 'ESPECIALISTA'],

    # Dashboard y reportes - todos los autenticados
    'home': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'dashboard': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'reporte_especialidades': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'reporte_emergencias_mes': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'reporte_ecosonogramas_enfermedades': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'reporte_no_asistidos': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'reporte_top_medicos': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'exportar_excel': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'api_dashboard_data': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'api_estadisticas_especialidad': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],

    # Perfil y contraseña - todos
    'perfil': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'cambiar_password': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'logout': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],

    # Movimientos
    'movimientos': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'restaurar_registro': ['ADMIN', 'ESPECIALISTA', 'PUBLICO'],
    'eliminar_definitivo': ['ADMIN'],
    'limpiar_archivados': ['ADMIN'],

    # Limpiar CRUDs (archivado masivo)
    'limpiar_emergencias': ['ADMIN', 'ESPECIALISTA'],
    'limpiar_especialistas': ['ADMIN', 'ESPECIALISTA'],
    'limpiar_no_asistidos': ['ADMIN', 'ESPECIALISTA'],
    'limpiar_ecosonogramas': ['ADMIN', 'ESPECIALISTA'],
}


class RBACMiddleware:
    """Middleware de Control de Acceso Basado en Roles"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                url_name = resolve(request.path_info).url_name
            except Exception:
                return self.get_response(request)

            if url_name and url_name in RBAC_CONFIG:
                roles_permitidos = RBAC_CONFIG[url_name]
                if request.user.rol not in roles_permitidos and not request.user.is_superuser:
                    # Registrar intento de acceso no autorizado
                    BitacoraAuditoria.registrar(
                        request.user,
                        BitacoraAuditoria.Accion.ACCESO_DENEGADO,
                        f'Acceso denegado a: {url_name}',
                        request,
                        'rbac'
                    )
                    logger.warning(
                        f'RBAC: Acceso denegado a {url_name} para {request.user.username} '
                        f'(rol: {request.user.rol})'
                    )
                    return HttpResponseForbidden(
                        '<div style="text-align:center;padding:50px;font-family:sans-serif;">'
                        '<h1>403 - Acceso Denegado</h1>'
                        '<p>No tiene permisos para acceder a este recurso.</p>'
                        '<a href="/dashboard/">Volver al Dashboard</a></div>'
                    )

        response = self.get_response(request)
        return response


class AuditMiddleware:
    """Middleware para auditoría automática de acciones"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
