"""
SICEME - Decoradores de Seguridad
"""
from functools import wraps
from django.http import HttpResponseForbidden


def rol_requerido(*roles):
    """
    Decorador para restringir acceso por rol.
    Uso: @rol_requerido('ADMIN') o @rol_requerido('ADMIN', 'ESPECIALISTA')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')

            if request.user.is_superuser or request.user.rol in roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                '<div style="text-align:center;padding:50px;font-family:sans-serif;">'
                '<h1>403 - Acceso Denegado</h1>'
                '<p>No tiene permisos para acceder a este recurso.</p>'
                '<a href="/dashboard/">Volver al Dashboard</a></div>'
            )
        return _wrapped_view
    return decorator
