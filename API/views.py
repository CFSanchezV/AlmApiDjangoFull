from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
import shutil

from . utils import *
from . models import ImageSegmentation, Measurement, Prenda, Tela, Empresa, Local, Cliente, ContactoCliente, ItemPedido, Pedido, Medida
from . serializers import ClienteSerializer, EmpresaSerializer, LocalesEmpresaSerializer, MeasurementSerializer, ImageSerializer, LocalSerializer, ContactoClienteSerializer, PrendaSerializer, TelaSerializer, PedidoSerializer, ItemPedidoSerializer, MedidaSerializer

# UTILITIES REQUEST HANDLERS

@api_view(['GET'])
@never_cache
def test_api(request):
    return Response({'response':"Successfully connected to ALMapi"})


# @api_view(['POST'])
# @never_cache
# def run_measureme_tool(request):
#     property_id = request.POST.get('property_id')

#     # converts querydict to original dict
#     images = dict((request.data).lists())['image']
#     # validated data flag
#     flag = 1
#     arr = []
#     for img_name in images:
#         modified_data = modify_input_for_multiple_files(property_id,
#                                                         img_name)
#         image_serializer = ImageSerializer(data=modified_data, context={'request': request})
#         if image_serializer.is_valid():
#             image_serializer.save()
#             arr.append(image_serializer.data)
#         else:
#             flag = 0
#             return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     if flag == 1:
#         frontimg_path = arr[0]['image']
#         sideimg_path = arr[1]['image']
#         # frontimg_path = os.path.relpath(arr[0]['image'], '/')
#         # sideimg_path = os.path.relpath(arr[1]['image'], '/')
#         front_image = ImageSegmentation.objects.create(front_input_image=frontimg_path, name='image_{:02d}'.format(int(uuid.uuid1() )))
#         side_image = ImageSegmentation.objects.create(side_input_image=sideimg_path, name='image_{:02d}'.format(int(uuid.uuid1() )))
#         runner = RunSegmentationInference(front_image, side_image)
#         runner.save_frontbg_output()
#         runner.save_sidebg_output()
#         measurements = runner.process_imgs()

#         #store measurements
#         measure = Measurement()
#         measure.neck = measurements.neck_perimeter
#         measure.chest = measurements.chest_perimeter
#         measure.waist = measurements.waist_perimeter
#         measure.hip = measurements.hip_perimeter
#         measure.height = measurements.MFront.Height
#         measure.arm = measurements.MFront.FLarmDist
#         measure.leg = measurements.MFront.FLlegDist
#         measure.save()

#         # returns results in Measurements
#         serializer = MeasurementSerializer(measure)
#         return Response(serializer.data)


@api_view(['GET'])
@never_cache
def clean_folders(request):
    folder_input = 'media/Input_image/'
    for filename in os.listdir(folder_input):
        file_path = os.path.join(folder_input, filename)
        # except gitkeep
        _, ext = os.path.splitext(file_path)     
        if (filename == '.gitkeep' or ext == '.txt'): continue
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete {}. Reason: {}'.format(file_path, e) )

    folder_output = 'media/Output_image/'
    for filename in os.listdir(folder_output):
        file_path = os.path.join(folder_output, filename)
        # except gitkeep
        _, ext = os.path.splitext(file_path)     
        if (filename == '.gitkeep' or ext == '.txt'): continue
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete {}. Reason: {}'.format(file_path, e) )

    return Response({'response': "Media folders were cleaned up!!"})

### ___________________________________________________________ ###

## MEDIDAS / MEASUREMENTS

# @api_view(['DELETE'])
# def delete_last_measurement(request):
#     # returns deleted Measurement Data
#     measure = Measurement.objects.last()
#     Measurement.objects.filter(uuid=measure.uuid).delete()

#     serializer = MeasurementSerializer(measure)
#     return Response(data=serializer.data)

class MeasurementList(ListCreateAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class MeasurementDetail(RetrieveUpdateDestroyAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def delete(self, request, pk):
        measurement = get_object_or_404(Measurement, pk=pk)
        if measurement.items_medida.count() > 0:
            return Response({'error': 'Las medidas no pueden ser eliminadas porque tiene ítems asociados.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        measurement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


### ___________________________________________________________ ###


## CLIENTES

class ClienteList(ListCreateAPIView):
    queryset = Cliente.objects.select_related('contacto').all()
    serializer_class = ClienteSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class ClienteDetail(RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def delete(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.pedidos_cliente.count() > 0:
            return Response({'error': 'Cliente no puede ser eliminado porque tiene un pedido asociado'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        cliente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ContactoClienteList(ListCreateAPIView):
    queryset = ContactoCliente.objects.select_related('cliente').all()
    serializer_class = ContactoClienteSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class ContactoClienteDetail(RetrieveUpdateDestroyAPIView):
    queryset = ContactoCliente.objects.select_related('cliente').all()
    serializer_class = ContactoClienteSerializer


## EMPRESAS

class EmpresaList(ListCreateAPIView):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class EmpresaDetail(RetrieveUpdateDestroyAPIView):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

    def delete(self, request, pk):
        empresa = get_object_or_404(Empresa, pk=pk)
        if empresa.locales.count() > 0:
            return Response({'error': 'Empresa no puede ser eliminada porque tiene locales asociados'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        empresa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LocalList(ListCreateAPIView):
    queryset = Local.objects.select_related('empresa').all()
    serializer_class = LocalSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class LocalDetail(RetrieveUpdateDestroyAPIView):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer

    def delete(self, request, pk):
        local = get_object_or_404(Local, pk=pk)
        if local.pedidos_local.count() > 0:
            return Response({'error': 'Local no puede ser eliminada porque tiene un pedido asociado'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        local.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


## PRENDAS

class PrendaList(ListCreateAPIView):
    queryset = Prenda.objects.select_related('tela').prefetch_related('empresas').all()
    serializer_class = PrendaSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class PrendaDetail(RetrieveUpdateDestroyAPIView):
    queryset = Prenda.objects.select_related('tela').prefetch_related('empresas').all()
    serializer_class = PrendaSerializer

    def delete(self, request, pk):
        prenda = get_object_or_404(Prenda, pk=pk)
        if prenda.items_prenda.count() > 0:
            return Response({'error': 'Prenda no puede ser eliminada porque tiene un item de Pedido asociado'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        prenda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TelaList(ListCreateAPIView):
    queryset = Tela.objects.all()
    serializer_class = TelaSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class TelaDetail(RetrieveUpdateDestroyAPIView):
    queryset = Tela.objects.all()
    serializer_class = TelaSerializer


## PEDIDOS

class ItemPedidoList(ListCreateAPIView):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class ItemPedidoDetail(RetrieveUpdateDestroyAPIView):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer


class PedidoList(ListCreateAPIView):
    queryset = Pedido.objects.select_related('cliente', 'local').prefetch_related('items_pedido').all()
    serializer_class = PedidoSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class PedidoDetail(RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def delete(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.items_pedido.count() > 0:
            return Response({'error': 'Pedido no puede ser eliminado porque tiene ítems asociados'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif pedido.estado_pedido == Pedido.ESTADO_PEDIDO_CONFIRMADO:
            return Response({'error': 'Pedido no puede ser eliminado porque ha sido confirmado'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif pedido.estado_pedido == Pedido.ESTADO_PEDIDO_PENDIENTE:
            return Response({'error': 'Pedido no puede ser eliminado porque tiene estado ''PENDIENTE''. Debe cambiarse a ''FALLIDO'''}, status=status.HTTP_405_METHOD_NOT_ALLOWED)            
        pedido.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


## LAS MEDIDAS VERDADERAS

class MedidaList(ListCreateAPIView):
    queryset = Medida.objects.select_related('cliente').all()
    serializer_class = MedidaSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class MedidaDetail(RetrieveUpdateDestroyAPIView):
    queryset = Medida.objects.select_related('cliente').all()
    serializer_class = MedidaSerializer


# __________CUSTOM VIEWS__________

from . serializers import PedidoClienteSerializer, EmpresaPrendaSerializer, PrendaTelaSerializer, LocalesEmpresaSerializer, MedidasClienteSerializer, ItemsPedidoPedidoSerializer

# prendas segun tela
@api_view(['GET'])
def prendas_por_tela(request, id_tela):
    queryset = Prenda.objects.select_related('tela').filter(tela__id=id_tela)
    #custom serializer
    serializer = PrendaTelaSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


# empresas segun prenda
@api_view(['GET'])
def empresas_por_prenda(request, id_prenda):
    queryset = Empresa.objects.prefetch_related('prendas').filter(prendas__id=id_prenda)
    #custom serializer
    serializer = EmpresaPrendaSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


# locales segun empresa
@api_view(['GET'])
def locales_por_empresa(request, id_empresa):
    queryset = Local.objects.filter(empresa__id=id_empresa)
    #custom serializer
    serializer = LocalesEmpresaSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


# medidas segun cliente
@api_view(['GET'])
def medidas_por_cliente(request, id_cliente):
    queryset = Medida.objects.prefetch_related('cliente').filter(cliente__id=id_cliente)
    #custom serializer
    serializer = MedidasClienteSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


# pedidos segun cliente
@api_view(['GET'])
def pedidos_por_cliente(request, id_cliente):
    queryset = Pedido.objects.select_related(
            'cliente', 'local').prefetch_related('items_pedido').filter(cliente__id=id_cliente).order_by('-creado_en')
    #custom serializer
    serializer = PedidoClienteSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


# itemspedido segun pedido
@api_view(['GET'])
def itemspedido_por_pedido(request, id_pedido):
    queryset = ItemPedido.objects.prefetch_related('pedido', 'prenda', 'medida').filter(pedido__id=id_pedido)
    #custom serializer
    serializer = ItemsPedidoPedidoSerializer(
        queryset, many=True, context={'request': request}
    )
    return Response(serializer.data)


## VIEWS CON AUTENTICACION

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from . serializers import ClienteUserSerializer, EmpresaUserSerializer, AssociatedClienteSerializer
from rest_framework.generics import UpdateAPIView

class RegistrarCliente(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cliente.objects.all()
    serializer_class = ClienteUserSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object() #cliente obj
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Actualizacion correcta", "Cliente": serializer.data})
        else:
            return Response({"message": "Actualizacion fallida", "Detalles": serializer.errors})

    def get_serializer_context(self):
        return {'request': self.request}


class RegistrarEmpresa(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Empresa.objects.all()
    serializer_class = EmpresaUserSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object() #empresa obj
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Actualizacion correcta", "Empresa": serializer.data})
        else:
            return Response({"message": "Actualizacion fallida", "Detalles": serializer.errors})

    def get_serializer_context(self):
        return {'request': self.request}


# Aux Utils

# get tipo_usuario from associated cliente/empresa, returns obj {"tipo_usuario": :str}
@api_view(['GET'])
def get_tipo_usuario(request, user_id):
    user = User.objects.filter(id=user_id).first()
    clientes = Cliente.objects.filter(user=user_id)
    empresas = Empresa.objects.filter(user=user_id)
    cliente = clientes.first()
    empresa = empresas.first()
    
    if user is None:
        return Response({"tipo_usuario" : "Usuario no asociado"})
    elif cliente is not None:
        return Response({"tipo_usuario" : cliente.tipo_usuario})
    elif empresa is not None:
        return Response({"tipo_usuario" : empresa.tipo_usuario})
    else:
        return Response({"tipo_usuario" : "Ninguno"})


# get user_id from username in URL/username, returns obj {"user_id": :id}
@api_view(['POST'])
def get_user_id(request, username):
    user = get_object_or_404(User, username=username)

    return Response({"user_id": user.id})

# UPDATE/GET/DELETE empresa or cliente linked to user_id in URL

from . serializers import AssociatedEmpresaSerializer, AssociatedClienteSerializer

class ClienteUserDetail(RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    lookup_field = 'user_id'
    serializer_class = AssociatedClienteSerializer

class EmpresaUserDetail(RetrieveUpdateDestroyAPIView):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    lookup_field = 'user_id'
    serializer_class = AssociatedEmpresaSerializer