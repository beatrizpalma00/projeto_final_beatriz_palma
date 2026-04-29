from django.db import models
from django.contrib.auth.models import User

class Receita(models.Model):
    # Lista de opções para a Dieta/Base alimentar
    OPCOES_CATEGORIA = [
        ('carne', 'Carne'),
        ('peixe', 'Peixe'),
        ('vegetariano', 'Vegetariano'),
        ('vegan', 'Vegan'),
    ]

    # Lista de opções para o Momento da Refeição
    OPCOES_TIPO = [
        ('entrada', 'Entrada'),
        ('prato_principal', 'Prato Principal'),
        ('sobremesa', 'Sobremesa'),
        ('lanche', 'Lanche/Pequeno-almoço'),
    ]

    titulo = models.CharField(max_length=200)
    # Implementação dos novos campos com escolhas pré-definidas
    categoria = models.CharField(max_length=50, choices=OPCOES_CATEGORIA, default='carne')
    tipo_prato = models.CharField(max_length=50, choices=OPCOES_TIPO, default='prato_principal')
    
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    preparacao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Ingrediente(models.Model):
    # uma receita, vários ingredientes.
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='ingredientes')
    nome = models.CharField(max_length=100)
    quantidade = models.DecimalField(max_digits=7, decimal_places=2) # Para dar pra somar números com vírgula
    unidade = models.CharField(max_length=50) # Ex: gramas, unidades, kg

    def __str__(self):
        return f"{self.nome} ({self.quantidade} {self.unidade})"