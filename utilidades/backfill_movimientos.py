import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Registros.settings')
django.setup()

from apps.reportes.models import Movimiento
from apps.emergencias.models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from apps.ecosonogramas.models import MorbilidadEcosonograma
from django.contrib.contenttypes.models import ContentType

def backfill():
    print("Iniciando sincronización histórica de Movimientos...")
    
    # Emergencias
    ct_em = ContentType.objects.get_for_model(MorbilidadEmergencia)
    for obj in MorbilidadEmergencia.objects.all():
        Movimiento.objects.get_or_create(
            content_type=ct_em,
            object_id=obj.pk,
            defaults={
                'tipo_mov': 'emergencia',
                'nombre_display': obj.nombre_apellido,
                'detalle': obj.medico,
                'usuario': obj.usuario,
                'activo': obj.activo,
                'created_at': obj.created_at
            }
        )
    print(f"- Emergencias: {MorbilidadEmergencia.objects.count()} registros procesados.")

    # Especialistas (en apps.emergencias.models)
    ct_es = ContentType.objects.get_for_model(MorbilidadEspecialista)
    for obj in MorbilidadEspecialista.objects.all():
        Movimiento.objects.get_or_create(
            content_type=ct_es,
            object_id=obj.pk,
            defaults={
                'tipo_mov': 'especialista',
                'nombre_display': obj.nombre_apellido,
                'detalle': f"{obj.especialista} - {obj.especialidad}",
                'usuario': obj.usuario,
                'activo': obj.activo,
                'created_at': obj.created_at
            }
        )
    print(f"- Especialistas: {MorbilidadEspecialista.objects.count()} registros procesados.")

    # No Asistidos
    ct_na = ContentType.objects.get_for_model(PacienteNoAsistido)
    for obj in PacienteNoAsistido.objects.all():
        Movimiento.objects.get_or_create(
            content_type=ct_na,
            object_id=obj.pk,
            defaults={
                'tipo_mov': 'no_asistido',
                'nombre_display': obj.nombre_completo,
                'detalle': f"{obj.medico} - {obj.especialidad}",
                'usuario': obj.usuario,
                'activo': obj.activo,
                'created_at': obj.created_at
            }
        )
    print(f"- No Asistidos: {PacienteNoAsistido.objects.count()} registros procesados.")

    # Ecosonogramas
    ct_eco = ContentType.objects.get_for_model(MorbilidadEcosonograma)
    for obj in MorbilidadEcosonograma.objects.all():
        Movimiento.objects.get_or_create(
            content_type=ct_eco,
            object_id=obj.pk,
            defaults={
                'tipo_mov': 'ecosonograma',
                'nombre_display': obj.nombre_apellido,
                'detalle': f"{obj.tipo_eco} - {obj.medico}",
                'usuario': obj.usuario,
                'activo': obj.activo,
                'created_at': obj.created_at
            }
        )
    print(f"- Ecosonogramas: {MorbilidadEcosonograma.objects.count()} registros procesados.")

    print("\n¡Sincronización completada exitosamente!")

if __name__ == '__main__':
    backfill()
