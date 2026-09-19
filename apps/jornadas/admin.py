from django.contrib import admin
from .models import Jornada

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    list_display = ['especialista', 'fecha', 'hora_entrada', 'hora_salida', 'total_horas']
    list_filter = ['especialista', 'fecha']
