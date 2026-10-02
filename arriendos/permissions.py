from rest_framework import permissions

# ==============================================================================
# PERMISOS PERSONALIZADOS (Seguridad de Rutas)
# Aquí definimos quién puede acceder a qué. Estos permisos se evalúan automáticamente
# cuando el Frontend envía el Token JWT en los headers de la petición HTTP.
# ==============================================================================

class IsClienteUser(permissions.BasePermission):
    """
    RÚBRICA: Permiso exclusivo para Clientes (Empresa Constructora).
    Verifica que el usuario haya iniciado sesión y que el 'rol' almacenado 
    en su perfil de PostgreSQL sea 'CLIENTE'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'CLIENTE')

class IsAdminRol(permissions.BasePermission):
    """
    RÚBRICA: Permiso exclusivo para Administradores (Ejecutivo de Arriendos).
    Verifica que el usuario haya iniciado sesión y que su 'rol' sea 'ADMIN'.
    Solo los ejecutivos pueden modificar el inventario y cambiar los estados de los contratos.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'ADMIN')
