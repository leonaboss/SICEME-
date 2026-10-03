# -*- coding: utf-8 -*-
from django.apps import AppConfig


class PacientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pacientes'
    verbose_name = 'Módulo de Pacientes'

    def ready(self):
        pass
