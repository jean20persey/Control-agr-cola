from django.contrib import admin
from .models import RegistroProduccion, PrediccionCosecha

@admin.register(RegistroProduccion)
class RegistroProduccionAdmin(admin.ModelAdmin):
    """Administración de registros de producción"""
    
    list_display = [
        'parcela', 'cultivo', 'fecha_registro', 'temporada',
        'cantidad_kg', 'rendimiento_hectarea', 'calidad',
        'anomalia_detectada', 'eficiencia_rendimiento'
    ]
    list_filter = [
        'temporada', 'calidad', 'anomalia_detectada',
        'fecha_registro', 'cultivo', 'parcela'
    ]
    search_fields = [
        'parcela__codigo', 'parcela__nombre',
        'cultivo__nombre', 'temporada'
    ]
    ordering = ['-fecha_registro']
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('parcela', 'cultivo', 'fecha_registro', 'temporada')
        }),
        ('Datos de Producción', {
            'fields': (
                'cantidad_kg', 'rendimiento_hectarea', 'calidad'
            )
        }),
        ('Condiciones Ambientales', {
            'fields': (
                'temperatura_promedio', 'precipitacion_mm', 'humedad_relativa'
            ),
            'classes': ('collapse',)
        }),
        ('Análisis Estadístico', {
            'fields': (
                'desviacion_esperada', 'anomalia_detectada', 'notas_anomalia'
            )
        }),
        ('Datos Adicionales', {
            'fields': ('datos_adicionales',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'rendimiento_hectarea', 'desviacion_esperada', 'anomalia_detectada',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    actions = ['marcar_sin_anomalia', 'recalcular_metricas']
    
    def eficiencia_rendimiento(self, obj):
        """Mostrar eficiencia del rendimiento"""
        return f"{obj.eficiencia_rendimiento:.1f}%"
    eficiencia_rendimiento.short_description = "Eficiencia (%)"
    
    def marcar_sin_anomalia(self, request, queryset):
        """Acción para marcar registros sin anomalía"""
        updated = queryset.update(anomalia_detectada=False)
        self.message_user(request, f'{updated} registros marcados sin anomalía.')
    marcar_sin_anomalia.short_description = "Marcar sin anomalía"
    
    def recalcular_metricas(self, request, queryset):
        """Acción para recalcular métricas de los registros"""
        for registro in queryset:
            registro.save()  # Esto ejecutará el método save() que recalcula las métricas
        self.message_user(request, f'Métricas recalculadas para {queryset.count()} registros.')
    recalcular_metricas.short_description = "Recalcular métricas"

@admin.register(PrediccionCosecha)
class PrediccionCosechaAdmin(admin.ModelAdmin):
    """Administración de predicciones de cosecha"""
    
    list_display = [
        'parcela', 'cultivo', 'temporada_objetivo', 'fecha_prediccion',
        'rendimiento_predicho', 'confianza_prediccion', 'modelo_utilizado',
        'precision_prediccion'
    ]
    list_filter = [
        'modelo_utilizado', 'fecha_prediccion', 'cultivo', 'parcela'
    ]
    search_fields = [
        'parcela__codigo', 'cultivo__nombre', 'temporada_objetivo'
    ]
    ordering = ['-fecha_prediccion']
    date_hierarchy = 'fecha_prediccion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('parcela', 'cultivo', 'fecha_prediccion', 'temporada_objetivo')
        }),
        ('Predicción', {
            'fields': (
                'rendimiento_predicho', 'confianza_prediccion',
                'rango_minimo', 'rango_maximo'
            )
        }),
        ('Modelo', {
            'fields': ('modelo_utilizado', 'parametros_modelo'),
            'classes': ('collapse',)
        }),
        ('Validación', {
            'fields': ('rendimiento_real', 'precision_prediccion')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['precision_prediccion', 'fecha_creacion']
    
    actions = ['calcular_precision']
    
    def calcular_precision(self, request, queryset):
        """Acción para calcular precisión de predicciones"""
        count = 0
        for prediccion in queryset:
            if prediccion.rendimiento_real:
                prediccion.calcular_precision()
                count += 1
        
        self.message_user(
            request, 
            f'Precisión calculada para {count} predicciones con resultado real.'
        )
    calcular_precision.short_description = "Calcular precisión"
