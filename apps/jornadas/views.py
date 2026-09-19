"""SICEME - Vistas de Jornadas Laborales"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from apps.especialistas.models import Especialista
from .models import Jornada


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def lista_jornadas_view(request):
    """Listado de jornadas laborales"""
    if request.user.rol == 'ADMIN':
        jornadas = Jornada.objects.select_related('especialista').all()
    else:
        try:
            esp = request.user.especialista_perfil
            jornadas = Jornada.objects.filter(especialista=esp)
        except Exception:
            jornadas = Jornada.objects.none()

    # Filtro por mes/año
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    if mes:
        jornadas = jornadas.filter(fecha__month=mes)
    if anio:
        jornadas = jornadas.filter(fecha__year=anio)

    total_horas = jornadas.aggregate(total=Sum('total_horas'))['total'] or 0

    paginator = Paginator(jornadas, 15)
    page = request.GET.get('page')
    jornadas = paginator.get_page(page)

    especialistas_lista = []
    if request.user.rol == 'ADMIN':
        especialistas_lista = Especialista.objects.all()

    return render(request, 'jornadas/lista.html', {
        'jornadas': jornadas,
        'total_horas': total_horas,
        'especialistas_lista': especialistas_lista,
        'filtros': {'mes': mes or '', 'anio': anio or ''}
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_entrada_view(request):
    """Registrar hora de entrada"""
    if request.method == 'POST':
        try:
            if request.user.rol == 'ADMIN':
                esp_id = request.POST.get('especialista_id')
                especialista = get_object_or_404(Especialista, pk=esp_id)
            else:
                especialista = request.user.especialista_perfil

            jornada = Jornada.objects.create(
                especialista=especialista,
                hora_entrada=timezone.now()
            )
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Entrada registrada: {especialista.nombre_completo}', request, 'jornadas'
            )
            messages.success(request, f'Entrada registrada a las {timezone.now().strftime("%H:%M")}.')
        except Exception as e:
            messages.error(request, f'Error al registrar entrada: {str(e)}')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_salida_view(request, pk):
    """Registrar hora de salida"""
    jornada = get_object_or_404(Jornada, pk=pk)
    if request.method == 'POST':
        jornada.hora_salida = timezone.now()
        jornada.save()
        jornada.calcular_horas()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.EDITAR,
            f'Salida registrada: {jornada.especialista.nombre_completo} - {jornada.total_horas}h',
            request, 'jornadas'
        )
        messages.success(request, f'Salida registrada. Total: {jornada.total_horas} horas.')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_inicio_view(request, pk):
    """Registrar inicio de pausa"""
    jornada = get_object_or_404(Jornada, pk=pk)
    if request.method == 'POST':
        jornada.pausa_inicio = timezone.now()
        jornada.save()
        messages.info(request, 'Pausa iniciada.')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_fin_view(request, pk):
    """Registrar fin de pausa"""
    jornada = get_object_or_404(Jornada, pk=pk)
    if request.method == 'POST':
        jornada.pausa_fin = timezone.now()
        jornada.save()
        messages.info(request, 'Pausa finalizada.')
    return redirect('lista_jornadas')
