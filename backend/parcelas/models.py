from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cultivos.models import Cultivo

class Parcela(models.Model):
    """Modelo para gestión de parcelas agrícolas"""
    
    TIPOS_SUELO = [
        ('arcilloso', 'Arcilloso'),
        ('arenoso', 'Arenoso'),
        ('franco', 'Franco'),
        ('franco_arcilloso', 'Franco Arcilloso'),
        ('franco_arenoso', 'Franco Arenoso'),
        ('limoso', 'Limoso'),
        ('franco_limoso', 'Franco Limoso'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS_PARCELA = [
        ('disponible', 'Disponible'),
        ('sembrada', 'Sembrada'),
        ('en_crecimiento', 'En Crecimiento'),
        ('lista_cosecha', 'Lista para Cosecha'),
        ('cosechada', 'Cosechada'),
        ('en_descanso', 'En Descanso'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    # Información básica
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,  # Índice hash para acceso rápido
        verbose_name='Código'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    
    # Ubicación y dimensiones
    area_hectareas = models.FloatField(
        validators=[MinValueValidator(0.01)],
        verbose_name='Área (hectáreas)'
    )
    ubicacion_lat = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name='Latitud'
    )
    ubicacion_lng = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name='Longitud'
    )
    altitud = models.FloatField(
        blank=True, null=True,
        verbose_name='Altitud (msnm)'
    )
    
    # Características del suelo
    tipo_suelo = models.CharField(
        max_length=20, 
        choices=TIPOS_SUELO,
        blank=True, null=True,
        verbose_name='Tipo de suelo'
    )
    ph_suelo = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        verbose_name='pH del suelo'
    )
    materia_organica = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Materia orgánica (%)'
    )
    capacidad_campo = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Capacidad de campo (%)'
    )
    
    # Cultivo actual
    cultivo_actual = models.ForeignKey(
        Cultivo,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='parcelas_actuales',
        verbose_name='Cultivo actual'
    )
    fecha_siembra = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha de siembra'
    )
    fecha_cosecha_estimada = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha estimada de cosecha'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PARCELA,
        default='disponible',
        verbose_name='Estado'
    )
    
    # Sistema de riego
    tiene_riego = models.BooleanField(default=False, verbose_name='Tiene sistema de riego')
    tipo_riego = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name='Tipo de riego'
    )
    
    # Metadatos
    activa = models.BooleanField(default=True, verbose_name='Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),  # Índice hash para acceso rápido
            models.Index(fields=['estado']),
            models.Index(fields=['cultivo_actual']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def ubicacion_completa(self):
        if self.ubicacion_lat and self.ubicacion_lng:
            return f"{self.ubicacion_lat}, {self.ubicacion_lng}"
        return "No especificada"
    
    @property
    def tiene_cultivo(self):
        return self.cultivo_actual is not None
    
    @property
    def dias_desde_siembra(self):
        if self.fecha_siembra:
            from django.utils import timezone
            return (timezone.now().date() - self.fecha_siembra).days
        return None
    
    @property
    def area_metros_cuadrados(self):
        return self.area_hectareas * 10000
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # Si tiene cultivo, debe tener fecha de siembra
        if self.cultivo_actual and not self.fecha_siembra:
            raise ValidationError('Si hay un cultivo asignado, debe especificar la fecha de siembra')
        
        # Si no tiene cultivo, el estado debe ser disponible
        if not self.cultivo_actual and self.estado not in ['disponible', 'en_descanso', 'mantenimiento']:
            raise ValidationError('Sin cultivo asignado, el estado debe ser disponible, en descanso o mantenimiento')

class HistorialParcela(models.Model):
    """Historial de cultivos por parcela"""
    
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Parcela'
    )
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        verbose_name='Cultivo'
    )
    fecha_siembra = models.DateField(verbose_name='Fecha de siembra')
    fecha_cosecha = models.DateField(blank=True, null=True, verbose_name='Fecha de cosecha')
    rendimiento_obtenido = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Rendimiento obtenido (kg/ha)'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        verbose_name = 'Historial de Parcela'
        verbose_name_plural = 'Historiales de Parcelas'
        ordering = ['-fecha_siembra']
    
    def __str__(self):
        return f"{self.parcela.codigo} - {self.cultivo.nombre} ({self.fecha_siembra})"
    
    @property
    def duracion_ciclo(self):
        if self.fecha_cosecha:
            return (self.fecha_cosecha - self.fecha_siembra).days
        return None
