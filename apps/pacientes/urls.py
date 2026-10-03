# -*- coding: utf-8 -*-
from django.urls import path
from apps.pacientes import views

urlpatterns = [
    path('', views.lista_pacientes_view, name='lista_pacientes'),
    path('crear/', views.crear_paciente_view, name='crear_paciente'),
    path('editar/<int:pk>/', views.editar_paciente_view, name='editar_paciente'),
    path('detalle/<int:pk>/', views.detalle_paciente_view, name='detalle_paciente'),
]
