from rest_framework import serializers
from . models import ImageSegmentation, Image, ItemPedido, Measurement, Cliente, Empresa, Local,  Pedido, ItemPedido, Prenda, Tela, ContactoCliente
import os

# placeholder for ImageSegmentationSerializer
class OutputImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSegmentation
        fields = ('uuid', 'name', 'front_input_image', 'side_input_image', 'verified', 'created_at', 'updated_at')


ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "bmp"]

def validate_extension(filename):
    extension = os.path.splitext(filename)[1].replace(".", "")
    if extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise serializers.ValidationError(
            (f"Tipo de archivo subido no válido: {filename}"),
            code='invalid')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('property_id', 'image')

    def validate(self, data):
        # list of keys
        keys = list(dict(self.context['request'].data).keys())
        for key in keys:
            if key != 'image' or not isinstance(key, str):
                raise serializers.ValidationError(f"Llave inválida: {key}",
                code='invalid')
        # list of images
        images = dict((self.context['request'].data).lists())['image']
        # validate quantity of files with key: "image"
        if len(images) != 2:
            raise serializers.ValidationError(
                ("Recuento de archivos subidos no válido"),
                code='invalid')
        # validate file types
        for img in images:
            validate_extension(img.name)
        return data


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


# __________CUSTOM SERIALIZERS__________

class PrendaTelaSerializer(serializers.ModelSerializer):
    tela = TelaSerializer(many=False)

    class Meta:
        model = Prenda
        fields = ['titulo', 'descripcion', 'precio', 'inventario', 'tela', 'empresas']
    

class EmpresaPrendaSerializer(serializers.ModelSerializer):
    prendas = PrendaSerializer(many=True)
    locales = LocalSerializer(many=True)

    class Meta:
        model = Empresa
        fields = ['tipo_usuario', 'nombre', 'ruc', 'email', 'prendas', 'locales']


class PedidoClienteSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(many=False)
    local = LocalSerializer(many=False)

    class Meta:
        model = Pedido
        fields = ['fecha_entrega', 'cliente', 'local', 'estado_pedido']