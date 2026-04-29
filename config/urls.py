from django.contrib import admin
from django.urls import path
from grao_a_grao import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls), #página de administrador
    path('', views.home, name='home'), # pagina inicial
    path('receitas/', views.lista_receitas, name='lista_receitas'), # página das receitas
    path('receita/<int:pk>/', views.detalhes_receita, name='detalhes_receita'), # página de detalhes da receita
    path('registo/', views.registo, name='registo'), # página de registo
    path('login/', auth_views.LoginView.as_view(), name='login'), # página de login
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # página de logout
    path('receita/nova/', views.registo_receita, name='registo_receita'),
    path('receita/<int:receita_id>/ingredientes/', views.adicionar_ingredientes, name='adicionar_ingredientes'),
    path('receita/<int:receita_id>/concluir/', views.concluir_receita, name='concluir_receita'),
]