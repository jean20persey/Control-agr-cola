from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from parcelas.models import Parcela
from cultivos.models import Cultivo

class RegistroProduccion(models.Model):
    """Modelo para registro y análisis de producción agrícola"""
    
    CALIDADES = [
        ('A', 'Excelente'),
        ('B', 'Buena'),
        ('C', 'Regular'),
        ('D', 'Deficiente'),
    ]
    
    # Información básica
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.CASCADE,
        related_name='registros_produccion',
        verbose_name='Parcela'
    )
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        related_name='registros_produccion',
        verbose_name='Cultivo'
    )
    fecha_registro = models.DateField(
        default=timezone.now,
        db_index=True,  # Para series temporales
        verbose_name='Fecha de registro'
    )
    temporada = models.CharField(
        max_length=20,
        db_index=True,  # Para análisis por temporada
        verbose_name='Temporada'
    )
    
    # Datos de producción
    cantidad_kg = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad producida (kg)'
    )
    rendimiento_hectarea = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Rendimiento por hectárea (kg/ha)'
    )
    calidad = models.CharField(
        max_length=1,
        choices=CALIDADES,
        blank=True, null=True,
        verbose_name='Calidad'
    )
    
    # Condiciones ambientales
    temperatura_promedio = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(-50), MaxValueValidator(60)],
        verbose_name='Temperatura promedio (°C)'
    )
    precipitacion_mm = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Precipitación (mm)'
    )
    humedad_relativa = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Humedad relativa (%)'
    )
    
    # Análisis estadístico
    desviacion_esperada = models.FloatField(
        blank=True, null=True,
        verbose_name='Desviación del rendimiento esperado'
    )
    anomalia_detectada = models.BooleanField(
        default=False,
        verbose_name='Anomalía detectada'
    )
    notas_anomalia = models.TextField(
        blank=True, null=True,
        verbose_name='Notas sobre anomalías'
    )
    
    # Datos adicionales flexibles
    datos_adicionales = models.JSONField(
        blank=True, null=True,
        verbose_name='Datos adicionales'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    
    class Meta:
        verbose_name = 'Registro de Producción'
        verbose_name_plural = 'Registros de Producción'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['parcela', 'fecha_registro']),  # Para series temporales
            models.Index(fields=['cultivo', 'temporada']),       # Para análisis por temporada
            models.Index(fields=['anomalia_detectada']),         # Para filtrar anomalías
        ]
    
    def __str__(self):
        return f"{self.parcela.codigo} - {self.cultivo.nombre} ({self.fecha_registro})"
    
    def save(self, *args, **kwargs):
        """Calcular métricas automáticamente al guardar"""
        # Calcular rendimiento por hectárea
        if self.parcela and self.cantidad_kg:
            self.rendimiento_hectarea = self.cantidad_kg / self.parcela.area_hectareas
        
        # Calcular desviación del rendimiento esperado
        if self.cultivo and self.rendimiento_hectarea:
            self.desviacion_esperada = self.rendimiento_hectarea - self.cultivo.rendimiento_esperado
            
            # Detectar anomalías (desviación mayor al 20% del rendimiento esperado)
            umbral_anomalia = self.cultivo.rendimiento_esperado * 0.2
            self.anomalia_detectada = abs(self.desviacion_esperada) > umbral_anomalia
        
        super().save(*args, **kwargs)
    
    @property
    def porcentaje_desviacion(self):
        """Porcentaje de desviación respecto al rendimiento esperado"""
        if self.cultivo and self.cultivo.rendimiento_esperado > 0:
            return (self.desviacion_esperada / self.cultivo.rendimiento_esperado) * 100
        return 0
    
    @property
    def eficiencia_rendimiento(self):
        """Eficiencia del rendimiento como porcentaje"""
        if self.cultivo and self.cultivo.rendimiento_esperado > 0:
            return (self.rendimiento_hectarea / self.cultivo.rendimiento_esperado) * 100
        return 0

class PrediccionCosecha(models.Model):
    """Modelo para almacenar predicciones de cosechas futuras"""
    
    MODELOS_PREDICCION = [
        ('linear', 'Regresión Lineal'),
        ('random_forest', 'Random Forest'),
        ('xgboost', 'XGBoost'),
        ('neural_network', 'Red Neuronal'),
    ]
    
    # Información básica
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.CASCADE,
        related_name='predicciones',
        verbose_name='Parcela'
    )
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        related_name='predicciones',
        verbose_name='Cultivo'
    )
    fecha_prediccion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de predicción'
    )
    temporada_objetivo = models.CharField(
        max_length=20,
        verbose_name='Temporada objetivo'
    )
    
    # Predicciones
    rendimiento_predicho = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Rendimiento predicho (kg/ha)'
    )
    confianza_prediccion = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name='Confianza de la predicción (0-1)'
    )
    rango_minimo = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Rango mínimo'
    )
    rango_maximo = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Rango máximo'
    )
    
    # Modelo utilizado
    modelo_utilizado = models.CharField(
        max_length=20,
        choices=MODELOS_PREDICCION,
        verbose_name='Modelo utilizado'
    )
    parametros_modelo = models.JSONField(
        blank=True, null=True,
        verbose_name='Parámetros del modelo'
    )
    
    # Validación posterior
    rendimiento_real = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Rendimiento real obtenido'
    )
    precision_prediccion = models.FloatField(
        blank=True, null=True,
        verbose_name='Precisión de la predicción (%)'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        verbose_name = 'Predicción de Cosecha'
        verbose_name_plural = 'Predicciones de Cosecha'
        ordering = ['-fecha_prediccion']
    
    def __str__(self):
        return f"Predicción {self.parcela.codigo} - {self.temporada_objetivo}"
    
    def calcular_precision(self):
        """Calcular precisión de la predicción cuando se conoce el resultado real"""
        if self.rendimiento_real and self.rendimiento_predicho > 0:
            error_absoluto = abs(self.rendimiento_real - self.rendimiento_predicho)
            error_relativo = (error_absoluto / self.rendimiento_real) * 100
            self.precision_prediccion = max(0, 100 - error_relativo)
            self.save()
            return self.precision_prediccion
        return None
