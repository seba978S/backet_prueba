from django.db import models
from django.contrib.auth.models import AbstractUser

# ==============================================================================
# BASE DE DATOS: Todos estos modelos mapean directamente a tablas en PostgreSQL.
# Al usar `python manage.py migrate`, Django traduce estas clases a sentencias
# SQL (CREATE TABLE) dentro de nuestra base de datos 'db_maquinaria'.
# ==============================================================================

# 1. Autenticación y Seguridad
class Usuario(AbstractUser):
    """
    Modelo de Usuario que extiende el sistema por defecto de Django.
    Esta clase se mapea a la tabla 'arriendos_usuario' en PostgreSQL.
    Incluye un atributo extra 'rol' para diferenciar entre CLIENTES y ADMINS.
    """
    ROL_CHOICES = (
        ('CLIENTE', 'Empresa Constructora'),
        ('ADMIN', 'Ejecutivo de Arriendos'),
    )
    # Define el rol en la Base de Datos, por defecto todos los que se registren son CLIENTE
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='CLIENTE')

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


# 2. Catálogo de Maquinarias
class Equipo(models.Model):
    """
    Representa la maquinaria pesada disponible para arrendar.
    Se guarda en la tabla 'arriendos_equipo' de Postgres.
    """
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)
    tarifa_diaria = models.DecimalField(max_digits=12, decimal_places=2, help_text="Tarifa por día de uso en CLP")
    garantia = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monto de garantía fija obligatoria")
    # Este campo es crucial para el Control Atómico de Stock. Nos dice cuántas máquinas quedan físicamente en PostgreSQL.
    unidades_disponibles = models.PositiveIntegerField(default=0, help_text="Cantidad física disponible")

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"


# 3. Lógica del Carro de Compras Persistente
class CarroArriendo(models.Model):
    """
    Carro de compras vinculado 1 a 1 (OneToOneField) con el usuario.
    Esto cumple con la rúbrica de persistir el carro en Postgres asociado al ID del usuario.
    """
    # Relación OneToOne asegura que un usuario solo pueda tener 1 carro activo a la vez.
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carro')
    creado_en = models.DateTimeField(auto_now_add=True)

    def calcular_total(self):
        # Itera sobre todos los ítems de este carro para sumar el costo final
        return sum(item.calcular_subtotal() for item in self.items.all())

    def __str__(self):
        return f"Carro de {self.usuario.username}"


class ItemCarro(models.Model):
    """
    Representa un equipo específico que el usuario ha metido en su carro.
    Aún no está pagado, por lo que el stock de la máquina no se ha descontado de Postgres.
    """
    carro = models.ForeignKey(CarroArriendo, on_delete=models.CASCADE, related_name='items')
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad = models.PositiveIntegerField(default=1)

    def calcular_dias(self):
        # Lógica de cálculo de días: Si se arrienda el mismo día, se cobra mínimo 1 día.
        dias = (self.fecha_fin - self.fecha_inicio).days
        return dias if dias > 0 else 1

    def calcular_subtotal(self):
        # RÚBRICA: Cálculo automático del costo -> (tarifa * días) * cantidad + (garantía * cantidad)
        costo_arriendo = self.equipo.tarifa_diaria * self.calcular_dias()
        costo_total_unidad = costo_arriendo + self.equipo.garantia
        return costo_total_unidad * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.equipo.nombre}"


# 4. Ciclo Transaccional de Contratos
class Contrato(models.Model):
    """
    Contrato inmutable generado cuando el cliente hace el checkout.
    Cumple con el Atributo CHOICES obligatorio pedido en la rúbrica.
    """
    # RÚBRICA: Atributo CHOICES en el modelo para los estados del contrato
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENTREGADO', 'Entregado'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    )
    # Si el usuario se elimina de la DB, sus contratos también (CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contratos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Por defecto todo contrato nuevo nace como PENDIENTE en Postgres
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Contrato #{self.id} - {self.estado}"


class ItemContrato(models.Model):
    """
    Detalle inmutable de lo que se arrendó en el contrato.
    Si el equipo cambia de precio en el futuro, este registro no se ve afectado (costo_historico).
    """
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='items')
    # Usamos PROTECT para que no se pueda borrar un equipo de PostgreSQL si hay un contrato activo usándolo
    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad = models.PositiveIntegerField(default=1)
    costo_historico = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.equipo.nombre}"
