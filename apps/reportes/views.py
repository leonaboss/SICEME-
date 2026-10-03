# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
from apps.morbilidades.models import Morbilidad, EstadisticaEspecialidad
from .models import Movimiento
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """Dashboard principal restaurado y conectado a Morbilidad centralizada"""
    hoy = timezone.localtime(timezone.now())
    mes_actual = hoy.month
    anio_actual = hoy.year
    es_admin = request.user.rol == 'ADMIN'
    filtro_usuario = {} if es_admin else {'usuario_registro': request.user}

    stats = Morbilidad.objects.filter(activo=True, **filtro_usuario).values('tipo_modulo').annotate(total=Count('id'))
    stats_dict = {item['tipo_modulo']: item['total'] for item in stats}

    total_movimientos = Movimiento.objects.filter(activo=True, **filtro_usuario).count()
    
    # Nuevos datos para el dashboard
    ultimos_registros = Morbilidad.objects.filter(activo=True, **filtro_usuario).order_by('-created_at')[:10]
    top_especialidades = EstadisticaEspecialidad.objects.filter(anio=anio_actual).values('especialidad__nombre').annotate(total=Sum('total_pacientes')).order_by('-total')

    context = {
        'total_emergencias': stats_dict.get('EMERGENCIA', 0),
        'total_especialistas_morb': stats_dict.get('CONSULTA_ESPECIALISTA', 0),
        'total_no_asistidos': stats_dict.get('NO_ASISTIDO', 0),
        'total_ecosonogramas': stats_dict.get('ECOSONOGRAMA', 0),
        'total_movimientos': total_movimientos,
        'emergencias_mes': Morbilidad.objects.filter(tipo_modulo='EMERGENCIA', activo=True, fecha_evento__month=mes_actual, fecha_evento__year=anio_actual, **filtro_usuario).count(),
        'fecha_actual': hoy.strftime('%d/%m/%Y'),
        'es_admin': es_admin,
        # Variables faltantes
        'ultimos_registros': ultimos_registros,
        'top_especialidades': top_especialidades,
        'anio_actual': anio_actual,
    }
    return render(request, 'dashboard/dashboard.html', context)

from django.db.models.functions import ExtractMonth
from django.db.models import Count, Sum

# ... (rest of imports)

@login_required
def api_dashboard_data(request):
    anio = request.GET.get('anio', timezone.now().year)
    es_admin = request.user.rol == 'ADMIN'
    filtro_usuario = {} if es_admin else {'usuario_registro': request.user}
    
    # Base queryset
    base_qs = Morbilidad.objects.filter(activo=True, fecha_evento__year=anio, **filtro_usuario)
    
    # 1. Emergencias mensual
    emergencias_mensual = base_qs.filter(tipo_modulo='EMERGENCIA').values('fecha_evento__month').annotate(total=Count('id')).order_by('fecha_evento__month')
    
    # 2. Por especialidad
    por_especialidad = base_qs.filter(tipo_modulo='CONSULTA_ESPECIALISTA').values('especialidad__nombre').annotate(total=Count('id')).order_by('-total')
    
    # 3. Top Médicos
    top_medicos = base_qs.filter(medico__isnull=False).values('medico__nombre_completo').annotate(total=Count('id')).order_by('-total')[:5]
    
    # 4. No asistidos por especialidad
    no_asistidos = base_qs.filter(tipo_modulo='NO_ASISTIDO').values('especialidad__nombre').annotate(total=Count('id')).order_by('-total')
    
    # 5. Ecosonogramas mensual
    ecosonogramas_mensual = base_qs.filter(tipo_modulo='ECOSONOGRAMA').values('fecha_evento__month').annotate(total=Count('id')).order_by('fecha_evento__month')
    
    # 6. Ecos por tipo
    eco_por_tipo = base_qs.filter(tipo_modulo='ECOSONOGRAMA').values('tipo_ecosonograma').annotate(total=Count('id')).order_by('-total')

    def format_mensual(data):
        res = {'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], 'data': [0]*12}
        for item in data:
            if item['fecha_evento__month']:
                res['data'][item['fecha_evento__month']-1] = item['total']
        return res

    data = {
        'anio': anio,
        'emergencias_mensual': format_mensual(emergencias_mensual),
        'por_especialidad': {
            'labels': [i['especialidad__nombre'] for i in por_especialidad],
            'data': [i['total'] for i in por_especialidad],
            'total': sum([i['total'] for i in por_especialidad])
        },
        'top_medicos': {
            'labels': [i['medico__nombre_completo'] for i in top_medicos],
            'data': [i['total'] for i in top_medicos]
        },
        'no_asistidos': {
            'labels': [i['especialidad__nombre'] for i in no_asistidos],
            'data': [i['total'] for i in no_asistidos]
        },
        'ecosonogramas_mensual': format_mensual(ecosonogramas_mensual),
        'eco_por_tipo': {
            'labels': [i['tipo_ecosonograma'] for i in eco_por_tipo],
            'data': [i['total'] for i in eco_por_tipo],
            'total': sum([i['total'] for i in eco_por_tipo])
        },
        'vigilancia_centinela': None # Opcional si no se usa
    }
    return JsonResponse(data)

@login_required
def api_estadisticas_especialidad(request):
    return JsonResponse({'estadisticas': []})

@login_required
def reporte_especialidades_view(request):
    return render(request, 'reportes/especialidades.html', {})

@login_required
def reporte_emergencias_mes_view(request):
    return render(request, 'reportes/emergencias_mes.html', {})

@login_required
def reporte_ecosonogramas_enfermedades_view(request):
    return render(request, 'reportes/ecosonogramas_enfermedades.html', {})

@login_required
def reporte_no_asistidos_view(request):
    return render(request, 'reportes/no_asistidos.html', {})

@login_required
def reporte_top_medicos_view(request):
    return render(request, 'reportes/top_medicos.html', {})

@login_required
def reporte_periodo_view(request):
    return render(request, 'reportes/reporte_periodo.html', {})

@login_required
def exportar_reporte_periodo_excel_view(request):
    return redirect('reporte_periodo')

@login_required
def exportar_excel_view(request):
    return redirect('dashboard')

@login_required
def importar_excel_view(request):
    return redirect('dashboard')

@login_required
def movimientos_view(request):
    return render(request, 'reportes/movimientos.html', {})

@login_required
def monitor_view(request):
    return render(request, 'reportes/monitor.html', {})

@login_required
def restaurar_registro_view(request):
    return redirect('movimientos')

@login_required
def eliminar_registro_permanente_view(request):
    return redirect('movimientos')

@login_required
def limpiar_actividad_global_view(request):
    return redirect('movimientos')

@login_required
def restaurar_masivo_view(request):
    return redirect('movimientos')

@login_required
def limpiar_archivados_view(request):
    return redirect('movimientos')

@login_required
def biblioteca_view(request):
    return render(request, 'reportes/biblioteca.html', {})

@login_required
def cerrar_mes_view(request):
    return redirect('biblioteca')

@login_required
def auto_organizar_biblioteca_view(request):
    return redirect('biblioteca')
