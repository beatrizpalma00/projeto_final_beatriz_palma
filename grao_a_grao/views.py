from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Planeamento, Receita, Ingrediente
from .forms import PlaneamentoForm, RegistoReceitaForm, IngredienteForm
from django.http import HttpResponse
from datetime import date
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



# Página de Login/Registo
def home(request):
    return render(request, 'grao_a_grao/home.html')

# Lista de receitas do utilizador
def lista_receitas(request):
    receitas = Receita.objects.filter(autor=request.user).order_by('-data_criacao')
    
    q = request.GET.get('q')
    cat = request.GET.get('categoria')
    tipo = request.GET.get('tipo')
    
    if q:
        receitas = receitas.filter(titulo__icontains=q)
        
    if cat:
        receitas = receitas.filter(categoria=cat)
        
    if tipo:
        receitas = receitas.filter(tipo_prato=tipo)

    return render(request, 'grao_a_grao/lista_receitas.html', {
        'receitas': receitas,
        'valor_pesquisa': q,           
        'categoria_selecionada': cat,  
        'tipo_selecionado': tipo       
    })

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

    ingredientes_atuais = receita.ingredientes.all()
    return render(request, 'grao_a_grao/adicionar_ingredientes.html', {
        'form': form,
        'receita': receita,
        'ingredientes': ingredientes_atuais
    })

@login_required
def concluir_receita(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id, autor=request.user)
        
    if receita.ingredientes.count() == 0:
        messages.error(request, "Erro: Tens de adicionar pelo menos um ingrediente antes de gravar a receita!")
        return redirect('adicionar_ingredientes', receita_id=receita.id)
        
    messages.success(request, f"Receita '{receita.titulo}' gravada com sucesso!")
    return redirect('lista_receitas')
    
@login_required
def eliminar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
    if request.method == 'POST':
        receita.delete()
        messages.success(request, "Receita eliminada com sucesso!")
        return redirect('lista_receitas')
    return redirect('detalhes_receita', pk=pk)

@login_required
def editar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
    
    if request.method == 'POST':
        form = RegistoReceitaForm(request.POST, instance=receita)
        if form.is_valid():
            form.save()
            messages.success(request, "Informações da receita atualizadas!")
            return redirect('adicionar_ingredientes', receita_id=receita.id)
    else:
        form = RegistoReceitaForm(instance=receita)
    
    return render(request, 'grao_a_grao/registo_receita.html', {
        'form': form,
        'editando': True,
        'receita': receita
    })
    
@login_required
def remover_ingrediente(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, receita__autor=request.user)
    receita_id = ingrediente.receita.id
    ingrediente.delete()
    messages.success(request, "Ingrediente removido com sucesso!")
    return redirect('adicionar_ingredientes', receita_id=receita_id)

@login_required
def adicionar_planeamento(request, receita_id):
    
    receita = get_object_or_404(Receita, id=receita_id)
    
    if request.method == 'POST':
        
        form = PlaneamentoForm(request.POST, user=request.user)
        if form.is_valid():
            planeamento = form.save(commit=False)
            planeamento.utilizador = request.user
            planeamento.receita = receita 
            planeamento.save()
            messages.success(request, f"{receita.titulo} adicionada ao planeamento!")
            return redirect('ver_planeamento')
    else:
        
        form = PlaneamentoForm(user=request.user, initial={'receita': receita})
    
    return render(request, 'grao_a_grao/adicionar_planeamento.html', {
        'form': form,
        'receita': receita
    })

@login_required
def ver_planeamento(request):
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    ).order_by('data', 'tipo_refeicao')
    
    return render(request, 'grao_a_grao/ver_planeamento.html', {'planos': planos})

@login_required
def gerar_lista_compras(request):
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    )

    lista_final = {}

    for plano in planos:
        receita = plano.receita
        for ing in receita.ingredientes.all():
            
            chave = f"{ing.nome.lower()}-{ing.unidade.lower()}-{ing.secao}"
            
            if chave in lista_final:
                lista_final[chave]['quantidade'] += ing.quantidade
            else:
                lista_final[chave] = {
                    'nome': ing.nome,
                    'quantidade': ing.quantidade,
                    'unidade': ing.unidade,
                    'secao': ing.secao, 
                    'secao_display': ing.get_secao_display() 
                }

    
    
    lista_ordenada = sorted(lista_final.values(), key=lambda x: x['secao'])

    return render(request, 'grao_a_grao/lista_compras.html', {
        'lista': lista_ordenada,
        'planos': planos
    })
    
@login_required
def eliminar_planeamento(request, plano_id):
    
    plano = get_object_or_404(Planeamento, id=plano_id, utilizador=request.user)
    
    if request.method == 'POST':
        plano.delete()
        messages.success(request, "Refeição removida do planeamento.")
    
    return redirect('ver_planeamento')

@login_required
def exportar_lista_txt(request):
    
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    )

    lista_final = {}
    for plano in planos:
        for ing in plano.receita.ingredientes.all():
            
            chave = f"{ing.nome.lower()}-{ing.unidade.lower()}-{ing.secao}"
            if chave in lista_final:
                lista_final[chave]['quantidade'] += ing.quantidade
            else:
                lista_final[chave] = {
                    'nome': ing.nome,
                    'quantidade': ing.quantidade,
                    'unidade': ing.unidade,
                    'secao_display': ing.get_secao_display()
                }

    
    lista_ordenada = sorted(lista_final.values(), key=lambda x: x['secao_display'])
    
    conteudo = "🛒 MINHA LISTA DE COMPRAS - GRAO A GRAO\n"
    conteudo += f"Gerada em: {date.today().strftime('%d/%m/%Y')}\n"
    conteudo += "------------------------------------------\n"

    seccao_atual = ""
    for item in lista_ordenada:
        if item['secao_display'] != seccao_atual:
            seccao_atual = item['secao_display']
            conteudo += f"\n[{seccao_atual.upper()}]\n"
                
        quantidade_formatada = f"{item['quantidade']:.2f}"
        conteudo += f"[ ] {quantidade_formatada} {item['unidade']} de {item['nome']}\n"
    
    response = HttpResponse(conteudo, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lista_compras_grao.txt"'
    
    return response

@login_required
def exportar_planeamento_pdf(request):
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    ).order_by('data', 'tipo_refeicao', 'receita__tipo_prato')

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4; margin: 1cm; }}
            body {{ font-family: Helvetica, sans-serif; color: #333; }}
            h1 {{ text-align: center; color: #2d6a4f; }}
            .dia-header {{ 
                background-color: #a3b18a; 
                color: white; 
                padding: 8px; 
                margin-top: 20px; 
                font-weight: bold;
                border-radius: 5px 5px 0 0;
            }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
            th {{ background-color: #f2f2f2; color: #2d6a4f; padding: 10px; text-align: left; font-size: 10px; border: 1px solid #ddd; }}
            td {{ border: 1px solid #ddd; padding: 10px; font-size: 11px; }}
            .footer {{ text-align: center; font-size: 9px; color: #7f8c8d; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <h1>Grão a Grão - O Meu Planeamento</h1>
    """

    data_atual = None
    
    for p in planos:
        
        if p.data != data_atual:
            if data_atual is not None:
                html_content += "</tbody></table>" # Fecha a tabela do dia anterior
            
            data_atual = p.data
            html_content += f"""
                <div class="dia-header">🗓️ {data_atual.strftime('%d/%m/%Y')}</div>
                <table>
                    <thead>
                        <tr>
                            <th width="20%">REFEIÇÃO</th>
                            <th width="20%">TIPO</th>
                            <th width="60%">RECEITA</th>
                        </tr>
                    </thead>
                    <tbody>
            """
                
        html_content += f"""
            <tr>
                <td>{p.get_tipo_refeicao_display()}</td> 
                <td>{p.receita.get_tipo_prato_display()}</td>
                <td>{p.receita.titulo}</td>
            </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="planeamento_organizado.pdf"'
    
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response    