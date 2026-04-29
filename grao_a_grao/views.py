from django.shortcuts import render,get_object_or_404
from .models import Receita

# futura página de Login/Registo
def home(request):
    return render(request, 'grao_a_grao/home.html')

# Lista de receitas do utilizador
def lista_receitas(request):
    receitas = Receita.objects.all().order_by('-data_criacao')
    return render(request, 'grao_a_grao/lista_receitas.html', {'receitas': receitas})

def detalhes_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    return render(request, 'grao_a_grao/detalhes_receita.html', {'receita': receita})