# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models

from apps.usuarios.decorators import rol_requerido
from apps.jornadas.models import Jornada
from apps.morbilidades.models import Especialista


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_jornadas_view(request):
    """Listado de jornadas laborales"""
    registros = Jornada.objects.all().select_related('especialista')
    especialistas_lista = Especialista.objects.filter(activo=True)
    
    total_horas = registros.aggregate(models.Sum('total_horas'))['total_horas__sum'] or 0
    
    paginator = Paginator(registros, 20)
    page = request.GET.get('page')
    registros = paginator.get_page(page)
    
    return render(request, 'jornadas/lista.html', {
        'jornadas': registros,
        'especialistas_lista': especialistas_lista,
        'total_horas': total_horas
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_entrada_view(request):
    if request.method == 'POST':
        especialista_id = request.POST.get('especialista_id')
        if not especialista_id and request.user.rol == 'ESPECIALISTA':
            if hasattr(request.user, 'especialista_perfil') and request.user.especialista_perfil:
                especialista_id = request.user.especialista_perfil.pk
        
        if especialista_id:
            especialista = get_object_or_404(Especialista, pk=especialista_id)
            Jornada.objects.create(especialista=especialista, hora_entrada=timezone.now())
            messages.success(request, 'Entrada registrada.')
        else:
            messages.error(request, 'Especialista no válido.')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_inicio_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.pausa_inicio = timezone.now()
    jornada.save()
    messages.success(request, 'Pausa iniciada.')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_fin_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.pausa_fin = timezone.now()
    jornada.save()
    messages.success(request, 'Pausa finalizada.')
    return redirect('lista_jornadas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_salida_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.hora_salida = timezone.now()
    jornada.calcular_horas()
    messages.success(request, 'Salida registrada.')
    return redirect('lista_jornadas')
