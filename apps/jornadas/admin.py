# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.jornadas.models import Jornada

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    list_display = ['especialista', 'fecha', 'hora_entrada', 'hora_salida', 'total_horas']
    list_filter = ['fecha', 'especialista']
