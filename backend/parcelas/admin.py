from django.contrib import admin
from .models import Parcela, HistorialParcela

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    """Administración de parcelas"""
    
    list_display = [
        'codigo', 'nombre', 'area_hectareas', 'estado', 'cultivo_actual',
        'fecha_siembra', 'tipo_suelo', 'activa', 'fecha_creacion'
    ]
    list_filter = ['estado', 'tipo_suelo', 'tiene_riego', 'activa', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['estado', 'activa']
    ordering = ['codigo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'area_hectareas')
        }),
        ('Ubicación', {
            'fields': (
                ('ubicacion_lat', 'ubicacion_lng'),
                'altitud'
            )
        }),
        ('Características del Suelo', {
            'fields': (
                'tipo_suelo', 'ph_suelo',
                'materia_organica', 'capacidad_campo'
            )
        }),
        ('Cultivo Actual', {
            'fields': (
                'cultivo_actual', 'fecha_siembra', 'fecha_cosecha_estimada',
                'estado'
            )
        }),
        ('Sistema de Riego', {
            'fields': ('tiene_riego', 'tipo_riego')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_queryset(self, request):
        """Mostrar todas las parcelas (activas e inactivas) en admin"""
        return Parcela.objects.all()
    
    actions = ['activar_parcelas', 'desactivar_parcelas', 'marcar_disponibles']
    
    def activar_parcelas(self, request, queryset):
        """Acción para activar parcelas seleccionadas"""
        updated = queryset.update(activa=True)
        self.message_user(request, f'{updated} parcelas activadas correctamente.')
    activar_parcelas.short_description = "Activar parcelas seleccionadas"
    
    def desactivar_parcelas(self, request, queryset):
        """Acción para desactivar parcelas seleccionadas"""
        updated = queryset.update(activa=False)
        self.message_user(request, f'{updated} parcelas desactivadas correctamente.')
    desactivar_parcelas.short_description = "Desactivar parcelas seleccionadas"
    
    def marcar_disponibles(self, request, queryset):
        """Acción para marcar parcelas como disponibles"""
        updated = queryset.update(
            estado='disponible',
            cultivo_actual=None,
            fecha_siembra=None,
            fecha_cosecha_estimada=None
        )
        self.message_user(request, f'{updated} parcelas marcadas como disponibles.')
    marcar_disponibles.short_description = "Marcar como disponibles"

@admin.register(HistorialParcela)
class HistorialParcelaAdmin(admin.ModelAdmin):
    """Administración del historial de parcelas"""
    
    list_display = [
        'parcela', 'cultivo', 'fecha_siembra', 'fecha_cosecha',
        'rendimiento_obtenido', 'duracion_ciclo', 'fecha_creacion'
    ]
    list_filter = ['fecha_siembra', 'fecha_cosecha', 'cultivo', 'fecha_creacion']
    search_fields = ['parcela__codigo', 'parcela__nombre', 'cultivo__nombre']
    ordering = ['-fecha_siembra']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('parcela', 'cultivo')
        }),
        ('Fechas', {
            'fields': ('fecha_siembra', 'fecha_cosecha')
        }),
        ('Resultados', {
            'fields': ('rendimiento_obtenido', 'observaciones')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_creacion']
    
    def duracion_ciclo(self, obj):
        """Mostrar duración del ciclo en días"""
        if obj.duracion_ciclo:
            return f"{obj.duracion_ciclo} días"
        return "En curso"
    duracion_ciclo.short_description = "Duración del ciclo"
