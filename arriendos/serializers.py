from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Equipo, CarroArriendo, ItemCarro, Contrato, ItemContrato

# ==============================================================================
# SERIALIZADORES (Traducción de Datos)
# Sirven para convertir las respuestas complejas de la base de datos (PostgreSQL)
# en un formato JSON fácil de leer para el Frontend, y viceversa.
# ==============================================================================

# RÚBRICA: Autenticación JWT (El payload debe incluir el Rol)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personalización de SimpleJWT para cumplir la rúbrica de inyectar
    el rol (CLIENTE o ADMIN) dentro de los 'Claims' (Payload) del token de sesión.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Conexión BD: Interceptamos el Token antes de mandarlo al frontend 
        # y le insertamos el Rol que está guardado en la tabla 'arriendos_usuario' de PostgreSQL.
        token['rol'] = user.rol
        return token


class EquipoSerializer(serializers.ModelSerializer):
    """
    Transforma la tabla Equipo de Postgres a formato JSON.
    """
    class Meta:
        model = Equipo
        fields = '__all__' # Extrae todos los campos


class ItemCarroSerializer(serializers.ModelSerializer):
    """
    Transforma cada ítem agregado al carro.
    """
    # Anidamos la información completa del equipo para que el Frontend 
    # tenga el nombre y tarifa en lugar de solo recibir el número de 'id' del equipo.
    equipo_detalle = EquipoSerializer(source='equipo', read_only=True)
    
    # RÚBRICA: Cálculo Automático (Campos virtuales calculados al vuelo usando models.py)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='calcular_subtotal')
    dias = serializers.IntegerField(read_only=True, source='calcular_dias')

    class Meta:
        model = ItemCarro
        fields = ['id', 'equipo', 'equipo_detalle', 'fecha_inicio', 'fecha_fin', 'cantidad', 'dias', 'subtotal']

    def validate(self, data):
        # Lógica de Validación: Evita que alguien envíe fechas imposibles
        if data['fecha_inicio'] >= data['fecha_fin']:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return data


class CarroArriendoSerializer(serializers.ModelSerializer):
    """
    Serializa el carro completo con todos sus ítems anidados y el total a pagar final.
    """
    items = ItemCarroSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='calcular_total')

    class Meta:
        model = CarroArriendo
        fields = ['id', 'usuario', 'creado_en', 'items', 'total']


class ItemContratoSerializer(serializers.ModelSerializer):
    """
    Serializa el detalle histórico e inmutable de lo que se arrendó.
    """
    equipo_detalle = EquipoSerializer(source='equipo', read_only=True)

    class Meta:
        model = ItemContrato
        fields = ['id', 'equipo', 'equipo_detalle', 'fecha_inicio', 'fecha_fin', 'cantidad', 'costo_historico']


class ContratoSerializer(serializers.ModelSerializer):
    """
    Serializa el contrato maestro (Estado, Costo Total, Fechas de Emisión).
    """
    items = ItemContratoSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Contrato
        fields = ['id', 'usuario', 'usuario_nombre', 'fecha_creacion', 'estado', 'costo_total', 'items']
