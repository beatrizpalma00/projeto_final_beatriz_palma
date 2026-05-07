from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Planeamento, Receita, Ingrediente, IngredienteDespensa, EstadoLista
from .forms import PlaneamentoForm, RegistoReceitaForm, IngredienteForm
from django.http import HttpResponse
from datetime import date
from decimal import Decimal
from django.db.models import Q
from xhtml2pdf import pisa

# FUNÇÕES DE AUTENTICAÇÃO E HOME

def home(request):
    return render(request, 'grao_a_grao/home.html')

# Página explicativa sobre o projeto
def sobre(request):
    return render(request, 'grao_a_grao/sobre.html')

# Função de registo de utilizadores
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

# FUNÇÕES DE GESTÃO DE RECEITAS

# Listagem de receitas do utilizador logado com filtros para pesquisa
def lista_receitas(request):    
    if request.user.is_authenticated:
        # Utilizador logado vê as suas + as públicas
        receitas = Receita.objects.filter(Q(autor=request.user) | Q(is_public=True))
    else:
        # Visitante vê apenas as públicas
        receitas = Receita.objects.filter(is_public=True)
    
    receitas = receitas.distinct().order_by('-data_criacao')
    
    q = request.GET.get('q')
    cat = request.GET.get('categoria')
    tipo = request.GET.get('tipo')
    origem = request.GET.get('origem')
    
    if q:
        receitas = receitas.filter(titulo__icontains=q)
        
    if cat:
        receitas = receitas.filter(categoria=cat)
        
    if tipo:
        receitas = receitas.filter(tipo_prato=tipo)

    # Lógica para o filtro de origem
    if request.user.is_authenticated:
        if origem == 'minhas' or origem is None: # Se logado e sem filtro, ou filtro 'minhas', mostra as próprias
            receitas = receitas.filter(autor=request.user)
        elif origem == 'publicas': # Se filtro 'publicas', mostra as públicas
            receitas = receitas.filter(is_public=True)
    elif origem == 'publicas': # Para visitantes, só mostra públicas se explicitamente filtrado (ou por defeito)
        receitas = receitas.filter(is_public=True)

    return render(request, 'grao_a_grao/lista_receitas.html', {
        'receitas': receitas,
        'valor_pesquisa': q,           
        'categoria_selecionada': cat,  
        'tipo_selecionado': tipo,
        'origem_selecionada': origem,
        
    })

# Detalhes de uma receita especifica
def detalhes_receita(request, pk):
    if request.user.is_authenticated:
        # Autor vê a sua (privada ou pública) ou qualquer uma pública
        receita = get_object_or_404(Receita.objects.filter(Q(autor=request.user) | Q(is_public=True)), pk=pk)
    else:
        # Visitante só vê se for pública
        receita = get_object_or_404(Receita, pk=pk, is_public=True)
        
    return render(request, 'grao_a_grao/detalhes_receita.html', {'receita': receita})

# Função de registo de receitas
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
    return render(request, 'grao_a_grao/registo_receita.html', {'form': form}) # redireciona para adicionar ingredientes

# Função de edição de receitas - com dados pré-preenchidos para alterar
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
    return render(request, 'grao_a_grao/registo_receita.html', {'form': form, 'editando': True, 'receita': receita})

# Função para concluir a receita - verifica se tem ingredientes antes de finalizar
@login_required
def concluir_receita(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id, autor=request.user)
        
    if receita.ingredientes.count() == 0:
        messages.error(request, "Erro: Tens de adicionar pelo menos um ingrediente antes de gravar a receita!")
        return redirect('adicionar_ingredientes', receita_id=receita.id)
        
    messages.success(request, f"Receita '{receita.titulo}' gravada com sucesso!")    
    return redirect('detalhes_receita', pk=receita.id)

# Função para eliminar uma receita   
@login_required
def eliminar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
    if request.method == 'POST':
        receita.delete()
        messages.success(request, "Receita eliminada com sucesso!")
        return redirect('lista_receitas')
    return redirect('lista_receitas')

# Função para alternar entre pública/privada diretamente na lista
@login_required
def toggle_publico(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
    if request.method == 'POST':
        receita.is_public = not receita.is_public
        receita.save()
        status = "pública" if receita.is_public else "privada"
        messages.success(request, f"A receita '{receita.titulo}' agora é {status}!")
    return redirect('lista_receitas')

# Função para copiar uma receita pública de outro utilizador para a lista pessoal
@login_required
def copiar_receita(request, pk):
    # Garante que apenas receitas públicas podem ser copiadas
    receita_original = get_object_or_404(Receita, pk=pk, is_public=True)
    
    if request.method == 'POST':
        # Cria a nova receita baseada na original, mas com o utilizador atual como autor para não apagar se o original for eliminado
        nova_receita = Receita.objects.create(
            titulo=f"{receita_original.titulo} (Cópia)",
            categoria=receita_original.categoria,
            tipo_prato=receita_original.tipo_prato,
            preparacao=receita_original.preparacao,
            autor=request.user,
            is_public=False # A cópia é privada por defeito
        )
        
        # Duplica todos os ingredientes da receita original
        for ing in receita_original.ingredientes.all():
            Ingrediente.objects.create(receita=nova_receita, nome=ing.nome, quantidade=ing.quantidade, unidade=ing.unidade, secao=ing.secao)
        
        messages.success(request, f"Receita '{receita_original.titulo}' copiada com sucesso para a sua lista!")
        return redirect('detalhes_receita', pk=nova_receita.id)
    return redirect('lista_receitas')

# FUNÇÕES DE GESTÃO DE INGREDIENTES

# Função para adicionar ingredientes à receita 
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
            return redirect('adicionar_ingredientes', receita_id=receita.id) # redireciona para a mesma página para adicionar mais ingredientes
    else:
        form = IngredienteForm()
    ingredientes_atuais = receita.ingredientes.all()
    return render(request, 'grao_a_grao/adicionar_ingredientes.html', {'form': form, 'receita': receita, 'ingredientes': ingredientes_atuais})

# Função para editar ingredientes - com dados pré-preenchidos para alterar   
@login_required
def editar_ingrediente(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, receita__autor=request.user)
    receita = ingrediente.receita
    
    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ingrediente '{ingrediente.nome}' atualizado!")
            return redirect('adicionar_ingredientes', receita_id=receita.id)
    else:
        form = IngredienteForm(instance=ingrediente)

    return render(request, 'grao_a_grao/adicionar_ingredientes.html', {
        'form': form,
        'receita': receita,
        'editando_ingrediente': True
    })

# Função para remover um ingrediente da receita
@login_required
def remover_ingrediente(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, receita__autor=request.user)
    receita_id = ingrediente.receita.id
    ingrediente.delete()
    messages.success(request, "Ingrediente removido com sucesso!")
    return redirect('adicionar_ingredientes', receita_id=receita_id)

# FUNÇÕES DE GESTÃO DO PLANEAMENTO

# Função para visualizar o planeamento organizado por dias e c/ tipos de refeição e pratos em etiquetas
@login_required
def ver_planeamento(request):
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    ).select_related('receita').order_by('data', 'tipo_refeicao', 'receita__tipo_prato')
    return render(request, 'grao_a_grao/ver_planeamento.html', {'planos': planos})

# Função para adicionar uma refeição ao planeamento - com formulário para escolher data e tipo de refeição
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
    return render(request, 'grao_a_grao/adicionar_planeamento.html', {'form': form, 'receita': receita})

# Função para gerir uma refeição do planeamento - permite mover ou copiar a refeição para outra data/tipo de refeição
@login_required
def gerir_refeicao(request, plano_id, acao):    
    plano_original = get_object_or_404(Planeamento, id=plano_id, utilizador=request.user)
    if request.method == 'POST':
        form = PlaneamentoForm(request.POST, user=request.user)
        if form.is_valid():
            nova_data = form.cleaned_data['data']
            novo_tipo = form.cleaned_data['tipo_refeicao']
            
            if acao == 'mover':
                plano_original.data = nova_data
                plano_original.tipo_refeicao = novo_tipo
                plano_original.save()
                messages.success(request, "Refeição alterada com sucesso!")
            
            elif acao == 'copiar':
                Planeamento.objects.create(
                    utilizador=request.user,
                    receita=plano_original.receita,
                    data=nova_data,
                    tipo_refeicao=novo_tipo
                )
                messages.success(request, "Refeição copiada com sucesso!")
            return redirect('ver_planeamento')
    else:
        form = PlaneamentoForm(user=request.user, instance=plano_original)
    return render(request, 'grao_a_grao/gerir_refeicao.html', {'plano': plano_original, 'acao': acao, 'form': form})

# Função para eliminar uma refeição específica do planeamento
@login_required
def eliminar_planeamento(request, plano_id):
    plano = get_object_or_404(Planeamento, id=plano_id, utilizador=request.user)
    if request.method == 'POST':
        plano.delete()
        messages.success(request, "Refeição removida do planeamento.")
    return redirect('ver_planeamento')

# Função para eliminar: todo o planeamento
@login_required
def limpar_tudo(request):
    if request.method == 'POST':
        Planeamento.objects.filter(utilizador=request.user, data__gte=date.today()).delete()
        IngredienteDespensa.objects.filter(utilizador=request.user).delete()
        # Reset do estado da lista na base de dados
        estado, _ = EstadoLista.objects.get_or_create(utilizador=request.user)
        estado.gerada = False
        estado.save()
        messages.success(request, "Todo o planeamento e produtos da lista e despensa foram apagados.")
    return redirect('ver_planeamento')

# Função para eliminar o histórico de dias anteriores ao dia atual
@login_required
def limpar_passado(request):
    if request.method == 'POST':
        Planeamento.objects.filter(utilizador=request.user, data__lt=date.today()).delete() # Apaga o planeamento antigo (data anterior a hoje)
        IngredienteDespensa.objects.filter(utilizador=request.user).delete() # Limpa os itens da despensa
        # Reset do estado da lista na base de dados
        estado, _ = EstadoLista.objects.get_or_create(utilizador=request.user)
        estado.gerada = False
        estado.save()
        messages.success(request, "O planeamento dos dias anteriores e produtos associados foram limpos.")
    return redirect('ver_planeamento')

# Função para eliminar um dia inteiro do planeamento
@login_required
def eliminar_dia_inteiro(request, data_str):
    if request.method == 'POST':
        Planeamento.objects.filter(utilizador=request.user, data=data_str).delete()
        messages.success(request, f"O dia {data_str} foi apagado do planeamento.")
    return redirect('ver_planeamento')

#FUNÇÕES DA LISTA DE COMPRAS E EXPORTAÇÕES

#Função auxiliar para a lógica de cálculo da lista de compras.
# Aplica as conversões necessárias para somar corretamente as quantidades dos ingredientes. 
def _obter_dados_lista_compras(user):   
    planos = Planeamento.objects.filter(
        utilizador=user, 
        data__gte=date.today()
    ).prefetch_related(
        'receita__ingredientes'
    ).order_by('data', 'tipo_refeicao', 'receita__tipo_prato')

    # Obtém itens que o utilizador já marcou como tendo na despensa
    itens_despensa = IngredienteDespensa.objects.filter(utilizador=user).values_list('chave_ingrediente', flat=True)

    # Tabela de conversão: normaliza tudo para Quilos (kg) e Litros (l) para somar corretamente
    CONVERSOES = {
        'gr': ('kg', Decimal('0.001')),
        'ml': ('l', Decimal('0.001')),
        'kg': ('kg', 1),
        'l': ('l', 1),
        'uni': ('uni', 1),
    }

    lista_final = {}
    lista_despensa_final = {}

    for plano in planos:
        for ing in plano.receita.ingredientes.all():
            # Normaliza as quantidades para a unidade base (kg ou l)
            unidade_info = CONVERSOES.get(ing.unidade, (ing.unidade, 1))
            unidade_base = unidade_info[0]
            fator = Decimal(str(unidade_info[1]))
            quantidade_base = ing.quantidade * fator
            
            # Remove espaços extras e converte para minúsculas para agrupar corretamente
            chave = f"{ing.nome.strip().lower()}-{unidade_base}-{ing.secao}"
            
            # Define em que dicionário guardar (lista de compras ou despensa)
            if chave in itens_despensa:
                target_dict = lista_despensa_final
            else:
                target_dict = lista_final

            if chave in target_dict:
                target_dict[chave]['quantidade'] += quantidade_base
            else:
                target_dict[chave] = {
                    'nome': ing.nome,
                    'quantidade': quantidade_base,
                    'chave': chave,
                    'unidade': unidade_base,
                    'secao': ing.secao, 
                    'secao_display': ing.get_secao_display() 
                }

    # Processar conversões finais para ambas as listas
    for d in [lista_final, lista_despensa_final]:
        for item in d.values():
            if item['unidade'] == 'kg' and item['quantidade'] < 1:
                item['quantidade'] = item['quantidade'] * 1000
                item['unidade'] = 'g'
            elif item['unidade'] == 'l' and item['quantidade'] < 1:
                item['quantidade'] = item['quantidade'] * 1000
                item['unidade'] = 'ml'
            if item['unidade'] == 'gr': item['unidade'] = 'g'

    lista_ordenada = sorted(lista_final.values(), key=lambda x: (x['secao_display'], x['nome']))
    despensa_ordenada = sorted(lista_despensa_final.values(), key=lambda x: (x['secao_display'], x['nome']))
    
    return lista_ordenada, despensa_ordenada, planos

# Função para gerar a lista de compras a partir do planeamento
@login_required
def gerar_lista_compras(request):
    estado, _ = EstadoLista.objects.get_or_create(utilizador=request.user)

    if request.GET.get('gerar') == '1':
        estado.gerada = True
        estado.save()

    if not estado.gerada:
        return render(request, 'grao_a_grao/lista_compras.html', {
            'lista': [],
            'planos': [],
            'lista_vazia': True
        })

    lista_ordenada, despensa_ordenada, planos = _obter_dados_lista_compras(request.user)

    return render(request, 'grao_a_grao/lista_compras.html', {
        'lista': lista_ordenada,
        'lista_despensa': despensa_ordenada,
        'planos': planos
    })

# Função para exportar a lista de compras em formato PDF
@login_required
def exportar_lista_pdf(request):
    lista_ordenada, _, _ = _obter_dados_lista_compras(request.user)

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4; margin: 1cm; }}
            body {{ font-family: Helvetica, sans-serif; color: #333; font-size: 13px; background-color: #ffffff; }}
            h1 {{ text-align: center; color: #556B2F; margin-bottom: 5px; font-size: 24px; }}
            .info {{ text-align: center; font-size: 11px; color: #666; margin-bottom: 20px; }}
            .intro {{ 
                background-color: #f2f0ef; 
                padding: 10px; 
                border: 0.5pt solid #636b2f; 
                margin-bottom: 20px;
            }}
            .seccao-header {{ 
                background-color: #556B2F; 
                color: white; 
                padding: 5px 10px; 
                margin-top: 20px; 
                font-weight: bold;
                border-radius: 3px;
                font-size: 15px;
            }}
            .item {{ 
                padding: 8px; 
                border-bottom: 0.5pt solid #eee; 
                font-size: 13px;
            }}
            .checkbox {{ 
                display: inline-block; 
                width: 14px; 
                height: 14px; 
                border: 1px solid #999; 
                margin-right: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>A Minha Lista de Compras</h1>
        <div class="info">Utilizador: {request.user.username} | Gerada em {date.today().strftime('%d/%m/%Y')} via Grão a Grão</div>
        
        <div class="intro">
            A sua lista de compras está organizada por secções e apresenta a quantidade dos produtos que vai precisar para realizar as suas refeições.<br>
            <i style="font-size: 11px; color: #666;">Nota: Os produtos à venda no supermercado podem ser em embalagens de quantidades diferentes.</i>
        </div>
    """

    seccao_atual = ""
    for item in lista_ordenada:
        if item['secao_display'] != seccao_atual:
            seccao_atual = item['secao_display']
            html_content += f'<div class="seccao-header">{seccao_atual.upper()}</div>'
                
        quantidade_formatada = float(item['quantidade'].normalize()) if isinstance(item['quantidade'], Decimal) else item['quantidade']
        
        # Limpar emojis do nome do ingrediente
        nome_limpo = "".join(c for c in item['nome'] if ord(c) < 1000).strip()

        html_content += f"""
            <div class="item">
                <span class="checkbox"></span> {quantidade_formatada} {item['unidade']} de {nome_limpo}
            </div>
        """
    
    html_content += """
    </body>
    </html>
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="lista_compras_grao.pdf"'
    
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response

# Função para esconder um item da lista (marcar como na despensa)
@login_required
def marcar_despensa(request):
    if request.method == 'POST':
        chave = request.POST.get('chave')
        if chave:
            IngredienteDespensa.objects.get_or_create(utilizador=request.user, chave_ingrediente=chave)
            messages.success(request, "Item movido para a despensa.")
    return redirect('gerar_lista_compras')

# Função para devolver um item à lista de compras (remover da despensa)
@login_required
def remover_despensa(request):
    if request.method == 'POST':
        chave = request.POST.get('chave')
        if chave:
            IngredienteDespensa.objects.filter(utilizador=request.user, chave_ingrediente=chave).delete()
            messages.success(request, "Item devolvido à lista de compras.")
    return redirect('gerar_lista_compras')

# Função para exportar o planeamento em formato PDF
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
            body {{ font-family: Helvetica, sans-serif; color: #333; font-size: 13px; background-color: #ffffff; }}
            h1 {{ text-align: center; color: #556B2F; font-size: 24px; }}
            .info {{ text-align: center; font-size: 11px; color: #666; margin-bottom: 20px; }}
            .dia-header {{ 
                background-color: #556B2F; 
                color: white; 
                padding: 8px; 
                margin-top: 20px; 
                font-weight: bold;
                border-radius: 5px 5px 0 0;
                font-size: 15px;
            }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
            th {{ background-color: #f2f0ef; color: #556B2F; padding: 10px; text-align: left; font-size: 12px; border: 1px solid #ddd; }}
            td {{ border: 1px solid #ddd; padding: 10px; font-size: 13px; }}
            .footer {{ text-align: center; font-size: 9px; color: #7f8c8d; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <h1>Grão a Grão - O Meu Planeamento</h1>
        <div class="info">Utilizador: {request.user.username} | Gerado em {date.today().strftime('%d/%m/%Y')}</div>
    """

    data_atual = None
    
    for p in planos:
        
        if p.data != data_atual:
            if data_atual is not None:
                html_content += "</tbody></table>" # Fecha a tabela por dias
            
            data_atual = p.data
            html_content += f"""
                <div class="dia-header">Dia: {data_atual.strftime('%d/%m/%Y')}</div>
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
                
        # Limpar os caracteres especiais para evitar quadrados pretos no PDF
        tipo_prato = "".join(c for c in p.receita.get_tipo_prato_display() if ord(c) < 1000).strip()
        titulo_receita = "".join(c for c in p.receita.titulo if ord(c) < 1000).strip()

        html_content += f"""
            <tr>
                <td>{p.get_tipo_refeicao_display()}</td> 
                <td>{tipo_prato}</td>
                <td>{titulo_receita}</td>
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