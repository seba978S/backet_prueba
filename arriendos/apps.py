from django.apps import AppConfig

# ==============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN (apps.py)
# Aquí se registra la aplicación "arriendos" dentro del ecosistema de Django.
# ==============================================================================

class ArriendosConfig(AppConfig):
    """
    Clase de configuración principal de nuestra app.
    Le indica a Django qué tipo de campo autoincremental usar por defecto
    para las llaves primarias (IDs) en PostgreSQL y el nombre interno de la app.
    """
    # Usamos BigAutoField para los IDs, lo cual permite millones de registros sin fallar
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación que luego agregamos a INSTALLED_APPS en settings.py
    name = 'arriendos'
