from django.shortcuts import render
from .models import Receita

# futura página de Login/Registo
def home(request):
    return render(request, 'grao_a_grao/home.html')

# Lista de receitas do utilizador
def lista_receitas(request):
    receitas = Receita.objects.all().order_by('-data_criacao')
    return render(request, 'grao_a_grao/lista_receitas.html', {'receitas': receitas})