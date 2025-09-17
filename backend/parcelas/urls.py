from django.urls import path
from .views import (
    ParcelaListCreateView,
    ParcelaDetailView,
    parcela_por_codigo_view,
    asignar_cultivo_view,
    cosechar_parcela_view,
    parcelas_disponibles_view,
    parcelas_por_cultivo_view,
    parcelas_stats_view,
    historial_parcela_view
)

urlpatterns = [
    # CRUD básico
    path('', ParcelaListCreateView.as_view(), name='parcela-list-create'),
    path('<int:pk>/', ParcelaDetailView.as_view(), name='parcela-detail'),
    
    # Acceso por código (índice hash)
    path('codigo/<str:codigo>/', parcela_por_codigo_view, name='parcela-por-codigo'),
    
    # Gestión de cultivos
    path('<int:pk>/asignar-cultivo/', asignar_cultivo_view, name='asignar-cultivo'),
    path('<int:pk>/cosechar/', cosechar_parcela_view, name='cosechar-parcela'),
    
    # Filtros y búsquedas
    path('disponibles/', parcelas_disponibles_view, name='parcelas-disponibles'),
    path('cultivo/<int:cultivo_id>/', parcelas_por_cultivo_view, name='parcelas-por-cultivo'),
    
    # Estadísticas e historial
    path('stats/', parcelas_stats_view, name='parcelas-stats'),
    path('<int:pk>/historial/', historial_parcela_view, name='historial-parcela'),
]
