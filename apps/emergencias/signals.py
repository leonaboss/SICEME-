"""
SICEME - Señales para Stock Dinámico
Actualiza automáticamente las estadísticas por especialidad al crear/eliminar registros
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from apps.especialistas.models import EstadisticaEspecialidad


def actualizar_estadistica(especialidad_nombre, medico_nombre, mes, anio, incremento=1):
    """Busca los objetos de especialidad y médico para actualizar estadísticas numéricas"""
    from apps.especialistas.models import Especialidad, Especialista
    
    try:
        # Intentar obtener los objetos por nombre (case-insensitive)
        esp_obj = Especialidad.objects.get(nombre__iexact=especialidad_nombre)
        med_obj = Especialista.objects.get(nombre_completo__iexact=medico_nombre)
        
        stat, created = EstadisticaEspecialidad.objects.get_or_create(
            especialidad=esp_obj,
            medico=med_obj,
            mes=mes,
            anio=anio,
            defaults={'total_pacientes': 0}
        )
        stat.total_pacientes += incremento
        if stat.total_pacientes < 0:
            stat.total_pacientes = 0
        stat.save()
    except (Especialidad.DoesNotExist, Especialista.DoesNotExist):
        # Si no existen en el catálogo maestro, no se registran estadísticas numéricas
        # Pero no lanzamos error para permitir que el registro de morbilidad se guarde
        pass


# ─── Señales para MorbilidadEspecialista ───
@receiver(post_save, sender=MorbilidadEspecialista)
def morbilidad_especialista_creada(sender, instance, created, **kwargs):
    if created:
        actualizar_estadistica(
            instance.especialidad,
            instance.especialista,
            instance.created_at.month,
            instance.created_at.year,
            incremento=1
        )


@receiver(post_delete, sender=MorbilidadEspecialista)
def morbilidad_especialista_eliminada(sender, instance, **kwargs):
    actualizar_estadistica(
        instance.especialidad,
        instance.especialista,
        instance.created_at.month,
        instance.created_at.year,
        incremento=-1
    )
