from django import forms
from .models import Receita, Ingrediente

class RegistoReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['titulo', 'categoria', 'tipo_prato', 'preparacao']
        labels = {
            'titulo': 'Título da Receita',
            'categoria': 'Base Alimentar',
            'tipo_prato': 'Momento da Refeição',
            'preparacao': 'Modo de Preparação',
        }

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nome', 'quantidade', 'unidade']
        labels = {
            'nome': 'Nome do Ingrediente',
            'quantidade': 'Quantidade',
            'unidade': 'Unidade (ex: gr, kg, un, colher)',
        }