from django.contrib import admin
from .models import Movimiento

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'accion', 'modulo_origen', 'nombre_display', 'detalle', 'usuario', 'created_at', 'activo')
    list_filter = ('accion', 'modulo_origen', 'activo', 'created_at')
    search_fields = ('nombre_display', 'detalle', 'usuario__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
