# -*- coding: utf-8 -*-
from django.urls import path
from apps.morbilidades import views

urlpatterns = [
    path('', views.lista_morbilidades_view, name='lista_morbilidades'),
    
    # Aliases de Listado (Compatibilidad)
    path('emergencias/', views.lista_morbilidades_view, {'tipo': 'EMERGENCIA'}, name='lista_emergencias'),
    path('especialistas/', views.lista_morbilidades_view, {'tipo': 'CONSULTA_ESPECIALISTA'}, name='lista_morbilidad_especialistas'),
    path('ecosonogramas/', views.lista_morbilidades_view, {'tipo': 'ECOSONOGRAMA'}, name='lista_ecosonogramas'),
    path('no-asistidos/', views.lista_morbilidades_view, {'tipo': 'NO_ASISTIDO'}, name='lista_no_asistidos'),
    
    # Aliases de Creación (Compatibilidad)
    path('crear/', views.crear_morbilidad_view, name='crear_morbilidad'),
    path('crear/emergencia/', views.crear_morbilidad_view, {'tipo': 'EMERGENCIA'}, name='crear_emergencia'),
    path('crear/especialista/', views.crear_morbilidad_view, {'tipo': 'CONSULTA_ESPECIALISTA'}, name='crear_morbilidad_especialista'),
    path('crear/ecosonograma/', views.crear_morbilidad_view, {'tipo': 'ECOSONOGRAMA'}, name='crear_ecosonograma'),
    path('crear/no-asistido/', views.crear_morbilidad_view, {'tipo': 'NO_ASISTIDO'}, name='crear_no_asistido'),
    
    # Aliases de Edición (Compatibilidad)
    path('editar/<int:pk>/', views.editar_morbilidad_view, name='editar_morbilidad'),
    path('editar/emergencia/<int:pk>/', views.editar_morbilidad_view, name='editar_emergencia'),
    path('editar/especialista/<int:pk>/', views.editar_morbilidad_view, name='editar_morbilidad_especialista'),
    path('editar/ecosonograma/<int:pk>/', views.editar_morbilidad_view, name='editar_ecosonograma'),
    path('editar/no-asistido/<int:pk>/', views.editar_morbilidad_view, name='editar_no_asistido'),
    
    # Aliases de Eliminación (Compatibilidad)
    path('eliminar/<int:pk>/', views.eliminar_morbilidad_view, name='eliminar_morbilidad'),
    path('eliminar/emergencia/<int:pk>/', views.eliminar_morbilidad_view, name='eliminar_emergencia'),
    path('eliminar/especialista/<int:pk>/', views.eliminar_morbilidad_view, name='eliminar_morbilidad_especialista'),
    path('eliminar/ecosonograma/<int:pk>/', views.eliminar_morbilidad_view, name='eliminar_ecosonograma'),
    path('eliminar/no-asistido/<int:pk>/', views.eliminar_morbilidad_view, name='eliminar_no_asistido'),
    
    # Aliases de Limpieza (Compatibilidad)
    path('limpiar/', views.limpiar_morbilidades_view, name='limpiar_morbilidades'),
    path('limpiar/emergencias/', views.limpiar_morbilidades_view, {'tipo': 'EMERGENCIA'}, name='limpiar_emergencias'),
    path('limpiar/especialistas/', views.limpiar_morbilidades_view, {'tipo': 'CONSULTA_ESPECIALISTA'}, name='limpiar_especialistas'),
    path('limpiar/ecosonogramas/', views.limpiar_morbilidades_view, {'tipo': 'ECOSONOGRAMA'}, name='limpiar_ecosonogramas'),
    path('limpiar/no-asistidos/', views.limpiar_morbilidades_view, {'tipo': 'NO_ASISTIDO'}, name='limpiar_no_asistidos'),

    # Rutas para Jornadas
    path('jornadas/', views.lista_jornadas_view, name='lista_jornadas'),
    path('jornadas/registrar_entrada/', views.registrar_entrada_view, name='registrar_entrada'),
    path('jornadas/pausa_inicio/<int:pk>/', views.registrar_pausa_inicio_view, name='registrar_pausa_inicio'),
    path('jornadas/pausa_fin/<int:pk>/', views.registrar_pausa_fin_view, name='registrar_pausa_fin'),
    path('jornadas/salida/<int:pk>/', views.registrar_salida_view, name='registrar_salida'),

    # Rutas para Especialidades
    path('especialidades/crud/', views.crud_especialidades_view, name='crud_especialidades'),
    path('especialidades/crear/', views.crear_especialidad_view, name='crear_especialidad'),
    path('especialidades/editar/<int:pk>/', views.editar_especialidad_view, name='editar_especialidad'),
    path('especialidades/eliminar/<int:pk>/', views.eliminar_especialidad_view, name='eliminar_especialidad'),

    # Rutas para Especialistas
    path('especialistas/crud/', views.crud_especialistas_view, name='crud_especialistas'),
    path('especialistas/crear/', views.crear_especialista_view, name='crear_especialista'),
    path('especialistas/editar/<int:pk>/', views.editar_especialista_view, name='editar_especialista'),
    path('especialistas/eliminar/<int:pk>/', views.eliminar_especialista_view, name='eliminar_especialista'),
]
