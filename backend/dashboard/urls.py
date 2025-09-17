from django.urls import path
from .views import (
    dashboard_stats_view,
    dashboard_kpis_view,
    dashboard_graficos_view,
    dashboard_alertas_view,
    dashboard_completo_view
)

urlpatterns = [
    # Dashboard principal
    path('', dashboard_completo_view, name='dashboard-completo'),
    
    # Componentes individuales
    path('stats/', dashboard_stats_view, name='dashboard-stats'),
    path('kpis/', dashboard_kpis_view, name='dashboard-kpis'),
    path('graficos/', dashboard_graficos_view, name='dashboard-graficos'),
    path('alertas/', dashboard_alertas_view, name='dashboard-alertas'),
]
