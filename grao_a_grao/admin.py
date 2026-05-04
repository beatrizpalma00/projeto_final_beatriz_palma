from django.contrib import admin
from .models import Planeamento, Receita, Ingrediente
admin.site.register(Planeamento)


class IngredienteInline(admin.TabularInline):
    model = Ingrediente
    extra = 3  # Linhas vazias para preencher

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    inlines = [IngredienteInline]
    list_display = ('titulo', 'autor', 'data_criacao')