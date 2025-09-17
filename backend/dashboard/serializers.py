from rest_framework import serializers

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    
    # Resumen general
    total_parcelas = serializers.IntegerField()
    parcelas_activas = serializers.IntegerField()
    total_cultivos = serializers.IntegerField()
    total_registros_produccion = serializers.IntegerField()
    
    # Producción
    produccion_total_kg = serializers.FloatField()
    rendimiento_promedio = serializers.FloatField()
    area_total_hectareas = serializers.FloatField()
    area_cultivada_hectareas = serializers.FloatField()
    
    # Anomalías y calidad
    anomalias_detectadas = serializers.IntegerField()
    porcentaje_anomalias = serializers.FloatField()
    distribucion_calidades = serializers.DictField()
    
    # Tendencias
    crecimiento_mensual = serializers.FloatField()
    eficiencia_promedio = serializers.FloatField()

class GraficoSerieTemporalSerializer(serializers.Serializer):
    """Serializer para datos de gráficos de series temporales"""
    
    fecha = serializers.DateField()
    valor = serializers.FloatField()
    categoria = serializers.CharField(required=False)

class GraficoBarrasSerializer(serializers.Serializer):
    """Serializer para datos de gráficos de barras"""
    
    etiqueta = serializers.CharField()
    valor = serializers.FloatField()
    color = serializers.CharField(required=False)

class GraficoPieSerializer(serializers.Serializer):
    """Serializer para datos de gráficos de pie"""
    
    etiqueta = serializers.CharField()
    valor = serializers.FloatField()
    porcentaje = serializers.FloatField()
    color = serializers.CharField(required=False)

class KPISerializer(serializers.Serializer):
    """Serializer para KPIs individuales"""
    
    nombre = serializers.CharField()
    valor = serializers.FloatField()
    unidad = serializers.CharField()
    tendencia = serializers.CharField()  # 'up', 'down', 'stable'
    cambio_porcentual = serializers.FloatField()
    descripcion = serializers.CharField()

class DashboardCompleteSerializer(serializers.Serializer):
    """Serializer completo para el dashboard"""
    
    estadisticas_generales = DashboardStatsSerializer()
    kpis_principales = serializers.ListField(child=KPISerializer())
    grafico_produccion_mensual = serializers.ListField(child=GraficoSerieTemporalSerializer())
    grafico_rendimiento_cultivos = serializers.ListField(child=GraficoBarrasSerializer())
    grafico_distribucion_calidades = serializers.ListField(child=GraficoPieSerializer())
    grafico_estados_parcelas = serializers.ListField(child=GraficoPieSerializer())
    top_parcelas_rendimiento = serializers.ListField()
    alertas_anomalias = serializers.ListField()
    predicciones_recientes = serializers.ListField()
