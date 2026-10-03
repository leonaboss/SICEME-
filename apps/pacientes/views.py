# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from apps.pacientes.models import Paciente
from apps.pacientes.forms import PacienteForm


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_pacientes_view(request):
    """Listado centralizado de pacientes"""
    query = request.GET.get('q', '')
    registros = Paciente.objects.filter(activo=True)

    if query:
        registros = registros.filter(
            Q(nombre_completo__icontains=query) |
            Q(cedula__icontains=query) |
            Q(dependencia__icontains=query)
        )

    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    return render(request, 'pacientes/lista.html', {
        'registros': registros,
        'query': query
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_paciente_view(request):
    """Registrar un nuevo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Paciente creado: {paciente.nombre_completo} ({paciente.cedula})', request, 'pacientes'
            )
            messages.success(request, 'Paciente registrado exitosamente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()

    return render(request, 'pacientes/form.html', {
        'form': form,
        'titulo': 'Registrar Nuevo Paciente'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_paciente_view(request, pk):
    """Editar datos demográficos de un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Paciente actualizado: {paciente.nombre_completo} ({paciente.cedula})', request, 'pacientes'
            )
            messages.success(request, 'Datos del paciente actualizados.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'pacientes/form.html', {
        'form': form,
        'titulo': 'Editar Datos de Paciente'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def detalle_paciente_view(request, pk):
    """Historial médico completo del paciente (todas sus morbilidades unificadas)"""
    paciente = get_object_or_404(Paciente, pk=pk)
    morbilidades = paciente.morbilidades.filter(activo=True).select_related('medico', 'especialidad', 'usuario_registro')
    
    return render(request, 'pacientes/detalle.html', {
        'paciente': paciente,
        'morbilidades': morbilidades
    })
