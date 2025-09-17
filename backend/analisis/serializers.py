from rest_framework import serializers
from .models import AnalisisComparativo, ClasificacionRendimiento, AnalisisSeriesTemporal
from cultivos.serializers import CultivoListSerializer
from parcelas.serializers import ParcelaListSerializer

class AnalisisComparativoSerializer(serializers.ModelSerializer):
    """Serializer para análisis comparativos"""
    
    cultivos_info = CultivoListSerializer(source='cultivos', many=True, read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.full_name', read_only=True)
    
    class Meta:
        model = AnalisisComparativo
        fields = [
            'id', 'nombre_analisis', 'descripcion', 'tipo_analisis',
            'cultivos', 'cultivos_info', 'temporada', 'fecha_inicio', 'fecha_fin',
            'estadistico', 'p_valor', 'nivel_significancia', 'diferencia_significativa',
            'resultados_detallados', 'fecha_analisis', 'creado_por', 'creado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_analisis', 'creado_por']

class ComparacionVariedadesSerializer(serializers.Serializer):
    """Serializer para solicitar comparación de variedades"""
    
    cultivo_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5
    )
    temporada = serializers.CharField(max_length=20, required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    tipo_analisis = serializers.ChoiceField(
        choices=['t_test', 'mann_whitney', 'anova', 'kruskal_wallis'],
        default='t_test'
    )
    nivel_significancia = serializers.FloatField(default=0.05, min_value=0.01, max_value=0.1)
    
    def validate_cultivo_ids(self, value):
        from cultivos.models import Cultivo
        cultivos_existentes = Cultivo.objects.filter(id__in=value, activo=True).count()
        if cultivos_existentes != len(value):
            raise serializers.ValidationError("Algunos cultivos no existen o no están activos")
        return value
    
    def validate(self, data):
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_inicio'] >= data['fecha_fin']:
                raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        return data

class ClasificacionRendimientoSerializer(serializers.ModelSerializer):
    """Serializer para clasificaciones de rendimiento"""
    
    cultivo_info = CultivoListSerializer(source='cultivo', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.full_name', read_only=True)
    
    class Meta:
        model = ClasificacionRendimiento
        fields = [
            'id', 'nombre_clasificacion', 'algoritmo_utilizado', 'cultivo', 'cultivo_info',
            'temporada', 'parametros_algoritmo', 'resultados_clasificacion',
            'estadisticas_generales', 'fecha_clasificacion', 'creado_por', 'creado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_clasificacion', 'creado_por']

class ClasificarPorRendimientoSerializer(serializers.Serializer):
    """Serializer para solicitar clasificación por rendimiento"""
    
    algoritmo = serializers.ChoiceField(
        choices=['percentiles', 'kmeans', 'quartiles', 'zscore'],
        default='quartiles'
    )
    cultivo_id = serializers.IntegerField(required=False)
    temporada = serializers.CharField(max_length=20, required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    
    def validate_cultivo_id(self, value):
        if value:
            from cultivos.models import Cultivo
            try:
                Cultivo.objects.get(id=value, activo=True)
                return value
            except Cultivo.DoesNotExist:
                raise serializers.ValidationError("Cultivo no encontrado o inactivo")
        return value

class AnalisisSeriesTemporalSerializer(serializers.ModelSerializer):
    """Serializer para análisis de series temporales"""
    
    parcela_info = ParcelaListSerializer(source='parcela', read_only=True)
    cultivo_info = CultivoListSerializer(source='cultivo', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.full_name', read_only=True)
    
    class Meta:
        model = AnalisisSeriesTemporal
        fields = [
            'id', 'parcela', 'parcela_info', 'cultivo', 'cultivo_info',
            'fecha_inicio', 'fecha_fin', 'total_registros', 'tipo_tendencia',
            'pendiente', 'r_cuadrado', 'rendimiento_promedio', 'desviacion_estandar',
            'coeficiente_variacion', 'rendimiento_minimo', 'rendimiento_maximo',
            'outliers_detectados', 'outliers_detalle', 'analisis_temporadas',
            'fecha_analisis', 'creado_por', 'creado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_analisis', 'creado_por']

class AnalizarSerieTemporalSerializer(serializers.Serializer):
    """Serializer para solicitar análisis de serie temporal"""
    
    parcela_id = serializers.IntegerField()
    cultivo_id = serializers.IntegerField(required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    
    def validate_parcela_id(self, value):
        from parcelas.models import Parcela
        try:
            Parcela.objects.get(id=value, activa=True)
            return value
        except Parcela.DoesNotExist:
            raise serializers.ValidationError("Parcela no encontrada o inactiva")
    
    def validate_cultivo_id(self, value):
        if value:
            from cultivos.models import Cultivo
            try:
                Cultivo.objects.get(id=value, activo=True)
                return value
            except Cultivo.DoesNotExist:
                raise serializers.ValidationError("Cultivo no encontrado o inactivo")
        return value

class EstadisticasGeneralesSerializer(serializers.Serializer):
    """Serializer para estadísticas generales del sistema"""
    
    total_registros = serializers.IntegerField()
    total_parcelas = serializers.IntegerField()
    total_cultivos = serializers.IntegerField()
    produccion_total = serializers.FloatField()
    rendimiento_promedio = serializers.FloatField()
    anomalias_total = serializers.IntegerField()
    porcentaje_anomalias = serializers.FloatField()
    distribucion_temporadas = serializers.ListField()
    top_cultivos_rendimiento = serializers.ListField()
    distribucion_calidades = serializers.DictField()
    eficiencia_promedio = serializers.FloatField()
