from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Cultivo(models.Model):
    """Modelo para gestión de cultivos"""
    
    TIPOS_CULTIVO = [
        ('cereales', 'Cereales'),
        ('hortalizas', 'Hortalizas'),
        ('frutales', 'Frutales'),
        ('legumbres', 'Legumbres'),
        ('tubérculos', 'Tubérculos'),
        ('oleaginosas', 'Oleaginosas'),
        ('forrajes', 'Forrajes'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    variedad = models.CharField(max_length=100, verbose_name='Variedad')
    tipo = models.CharField(max_length=20, choices=TIPOS_CULTIVO, verbose_name='Tipo')
    ciclo_dias = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='Ciclo en días'
    )
    rendimiento_esperado = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Rendimiento esperado (kg/ha)'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    
    # Características agronómicas
    temperatura_optima_min = models.FloatField(
        blank=True, null=True,
        verbose_name='Temperatura óptima mínima (°C)'
    )
    temperatura_optima_max = models.FloatField(
        blank=True, null=True,
        verbose_name='Temperatura óptima máxima (°C)'
    )
    ph_suelo_min = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        verbose_name='pH mínimo del suelo'
    )
    ph_suelo_max = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        verbose_name='pH máximo del suelo'
    )
    precipitacion_anual = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Precipitación anual requerida (mm)'
    )
    
    # Metadatos
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Cultivo'
        verbose_name_plural = 'Cultivos'
        ordering = ['nombre']
        
    def __str__(self):
        return f"{self.nombre} - {self.variedad}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} ({self.variedad})"
    
    @property
    def rango_temperatura(self):
        if self.temperatura_optima_min and self.temperatura_optima_max:
            return f"{self.temperatura_optima_min}°C - {self.temperatura_optima_max}°C"
        return "No especificado"
    
    @property
    def rango_ph(self):
        if self.ph_suelo_min and self.ph_suelo_max:
            return f"{self.ph_suelo_min} - {self.ph_suelo_max}"
        return "No especificado"
