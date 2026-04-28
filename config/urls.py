from django.contrib import admin
from django.urls import path
from grao_a_grao import views

urlpatterns = [
    path('admin/', admin.site.urls), #Caminho para acessar o painel de administração do Django
    path('', views.home, name='home'), # O caminho '' significa a página inicial home
]