from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Movimiento(models.Model):
    """
    Tabla centralizada de movimientos (Registro unificado de actividad).
    Materializa en una sola tabla lo que antes se consultaba en 4 diferentes.
    """
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
    ]

    MODULO_CHOICES = [
        ('EMERGENCIA', 'Emergencia'),
        ('CONSULTA_ESPECIALISTA', 'Consulta Especialista'),
        ('ECOSONOGRAMA', 'Ecosonograma'),
        ('NO_ASISTIDO', 'No Asistido'),
    ]

    accion = models.CharField('Acción Realizada', max_length=20, choices=ACCION_CHOICES, default='CREAR')
    modulo_origen = models.CharField('Módulo Origen', max_length=30, choices=MODULO_CHOICES, default='EMERGENCIA')
    nombre_display = models.CharField('Nombre de Paciente', max_length=255)
    detalle = models.CharField('Detalles Adicionales', max_length=255, blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movimientos_generados'
    )
    created_at = models.DateTimeField('Fecha de Registro', default=timezone.now)
    activo = models.BooleanField('Activo', default=True)

    # Relación genérica al registro original (para trazabilidad y restaurar/eliminar)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    registro_original = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['activo', 'created_at']),
            models.Index(fields=['accion']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_accion_display()} - {self.nombre_display} ({self.created_at.strftime('%d/%m/%Y')})"
class CierreMes(models.Model):
    """
    Registro formal de cierre de mes para la Biblioteca Histórica.
    """
    mes = models.PositiveIntegerField()
    anio = models.PositiveIntegerField()
    fecha_cierre = models.DateTimeField('Fecha de Cierre', auto_now_add=True)
    usuario_cierre = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cierres_realizados'
    )
    total_registros = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Cierre de Mes'
        verbose_name_plural = 'Cierres de Meses'
        unique_together = ['mes', 'anio']
        ordering = ['-anio', '-mes']

    def __str__(self):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"Cierre {meses[self.mes-1]} {self.anio}"
