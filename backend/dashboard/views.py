from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict

from .serializers import (
    DashboardStatsSerializer,
    DashboardCompleteSerializer,
    KPISerializer,
    GraficoSerieTemporalSerializer,
    GraficoBarrasSerializer,
    GraficoPieSerializer
)
from produccion.models import RegistroProduccion, PrediccionCosecha
from cultivos.models import Cultivo
from parcelas.models import Parcela

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    """Obtener estadísticas principales del dashboard"""
    
    # Estadísticas básicas
    total_parcelas = Parcela.objects.count()
    parcelas_activas = Parcela.objects.filter(activa=True).count()
    total_cultivos = Cultivo.objects.filter(activo=True).count()
    total_registros = RegistroProduccion.objects.count()
    
    # Producción y área
    produccion_stats = RegistroProduccion.objects.aggregate(
        produccion_total=Sum('cantidad_kg'),
        rendimiento_promedio=Avg('rendimiento_hectarea')
    )
    
    area_stats = Parcela.objects.filter(activa=True).aggregate(
        area_total=Sum('area_hectareas')
    )
    
    area_cultivada = Parcela.objects.filter(
        activa=True,
        cultivo_actual__isnull=False
    ).aggregate(
        area_cultivada=Sum('area_hectareas')
    )
    
    # Anomalías
    anomalias = RegistroProduccion.objects.filter(anomalia_detectada=True).count()
    porcentaje_anomalias = (anomalias / total_registros * 100) if total_registros > 0 else 0
    
    # Distribución de calidades
    calidades = RegistroProduccion.objects.exclude(
        calidad__isnull=True
    ).values('calidad').annotate(
        cantidad=Count('id')
    )
    distribucion_calidades = {item['calidad']: item['cantidad'] for item in calidades}
    
    # Crecimiento mensual (últimos 30 días vs 30 días anteriores)
    hace_30_dias = timezone.now().date() - timedelta(days=30)
    hace_60_dias = timezone.now().date() - timedelta(days=60)
    
    produccion_reciente = RegistroProduccion.objects.filter(
        fecha_registro__gte=hace_30_dias
    ).aggregate(
        total=Sum('cantidad_kg')
    )['total'] or 0
    
    produccion_anterior = RegistroProduccion.objects.filter(
        fecha_registro__gte=hace_60_dias,
        fecha_registro__lt=hace_30_dias
    ).aggregate(
        total=Sum('cantidad_kg')
    )['total'] or 0
    
    crecimiento_mensual = 0
    if produccion_anterior > 0:
        crecimiento_mensual = ((produccion_reciente - produccion_anterior) / produccion_anterior) * 100
    
    # Eficiencia promedio
    eficiencia_promedio = RegistroProduccion.objects.aggregate(
        eficiencia=Avg('rendimiento_hectarea')
    )['eficiencia'] or 0
    
    data = {
        'total_parcelas': total_parcelas,
        'parcelas_activas': parcelas_activas,
        'total_cultivos': total_cultivos,
        'total_registros_produccion': total_registros,
        'produccion_total_kg': float(produccion_stats['produccion_total'] or 0),
        'rendimiento_promedio': float(produccion_stats['rendimiento_promedio'] or 0),
        'area_total_hectareas': float(area_stats['area_total'] or 0),
        'area_cultivada_hectareas': float(area_cultivada['area_cultivada'] or 0),
        'anomalias_detectadas': anomalias,
        'porcentaje_anomalias': float(porcentaje_anomalias),
        'distribucion_calidades': distribucion_calidades,
        'crecimiento_mensual': float(crecimiento_mensual),
        'eficiencia_promedio': float(eficiencia_promedio)
    }
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_kpis_view(request):
    """Obtener KPIs principales"""
    
    # KPI 1: Rendimiento Promedio
    rendimiento_actual = RegistroProduccion.objects.aggregate(
        promedio=Avg('rendimiento_hectarea')
    )['promedio'] or 0
    
    # Comparar con mes anterior
    hace_30_dias = timezone.now().date() - timedelta(days=30)
    rendimiento_anterior = RegistroProduccion.objects.filter(
        fecha_registro__lt=hace_30_dias
    ).aggregate(
        promedio=Avg('rendimiento_hectarea')
    )['promedio'] or 0
    
    cambio_rendimiento = 0
    if rendimiento_anterior > 0:
        cambio_rendimiento = ((rendimiento_actual - rendimiento_anterior) / rendimiento_anterior) * 100
    
    # KPI 2: Producción Total
    produccion_total = RegistroProduccion.objects.aggregate(
        total=Sum('cantidad_kg')
    )['total'] or 0
    
    # KPI 3: Eficiencia de Parcelas
    parcelas_con_cultivo = Parcela.objects.filter(
        activa=True,
        cultivo_actual__isnull=False
    ).count()
    
    total_parcelas_activas = Parcela.objects.filter(activa=True).count()
    eficiencia_parcelas = (parcelas_con_cultivo / total_parcelas_activas * 100) if total_parcelas_activas > 0 else 0
    
    # KPI 4: Tasa de Anomalías
    total_registros = RegistroProduccion.objects.count()
    anomalias = RegistroProduccion.objects.filter(anomalia_detectada=True).count()
    tasa_anomalias = (anomalias / total_registros * 100) if total_registros > 0 else 0
    
    kpis = [
        {
            'nombre': 'Rendimiento Promedio',
            'valor': float(rendimiento_actual),
            'unidad': 'kg/ha',
            'tendencia': 'up' if cambio_rendimiento > 0 else 'down' if cambio_rendimiento < 0 else 'stable',
            'cambio_porcentual': float(cambio_rendimiento),
            'descripcion': 'Rendimiento promedio por hectárea'
        },
        {
            'nombre': 'Producción Total',
            'valor': float(produccion_total),
            'unidad': 'kg',
            'tendencia': 'up',
            'cambio_porcentual': 0.0,
            'descripcion': 'Producción total acumulada'
        },
        {
            'nombre': 'Eficiencia de Parcelas',
            'valor': float(eficiencia_parcelas),
            'unidad': '%',
            'tendencia': 'stable',
            'cambio_porcentual': 0.0,
            'descripcion': 'Porcentaje de parcelas en uso'
        },
        {
            'nombre': 'Tasa de Anomalías',
            'valor': float(tasa_anomalias),
            'unidad': '%',
            'tendencia': 'down' if tasa_anomalias < 10 else 'up',
            'cambio_porcentual': 0.0,
            'descripcion': 'Porcentaje de registros con anomalías'
        }
    ]
    
    serializer = KPISerializer(kpis, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_graficos_view(request):
    """Obtener datos para gráficos del dashboard"""
    
    # Gráfico 1: Producción mensual (últimos 12 meses)
    hace_12_meses = timezone.now().date() - timedelta(days=365)
    
    produccion_mensual = RegistroProduccion.objects.filter(
        fecha_registro__gte=hace_12_meses
    ).extra(
        select={'mes': "DATE_TRUNC('month', fecha_registro)"}
    ).values('mes').annotate(
        total_produccion=Sum('cantidad_kg')
    ).order_by('mes')
    
    grafico_produccion = [
        {
            'fecha': item['mes'],
            'valor': float(item['total_produccion']),
            'categoria': 'produccion'
        }
        for item in produccion_mensual
    ]
    
    # Gráfico 2: Rendimiento por cultivo
    rendimiento_cultivos = RegistroProduccion.objects.values(
        'cultivo__nombre'
    ).annotate(
        rendimiento_promedio=Avg('rendimiento_hectarea'),
        registros=Count('id')
    ).filter(registros__gte=3).order_by('-rendimiento_promedio')[:10]
    
    grafico_rendimiento = [
        {
            'etiqueta': item['cultivo__nombre'],
            'valor': float(item['rendimiento_promedio']),
            'color': f'hsl({i * 36}, 70%, 50%)'
        }
        for i, item in enumerate(rendimiento_cultivos)
    ]
    
    # Gráfico 3: Distribución de calidades
    calidades = RegistroProduccion.objects.exclude(
        calidad__isnull=True
    ).values('calidad').annotate(
        cantidad=Count('id')
    )
    
    total_con_calidad = sum(item['cantidad'] for item in calidades)
    colores_calidad = {'A': '#4CAF50', 'B': '#8BC34A', 'C': '#FFC107', 'D': '#F44336'}
    
    grafico_calidades = [
        {
            'etiqueta': f'Calidad {item["calidad"]}',
            'valor': float(item['cantidad']),
            'porcentaje': float((item['cantidad'] / total_con_calidad) * 100) if total_con_calidad > 0 else 0,
            'color': colores_calidad.get(item['calidad'], '#9E9E9E')
        }
        for item in calidades
    ]
    
    # Gráfico 4: Estados de parcelas
    estados_parcelas = Parcela.objects.filter(activa=True).values('estado').annotate(
        cantidad=Count('id')
    )
    
    total_parcelas = sum(item['cantidad'] for item in estados_parcelas)
    colores_estado = {
        'disponible': '#2196F3',
        'sembrada': '#4CAF50',
        'en_crecimiento': '#8BC34A',
        'lista_cosecha': '#FF9800',
        'cosechada': '#9C27B0',
        'en_descanso': '#607D8B'
    }
    
    grafico_estados = [
        {
            'etiqueta': item['estado'].replace('_', ' ').title(),
            'valor': float(item['cantidad']),
            'porcentaje': float((item['cantidad'] / total_parcelas) * 100) if total_parcelas > 0 else 0,
            'color': colores_estado.get(item['estado'], '#9E9E9E')
        }
        for item in estados_parcelas
    ]
    
    return Response({
        'produccion_mensual': grafico_produccion,
        'rendimiento_cultivos': grafico_rendimiento,
        'distribucion_calidades': grafico_calidades,
        'estados_parcelas': grafico_estados
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_alertas_view(request):
    """Obtener alertas y notificaciones"""
    
    # Alertas de anomalías recientes (últimos 7 días)
    hace_7_dias = timezone.now().date() - timedelta(days=7)
    anomalias_recientes = RegistroProduccion.objects.filter(
        anomalia_detectada=True,
        fecha_registro__gte=hace_7_dias
    ).select_related('parcela', 'cultivo').order_by('-fecha_registro')[:10]
    
    alertas_anomalias = [
        {
            'tipo': 'anomalia',
            'titulo': f'Anomalía en {registro.parcela.codigo}',
            'descripcion': f'Rendimiento anómalo en {registro.cultivo.nombre}: {registro.rendimiento_hectarea:.1f} kg/ha',
            'fecha': registro.fecha_registro,
            'severidad': 'alta' if abs(registro.porcentaje_desviacion) > 30 else 'media',
            'parcela': registro.parcela.codigo,
            'cultivo': registro.cultivo.nombre
        }
        for registro in anomalias_recientes
    ]
    
    # Predicciones recientes
    predicciones_recientes = PrediccionCosecha.objects.select_related(
        'parcela', 'cultivo'
    ).order_by('-fecha_prediccion')[:5]
    
    alertas_predicciones = [
        {
            'tipo': 'prediccion',
            'titulo': f'Nueva predicción para {pred.parcela.codigo}',
            'descripcion': f'Rendimiento estimado: {pred.rendimiento_predicho:.1f} kg/ha (Confianza: {pred.confianza_prediccion*100:.1f}%)',
            'fecha': pred.fecha_prediccion,
            'severidad': 'info',
            'parcela': pred.parcela.codigo,
            'cultivo': pred.cultivo.nombre if pred.cultivo else 'N/A'
        }
        for pred in predicciones_recientes
    ]
    
    # Parcelas que necesitan atención
    parcelas_atencion = Parcela.objects.filter(
        activa=True,
        estado='lista_cosecha'
    ).select_related('cultivo_actual')[:5]
    
    alertas_parcelas = [
        {
            'tipo': 'parcela',
            'titulo': f'Parcela {parcela.codigo} lista para cosecha',
            'descripcion': f'Cultivo: {parcela.cultivo_actual.nombre if parcela.cultivo_actual else "N/A"}',
            'fecha': timezone.now().date(),
            'severidad': 'media',
            'parcela': parcela.codigo,
            'cultivo': parcela.cultivo_actual.nombre if parcela.cultivo_actual else 'N/A'
        }
        for parcela in parcelas_atencion
    ]
    
    todas_alertas = alertas_anomalias + alertas_predicciones + alertas_parcelas
    todas_alertas.sort(key=lambda x: x['fecha'], reverse=True)
    
    return Response(todas_alertas[:15])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_completo_view(request):
    """Obtener datos completos del dashboard"""
    
    # Obtener todos los datos
    stats_response = dashboard_stats_view(request)
    kpis_response = dashboard_kpis_view(request)
    graficos_response = dashboard_graficos_view(request)
    alertas_response = dashboard_alertas_view(request)
    
    # Top parcelas por rendimiento
    top_parcelas = RegistroProduccion.objects.values(
        'parcela__codigo', 'parcela__nombre'
    ).annotate(
        rendimiento_promedio=Avg('rendimiento_hectarea'),
        registros=Count('id')
    ).filter(registros__gte=3).order_by('-rendimiento_promedio')[:5]
    
    data = {
        'estadisticas_generales': stats_response.data,
        'kpis_principales': kpis_response.data,
        'grafico_produccion_mensual': graficos_response.data['produccion_mensual'],
        'grafico_rendimiento_cultivos': graficos_response.data['rendimiento_cultivos'],
        'grafico_distribucion_calidades': graficos_response.data['distribucion_calidades'],
        'grafico_estados_parcelas': graficos_response.data['estados_parcelas'],
        'top_parcelas_rendimiento': list(top_parcelas),
        'alertas_anomalias': [a for a in alertas_response.data if a['tipo'] == 'anomalia'],
        'predicciones_recientes': [a for a in alertas_response.data if a['tipo'] == 'prediccion']
    }
    
    serializer = DashboardCompleteSerializer(data)
    return Response(serializer.data)
