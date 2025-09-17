from rest_framework import serializers
from .models import RegistroProduccion, PrediccionCosecha
from parcelas.serializers import ParcelaListSerializer
from cultivos.serializers import CultivoListSerializer

class RegistroProduccionSerializer(serializers.ModelSerializer):
    """Serializer completo para registros de producción"""
    
    parcela_info = ParcelaListSerializer(source='parcela', read_only=True)
    cultivo_info = CultivoListSerializer(source='cultivo', read_only=True)
    porcentaje_desviacion = serializers.ReadOnlyField()
    eficiencia_rendimiento = serializers.ReadOnlyField()
    
    class Meta:
        model = RegistroProduccion
        fields = [
            'id', 'parcela', 'parcela_info', 'cultivo', 'cultivo_info',
            'fecha_registro', 'temporada', 'cantidad_kg', 'rendimiento_hectarea',
            'calidad', 'temperatura_promedio', 'precipitacion_mm', 'humedad_relativa',
            'desviacion_esperada', 'anomalia_detectada', 'notas_anomalia',
            'porcentaje_desviacion', 'eficiencia_rendimiento', 'datos_adicionales',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'rendimiento_hectarea', 'desviacion_esperada', 'anomalia_detectada',
            'fecha_creacion', 'fecha_actualizacion'
        ]

class RegistroProduccionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear registros de producción"""
    
    class Meta:
        model = RegistroProduccion
        fields = [
            'parcela', 'cultivo', 'fecha_registro', 'temporada', 'cantidad_kg',
            'calidad', 'temperatura_promedio', 'precipitacion_mm', 'humedad_relativa',
            'notas_anomalia', 'datos_adicionales'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        parcela = data.get('parcela')
        cultivo = data.get('cultivo')
        
        # Validar que la parcela esté activa
        if parcela and not parcela.activa:
            raise serializers.ValidationError("La parcela no está activa")
        
        # Validar que el cultivo esté activo
        if cultivo and not cultivo.activo:
            raise serializers.ValidationError("El cultivo no está activo")
        
        return data

class RegistroProduccionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de registros"""
    
    parcela_codigo = serializers.CharField(source='parcela.codigo', read_only=True)
    cultivo_nombre = serializers.CharField(source='cultivo.nombre', read_only=True)
    eficiencia_rendimiento = serializers.ReadOnlyField()
    
    class Meta:
        model = RegistroProduccion
        fields = [
            'id', 'parcela', 'parcela_codigo', 'cultivo', 'cultivo_nombre',
            'fecha_registro', 'temporada', 'cantidad_kg', 'rendimiento_hectarea',
            'calidad', 'anomalia_detectada', 'eficiencia_rendimiento'
        ]

class PrediccionCosechaSerializer(serializers.ModelSerializer):
    """Serializer para predicciones de cosecha"""
    
    parcela_info = ParcelaListSerializer(source='parcela', read_only=True)
    cultivo_info = CultivoListSerializer(source='cultivo', read_only=True)
    
    class Meta:
        model = PrediccionCosecha
        fields = [
            'id', 'parcela', 'parcela_info', 'cultivo', 'cultivo_info',
            'fecha_prediccion', 'temporada_objetivo', 'rendimiento_predicho',
            'confianza_prediccion', 'rango_minimo', 'rango_maximo',
            'modelo_utilizado', 'parametros_modelo', 'rendimiento_real',
            'precision_prediccion', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'precision_prediccion', 'fecha_creacion']

class PrediccionCreateSerializer(serializers.Serializer):
    """Serializer para crear predicciones"""
    
    parcela_id = serializers.IntegerField()
    cultivo_id = serializers.IntegerField()
    temporada_objetivo = serializers.CharField(max_length=20)
    modelo = serializers.ChoiceField(
        choices=['linear', 'random_forest', 'xgboost'],
        default='linear'
    )
    
    def validate_parcela_id(self, value):
        from parcelas.models import Parcela
        try:
            parcela = Parcela.objects.get(id=value, activa=True)
            return value
        except Parcela.DoesNotExist:
            raise serializers.ValidationError("Parcela no encontrada o inactiva")
    
    def validate_cultivo_id(self, value):
        from cultivos.models import Cultivo
        try:
            cultivo = Cultivo.objects.get(id=value, activo=True)
            return value
        except Cultivo.DoesNotExist:
            raise serializers.ValidationError("Cultivo no encontrado o inactivo")

class EstadisticasProduccionSerializer(serializers.Serializer):
    """Serializer para estadísticas de producción"""
    
    total_registros = serializers.IntegerField()
    produccion_total = serializers.FloatField()
    rendimiento_promedio = serializers.FloatField()
    anomalias_detectadas = serializers.IntegerField()
    porcentaje_anomalias = serializers.FloatField()
    distribucion_calidad = serializers.DictField()
    top_parcelas = serializers.ListField()

class SerieTemporalSerializer(serializers.Serializer):
    """Serializer para series temporales"""
    
    fecha = serializers.DateField()
    rendimiento = serializers.FloatField()
    cantidad = serializers.FloatField()
    temporada = serializers.CharField()
    anomalia = serializers.BooleanField()
    temperatura = serializers.FloatField(allow_null=True)
    precipitacion = serializers.FloatField(allow_null=True)
