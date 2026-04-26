"""SICEME - Admin de Especialistas"""
from django.contrib import admin
from .models import Especialidad, Especialista, EstadisticaEspecialidad


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'es_vigilancia_centinela']
    search_fields = ['nombre']


@admin.register(Especialista)
class EspecialistaAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'especialidad', 'telefono', 'usuario']
    list_filter = ['especialidad']
    search_fields = ['nombre_completo']


@admin.register(EstadisticaEspecialidad)
class EstadisticaEspecialidadAdmin(admin.ModelAdmin):
    list_display = ['medico', 'especialidad', 'total_pacientes', 'mes', 'anio']
    list_filter = ['especialidad', 'anio', 'mes']
