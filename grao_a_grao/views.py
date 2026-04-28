from django.shortcuts import render

# Função para renderizar a página inicial (home)
def home(request):
    return render(request, 'grao_a_grao/home.html')