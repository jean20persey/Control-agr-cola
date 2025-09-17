from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Parcela, HistorialParcela
from .serializers import (
    ParcelaSerializer, 
    ParcelaCreateSerializer, 
    ParcelaListSerializer,
    ParcelaAsignarCultivoSerializer,
    HistorialParcelaSerializer,
    ParcelaStatsSerializer
)
from cultivos.models import Cultivo

class ParcelaListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear parcelas"""
    
    queryset = Parcela.objects.filter(activa=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tipo_suelo', 'tiene_riego', 'cultivo_actual']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering_fields = ['codigo', 'nombre', 'area_hectareas', 'fecha_creacion']
    ordering = ['codigo']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ParcelaCreateSerializer
        return ParcelaListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            parcela = serializer.save()
            response_serializer = ParcelaSerializer(parcela)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParcelaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una parcela específica"""
    
    queryset = Parcela.objects.all()
    serializer_class = ParcelaSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """Eliminación lógica (desactivar)"""
        parcela = self.get_object()
        parcela.activa = False
        parcela.save()
        return Response({
            'message': 'Parcela desactivada correctamente'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parcela_por_codigo_view(request, codigo):
    """Obtener parcela por código (acceso rápido con índice hash)"""
    try:
        parcela = Parcela.objects.get(codigo__iexact=codigo, activa=True)
        serializer = ParcelaSerializer(parcela)
        return Response(serializer.data)
    except Parcela.DoesNotExist:
        return Response({
            'error': 'Parcela no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_cultivo_view(request, pk):
    """Asignar cultivo a una parcela"""
    try:
        parcela = Parcela.objects.get(pk=pk, activa=True)
        
        if parcela.cultivo_actual:
            return Response({
                'error': 'La parcela ya tiene un cultivo asignado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ParcelaAsignarCultivoSerializer(data=request.data)
        if serializer.is_valid():
            cultivo = Cultivo.objects.get(id=serializer.validated_data['cultivo_id'])
            
            # Asignar cultivo
            parcela.cultivo_actual = cultivo
            parcela.fecha_siembra = serializer.validated_data['fecha_siembra']
            parcela.fecha_cosecha_estimada = serializer.validated_data.get('fecha_cosecha_estimada')
            parcela.estado = 'sembrada'
            parcela.save()
            
            # Crear entrada en historial
            HistorialParcela.objects.create(
                parcela=parcela,
                cultivo=cultivo,
                fecha_siembra=parcela.fecha_siembra
            )
            
            response_serializer = ParcelaSerializer(parcela)
            return Response({
                'message': 'Cultivo asignado correctamente',
                'parcela': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Parcela.DoesNotExist:
        return Response({
            'error': 'Parcela no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cosechar_parcela_view(request, pk):
    """Marcar parcela como cosechada"""
    try:
        parcela = Parcela.objects.get(pk=pk, activa=True)
        
        if not parcela.cultivo_actual:
            return Response({
                'error': 'La parcela no tiene cultivo asignado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener datos de la cosecha
        fecha_cosecha = request.data.get('fecha_cosecha', timezone.now().date())
        rendimiento = request.data.get('rendimiento_obtenido')
        observaciones = request.data.get('observaciones', '')
        
        # Actualizar historial
        historial = HistorialParcela.objects.filter(
            parcela=parcela,
            cultivo=parcela.cultivo_actual,
            fecha_cosecha__isnull=True
        ).first()
        
        if historial:
            historial.fecha_cosecha = fecha_cosecha
            historial.rendimiento_obtenido = rendimiento
            historial.observaciones = observaciones
            historial.save()
        
        # Limpiar parcela
        parcela.cultivo_actual = None
        parcela.fecha_siembra = None
        parcela.fecha_cosecha_estimada = None
        parcela.estado = 'cosechada'
        parcela.save()
        
        response_serializer = ParcelaSerializer(parcela)
        return Response({
            'message': 'Parcela cosechada correctamente',
            'parcela': response_serializer.data
        })
        
    except Parcela.DoesNotExist:
        return Response({
            'error': 'Parcela no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parcelas_disponibles_view(request):
    """Obtener parcelas disponibles para siembra"""
    parcelas = Parcela.objects.filter(
        activa=True,
        cultivo_actual__isnull=True,
        estado__in=['disponible', 'cosechada']
    )
    serializer = ParcelaListSerializer(parcelas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parcelas_por_cultivo_view(request, cultivo_id):
    """Obtener parcelas con un cultivo específico"""
    try:
        cultivo = Cultivo.objects.get(id=cultivo_id, activo=True)
        parcelas = Parcela.objects.filter(
            activa=True,
            cultivo_actual=cultivo
        )
        serializer = ParcelaListSerializer(parcelas, many=True)
        return Response({
            'cultivo': cultivo.nombre,
            'parcelas': serializer.data
        })
    except Cultivo.DoesNotExist:
        return Response({
            'error': 'Cultivo no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parcelas_stats_view(request):
    """Obtener estadísticas de parcelas"""
    
    # Estadísticas básicas
    total_parcelas = Parcela.objects.filter(activa=True).count()
    parcelas_con_cultivo = Parcela.objects.filter(
        activa=True, 
        cultivo_actual__isnull=False
    ).count()
    parcelas_disponibles = total_parcelas - parcelas_con_cultivo
    
    # Áreas
    area_stats = Parcela.objects.filter(activa=True).aggregate(
        area_total=Sum('area_hectareas')
    )
    area_cultivada = Parcela.objects.filter(
        activa=True,
        cultivo_actual__isnull=False
    ).aggregate(
        area_cultivada=Sum('area_hectareas')
    )
    
    # Distribución por estados
    estados = Parcela.objects.filter(activa=True).values('estado').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    distribucion_estados = []
    for estado in estados:
        nombre_estado = dict(Parcela.ESTADOS_PARCELA).get(estado['estado'], estado['estado'])
        distribucion_estados.append({
            'estado': estado['estado'],
            'nombre': nombre_estado,
            'cantidad': estado['cantidad']
        })
    
    # Distribución por tipos de suelo
    suelos = Parcela.objects.filter(
        activa=True,
        tipo_suelo__isnull=False
    ).values('tipo_suelo').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    distribucion_suelos = []
    for suelo in suelos:
        nombre_suelo = dict(Parcela.TIPOS_SUELO).get(suelo['tipo_suelo'], suelo['tipo_suelo'])
        distribucion_suelos.append({
            'tipo': suelo['tipo_suelo'],
            'nombre': nombre_suelo,
            'cantidad': suelo['cantidad']
        })
    
    data = {
        'total_parcelas': total_parcelas,
        'parcelas_activas': total_parcelas,
        'parcelas_con_cultivo': parcelas_con_cultivo,
        'parcelas_disponibles': parcelas_disponibles,
        'area_total': float(area_stats['area_total'] or 0),
        'area_cultivada': float(area_cultivada['area_cultivada'] or 0),
        'distribucion_estados': distribucion_estados,
        'distribucion_suelos': distribucion_suelos
    }
    
    serializer = ParcelaStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_parcela_view(request, pk):
    """Obtener historial de una parcela"""
    try:
        parcela = Parcela.objects.get(pk=pk, activa=True)
        historial = HistorialParcela.objects.filter(parcela=parcela).order_by('-fecha_siembra')
        serializer = HistorialParcelaSerializer(historial, many=True)
        return Response({
            'parcela': {
                'id': parcela.id,
                'codigo': parcela.codigo,
                'nombre': parcela.nombre
            },
            'historial': serializer.data
        })
    except Parcela.DoesNotExist:
        return Response({
            'error': 'Parcela no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
