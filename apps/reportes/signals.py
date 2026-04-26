from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Movimiento
# IMPORTS CRÍTICOS (Corregidos según ubicación real en este proyecto)
from apps.emergencias.models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from apps.ecosonogramas.models import MorbilidadEcosonograma

def sync_movimiento(instance, tipo_mov, nombre_display, detalle):
    """Sincroniza un registro original con la tabla central de Movimientos"""
    ct = ContentType.objects.get_for_model(instance.__class__)
    
    # Buscamos si ya existe el movimiento para actualizarlo, o creamos uno nuevo
    Movimiento.objects.update_or_create(
        content_type=ct,
        object_id=instance.pk,
        defaults={
            'tipo_mov': tipo_mov,
            'nombre_display': nombre_display,
            'detalle': detalle,
            'usuario': getattr(instance, 'usuario', None),
            'activo': getattr(instance, 'activo', True),
            'created_at': getattr(instance, 'created_at', timezone.now()) or timezone.now(),
        }
    )

def clear_movimiento(instance):
    """Elimina el registro de la tabla de movimientos si se borra el original"""
    ct = ContentType.objects.get_for_model(instance.__class__)
    Movimiento.objects.filter(content_type=ct, object_id=instance.pk).delete()

# --- Señal: Emergencias ---
@receiver(post_save, sender=MorbilidadEmergencia)
def emergencia_post_save(sender, instance, **kwargs):
    sync_movimiento(instance, 'emergencia', instance.nombre_apellido, instance.medico)

@receiver(post_delete, sender=MorbilidadEmergencia)
def emergencia_post_delete(sender, instance, **kwargs):
    clear_movimiento(instance)

# --- Señal: Especialistas ---
@receiver(post_save, sender=MorbilidadEspecialista)
def especialista_post_save(sender, instance, **kwargs):
    detalle = f"{instance.especialista} - {instance.especialidad}"
    sync_movimiento(instance, 'especialista', instance.nombre_apellido, detalle)

@receiver(post_delete, sender=MorbilidadEspecialista)
def especialista_post_delete(sender, instance, **kwargs):
    clear_movimiento(instance)

# --- Señal: No Asistidos ---
@receiver(post_save, sender=PacienteNoAsistido)
def no_asistido_post_save(sender, instance, **kwargs):
    detalle = f"{instance.medico} - {instance.especialidad}"
    sync_movimiento(instance, 'no_asistido', instance.nombre_completo, detalle)

@receiver(post_delete, sender=PacienteNoAsistido)
def no_asistido_post_delete(sender, instance, **kwargs):
    clear_movimiento(instance)

# --- Señal: Ecosonogramas ---
@receiver(post_save, sender=MorbilidadEcosonograma)
def ecosonograma_post_save(sender, instance, **kwargs):
    detalle = f"{instance.tipo_eco} - {instance.medico}"
    sync_movimiento(instance, 'ecosonograma', instance.nombre_apellido, detalle)

@receiver(post_delete, sender=MorbilidadEcosonograma)
def ecosonograma_post_delete(sender, instance, **kwargs):
    clear_movimiento(instance)
