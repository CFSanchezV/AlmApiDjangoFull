from django.urls import path
from . import views

urlpatterns = [
    path('ALMpedidos/hello',views.say_hello),
]