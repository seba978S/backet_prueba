#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para tareas administrativas.
Este es el archivo principal que nos permite ejecutar comandos como 
'python manage.py runserver' o 'python manage.py migrate' para 
interactuar con nuestra base de datos PostgreSQL.
"""
import os
import sys

def main():
    """Ejecutar tareas administrativas."""
    # Le indicamos a Django cuál es nuestro archivo principal de configuraciones
    # donde están las credenciales de nuestra base de datos PostgreSQL (settings.py)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heavy_machinery.settings')
    try:
        # Importamos la función de Django encargada de interpretar los comandos de la consola
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste activar "
            "tu entorno virtual?"
        ) from exc
    # Ejecutamos el comando enviado por la terminal (ej: runserver, migrate)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
