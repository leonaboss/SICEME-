"""SICEME - Modelo de Jornadas Laborales"""
from django.db import models
from apps.especialistas.models import Especialista


class Jornada(models.Model):
    """Control de jornada laboral de especialistas"""
    especialista = models.ForeignKey(
        Especialista, on_delete=models.CASCADE,
        related_name='jornadas', verbose_name='Especialista'
    )
    hora_entrada = models.DateTimeField(null=True, blank=True, verbose_name='Hora de Entrada')
    hora_salida = models.DateTimeField(null=True, blank=True, verbose_name='Hora de Salida')
    pausa_inicio = models.DateTimeField(null=True, blank=True, verbose_name='Inicio de Pausa')
    pausa_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fin de Pausa')
    total_horas = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0, verbose_name='Total Horas'
    )
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        db_table = 'jornadas'
        verbose_name = 'Jornada'
        verbose_name_plural = 'Jornadas'
        ordering = ['-fecha', '-hora_entrada']

    def __str__(self):
        return f"{self.especialista.nombre_completo} - {self.fecha}"

    def calcular_horas(self):
        """Calcula el total de horas trabajadas descontando pausas"""
        if self.hora_entrada and self.hora_salida:
            total = (self.hora_salida - self.hora_entrada).total_seconds() / 3600
            if self.pausa_inicio and self.pausa_fin:
                pausa = (self.pausa_fin - self.pausa_inicio).total_seconds() / 3600
                total -= pausa
            self.total_horas = round(max(total, 0), 2)
            self.save(update_fields=['total_horas'])
        return self.total_horas
