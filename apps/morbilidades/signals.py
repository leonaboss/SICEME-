# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from apps.morbilidades.models import Morbilidad, EstadisticaEspecialidad
from apps.reportes.models import Movimiento


def sync_movimiento(instance, accion):
    """Sincroniza un registro de morbilidad con la tabla centralizada de Movimientos"""
    ct = ContentType.objects.get_for_model(instance.__class__)
    
    nombre_display = instance.paciente.nombre_completo if instance.paciente else 'Sin Paciente'
    detalle = f"Diag: {instance.diagnostico or 'N/A'} | Med: {instance.medico or 'N/A'}"

    Movimiento.objects.update_or_create(
        content_type=ct,
        object_id=instance.pk,
        defaults={
            'accion': accion,
            'modulo_origen': instance.tipo_modulo, # Ahora usamos el Enum tipo_modulo
            'nombre_display': nombre_display,
            'detalle': detalle,
            'usuario': instance.usuario_registro,
            'activo': instance.activo,
            'created_at': instance.created_at or timezone.now(),
        }
    )

@receiver(post_save, sender=Morbilidad)
def morbilidad_post_save(sender, instance, created, **kwargs):
    # 1. Sincronizar con Movimientos (Reportes)
    accion = 'CREAR' if created else 'EDITAR'
    sync_movimiento(instance, accion)

    # 2. Gestionar estadísticas
    if instance.medico and instance.activo:
        # Intentamos obtener la especialidad directamente o del médico
        especialidad = instance.especialidad or instance.medico.especialidad
        
        if especialidad:
            fecha = instance.fecha_evento
            
            # Obtenemos o creamos la estadística para ese mes y año
            estadistica, _ = EstadisticaEspecialidad.objects.get_or_create(
                especialidad=especialidad,
                medico=instance.medico,
                mes=fecha.month,
                anio=fecha.year,
                defaults={'total_pacientes': 0}
            )
            
            # Si fue creado, incrementamos.
            if created:
                estadistica.total_pacientes += 1
                estadistica.save()

@receiver(post_delete, sender=Morbilidad)
def morbilidad_post_delete(sender, instance, **kwargs):
    # En caso de borrado físico, registramos ELIMINAR
    sync_movimiento(instance, 'ELIMINAR')

