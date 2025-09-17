from django.contrib import admin
from .models import AnalisisComparativo, ClasificacionRendimiento, AnalisisSeriesTemporal

@admin.register(AnalisisComparativo)
class AnalisisComparativoAdmin(admin.ModelAdmin):
    """Administración de análisis comparativos"""
    
    list_display = [
        'nombre_analisis', 'tipo_analisis', 'diferencia_significativa',
        'p_valor', 'fecha_analisis', 'creado_por'
    ]
    list_filter = ['tipo_analisis', 'diferencia_significativa', 'fecha_analisis']
    search_fields = ['nombre_analisis', 'descripcion']
    ordering = ['-fecha_analisis']
    date_hierarchy = 'fecha_analisis'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_analisis', 'descripcion', 'tipo_analisis')
        }),
        ('Cultivos y Filtros', {
            'fields': ('cultivos', 'temporada', 'fecha_inicio', 'fecha_fin')
        }),
        ('Resultados Estadísticos', {
            'fields': (
                'estadistico', 'p_valor', 'nivel_significancia',
                'diferencia_significativa'
            )
        }),
        ('Resultados Detallados', {
            'fields': ('resultados_detallados',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_analisis', 'creado_por'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_analisis']
    filter_horizontal = ['cultivos']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('cultivos')

@admin.register(ClasificacionRendimiento)
class ClasificacionRendimientoAdmin(admin.ModelAdmin):
    """Administración de clasificaciones de rendimiento"""
    
    list_display = [
        'nombre_clasificacion', 'algoritmo_utilizado', 'cultivo',
        'temporada', 'fecha_clasificacion', 'creado_por'
    ]
    list_filter = ['algoritmo_utilizado', 'cultivo', 'fecha_clasificacion']
    search_fields = ['nombre_clasificacion', 'cultivo__nombre']
    ordering = ['-fecha_clasificacion']
    date_hierarchy = 'fecha_clasificacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_clasificacion', 'algoritmo_utilizado')
        }),
        ('Filtros Aplicados', {
            'fields': ('cultivo', 'temporada')
        }),
        ('Parámetros y Resultados', {
            'fields': ('parametros_algoritmo', 'resultados_clasificacion'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('estadisticas_generales',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_clasificacion', 'creado_por'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_clasificacion']

@admin.register(AnalisisSeriesTemporal)
class AnalisisSeriesTemporalAdmin(admin.ModelAdmin):
    """Administración de análisis de series temporales"""
    
    list_display = [
        'parcela', 'cultivo', 'tipo_tendencia', 'total_registros',
        'rendimiento_promedio', 'outliers_detectados', 'fecha_analisis', 'creado_por'
    ]
    list_filter = ['tipo_tendencia', 'cultivo', 'fecha_analisis']
    search_fields = ['parcela__codigo', 'parcela__nombre', 'cultivo__nombre']
    ordering = ['-fecha_analisis']
    date_hierarchy = 'fecha_analisis'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('parcela', 'cultivo', 'fecha_inicio', 'fecha_fin', 'total_registros')
        }),
        ('Análisis de Tendencia', {
            'fields': ('tipo_tendencia', 'pendiente', 'r_cuadrado')
        }),
        ('Estadísticas Descriptivas', {
            'fields': (
                'rendimiento_promedio', 'desviacion_estandar', 'coeficiente_variacion',
                'rendimiento_minimo', 'rendimiento_maximo'
            )
        }),
        ('Detección de Outliers', {
            'fields': ('outliers_detectados', 'outliers_detalle'),
            'classes': ('collapse',)
        }),
        ('Análisis por Temporadas', {
            'fields': ('analisis_temporadas',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_analisis', 'creado_por'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_analisis']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parcela', 'cultivo', 'creado_por')
