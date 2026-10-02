from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import EquipoViewSet, CarroArriendoViewSet, ContratoViewSet

# ==============================================================================
# RUTAS DE LA API REST (Endpoints)
# Estas son las URLs a las que el Frontend enviará las peticiones fetch().
# ==============================================================================

# El DefaultRouter crea automáticamente todas las rutas CRUD para nuestras vistas:
# - GET /api/maquinarias/
# - POST /api/maquinarias/
# - GET /api/carro-arriendo/
# etc.
router = DefaultRouter()
router.register(r'maquinarias', EquipoViewSet, basename='equipo')
router.register(r'carro-arriendo', CarroArriendoViewSet, basename='carro')
router.register(r'contratos', ContratoViewSet, basename='contrato')

from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    RÚBRICA: Usamos esta vista personalizada para forzar a que el token JWT 
    incluya el Rol del usuario (definido en PostgreSQL). 
    """
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    # 1. Incluimos las rutas CRUD autogeneradas por el Router
    path('', include(router.urls)),
    
    # 2. Rutas para Autenticación con JWT (JSON Web Tokens)
    # Aquí el frontend manda usuario y contraseña para obtener su token de acceso.
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Permite renovar el token si el original expira, sin tener que volver a loguearse.
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
