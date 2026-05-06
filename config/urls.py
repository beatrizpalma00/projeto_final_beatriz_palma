from django.contrib import admin
from django.urls import path
from grao_a_grao import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # AUTENTICAÇÃO E HOME
    
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('registo/', views.registo, name='registo'),
    path('login/', auth_views.LoginView.as_view(template_name='grao_a_grao/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ALTERAÇÃO DE PASSWORD
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='grao_a_grao/password_change_form.html'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='grao_a_grao/password_change_done.html'
    ), name='password_change_done'),
    
    # GESTÃO DE RECEITAS
    
    path('receitas/', views.lista_receitas, name='lista_receitas'),
    path('receita/nova/', views.registo_receita, name='registo_receita'),
    path('receita/<int:pk>/', views.detalhes_receita, name='detalhes_receita'),
    path('receita/<int:pk>/editar/', views.editar_receita, name='editar_receita'),
    path('receita/<int:pk>/eliminar/', views.eliminar_receita, name='eliminar_receita'),
    path('receita/<int:pk>/toggle-publico/', views.toggle_publico, name='toggle_publico'),
    path('receita/<int:pk>/copiar/', views.copiar_receita, name='copiar_receita'),
        
    # GESTÃO DE INGREDIENTES
  
    path('receita/<int:receita_id>/ingredientes/', views.adicionar_ingredientes, name='adicionar_ingredientes'),
    path('receita/<int:receita_id>/concluir/', views.concluir_receita, name='concluir_receita'),
    path('ingrediente/remover/<int:ingrediente_id>/', views.remover_ingrediente, name='remover_ingrediente'),
    path('ingrediente/editar/<int:ingrediente_id>/', views.editar_ingrediente, name='editar_ingrediente'),
    
    # PLANEAMENTO DE REFEIÇÕES
    
    path('planeamento/', views.ver_planeamento, name='ver_planeamento'),
    path('planeamento/adicionar/<int:receita_id>/', views.adicionar_planeamento, name='adicionar_planeamento'),
    path('planeamento/limpar-tudo/', views.limpar_tudo, name='limpar_tudo'),
    path('planeamento/limpar-passado/', views.limpar_passado, name='limpar_passado'),
    path('planeamento/eliminar-dia/<str:data_str>/', views.eliminar_dia_inteiro, name='eliminar_dia_inteiro'),
    path('planeamento/eliminar-refeicao/<int:plano_id>/', views.eliminar_planeamento, name='eliminar_planeamento'),
    path('planeamento/gerir/<int:plano_id>/<str:acao>/', views.gerir_refeicao, name='gerir_refeicao'),
        
    #  LISTA DE COMPRAS E EXPORTAÇÕES
    
    path('planeamento/lista-compras/', views.gerar_lista_compras, name='gerar_lista_compras'),
    path('planeamento/lista-compras/despensa/', views.marcar_despensa, name='marcar_despensa'),
    path('planeamento/lista-compras/despensa/remover/', views.remover_despensa, name='remover_despensa'),
    path('lista-compras/pdf/', views.exportar_lista_pdf, name='exportar_lista_pdf'),
    path('planeamento/pdf/', views.exportar_planeamento_pdf, name='exportar_planeamento_pdf'),
]