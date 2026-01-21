"""
URL configuration for spotify_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_root(request):
    return JsonResponse({
        'message': 'Enhanced Spotify App API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'upload': '/api/upload/',
            'docs': '/api/docs/',
            'schema': '/api/schema/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root-slash'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/upload/', include('data_upload.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
