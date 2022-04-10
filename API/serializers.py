from rest_framework import serializers
from . models import ImageSegmentation, Image, ItemPedido, Measurement, Cliente, Empresa, Local,  Pedido, ItemPedido, Prenda, Tela, ContactoCliente

class OutputImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSegmentation
        fields = ('uuid', 'name', 'front_input_image', 'side_input_image', 'verified', 'created_at', 'updated_at')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('property_id', 'image')

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ('uuid', 'neck', 'chest', 'waist', 'hip', 'height', 'arm', 'leg')


## clientes
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['tipo_usuario', 'nombre', 'apellido', 'dni', 'email', 'contacto']

    tipo_usuario = serializers.CharField(read_only=True)

    contacto = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

class ContactoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoCliente
        fields = ['direccion', 'telefono', 'ciudad', 'cliente']

    # cliente = serializers.PrimaryKeyRelatedField(read_only=True)


## empresas
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['tipo_usuario', 'nombre', 'ruc', 'email', 'prendas', 'locales']
    
    tipo_usuario = serializers.CharField(read_only=True)

    prendas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    locales = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['nombre_sede', 'direccion', 'ciudad', 'telefono', 'empresa']

    # empresa = serializers.PrimaryKeyRelatedField(read_only=True)


## prendas

class PrendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prenda
        fields = ['titulo', 'descripcion', 'precio', 'inventario', 'tela', 'empresas']

    # tela = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # empresas = serializers.PrimaryKeyRelatedField(many=True)

class TelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tela
        fields = ['titulo', 'descripcion', 'img_url', 'prenda']

    prenda = serializers.PrimaryKeyRelatedField(many=False, read_only=True)


## pedidos

class PedidoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pedido
        fields = ['fecha_entrega', 'cliente', 'local', 'estado_pedido']
    
    #local = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ['pedido', 'prenda', 'medida', 'cantidad', 'precio_unitario']

    # pedido = serializers.PrimaryKeyRelatedField(many=True, read_only=True)