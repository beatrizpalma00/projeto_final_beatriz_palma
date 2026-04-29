from django.contrib import admin
from .models import Receita, Ingrediente

# Os ingredientes aparecem na página da receita
class IngredienteInline(admin.TabularInline):
    model = Ingrediente
    extra = 3  # Linhas vazias para preencher

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    inlines = [IngredienteInline]
    list_display = ('titulo', 'autor', 'data_criacao')