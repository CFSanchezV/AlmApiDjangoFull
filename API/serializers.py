from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from . models import ImageSegmentation, Image, ItemPedido, Measurement, Cliente, Empresa, Local,  Pedido, ItemPedido, Prenda, Tela, ContactoCliente, Medida
import os

# placeholder for ImageSegmentationSerializer
class OutputImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSegmentation
        fields = ('uuid', 'name', 'front_input_image', 'side_input_image', 'verified', 'created_at', 'updated_at')


## VALIDATORS

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
        fields = ['nombre', 'apellido', 'dni', 'email', 'contacto', 'user']

    # tipo_usuario = serializers.CharField(read_only=True)

    contacto = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # # cliente_id en medidas puede ser nulo, no se necesita agregar medidas al crear ni editar cliente
    # medidas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class ContactoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoCliente
        fields = ['cliente', 'direccion', 'telefono', 'distrito']

    # cliente = serializers.PrimaryKeyRelatedField(read_only=True)


## MEDIDAS
class MedidaSerializer(serializers.ModelSerializer):
    # cliente = ClienteSerializer(many=False, read_only=True)

    class Meta:
        model = Medida
        fields = ('cliente', 'cuello', 'pecho', 'cintura', 'cadera', 'altura', 'brazo', 'pierna')
    

## empresas
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['tipo_usuario', 'nombre', 'ruc', 'email', 'prendas', 'locales', 'user']
    
    tipo_usuario = serializers.CharField(read_only=True)

    prendas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    locales = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['nombre_sede', 'direccion', 'distrito', 'telefono', 'empresa']

    # empresa = serializers.PrimaryKeyRelatedField(read_only=True)


## prendas

class PrendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prenda
        fields = ['titulo', 'descripcion', 'precio_sugerido', 'tela', 'empresas']

    # tela = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # empresas = serializers.PrimaryKeyRelatedField(many=True)

class TelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tela
        fields = ['titulo', 'descripcion', 'url_imagen', 'prenda']

    prenda = serializers.PrimaryKeyRelatedField(many=False, read_only=True)


## pedidos

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['fecha_entrega', 'cliente', 'local', 'estado_pedido']
    
    #local = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def validate(self, data):
        # validate future date only
        input_date = data['fecha_entrega']
        extracted_date = datetime.date(input_date)
        extracted_time = datetime.time(input_date)
        right_now = datetime.now()
        today8AM = right_now.replace(hour=8, minute=0, second=0, microsecond=0)
        today8PM = right_now.replace(hour=20, minute=0, second=0, microsecond=0)
        # the format of the input datetime = 2022-04-21 16:37:00-05:00
        if extracted_date <= timezone.localtime(timezone.now()).date():
            raise serializers.ValidationError(
                ("La fecha de entrega debe ser futura"),
                code='Invalid')
        if extracted_time < datetime.time(today8AM) or extracted_time > datetime.time(today8PM):
            raise serializers.ValidationError(
                ("La hora de entrega debe estar entre 8:00am y 8:00pm"),
                code='Invalid')
        return data

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


### EXTRA: Assigns user IDs to cliente/empresa

class ClienteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'user']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != validated_data.get('user', instance.user).pk:
            raise serializers.ValidationError({"authorize": "No tiene permisos para este usuario."})

        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance


class EmpresaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'user']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != validated_data.get('user', instance.user).pk:
            raise serializers.ValidationError({"authorize": "No tiene permisos para este usuario."})

        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance