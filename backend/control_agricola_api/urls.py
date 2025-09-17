"""
URL configuration for control_agricola_api project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    """
    API Root - Información general de la API de Control Agrícola
    """
    return Response({
        'message': 'Bienvenido a la API de Control Agrícola',
        'version': '1.0.0',
        'description': 'Sistema de gestión y análisis de producción agrícola',
        'endpoints': {
            'authentication': '/api/auth/',
            'cultivos': '/api/cultivos/',
            'parcelas': '/api/parcelas/',
            'produccion': '/api/produccion/',
            'analisis': '/api/analisis/',
            'dashboard': '/api/dashboard/',
            'admin': '/admin/',
        },
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # API Endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/cultivos/', include('cultivos.urls')),
    path('api/parcelas/', include('parcelas.urls')),
    path('api/produccion/', include('produccion.urls')),
    path('api/analisis/', include('analisis.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
