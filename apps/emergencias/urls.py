"""SICEME - URLs de Emergencias"""
from django.urls import path
from . import views

urlpatterns = [
    # Morbilidad Emergencias
    path('', views.lista_emergencias_view, name='lista_emergencias'),
    path('crear/', views.crear_emergencia_view, name='crear_emergencia'),
    path('editar/<int:pk>/', views.editar_emergencia_view, name='editar_emergencia'),
    path('eliminar/<int:pk>/', views.eliminar_emergencia_view, name='eliminar_emergencia'),

    # Morbilidad Especialistas
    path('especialistas/', views.lista_morbilidad_especialistas_view, name='lista_morbilidad_especialistas'),
    path('especialistas/crear/', views.crear_morbilidad_especialista_view, name='crear_morbilidad_especialista'),
    path('especialistas/editar/<int:pk>/', views.editar_morbilidad_especialista_view, name='editar_morbilidad_especialista'),
    path('especialistas/eliminar/<int:pk>/', views.eliminar_morbilidad_especialista_view, name='eliminar_morbilidad_especialista'),

    # Pacientes No Asistidos
    path('no-asistidos/', views.lista_no_asistidos_view, name='lista_no_asistidos'),
    path('no-asistidos/crear/', views.crear_no_asistido_view, name='crear_no_asistido'),
    path('no-asistidos/editar/<int:pk>/', views.editar_no_asistido_view, name='editar_no_asistido'),
    path('no-asistidos/eliminar/<int:pk>/', views.eliminar_no_asistido_view, name='eliminar_no_asistido'),

    # Limpiar (Archivar masivo)
    path('limpiar/', views.limpiar_emergencias_view, name='limpiar_emergencias'),
    path('especialistas/limpiar/', views.limpiar_especialistas_view, name='limpiar_especialistas'),
    path('no-asistidos/limpiar/', views.limpiar_no_asistidos_view, name='limpiar_no_asistidos'),
]
