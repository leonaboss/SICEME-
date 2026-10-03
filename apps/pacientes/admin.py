# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.pacientes.models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cedula', 'edad', 'sexo', 'telefono', 'dependencia', 'activo']
    list_filter = ['sexo', 'activo']
    search_fields = ['nombre_completo', 'cedula', 'dependencia']
    date_hierarchy = 'created_at'
