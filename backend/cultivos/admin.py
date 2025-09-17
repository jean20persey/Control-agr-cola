from django.contrib import admin
from .models import Cultivo

@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    """Administración de cultivos"""
    
    list_display = [
        'nombre', 'variedad', 'tipo', 'ciclo_dias', 
        'rendimiento_esperado', 'activo', 'fecha_creacion'
    ]
    list_filter = ['tipo', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'variedad', 'descripcion']
    list_editable = ['activo']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'variedad', 'tipo', 'descripcion')
        }),
        ('Características Agronómicas', {
            'fields': (
                'ciclo_dias', 'rendimiento_esperado',
                ('temperatura_optima_min', 'temperatura_optima_max'),
                ('ph_suelo_min', 'ph_suelo_max'),
                'precipitacion_anual'
            )
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_queryset(self, request):
        """Mostrar todos los cultivos (activos e inactivos) en admin"""
        return Cultivo.objects.all()
    
    actions = ['activar_cultivos', 'desactivar_cultivos']
    
    def activar_cultivos(self, request, queryset):
        """Acción para activar cultivos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} cultivos activados correctamente.')
    activar_cultivos.short_description = "Activar cultivos seleccionados"
    
    def desactivar_cultivos(self, request, queryset):
        """Acción para desactivar cultivos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} cultivos desactivados correctamente.')
    desactivar_cultivos.short_description = "Desactivar cultivos seleccionados"
