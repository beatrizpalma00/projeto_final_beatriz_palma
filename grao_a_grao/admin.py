from django.contrib import admin
from .models import Planeamento, Receita, Ingrediente

# GESTÃO DE RECEITAS E INGREDIENTES

class IngredienteInline(admin.TabularInline):
    model = Ingrediente
    extra = 0  # Alterado para 0 para limpar a interface pq os ingredientes agr são geridos nos detalhes da receita

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    inlines = [IngredienteInline]
    list_display = ('titulo', 'autor', 'data_criacao')

# GESTÃO DO PLANEAMENTO

admin.site.register(Planeamento)