from rest_framework import serializers
from .models import Parcela, HistorialParcela
from cultivos.serializers import CultivoListSerializer

class ParcelaSerializer(serializers.ModelSerializer):
    """Serializer completo para parcelas"""
    
    cultivo_actual_info = CultivoListSerializer(source='cultivo_actual', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    tiene_cultivo = serializers.ReadOnlyField()
    dias_desde_siembra = serializers.ReadOnlyField()
    area_metros_cuadrados = serializers.ReadOnlyField()
    
    class Meta:
        model = Parcela
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'area_hectareas', 'area_metros_cuadrados',
            'ubicacion_lat', 'ubicacion_lng', 'ubicacion_completa', 'altitud',
            'tipo_suelo', 'ph_suelo', 'materia_organica', 'capacidad_campo',
            'cultivo_actual', 'cultivo_actual_info', 'fecha_siembra', 'fecha_cosecha_estimada',
            'estado', 'tiene_riego', 'tipo_riego', 'activa', 'fecha_creacion',
            'fecha_actualizacion', 'tiene_cultivo', 'dias_desde_siembra'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

class ParcelaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear parcelas"""
    
    class Meta:
        model = Parcela
        fields = [
            'codigo', 'nombre', 'descripcion', 'area_hectareas',
            'ubicacion_lat', 'ubicacion_lng', 'altitud',
            'tipo_suelo', 'ph_suelo', 'materia_organica', 'capacidad_campo',
            'tiene_riego', 'tipo_riego'
        ]
    
    def validate_codigo(self, value):
        """Validar que el código sea único"""
        if Parcela.objects.filter(codigo__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una parcela con este código")
        return value.upper()

class ParcelaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de parcelas"""
    
    cultivo_actual_nombre = serializers.CharField(source='cultivo_actual.nombre', read_only=True)
    tiene_cultivo = serializers.ReadOnlyField()
    
    class Meta:
        model = Parcela
        fields = [
            'id', 'codigo', 'nombre', 'area_hectareas', 'estado',
            'cultivo_actual', 'cultivo_actual_nombre', 'fecha_siembra',
            'activa', 'tiene_cultivo'
        ]

class ParcelaAsignarCultivoSerializer(serializers.Serializer):
    """Serializer para asignar cultivo a parcela"""
    
    cultivo_id = serializers.IntegerField()
    fecha_siembra = serializers.DateField()
    fecha_cosecha_estimada = serializers.DateField(required=False)
    
    def validate_cultivo_id(self, value):
        from cultivos.models import Cultivo
        try:
            cultivo = Cultivo.objects.get(id=value, activo=True)
            return value
        except Cultivo.DoesNotExist:
            raise serializers.ValidationError("Cultivo no encontrado o inactivo")
    
    def validate(self, data):
        if data.get('fecha_cosecha_estimada') and data['fecha_cosecha_estimada'] <= data['fecha_siembra']:
            raise serializers.ValidationError("La fecha de cosecha debe ser posterior a la siembra")
        return data

class HistorialParcelaSerializer(serializers.ModelSerializer):
    """Serializer para historial de parcelas"""
    
    cultivo_info = CultivoListSerializer(source='cultivo', read_only=True)
    duracion_ciclo = serializers.ReadOnlyField()
    
    class Meta:
        model = HistorialParcela
        fields = [
            'id', 'parcela', 'cultivo', 'cultivo_info', 'fecha_siembra',
            'fecha_cosecha', 'rendimiento_obtenido', 'observaciones',
            'duracion_ciclo', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']

class ParcelaStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de parcelas"""
    
    total_parcelas = serializers.IntegerField()
    parcelas_activas = serializers.IntegerField()
    parcelas_con_cultivo = serializers.IntegerField()
    parcelas_disponibles = serializers.IntegerField()
    area_total = serializers.FloatField()
    area_cultivada = serializers.FloatField()
    distribucion_estados = serializers.ListField()
    distribucion_suelos = serializers.ListField()
