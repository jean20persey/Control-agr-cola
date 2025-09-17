from django.db import models
from django.utils import timezone
from cultivos.models import Cultivo
from parcelas.models import Parcela

class AnalisisComparativo(models.Model):
    """Modelo para almacenar análisis comparativos entre variedades"""
    
    TIPOS_ANALISIS = [
        ('t_test', 'Prueba T de Student'),
        ('mann_whitney', 'Prueba Mann-Whitney U'),
        ('anova', 'Análisis de Varianza (ANOVA)'),
        ('kruskal_wallis', 'Prueba Kruskal-Wallis'),
    ]
    
    # Información básica
    nombre_analisis = models.CharField(
        max_length=200,
        verbose_name='Nombre del análisis'
    )
    descripcion = models.TextField(
        blank=True, null=True,
        verbose_name='Descripción'
    )
    tipo_analisis = models.CharField(
        max_length=20,
        choices=TIPOS_ANALISIS,
        verbose_name='Tipo de análisis'
    )
    
    # Cultivos comparados
    cultivos = models.ManyToManyField(
        Cultivo,
        related_name='analisis_comparativos',
        verbose_name='Cultivos comparados'
    )
    
    # Filtros aplicados
    temporada = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name='Temporada'
    )
    fecha_inicio = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha de inicio'
    )
    fecha_fin = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha de fin'
    )
    
    # Resultados del análisis
    estadistico = models.FloatField(
        verbose_name='Estadístico de prueba'
    )
    p_valor = models.FloatField(
        verbose_name='Valor p'
    )
    nivel_significancia = models.FloatField(
        default=0.05,
        verbose_name='Nivel de significancia'
    )
    diferencia_significativa = models.BooleanField(
        verbose_name='Diferencia significativa'
    )
    
    # Estadísticas descriptivas
    resultados_detallados = models.JSONField(
        verbose_name='Resultados detallados'
    )
    
    # Metadatos
    fecha_analisis = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha del análisis'
    )
    creado_por = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Análisis Comparativo'
        verbose_name_plural = 'Análisis Comparativos'
        ordering = ['-fecha_analisis']
    
    def __str__(self):
        return f"{self.nombre_analisis} ({self.get_tipo_analisis_display()})"

class ClasificacionRendimiento(models.Model):
    """Modelo para almacenar clasificaciones de parcelas por rendimiento"""
    
    ALGORITMOS_CLASIFICACION = [
        ('percentiles', 'Clasificación por Percentiles'),
        ('kmeans', 'K-Means Clustering'),
        ('quartiles', 'Clasificación por Cuartiles'),
        ('zscore', 'Clasificación por Z-Score'),
    ]
    
    CATEGORIAS_RENDIMIENTO = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('bajo', 'Bajo'),
    ]
    
    # Información básica
    nombre_clasificacion = models.CharField(
        max_length=200,
        verbose_name='Nombre de la clasificación'
    )
    algoritmo_utilizado = models.CharField(
        max_length=20,
        choices=ALGORITMOS_CLASIFICACION,
        verbose_name='Algoritmo utilizado'
    )
    
    # Filtros aplicados
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name='Cultivo filtrado'
    )
    temporada = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name='Temporada'
    )
    
    # Parámetros del algoritmo
    parametros_algoritmo = models.JSONField(
        verbose_name='Parámetros del algoritmo'
    )
    
    # Resultados de la clasificación
    resultados_clasificacion = models.JSONField(
        verbose_name='Resultados de la clasificación'
    )
    estadisticas_generales = models.JSONField(
        verbose_name='Estadísticas generales'
    )
    
    # Metadatos
    fecha_clasificacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de clasificación'
    )
    creado_por = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Clasificación de Rendimiento'
        verbose_name_plural = 'Clasificaciones de Rendimiento'
        ordering = ['-fecha_clasificacion']
    
    def __str__(self):
        return f"{self.nombre_clasificacion} ({self.get_algoritmo_utilizado_display()})"

class AnalisisSeriesTemporal(models.Model):
    """Modelo para almacenar análisis de series temporales"""
    
    TIPOS_TENDENCIA = [
        ('creciente', 'Tendencia Creciente'),
        ('decreciente', 'Tendencia Decreciente'),
        ('estable', 'Tendencia Estable'),
        ('ciclica', 'Tendencia Cíclica'),
    ]
    
    # Información básica
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.CASCADE,
        related_name='analisis_series',
        verbose_name='Parcela'
    )
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name='Cultivo'
    )
    
    # Período de análisis
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de fin')
    total_registros = models.IntegerField(verbose_name='Total de registros')
    
    # Análisis de tendencia
    tipo_tendencia = models.CharField(
        max_length=20,
        choices=TIPOS_TENDENCIA,
        verbose_name='Tipo de tendencia'
    )
    pendiente = models.FloatField(verbose_name='Pendiente de la tendencia')
    r_cuadrado = models.FloatField(verbose_name='Coeficiente R²')
    
    # Estadísticas descriptivas
    rendimiento_promedio = models.FloatField(verbose_name='Rendimiento promedio')
    desviacion_estandar = models.FloatField(verbose_name='Desviación estándar')
    coeficiente_variacion = models.FloatField(verbose_name='Coeficiente de variación')
    rendimiento_minimo = models.FloatField(verbose_name='Rendimiento mínimo')
    rendimiento_maximo = models.FloatField(verbose_name='Rendimiento máximo')
    
    # Detección de valores atípicos
    outliers_detectados = models.IntegerField(
        default=0,
        verbose_name='Outliers detectados'
    )
    outliers_detalle = models.JSONField(
        blank=True, null=True,
        verbose_name='Detalle de outliers'
    )
    
    # Análisis por temporadas
    analisis_temporadas = models.JSONField(
        blank=True, null=True,
        verbose_name='Análisis por temporadas'
    )
    
    # Metadatos
    fecha_analisis = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha del análisis'
    )
    creado_por = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Análisis de Series Temporal'
        verbose_name_plural = 'Análisis de Series Temporales'
        ordering = ['-fecha_analisis']
    
    def __str__(self):
        return f"Serie Temporal {self.parcela.codigo} ({self.fecha_inicio} - {self.fecha_fin})"
