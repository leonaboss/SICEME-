# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.morbilidades.models import Especialidad, Especialista, EstadisticaEspecialidad, Morbilidad

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'es_vigilancia_centinela', 'activo']
    search_fields = ['nombre']

@admin.register(Especialista)
class EspecialistaAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cedula', 'especialidad', 'telefono', 'activo']
    search_fields = ['nombre_completo', 'cedula']
    list_filter = ['especialidad', 'activo']

@admin.register(EstadisticaEspecialidad)
class EstadisticaEspecialidadAdmin(admin.ModelAdmin):
    list_display = ['medico', 'especialidad', 'total_pacientes', 'mes', 'anio']
    list_filter = ['mes', 'anio', 'especialidad']

@admin.register(Morbilidad)
class MorbilidadAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo_modulo', 'medico', 'especialidad', 'fecha_evento', 'activo']
    list_filter = ['tipo_modulo', 'activo', 'fecha_evento']
    search_fields = ['paciente__nombre_completo', 'paciente__cedula', 'diagnostico']
    date_hierarchy = 'fecha_evento'
