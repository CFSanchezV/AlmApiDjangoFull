from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
import shutil

from . utils import *
from . models import ImageSegmentation, Measurement, Prenda, Tela, Empresa, Local, Cliente, ContactoCliente, ItemPedido, Pedido
from . serializers import ClienteSerializer, EmpresaSerializer, MeasurementSerializer, ImageSerializer, LocalSerializer, ContactoClienteSerializer, PrendaSerializer, TelaSerializer, PedidoSerializer, ItemPedidoSerializer


# UTILITIES REQUEST HANDLERS

@api_view(['GET'])
@never_cache
def test_api(request):
    return Response({'response':"Successfully connected to ALMapi"})


@api_view(['POST'])
@never_cache
def run_measureme_tool(request):
    property_id = request.POST.get('property_id')

    # converts querydict to original dict
    images = dict((request.data).lists())['image']
    flag = 1
    arr = []
    for img_name in images:
        modified_data = modify_input_for_multiple_files(property_id,
                                                        img_name)
        file_serializer = ImageSerializer(data=modified_data)
        if file_serializer.is_valid():
            file_serializer.save()
            arr.append(file_serializer.data)
        else:
            flag = 0

    if flag == 1:
        frontimg_path = os.path.relpath(arr[0]['image'], '/')
        sideimg_path = os.path.relpath(arr[1]['image'], '/')
        front_image = ImageSegmentation.objects.create(front_input_image=frontimg_path, name='image_{:02d}'.format(int(uuid.uuid1() )))
        side_image = ImageSegmentation.objects.create(side_input_image=sideimg_path, name='image_{:02d}'.format(int(uuid.uuid1() )))
        runner = RunSegmentationInference(front_image, side_image)
        runner.save_frontbg_output()
        runner.save_sidebg_output()
        measurements = runner.process_imgs()

        #store measurements
        measure = Measurement()
        measure.neck = measurements.neck_perimeter
        measure.chest = measurements.chest_perimeter
        measure.waist = measurements.waist_perimeter
        measure.hip = measurements.hip_perimeter
        measure.height = measurements.MFront.Height
        measure.arm = measurements.MFront.FLarmDist
        measure.leg = measurements.MFront.FLlegDist
        measure.save()

        serializer = MeasurementSerializer(measure)
        return Response(serializer.data)


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

@api_view(['DELETE'])
def delete_last_measurement(request):
    # returns deleted Measurement Data
    measure = Measurement.objects.last()
    Measurement.objects.filter(uuid=measure.uuid).delete()

    serializer = MeasurementSerializer(measure)
    return Response(data=serializer.data)

class MeasurementList(ListCreateAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class MeasurementDetail(RetrieveUpdateDestroyAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

    def delete(self, request, pk):
        medida = get_object_or_404(Measurement, pk=pk)
        if medida.items_medida.count() > 0:
            return Response({'error': 'Las medidas no pueden ser eliminadas porque tiene ítems asociados.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        medida.delete()
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


### ___________________________________________________________ ###


## CUSTOM VIEWS

from rest_framework.generics import ListAPIView
from . serializers import PedidoClienteSerializer, PrendaEmpresaSerializer, PrendaTelaSerializer

# empresas segun prenda
class PrendaEmpresasList(ListAPIView):
    #custom serializer?
    serializer_class = PrendaEmpresaSerializer
    queryset = Pedido.objects.prefetch_related('empresas')


# prendas segun tela
class PrendasTelaList(ListAPIView):
    #custom serializer
    serializer_class = PrendaTelaSerializer
    queryset = Pedido.objects.select_related('telas').all()


# pedidos segun cliente
class PedidoClienteList(ListAPIView):
    #custom serializer
    serializer_class = PedidoClienteSerializer
    # pedidos del cliente incluyendo los ítems (y la prenda asociada), en orden de fecha desc | eager
    queryset = Pedido.objects.select_related(
        'cliente').prefetch_related('items_pedido__prenda').order_by('-placed_at').all()