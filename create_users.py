import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heavy_machinery.settings')
django.setup()

from arriendos.models import Usuario

if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser('admin', 'admin@example.com', 'admin123', rol='ADMIN')
    print("User admin created")

if not Usuario.objects.filter(username='cliente').exists():
    Usuario.objects.create_user('cliente', 'cliente@example.com', 'cliente123', rol='CLIENTE')
    print("User cliente created")
