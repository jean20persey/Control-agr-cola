from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .models import Cultivo
from .serializers import (
    CultivoSerializer, 
    CultivoCreateSerializer, 
    CultivoListSerializer,
    CultivoStatsSerializer
)

class CultivoListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear cultivos"""
    
    queryset = Cultivo.objects.filter(activo=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'activo']
    search_fields = ['nombre', 'variedad', 'descripcion']
    ordering_fields = ['nombre', 'tipo', 'ciclo_dias', 'rendimiento_esperado', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CultivoCreateSerializer
        return CultivoListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            cultivo = serializer.save()
            response_serializer = CultivoSerializer(cultivo)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CultivoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un cultivo específico"""
    
    queryset = Cultivo.objects.all()
    serializer_class = CultivoSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """Eliminación lógica (desactivar)"""
        cultivo = self.get_object()
        cultivo.activo = False
        cultivo.save()
        return Response({
            'message': 'Cultivo desactivado correctamente'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cultivos_tipos_view(request):
    """Obtener tipos de cultivos disponibles"""
    # Devolver todos los tipos definidos en el modelo, no solo los que existen en la BD
    tipos_con_nombres = []
    
    for value, label in Cultivo.TIPOS_CULTIVO:
        tipos_con_nombres.append({
            'value': value,
            'label': label
        })
    
    return Response(tipos_con_nombres)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cultivos_stats_view(request):
    """Obtener estadísticas de cultivos"""
    
    total_cultivos = Cultivo.objects.count()
    cultivos_activos = Cultivo.objects.filter(activo=True).count()
    
    # Tipos disponibles
    tipos = list(Cultivo.objects.filter(activo=True).values_list('tipo', flat=True).distinct())
    
    # Promedios
    stats = Cultivo.objects.filter(activo=True).aggregate(
        rendimiento_promedio=Avg('rendimiento_esperado'),
        ciclo_promedio=Avg('ciclo_dias')
    )
    
    data = {
        'total_cultivos': total_cultivos,
        'cultivos_activos': cultivos_activos,
        'tipos_disponibles': tipos,
        'rendimiento_promedio': round(stats['rendimiento_promedio'] or 0, 2),
        'ciclo_promedio': round(stats['ciclo_promedio'] or 0, 2)
    }
    
    serializer = CultivoStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cultivos_por_tipo_view(request):
    """Obtener distribución de cultivos por tipo"""
    
    distribucion = Cultivo.objects.filter(activo=True).values('tipo').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    # Agregar nombres legibles
    resultado = []
    for item in distribucion:
        nombre_tipo = dict(Cultivo.TIPOS_CULTIVO).get(item['tipo'], item['tipo'])
        resultado.append({
            'tipo': item['tipo'],
            'nombre': nombre_tipo,
            'cantidad': item['cantidad']
        })
    
    return Response(resultado)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cultivo_activar_view(request, pk):
    """Reactivar un cultivo desactivado"""
    try:
        cultivo = Cultivo.objects.get(pk=pk)
        cultivo.activo = True
        cultivo.save()
        
        serializer = CultivoSerializer(cultivo)
        return Response({
            'message': 'Cultivo reactivado correctamente',
            'cultivo': serializer.data
        })
    except Cultivo.DoesNotExist:
        return Response({
            'error': 'Cultivo no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cultivos_buscar_view(request):
    """Búsqueda avanzada de cultivos"""
    
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    rendimiento_min = request.GET.get('rendimiento_min', '')
    rendimiento_max = request.GET.get('rendimiento_max', '')
    
    cultivos = Cultivo.objects.filter(activo=True)
    
    if query:
        cultivos = cultivos.filter(
            models.Q(nombre__icontains=query) |
            models.Q(variedad__icontains=query) |
            models.Q(descripcion__icontains=query)
        )
    
    if tipo:
        cultivos = cultivos.filter(tipo=tipo)
    
    if rendimiento_min:
        try:
            cultivos = cultivos.filter(rendimiento_esperado__gte=float(rendimiento_min))
        except ValueError:
            pass
    
    if rendimiento_max:
        try:
            cultivos = cultivos.filter(rendimiento_esperado__lte=float(rendimiento_max))
        except ValueError:
            pass
    
    serializer = CultivoListSerializer(cultivos, many=True)
    return Response(serializer.data)
