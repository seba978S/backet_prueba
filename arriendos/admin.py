from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Equipo, CarroArriendo, ItemCarro, Contrato, ItemContrato

# ==============================================================================
# PANEL DE ADMINISTRACIÓN (admin.py)
# Al registrar los modelos aquí, le decimos a Django que genere una interfaz 
# gráfica automática (en la ruta /admin/) para poder leer, crear, actualizar 
# y borrar datos directamente de las tablas de PostgreSQL.
# ==============================================================================

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Registra nuestro modelo de Usuario personalizado.
    Como agregamos el campo 'rol', tenemos que decirle al panel de control
    dónde y cómo mostrarlo, de lo contrario no aparecería en pantalla.
    """
    # Columnas que se verán en la tabla resumen
    list_display = ('username', 'email', 'rol', 'is_staff')
    
    # Secciones que aparecerán al Editar a un usuario existente
    fieldsets = UserAdmin.fieldsets + (
        ('Roles de la Aplicación', {'fields': ('rol',)}),
    )
    # Secciones que aparecerán al Crear a un usuario nuevo
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Roles de la Aplicación', {'fields': ('rol',)}),
    )

# Registrar los demás modelos de la base de datos para verlos en el panel web
admin.site.register(Equipo)        # Para gestionar el inventario de máquinas
admin.site.register(CarroArriendo) # Para revisar carritos temporales (debug)
admin.site.register(ItemCarro)     # Detalles dentro de un carro temporal
admin.site.register(Contrato)      # Revisar ventas concretadas (Checkout)
admin.site.register(ItemContrato)  # Histórico inmutable de lo que se arrendó
