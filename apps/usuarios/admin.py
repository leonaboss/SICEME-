"""SICEME - Admin de Usuarios"""
from django.contrib import admin
from .models import Usuario, BitacoraAuditoria


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'rol', 'is_active', 'is_locked', 'failed_attempts', 'date_joined']
    list_filter = ['rol', 'is_active', 'is_locked']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']


@admin.register(BitacoraAuditoria)
class BitacoraAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'usuario', 'accion', 'modulo', 'direccion_ip']
    list_filter = ['accion', 'modulo']
    search_fields = ['usuario__username', 'descripcion']
    readonly_fields = ['usuario', 'accion', 'descripcion', 'fecha_hora', 'direccion_ip', 'modulo', 'user_agent']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
