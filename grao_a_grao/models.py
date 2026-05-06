from django.db import models
from django.contrib.auth.models import User

# GESTÃO DE RECEITAS

class Receita(models.Model):
    OPCOES_CATEGORIA = [
        ('carne', '🥩 Carne'),
        ('peixe', '🐟 Peixe'),
        ('vegetariano', '🥗 Vegetariano'),
        ('vegan', '🌱 Vegan'),
        ('outros', '🍽️ Outros/Geral'),
    ]

    
    OPCOES_TIPO = [
        ('1_entrada', '🥟 Entrada'),
        ('1.5_sopa', '🥣 Sopa'),
        ('2_principal', '🍽️ Prato Principal'),
        ('3_sobremesa', '🍰 Sobremesa'),
        ('4_lanche_pq_almoco', '☕🥪 Lanche / Pequeno-Almoço'),
    ]

    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=OPCOES_CATEGORIA, default='carne')
    tipo_prato = models.CharField(max_length=20, choices=OPCOES_TIPO, default='2_principal')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    preparacao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

# GESTÃO DE INGREDIENTES

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
    unidade = models.CharField(max_length=20, choices=UNIDADE_CHOICES)
    secao = models.CharField(max_length=50, choices=SECOES_CHOICES, default='outros')
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade} {self.unidade})"

# GESTÃO DO PLANEAMENTO

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

# LISTA DE COMPRAS E EXPORTAÇÕES

class IngredienteDespensa(models.Model):
    utilizador = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    chave_ingrediente = models.CharField(max_length=255) # Identificador único: nome-unidade-seccao

    def __str__(self):
        return f"{self.utilizador.username} tem: {self.chave_ingrediente}"

class EstadoLista(models.Model):
    utilizador = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estado_lista')
    gerada = models.BooleanField(default=False)

    def __str__(self):
        return f"Lista de {self.utilizador.username}: {'Ativa' if self.gerada else 'Inativa'}"