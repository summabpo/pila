# pila_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('pila/planillas/', views.crear_planilla, name='crear_planilla'),
    path('pila/planillas/<int:planilla_id>/', views.consultar_planilla, name='consultar_planilla'),
    path('pila/planillas/<int:planilla_id>/archivo/', views.descargar_archivo, name='descargar_archivo'),
    #path('pila/planillas/by-ref/<str:numero_interno>/', views.consultar_por_referencia, name='consultar_por_referencia'),
    path("pila/planillas/<int:planilla_id>/detalles/", views.listar_detalles, name="pila_listar_detalles"),
    path("pila/planillas/<int:planilla_id>/calcular/",views.calcular_planilla_view, name="pila_calcular_planilla",),
]