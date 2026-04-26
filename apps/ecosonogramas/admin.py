from django.contrib import admin
from .models import MorbilidadEcosonograma

@admin.register(MorbilidadEcosonograma)
class EcosonogramaAdmin(admin.ModelAdmin):
    list_display = ['nombre_apellido', 'tipo_eco', 'medico', 'fecha']
    search_fields = ['nombre_apellido', 'cedula']
    date_hierarchy = 'fecha'
