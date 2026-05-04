from django.db import models
from django.contrib.auth.models import User

class Receita(models.Model):
    OPCOES_CATEGORIA = [
        ('carne', 'Carne'),
        ('peixe', 'Peixe'),
        ('vegetariano', 'Vegetariano'),
        ('vegan', 'Vegan'),
    ]

    
    OPCOES_TIPO = [
        ('1_entrada', 'Entrada'),
        ('2_principal', 'Prato Principal'),
        ('3_sobremesa', 'Sobremesa'),
        ('4_lanche_pq_almoco', 'Lanche / Pequeno-Almoço'),
    ]

    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=OPCOES_CATEGORIA, default='carne')
    tipo_prato = models.CharField(max_length=50, choices=OPCOES_TIPO, default='2_principal')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    preparacao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Ingrediente(models.Model):
    UNIDADE_CHOICES = [
        ('gr', 'g'),
        ('kg', 'kg'),
        ('uni', 'un'),
        ('l', 'l'),
        ('ml', 'ml'),
    ]
    
    SECOES_CHOICES = [
        ('legumes_fruta', 'Legumes e Fruta'),
        ('talho_peixaria', 'Talho e Peixaria'),
        ('mercearia', 'Mercearia'),
        ('laticinios_ovos', 'Laticínios e Ovos'),
        ('congelados', 'Congelados'),
        ('temperos_especiarias', 'Temperos e Especiarias'),
        ('outros', 'Outros'),
    ]
    
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='ingredientes')
    nome = models.CharField(max_length=100)
    quantidade = models.DecimalField(max_digits=7, decimal_places=2)
    unidade = models.CharField(max_length=50, choices=UNIDADE_CHOICES, default='gr')
    secao = models.CharField(max_length=50, choices=SECOES_CHOICES, default='outros')
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade} {self.unidade})"
    
class Planeamento(models.Model):
    
    REFEICAO_CHOICES = [
        ('1_pequeno_almoco', 'Pequeno-almoço'),
        ('2_almoco', 'Almoço'),
        ('3_lanche', 'Lanche'),
        ('4_jantar', 'Jantar'),
    ]

    utilizador = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    data = models.DateField()
    tipo_refeicao = models.CharField(max_length=20, choices=REFEICAO_CHOICES)
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)

    class Meta:
                
        ordering = ['data', 'tipo_refeicao', 'receita__tipo_prato']

    def __str__(self):
        return f"{self.data} - {self.get_tipo_refeicao_display()} - {self.receita.titulo}"