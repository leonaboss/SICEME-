"""SICEME - URLs de Especialistas"""
from django.urls import path
from . import views

urlpatterns = [
    # Especialidades
    path('especialidades/', views.lista_especialidades_view, name='crud_especialidades'),
    path('especialidades/crear/', views.crear_especialidad_view, name='crear_especialidad'),
    path('especialidades/editar/<int:pk>/', views.editar_especialidad_view, name='editar_especialidad'),
    path('especialidades/eliminar/<int:pk>/', views.eliminar_especialidad_view, name='eliminar_especialidad'),

    # Especialistas
    path('', views.lista_especialistas_view, name='crud_especialistas'),
    path('crear/', views.crear_especialista_view, name='crear_especialista'),
    path('editar/<int:pk>/', views.editar_especialista_view, name='editar_especialista'),
    path('eliminar/<int:pk>/', views.eliminar_especialista_view, name='eliminar_especialista'),
]
