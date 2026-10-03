# -*- coding: utf-8 -*-
from django.urls import path
from apps.jornadas import views

urlpatterns = [
    path('', views.lista_jornadas_view, name='lista_jornadas'),
    path('registrar_entrada/', views.registrar_entrada_view, name='registrar_entrada'),
    path('pausa_inicio/<int:pk>/', views.registrar_pausa_inicio_view, name='registrar_pausa_inicio'),
    path('pausa_fin/<int:pk>/', views.registrar_pausa_fin_view, name='registrar_pausa_fin'),
    path('salida/<int:pk>/', views.registrar_salida_view, name='registrar_salida'),
]
