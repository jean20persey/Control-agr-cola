from rest_framework import serializers
from .models import Cultivo

class CultivoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Cultivo"""
    
    nombre_completo = serializers.ReadOnlyField()
    rango_temperatura = serializers.ReadOnlyField()
    rango_ph = serializers.ReadOnlyField()
    
    class Meta:
        model = Cultivo
        fields = [
            'id', 'nombre', 'variedad', 'tipo', 'ciclo_dias', 'rendimiento_esperado',
            'descripcion', 'temperatura_optima_min', 'temperatura_optima_max',
            'ph_suelo_min', 'ph_suelo_max', 'precipitacion_anual', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'nombre_completo',
            'rango_temperatura', 'rango_ph'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que temperatura mínima sea menor que máxima
        temp_min = data.get('temperatura_optima_min')
        temp_max = data.get('temperatura_optima_max')
        
        if temp_min and temp_max and temp_min >= temp_max:
            raise serializers.ValidationError(
                "La temperatura mínima debe ser menor que la máxima"
            )
        
        # Validar que pH mínimo sea menor que máximo
        ph_min = data.get('ph_suelo_min')
        ph_max = data.get('ph_suelo_max')
        
        if ph_min and ph_max and ph_min >= ph_max:
            raise serializers.ValidationError(
                "El pH mínimo debe ser menor que el máximo"
            )
        
        return data

class CultivoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear cultivos"""
    
    class Meta:
        model = Cultivo
        fields = [
            'nombre', 'variedad', 'tipo', 'ciclo_dias', 'rendimiento_esperado',
            'descripcion', 'temperatura_optima_min', 'temperatura_optima_max',
            'ph_suelo_min', 'ph_suelo_max', 'precipitacion_anual'
        ]
    
    def validate_nombre(self, value):
        """Validar que el nombre sea único"""
        if Cultivo.objects.filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un cultivo con este nombre")
        return value

class CultivoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de cultivos"""
    
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Cultivo
        fields = [
            'id', 'nombre', 'variedad', 'tipo', 'ciclo_dias', 
            'rendimiento_esperado', 'activo', 'nombre_completo'
        ]

class CultivoStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de cultivos"""
    
    total_cultivos = serializers.IntegerField()
    cultivos_activos = serializers.IntegerField()
    tipos_disponibles = serializers.ListField(child=serializers.CharField())
    rendimiento_promedio = serializers.FloatField()
    ciclo_promedio = serializers.FloatField()
