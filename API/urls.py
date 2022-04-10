from django.urls import path
from django.urls import include, path
from rest_framework import routers
from . import views
from . import views

app_name = 'api'

# URL config
urlpatterns = [
    path('test/', views.test_api, name='test_api_communication'),
    path('clean_folders/', views.clean_folders, name='clean_img_folders'),

    path('measureme/', views.run_measureme_tool, name='run_measurements_on_images'),
    
    path('delete_last_measurement/', views.delete_last_measurement, name='delete_last_measurement'),
    path('medidas/', views.MeasurementList.as_view(), name='lista_medidas'),
    path('medidas/<uuid:pk>', views.MeasurementDetail.as_view(), name='detalle_medida'),

    path('clientes/', views.ClienteList.as_view(), name='lista_clientes'),
    path('clientes/<int:pk>', views.ClienteDetail.as_view(), name='detalle_cliente'),
    path('contactos/', views.ContactoClienteList.as_view(), name='lista_contactos'),
    path('contactos/<int:pk>', views.ContactoClienteDetail.as_view(), name='detalle_contacto'),

    path('empresas/', views.EmpresaList.as_view(), name='lista_empresas'),
    path('empresas/<int:pk>', views.EmpresaDetail.as_view(), name='detalle_empresa'),
    path('locales/', views.LocalList.as_view(), name='lista_locales'),
    path('locales/<int:pk>', views.LocalDetail.as_view(), name='detalle_local'),

    path('prendas/', views.PrendaList.as_view(), name='lista_prendas'),
    path('prendas/<int:pk>', views.PrendaDetail.as_view(), name='detalle_prenda'),
    path('telas/', views.TelaList.as_view(), name='lista_telas'),
    path('telas/<int:pk>', views.TelaDetail.as_view(), name='detalle_tela'),

    path('items_pedido/', views.ItemPedidoList.as_view(), name='lista_items_pedidos'),
    path('items_pedido/<int:pk>', views.ItemPedidoDetail.as_view(), name='detalle_items_pedido'),
    path('pedidos/', views.PedidoList.as_view(), name='lista_pedidos'),
    path('pedidos/<int:pk>', views.PedidoDetail.as_view(), name='detalle_pedidos'),
]