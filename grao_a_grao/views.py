from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Receita, Ingrediente
from .forms import RegistoReceitaForm, IngredienteForm

#página de Login/Registo
def home(request):
    return render(request, 'grao_a_grao/home.html')

# Lista de receitas do utilizador
@login_required
def lista_receitas(request):
    receitas = Receita.objects.filter(autor=request.user).order_by('-data_criacao')
    return render(request, 'grao_a_grao/lista_receitas.html', {'receitas': receitas})

@login_required
def detalhes_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
    return render(request, 'grao_a_grao/detalhes_receita.html', {'receita': receita})

def registo(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registo concluído com sucesso!")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'grao_a_grao/registo.html', {'form': form})


@login_required
def registo_receita(request):
    if request.method == 'POST':
        form = RegistoReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.autor = request.user
            receita.save()
            return redirect('adicionar_ingredientes', receita_id=receita.id)
    else:
        form = RegistoReceitaForm()
    return render(request, 'grao_a_grao/registo_receita.html', {'form': form})

@login_required
def adicionar_ingredientes(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id, autor=request.user)
    
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            ingrediente = form.save(commit=False)
            ingrediente.receita = receita
            ingrediente.save()
            messages.success(request, f"Adicionado: {ingrediente.nome}")
            return redirect('adicionar_ingredientes', receita_id=receita.id)
    else:
        form = IngredienteForm()

    ingredientes_atuais = Ingrediente.objects.filter(receita=receita)
    return render(request, 'grao_a_grao/adicionar_ingredientes.html', {
        'form': form,
        'receita': receita,
        'ingredientes': ingredientes_atuais
    })

@login_required
def concluir_receita(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id, autor=request.user)
    
    # Usamos 'ingredientes' porque foi o que definiste no related_name
    if receita.ingredientes.exists():
        messages.success(request, "Receita guardada com sucesso!")
        return redirect('lista_receitas')
    else:
        messages.error(request, "Adiciona pelo menos um ingrediente antes de concluir.")
        return redirect('adicionar_ingredientes', receita_id=receita.id)