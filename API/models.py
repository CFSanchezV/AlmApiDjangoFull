from django.db import models
from django.utils.timezone import now
from API.utils import get_input_image_path, get_output_image_path
from django.core.validators import RegexValidator
import uuid

### Images for processing ###
class ImageSegmentation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name='nombre', max_length=255, null=True, blank=True)
    front_input_image = models.FileField(verbose_name='Imagen fontal', upload_to=get_output_image_path, null=True, blank=True, max_length=255)
    side_input_image = models.FileField(verbose_name='Imagen de perfil', upload_to=get_output_image_path, null=True, blank=True, max_length=255)
    verified = models.BooleanField(verbose_name='Verificado', default=False)
    created_at = models.DateTimeField(verbose_name='Creado en', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Actualizado en', auto_now=True)

    def __str__(self):
        return "{0}".format(self.name)


### Images from request ###
class Image(models.Model):
    property_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.FileField(verbose_name='Path de imagen de entrada', upload_to=get_input_image_path, null=True, blank=True)


### Measurements from Images | no association to user | Imgs get deleted in server (privacy policy) ###
class Measurement(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    neck = models.FloatField(default=0)
    chest = models.FloatField(default=0)
    waist = models.FloatField(default=0)
    hip = models.FloatField(default=0)
    height = models.FloatField(default=0)
    arm = models.FloatField(default=0)
    leg = models.FloatField(default=0)
    created_at = models.DateTimeField(verbose_name='Creado en', default=now, editable=False)

    def __str__(self):
        return "Medidas | cuello:{}, pecho:{}, cintura:{}, cadera:{}, altura:{}, brazos:{}, piernas:{}".format(self.neck, self.chest, self.waist, self.hip, self.height, self.arm, self.leg)


## RESTO DEL API

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters')

class Cliente(models.Model):
    TIPO_USUARIO_CLIENTE = 'C'
    TIPO_USUARIO_EMPRESA = 'E'
    TIPO_USUARIO_OPCIONES = [
        (TIPO_USUARIO_CLIENTE, 'Cliente'),
        (TIPO_USUARIO_EMPRESA, 'Empresa')
    ]
    tipo_usuario = models.CharField(
        max_length=1, choices=TIPO_USUARIO_OPCIONES, default=TIPO_USUARIO_CLIENTE, editable=False)
    nombre = models.CharField(max_length=255, null=True)
    apellido = models.CharField(max_length=255, null=True)
    dni = models.CharField(verbose_name='DNI', max_length=8, unique=True, validators=[alphanumeric])
    email = models.EmailField(unique=True, null=True)

    class Meta:
        db_table = 'cliente'

    def __str__(self):
        return "{} {}".format(self.nombre, self.apellido)

class ContactoCliente(models.Model):
    direccion = models.CharField(max_length=255, null=True)
    telefono = models.CharField(max_length=255, null=True)
    ciudad = models.CharField(max_length=255, null=True)
    cliente = models.OneToOneField(Cliente, null=True, on_delete=models.SET_NULL, related_name='contacto')
    
    class Meta:
        db_table = 'contacto_cliente'

    def __str__(self):
        return "Info de contacto de: {}".format(self.cliente)


## EMPRESAS
class Empresa(models.Model):
    TIPO_USUARIO_CLIENTE = 'C'
    TIPO_USUARIO_EMPRESA = 'E'
    TIPO_USUARIO_OPCIONES = [
        (TIPO_USUARIO_CLIENTE, 'Cliente'),
        (TIPO_USUARIO_EMPRESA, 'Empresa')
    ]
    tipo_usuario = models.CharField(
        max_length=1, choices=TIPO_USUARIO_OPCIONES, default=TIPO_USUARIO_EMPRESA, editable=False)
    nombre = models.CharField(verbose_name='Nombre o Razon social', max_length=255, null=True)
    ruc = models.CharField(max_length=11, unique=True, validators=[alphanumeric])
    email = models.EmailField(unique=True, null=True)

    class Meta:
        db_table = 'empresa'

    def __str__(self):
        return "{0}".format(self.nombre)

class Local(models.Model):
    nombre_sede = models.CharField(verbose_name='Nombre de sede', max_length=255, null=True)
    direccion = models.CharField(max_length=255, null=True)
    ciudad = models.CharField(max_length=255, null=True)
    telefono = models.CharField(max_length=255, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='locales')

    class Meta:
        db_table = 'local'

    def __str__(self):
        return "Sede: {} de la empresa: {}".format(self.nombre_sede, self.empresa)


## ENTIDADES
class Tela(models.Model):
    titulo = models.CharField(max_length=255, null=True)
    descripcion = models.TextField(null=True)
    img_url = models.TextField()

    class Meta:
        db_table = 'tela'

    def __str__(self):
        return "{}: {}".format(self.titulo, self.descripcion)

class Prenda(models.Model):
    titulo = models.CharField(max_length=255, null=True)
    descripcion = models.TextField(null=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    inventario = models.PositiveIntegerField(null=True)
    tela = models.ForeignKey(Tela, on_delete=models.PROTECT, related_name='prendas', null=True)
    last_update = models.DateTimeField(auto_now=True)
    empresas = models.ManyToManyField(Empresa, related_name='prendas') #many-many

    class Meta:
        db_table = 'prenda'

    def __str__(self):
        return "{}: {} | hecho(a) de {}".format(self.titulo, self.descripcion, self.tela)

class Pedido(models.Model):
    ESTADO_PEDIDO_PENDIENTE = 'P'
    ESTADO_PEDIDO_CONFIRMADO = 'C'
    ESTADO_PEDIDO_FALLIDO = 'F'
    ESTADO_PEDIDO_OPCIONES = [
        (ESTADO_PEDIDO_PENDIENTE, 'Pendiente'),
        (ESTADO_PEDIDO_CONFIRMADO, 'Confirmado'),
        (ESTADO_PEDIDO_FALLIDO, 'Fallido')
    ]
    estado_pedido = models.CharField(
        max_length=1, choices=ESTADO_PEDIDO_OPCIONES, default=ESTADO_PEDIDO_PENDIENTE)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos_cliente')
    local = models.ForeignKey(Local, on_delete=models.PROTECT, related_name='pedidos_local')
    fecha_entrega = models.DateTimeField(verbose_name='Fecha y hora de entrega', default=now)
    placed_at = models.DateTimeField(verbose_name='Creada en', auto_now_add=True)

    class Meta:
        db_table = 'pedido'

    def __str__(self):
        return "Pedido con fecha {}| de {}| para {}".format(self.fecha_entrega, self.local, self.cliente)
    

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='items_pedido', null=True)
    prenda = models.ForeignKey(Prenda, on_delete=models.PROTECT, related_name='items_prenda')
    medida = models.ForeignKey(Measurement, on_delete=models.PROTECT, related_name='items_medida', null=True)
    cantidad = models.PositiveSmallIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'item_pedido'
        unique_together = [['pedido', 'prenda', 'medida']]

    def __str__(self):
        return "Item de {}".format(self.pedido)