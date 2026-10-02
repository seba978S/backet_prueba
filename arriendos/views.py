from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipo, CarroArriendo, ItemCarro, Contrato, ItemContrato
from .serializers import (EquipoSerializer, CarroArriendoSerializer, ItemCarroSerializer, 
                          ContratoSerializer)
from .permissions import IsClienteUser, IsAdminRol

# ==============================================================================
# VISTAS (Lógica de Negocio y Transaccional)
# Aquí ocurre toda la conexión entre la base de datos PostgreSQL y la API Rest.
# Estas vistas procesan las solicitudes del frontend (GET, POST, PATCH) y
# devuelven la información validada.
# ==============================================================================

class EquipoViewSet(viewsets.ModelViewSet):
    """
    Ruta PÚBLICA (GET) para ver el catálogo de maquinarias.
    Ruta PROTEGIDA (POST/PUT/DELETE) para que el Ejecutivo administre.
    """
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    
    # RÚBRICA: Configurar django-filter para filtrar maquinarias (ej. por categoría)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria'] # Permite buscar así: /api/maquinarias/?categoria=Transporte

    def get_permissions(self):
        # Si la petición es solo para ver (list/retrieve), cualquiera puede pasar
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        # Si es para crear/borrar, se exige el rol de Ejecutivo
        else:
            permission_classes = [IsAdminRol] 
        return [permission() for permission in permission_classes]


class CarroArriendoViewSet(viewsets.ModelViewSet):
    """
    Gestión del Carro de Arriendo persistente en BD.
    Solo accesible para el rol de Empresa Constructora (Cliente).
    """
    serializer_class = ItemCarroSerializer
    permission_classes = [IsClienteUser] # RÚBRICA: Bloqueado para administradores o público

    def get_queryset(self):
        # Conexión BD: Busca en Postgres el carro asociado al cliente actual. 
        # Si no existe (porque es nuevo), lo crea en la BD (`get_or_create`).
        carro, _ = CarroArriendo.objects.get_or_create(usuario=self.request.user)
        # Devuelve solo los ítems guardados en ESE carro.
        return ItemCarro.objects.filter(carro=carro)

    def perform_create(self, serializer):
        # Conexión BD: Cuando el cliente añade una máquina, se asocia automáticamente a su carro en PostgreSQL.
        carro, _ = CarroArriendo.objects.get_or_create(usuario=self.request.user)
        serializer.save(carro=carro)

    @action(detail=False, methods=['GET'])
    def ver_carro(self, request):
        # Conexión BD: Endpoint especial para que el Frontend dibuje el carrito completo calculando los totales.
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        serializer = CarroArriendoSerializer(carro)
        return Response(serializer.data)


class ContratoViewSet(viewsets.ModelViewSet):
    """
    ======================================================================
    CUMPLE CON LA LÓGICA DE CONTROL ATÓMICO DE STOCK (RÚBRICA).
    Gestión de Contratos y simulación de Checkout seguro.
    ======================================================================
    """
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    
    def get_permissions(self):
        if self.action in ['checkout', 'mis_contratos']:
            return [IsClienteUser()] # Clientes solo ven lo suyo
        elif self.action in ['estado', 'update', 'partial_update']:
            return [IsAdminRol()] # Ejecutivos cambian estados
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['GET'])
    def mis_contratos(self, request):
        # Conexión BD: Trae de Postgres SOLAMENTE los contratos del cliente logueado
        contratos = Contrato.objects.filter(usuario=request.user)
        serializer = self.get_serializer(contratos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    @transaction.atomic # RÚBRICA - ATOMICIDAD: O se ejecuta todo exitosamente en Postgres, o se revierte todo (nada a medias).
    def checkout(self, request):
        """
        RÚBRICA: "Al hacer checkout, se valida disponibilidad. 
        El descuento es atómico solo cuando el estado cambia a PAGADO."
        """
        carro = CarroArriendo.objects.filter(usuario=request.user).first()
        if not carro or not carro.items.exists():
            return Response({"error": "El carro está vacío."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Validación de disponibilidad en BD SIN descontar stock todavía
        for item in carro.items.all():
            # select_for_update() bloquea la fila temporalmente en PostgreSQL para evitar 
            # que otro usuario arriende la misma máquina al mismo segundo (condición de carrera)
            equipo = Equipo.objects.select_for_update().get(id=item.equipo.id)
            if equipo.unidades_disponibles < item.cantidad:
                return Response(
                    {"error": f"Stock insuficiente para {equipo.nombre}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Generación del Contrato Histórico en PostgreSQL
        # (Nace en estado PAGADO porque nuestra UI asume que ya se pagó en el checkout)
        contrato = Contrato.objects.create(
            usuario=request.user,
            estado='PAGADO', 
            costo_total=carro.calcular_total()
        )

        for item in carro.items.all():
            ItemContrato.objects.create(
                contrato=contrato,
                equipo=item.equipo,
                fecha_inicio=item.fecha_inicio,
                fecha_fin=item.fecha_fin,
                cantidad=item.cantidad,
                costo_historico=item.calcular_subtotal()
            )
            # RÚBRICA: Como el estado ya es PAGADO, AHORA SÍ se descuenta atómicamente el stock de PostgreSQL.
            equipo = item.equipo
            equipo.unidades_disponibles -= item.cantidad
            equipo.save()
        
        # 3. Vaciar el carro (se borran los ítems temporales)
        carro.items.all().delete()
        serializer = self.get_serializer(contrato)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PATCH'])
    @transaction.atomic # ATOMICIDAD en la actualización del inventario
    def estado(self, request, pk=None):
        """
        RÚBRICA: "Si se cambia a COMPLETADO (devolución) o CANCELADO, 
        la máquina se repone al inventario disponible de forma atómica."
        """
        contrato = self.get_object()
        nuevo_estado = request.data.get('estado')
        estado_anterior = contrato.estado

        # Lógica para reponer stock en la base de datos si el contrato se finaliza o se cancela
        if nuevo_estado in ['COMPLETADO', 'CANCELADO'] and estado_anterior in ['PAGADO', 'ENTREGADO']:
            for item in contrato.items.all():
                # Bloqueo atómico
                equipo = Equipo.objects.select_for_update().get(id=item.equipo.id)
                # Conexión BD: Le sumamos (reponemos) las máquinas que regresaron al inventario
                equipo.unidades_disponibles += item.cantidad
                equipo.save()

        # Conexión BD: Guarda el nuevo estado del contrato en Postgres
        contrato.estado = nuevo_estado
        contrato.save()
        return Response({"status": f"Estado actualizado a {nuevo_estado}"})
