# -*- coding: utf-8 -*-
from apps.morbilidades.models import Especialidad, Especialista

def normalizar_especialista(nombre_medico):
    if not nombre_medico:
        return None
    esp, _ = Especialidad.objects.get_or_create(nombre='General')
    med, _ = Especialista.objects.get_or_create(
        nombre_completo=nombre_medico.strip().title(),
        defaults={'especialidad': esp}
    )
    return med

def normalizar_especialidad(nombre_especialidad):
    if not nombre_especialidad:
        return None
    esp, _ = Especialidad.objects.get_or_create(nombre=nombre_especialidad.strip().title())
    return esp
