from django.urls import path
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

    path('medidas_clientes/', views.MedidaList.as_view(), name='medidas_lista'),
    path('medidas_clientes/<int:pk>', views.MedidaDetail.as_view(), name='medida_detalle'),

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

    # __________CUSTOM URLS__________
    path('prendas_tela/<int:id_tela>', views.prendas_por_tela, name='lista_prendas_tela'),
    path('empresas_prenda/<int:id_prenda>', views.empresas_por_prenda, name='lista_empresas_prenda'),
    path('pedidos_cliente/<int:id_cliente>', views.pedidos_por_cliente, name='lista_pedidos_cliente'),

    # __________Association urls__________
    path('registrar_cliente/<int:pk>', views.RegistrarCliente.as_view(), name='registrar_cliente'),
    path('registrar_empresa/<int:pk>', views.RegistrarEmpresa.as_view(), name='registrar_empresa'),
]