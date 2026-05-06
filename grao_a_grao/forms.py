from django import forms
from .models import Receita, Ingrediente, Planeamento
from django.db.models import Q

# GESTÃO DE RECEITAS

class RegistoReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['titulo', 'categoria', 'tipo_prato', 'preparacao', 'is_public']
        labels = {
            'titulo': 'Título da Receita',
            'categoria': 'Categoria',
            'tipo_prato': 'Tipo de Prato',
            'preparacao': 'Modo de Preparação',
            'is_public': 'Tornar Receita Pública (visível para todos)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Arroz de Lentilhas'}),
            'preparacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

# GESTÃO DE INGREDIENTES

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nome', 'quantidade', 'unidade', 'secao']
        labels = {
            'nome': 'Nome do Ingrediente',
            'quantidade': 'Quantidade',
            'unidade': 'Unidade',
            'secao': 'Secção',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Farinha de Trigo'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'secao': forms.Select(attrs={'class': 'form-control'}),
        }

# GESTÃO DO PLANEAMENTO

class PlaneamentoForm(forms.ModelForm):
    class Meta:
        model = Planeamento
        fields = ['data', 'tipo_refeicao', 'receita']
        labels = {
            'data': 'Para quando?',
            'tipo_refeicao': 'Qual a refeição?',
            'receita': 'Escolhe a tua receita',
        }
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_refeicao': forms.Select(attrs={'class': 'form-control'}),
            'receita': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PlaneamentoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['receita'].queryset = Receita.objects.filter(Q(autor=user) | Q(is_public=True)).distinct()