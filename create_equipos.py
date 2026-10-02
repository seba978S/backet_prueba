import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heavy_machinery.settings')
django.setup()

from arriendos.models import Equipo

equipos = [
    {"nombre": "Excavadora CAT 320", "categoria": "Excavadoras", "tarifa_diaria": 150000, "garantia": 500000, "unidades_disponibles": 3},
    {"nombre": "Camión Tolva Volvo", "categoria": "Transporte", "tarifa_diaria": 200000, "garantia": 800000, "unidades_disponibles": 5},
    {"nombre": "Generador 100KVA Diesel", "categoria": "Generadores", "tarifa_diaria": 80000, "garantia": 200000, "unidades_disponibles": 10},
]

for eq in equipos:
    Equipo.objects.get_or_create(nombre=eq['nombre'], defaults=eq)

print("Equipos creados")
