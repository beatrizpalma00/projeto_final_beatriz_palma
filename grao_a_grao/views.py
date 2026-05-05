from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Planeamento, Receita, Ingrediente, IngredienteDespensa, EstadoLista
from .forms import PlaneamentoForm, RegistoReceitaForm, IngredienteForm
from django.http import HttpResponse
from datetime import date
from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa

# FUNÇÕES DE AUTENTICAÇÃO E HOME

def home(request):
    return render(request, 'grao_a_grao/home.html')

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
@login_required
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
        'tipo_selecionado': tipo,
        
    })

# Detalhes de uma receita especifica
@login_required
def detalhes_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, autor=request.user)
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
    return render(request, 'grao_a_grao/registo_receita.html', {'form': form}) #redireciona para adicionar ingredientes

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

# Função para visualizar o planeamento semanal organizado por dias e c/ tipos de refeição e pratos em etiquetas
@login_required
def ver_planeamento(request):
    planos = Planeamento.objects.filter(utilizador=request.user, data__gte=date.today()).order_by('data', 'tipo_refeicao', 'receita__tipo_prato')
    return render(request, 'grao_a_grao/ver_planeamento.html', {'planos': planos})

# Função para adicionar uma refeição ao planeamento - com formulário para escolher data e tipo de refeição (pequeno-almoço, almoço, jantar)
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
    """Função única para Mover ou Copiar uma refeição."""
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
        messages.success(request, "Todo o planeamento e marcações de despensa foram apagados.")
    return redirect('ver_planeamento')

# Função para eliminar o histórico de dias anteriores ao dia atual
@login_required
def limpar_passado(request):
    if request.method == 'POST':
        Planeamento.objects.filter(utilizador=request.user, data__lt=date.today()).delete() # Apaga o planeamento antigo (data menor que hoje)
        IngredienteDespensa.objects.filter(utilizador=request.user).delete() # Limpa os itens da despensa
        # Reset do estado da lista na base de dados
        estado, _ = EstadoLista.objects.get_or_create(utilizador=request.user)
        estado.gerada = False
        estado.save()
        messages.success(request, "Histórico e marcações da despensa foram limpos.")
    return redirect('ver_planeamento')

# Função para eliminar um dia inteiro do planeamento
@login_required
def eliminar_dia_inteiro(request, data_str):
    if request.method == 'POST':
        Planeamento.objects.filter(utilizador=request.user, data=data_str).delete()
        messages.success(request, f"O dia {data_str} foi apagado do planeamento.")
    return redirect('ver_planeamento')

#FUNÇÕES DA LISTA DE COMPRAS E EXPORTAÇÕES

# Função para gerar a lista de compras a partir do planeamento - soma as quantidades dos ingredientes necessários para as receitas planeadas e organiza por secção do supermercado
@login_required
def gerar_lista_compras(request):
    estado, _ = EstadoLista.objects.get_or_create(utilizador=request.user)

    # Se o utilizador clicar no botão (parâmetro ?gerar=1), ativamos a lista
    if request.GET.get('gerar') == '1':
        estado.gerada = True
        estado.save()

    # Se a lista ainda não foi "criada" ou está inativa, retorna a página vazia
    if not estado.gerada:
        return render(request, 'grao_a_grao/lista_compras.html', {
            'lista': [],
            'planos': [],
            'lista_vazia': True
        })

    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    )

    # Obtém itens que o utilizador já marcou como tendo na despensa
    itens_despensa = IngredienteDespensa.objects.filter(utilizador=request.user).values_list('chave_ingrediente', flat=True)

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
                    'chave': chave, # Enviamos a chave para o botão do template
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

    return render(request, 'grao_a_grao/lista_compras.html', {
        'lista': lista_ordenada,
        'lista_despensa': despensa_ordenada,
        'planos': planos
    })

# Função para exportar a lista de compras em formato TXT  
@login_required
def exportar_lista_txt(request):
    
    planos = Planeamento.objects.filter(
        utilizador=request.user, 
        data__gte=date.today()
    )

    itens_despensa = IngredienteDespensa.objects.filter(utilizador=request.user).values_list('chave_ingrediente', flat=True)

    # Tabela de conversão idêntica à da visualização
    CONVERSOES = {
        'gr': ('kg', Decimal('0.001')),
        'ml': ('l', Decimal('0.001')),
        'kg': ('kg', 1),
        'l': ('l', 1),
        'uni': ('uni', 1),
    }

    lista_final = {}
    for plano in planos:
        for ing in plano.receita.ingredientes.all():
            # Normaliza as quantidades para unidade base
            unidade_info = CONVERSOES.get(ing.unidade, (ing.unidade, 1))
            unidade_base = unidade_info[0]
            fator = Decimal(str(unidade_info[1]))
            quantidade_base = ing.quantidade * fator
            
            # Normalização para agrupamento na exportação
            chave = f"{ing.nome.strip().lower()}-{unidade_base}-{ing.secao}"
            
            # Ignora na exportação itens que estão na despensa
            if chave in itens_despensa:
                continue
            
            if chave in lista_final:
                lista_final[chave]['quantidade'] += quantidade_base
            else:
                lista_final[chave] = {
                    'nome': ing.nome,
                    'quantidade': quantidade_base,
                    'unidade': unidade_base,
                    'secao': ing.secao,
                    'secao_display': ing.get_secao_display()
                }

    # Ajuste final de unidades para o ficheiro TXT
    for item in lista_final.values():
        if item['unidade'] == 'kg' and item['quantidade'] < 1:
            item['quantidade'] = item['quantidade'] * 1000
            item['unidade'] = 'g'
        elif item['unidade'] == 'l' and item['quantidade'] < 1:
            item['quantidade'] = item['quantidade'] * 1000
            item['unidade'] = 'ml'
        if item['unidade'] == 'gr': item['unidade'] = 'g'

    
    # Ordena por secção e nome para combinar com o site
    lista_ordenada = sorted(lista_final.values(), key=lambda x: (x['secao_display'], x['nome']))
    
    conteudo = "🛒 MINHA LISTA DE COMPRAS - GRAO A GRAO\n"
    conteudo += f"Gerada em: {date.today().strftime('%d/%m/%Y')}\n"
    conteudo += "A sua lista de compras está organizada por secções e apresenta a quantidade dos produtos que vai precisar para realizar as suas refeições.\n"
    conteudo += "Nota: Os produtos à venda no supermercado podem ser em embalagens de quantidades diferentes.\n"
    conteudo += "------------------------------------------\n"

    seccao_atual = ""
    for item in lista_ordenada:
        if item['secao_display'] != seccao_atual:
            seccao_atual = item['secao_display']
            conteudo += f"\n[{seccao_atual.upper()}]\n"
                
        # Formata para remover zeros desnecessários (ex: 1.00 vira 1)
        quantidade_formatada = float(item['quantidade'].normalize()) if isinstance(item['quantidade'], Decimal) else item['quantidade']
        conteudo += f"[ ] {quantidade_formatada} {item['unidade']} de {item['nome']}\n"
    
    response = HttpResponse(conteudo, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lista_compras_grao.txt"'
    
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

# Função para exportar o planeamento semanal em formato PDF
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
                
        # Limpar emojis e ícones (caracteres Unicode SMP) para evitar quadrados pretos no PDF
        tipo_prato = "".join(c for c in p.receita.get_tipo_prato_display() if ord(c) < 65536).strip()
        titulo_receita = "".join(c for c in p.receita.titulo if ord(c) < 65536).strip()

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