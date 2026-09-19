"""SICEME - Admin de Emergencias"""
from django.contrib import admin
from .models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido


@admin.register(MorbilidadEmergencia)
class MorbilidadEmergenciaAdmin(admin.ModelAdmin):
    list_display = ['nombre_apellido', 'cedula', 'medico', 'fecha_diagnostico']
    list_filter = ['sexo', 'medico']
    search_fields = ['nombre_apellido', 'cedula']
    date_hierarchy = 'fecha_diagnostico'


@admin.register(MorbilidadEspecialista)
class MorbilidadEspecialistaAdmin(admin.ModelAdmin):
    list_display = ['nombre_apellido', 'especialista', 'especialidad', 'created_at']
    list_filter = ['especialidad']
    search_fields = ['nombre_apellido']


@admin.register(PacienteNoAsistido)
class PacienteNoAsistidoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'especialidad', 'medico', 'fecha_cita']
    list_filter = ['especialidad']
    search_fields = ['nombre_completo']
    date_hierarchy = 'fecha_cita'
