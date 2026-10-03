from django.apps import AppConfig


class MorbilidadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.morbilidades'
    verbose_name = 'Módulo Central de Morbilidades'

    def ready(self):
        import apps.morbilidades.signals
