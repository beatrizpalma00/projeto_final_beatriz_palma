from django.contrib import admin
from django.urls import path
from grao_a_grao import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # autenticação/login
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('registo/', views.registo, name='registo'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Receitas
    path('receitas/', views.lista_receitas, name='lista_receitas'),
    path('receita/nova/', views.registo_receita, name='registo_receita'),
    path('receita/<int:pk>/', views.detalhes_receita, name='detalhes_receita'),
    path('receita/<int:pk>/editar/', views.editar_receita, name='editar_receita'),
    path('receita/<int:pk>/eliminar/', views.eliminar_receita, name='eliminar_receita'),
    
    # Ingredientes (dentro das receitas)
    path('receita/<int:receita_id>/ingredientes/', views.adicionar_ingredientes, name='adicionar_ingredientes'),
    path('receita/<int:receita_id>/concluir/', views.concluir_receita, name='concluir_receita'),
    path('ingrediente/remover/<int:ingrediente_id>/', views.remover_ingrediente, name='remover_ingrediente'),

    # Planeamento e Lista de Compras
    path('planeamento/', views.ver_planeamento, name='ver_planeamento'),
    path('planeamento/adicionar/<int:receita_id>/', views.adicionar_planeamento, name='adicionar_planeamento'),
    path('planeamento/lista-compras/', views.gerar_lista_compras, name='gerar_lista_compras'),
    path('planeamento/eliminar/<int:plano_id>/', views.eliminar_planeamento, name='eliminar_planeamento'),
    path('planeamento/pdf/', views.exportar_planeamento_pdf, name='exportar_planeamento_pdf'),
    
    # Lista de Compras
    path('lista-compras/exportar/', views.exportar_lista_txt, name='exportar_lista_txt'),
]