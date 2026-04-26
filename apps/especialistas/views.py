"""SICEME - Vistas de Especialistas y Especialidades"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from .models import Especialidad, Especialista
from .forms import EspecialidadForm, EspecialistaForm


# ─────────────────────────────────────────────
# CRUD ESPECIALIDADES
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def lista_especialidades_view(request):
    query = request.GET.get('q', '')
    especialidades = Especialidad.objects.filter(activo=True)
    if query:
        especialidades = especialidades.filter(nombre__icontains=query)
    paginator = Paginator(especialidades, 15)
    page = request.GET.get('page')
    especialidades = paginator.get_page(page)
    return render(request, 'especialistas/lista_especialidades.html', {
        'especialidades': especialidades, 'query': query
    })


@login_required
@rol_requerido('ADMIN')
def crear_especialidad_view(request):
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            esp = form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Especialidad creada: {esp.nombre}', request, 'especialistas'
            )
            messages.success(request, f'Especialidad "{esp.nombre}" creada.')
            return redirect('crud_especialidades')
    else:
        form = EspecialidadForm()
    return render(request, 'especialistas/form_especialidad.html', {
        'form': form, 'titulo': 'Nueva Especialidad'
    })


@login_required
@rol_requerido('ADMIN')
def editar_especialidad_view(request, pk):
    esp = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=esp)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Especialidad editada: {esp.nombre}', request, 'especialistas'
            )
            messages.success(request, f'Especialidad "{esp.nombre}" actualizada.')
            return redirect('crud_especialidades')
    else:
        form = EspecialidadForm(instance=esp)
    return render(request, 'especialistas/form_especialidad.html', {
        'form': form, 'titulo': 'Editar Especialidad'
    })


@login_required
@rol_requerido('ADMIN')
def eliminar_especialidad_view(request, pk):
    esp = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        nombre = esp.nombre
        esp.activo = False
        esp.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Especialidad archivada (Soft Delete): {nombre}', request, 'especialistas'
        )
        messages.success(request, f'Especialidad "{nombre}" archivada exitosamente.')
        return redirect('crud_especialidades')
    return render(request, 'especialistas/eliminar_especialidad.html', {'especialidad': esp})


# ─────────────────────────────────────────────
# CRUD ESPECIALISTAS
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def lista_especialistas_view(request):
    query = request.GET.get('q', '')
    especialistas = Especialista.objects.select_related('especialidad', 'usuario').filter(activo=True)
    if query:
        especialistas = especialistas.filter(
            Q(nombre_completo__icontains=query) |
            Q(especialidad__nombre__icontains=query)
        )
    paginator = Paginator(especialistas, 15)
    page = request.GET.get('page')
    especialistas = paginator.get_page(page)
    return render(request, 'especialistas/lista_especialistas.html', {
        'especialistas': especialistas, 'query': query
    })


@login_required
@rol_requerido('ADMIN')
def crear_especialista_view(request):
    if request.method == 'POST':
        form = EspecialistaForm(request.POST)
        if form.is_valid():
            esp = form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Especialista creado: {esp.nombre_completo}', request, 'especialistas'
            )
            messages.success(request, f'Especialista "{esp.nombre_completo}" creado.')
            return redirect('crud_especialistas')
    else:
        form = EspecialistaForm()
    return render(request, 'especialistas/form_especialista.html', {
        'form': form, 
        'titulo': 'Nuevo Especialista',
        'especialidades': Especialidad.objects.all().order_by('nombre')
    })


@login_required
@rol_requerido('ADMIN')
def editar_especialista_view(request, pk):
    esp = get_object_or_404(Especialista, pk=pk)
    if request.method == 'POST':
        form = EspecialistaForm(request.POST, instance=esp)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Especialista editado: {esp.nombre_completo}', request, 'especialistas'
            )
            messages.success(request, f'Especialista "{esp.nombre_completo}" actualizado.')
            return redirect('crud_especialistas')
    else:
        form = EspecialistaForm(instance=esp)
    return render(request, 'especialistas/form_especialista.html', {
        'form': form, 
        'titulo': 'Editar Especialista',
        'especialidades': Especialidad.objects.all().order_by('nombre')
    })


@login_required
@rol_requerido('ADMIN')
def eliminar_especialista_view(request, pk):
    esp = get_object_or_404(Especialista, pk=pk)
    if request.method == 'POST':
        nombre = esp.nombre_completo
        esp.activo = False
        esp.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Especialista archivado (Soft Delete): {nombre}', request, 'especialistas'
        )
        messages.success(request, f'Especialista "{nombre}" archivado exitosamente.')
        return redirect('crud_especialistas')
    return render(request, 'especialistas/eliminar_especialista.html', {'especialista': esp})
