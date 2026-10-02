from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# ==============================================================================
# RUTAS GLOBALES DEL PROYECTO
# Aquí se configuran las URLs principales que levanta nuestro servidor.
# ==============================================================================

urlpatterns = [
    # 1. Panel de Administración nativo de Django
    # (Donde puedes ver y editar la base de datos PostgreSQL visualmente)
    path('admin/', admin.site.urls),
    
    # 2. Vista Frontend (Ruta raíz: /)
    # Enlaza nuestra plantilla index.html para que sea la primera pantalla que se carga.
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # 3. Endpoints de la Aplicación Arriendos
    # Todas las rutas de la app "arriendos" estarán prefijadas con "/api/"
    # Ejemplo: /api/maquinarias/
    path('api/', include('arriendos.urls')),
    
    # 4. RÚBRICA: Documentación Swagger / OpenAPI
    # Ruta estandarizada que extrae automáticamente la estructura de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Ruta /api/docs/ que muestra la interfaz visual (Swagger UI) para probar los endpoints
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
