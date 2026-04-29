from django.contrib import admin
from django.urls import path
from grao_a_grao import views

urlpatterns = [
    path('admin/', admin.site.urls), #página de administrador
    path('', views.home, name='home'), # pagina inicial
    path('receitas/', views.lista_receitas, name='lista_receitas'), # página das receitas
    path('receita/<int:pk>/', views.detalhes_receita, name='detalhes_receita'), # página de detalhes da receita
]