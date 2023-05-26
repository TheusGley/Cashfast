from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import  *
from .models import *
# from django.views.generic import ListView 
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import requests
import pandas as pd
from datetime import datetime,timedelta,date
from django.utils import timezone
import os
from django.db.models import F
from django.db.models import Count



import csv 







# Create your views here.

# Renderização de templates

@login_required
def lista_estabelecimentos (request): 
    
    estabelecimentos = Estabelecimento.objects.all() 
    form = EstabelecimentoForm()     
    data = {'estabelecimentos': estabelecimentos, 'form': form } 

    return render(request, 'bond/tabela_data.html', data )   

@login_required
def listar_vendas (request): 
    
    vendas = Vendas.objects.all() 
    form = EstabelecimentoForm()     
    data = {'estabelecimentos': vendas, 'form': form } 

    return render(request, 'bond/lista_vendas.html', data )   



   
@login_required
def index(request):


    data = {}    
    data_vendas =   Vendas.objects.all().count()
    data_D195   =     Vendas.objects.filter(modelo="D195").count()
    data_S920   =     Vendas.objects.filter(modelo="S920").count()
    data_1470   =      Vendas.objects.filter(modelo="1470").count()
    data_identificadas = Vendas.objects.filter(modelo=None).count()
    

    
    data['data_vendas'] = data_vendas
    data['data_D195']   = data_D195
    data['data_S920']   = data_S920
    data['data_1470']   = data_1470
    data ['data_identificadas'] = data_identificadas 

    data_ativo = Vendas.objects.filter(status= "ATIVO (Últimos 15 dias)").count()
    data_parado = Vendas.objects.filter(status="PARADO (16 à 30 dias)").count()
    data_retirar = Vendas.objects.filter(status="RETIRAR (Acima de 31 dias)").count()
    
    data['maquinas_ativa'] = data_ativo
    data['maquinas_parada'] = data_parado
    data['maquinas_retirar'] = data_retirar



    
    
    return render(request,'bond/index.html',data)

@login_required
def maquina(request):
    data_vendas = Vendas.objects.all()
    data = {'estabelecimentos': data_vendas }

    return render(request,'bond/maquina.html',data)
   
@login_required
def representantes(request):

    data_vendas = Vendas.objects.all()
    data = {'estabelecimentos': data_vendas }
    
    return render(request,'bond/representantes.html',data)

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Estabelecimento.csv"'
    response.write('\ufeff')  
    
    estabelecimentos  = Vendas.objects.all()
    writer = csv.writer(response)
    writer.writerow(['id','id_vendas', 'nome','representante', 'modelo', 'maquina', 'status', 'ultima_venda' ])
    
    for estabelecimento in  estabelecimentos:
        writer.writerow(
            [estabelecimento.id, estabelecimento.id_vendas, estabelecimento.nome,estabelecimento.representante, estabelecimento.modelo, estabelecimento.status, estabelecimento.ultima_venda,])
        
    return response
 




 # Formularios  
   
@login_required 
def estabelecimento_redirect (request):
   form = EstabelecimentoForm(request.POST or None)
   if form.is_valid():
        form.save()
   
   return redirect('index')  

@login_required
def update_estabelecimento (request, id) :
    data = {}
    estabelecimento = Estabelecimento.objects.get(id=id)
    form = EstabelecimentoForm(request.POST or None, instance=estabelecimento)
    data['estabelecimento'] = estabelecimento
    data['form']= form
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('estabelecimento')
    else:
            return render(request, 'bond/atualizar.html', data)
    
    
    
# Login

@login_required
def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Nome de usuário ou senha inválidos'
            return render(request, 'registration/login.html', {'error_message': error_message})
    else:
        return render(request, 'registration/login.html')

#Views de requisicao

 
def api_estabelecimento():    
    
    TOKEN_BEARER = os.environ.get('TOKEN_BEARER')
    
    
    today = date.today()
    yesterday = today - timedelta(days=3)

    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    api_vendas = f"https://api.zsystems.com.br/vendas?page=1&limit=99999&startDate={start_date}T03:00:00.000Z&endDate={end_date}T03:00:00.000Z&date1=2022-07-28T17:24:13.326Z&date=%7B%22start%22:%222022-11-01T03:00:00.000Z%22,%22end%22:%222022-12-31T03:00:00.000Z%22%7D&omniEstabelecimento&pos&loading=false"

    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(TOKEN_BEARER)}
   
    vendas_response = requests.request("GET", api_vendas, headers=headers)

    dados_vendas = vendas_response.json()
    df_vendas = pd.DataFrame(dados_vendas['vendas'])
    
    ######
    df_excel = pd.read_excel('bond_estabelecimento.xlsx', sheet_name='bond_estabelecimento')
    
    maquina_dict = {}
    serial_set = set()
    for _, row in df_excel.iterrows():
        estabelecimento = Estabelecimento()
        estabelecimento.nome = row['estabelecimento']
        estabelecimento.representante = row['representante']
        estabelecimento.maquina = row['maquina']
        maquina_dict[row['maquina']] = estabelecimento
        serial_set.add(row['maquina'])

    for _, row in df_vendas.iterrows():
        
        if pd.isnull(row['serial']):
            continue
        if Estabelecimento.objects.filter(id_vendas=row['id']).exists():
            continue
        else:
            modelo = 'D195' if str(row['serial']).startswith('1470') else 'S920' if str(row['serial']).startswith('6') else 'Link Pagamento / PIX'
            created = datetime.strptime(row['created'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y')
            estabelecimento_banco = Estabelecimento.objects.filter(maquina=row['serial']).first()
        
            # Verifica se o serial já existe no conjunto
            if estabelecimento_banco:
                
                estabelecimento.ultima_venda = created  # Atualize a última venda para a data atual
                estabelecimento.save()

            else:
                # A máquina não existe, então crie uma nova e adicione ao dicionário e ao conjunto
                estabelecimento = Estabelecimento(maquina=row['serial'], modelo=modelo, ultima_venda=created)
                if pd.notna(row['estabelecimento']):
                    estabelecimento.id_vendas = row['id']
                    estabelecimento.nome = row['estabelecimento']['nome_fantasia']
                    estabelecimento.representante =row['representante'] 
                maquina_dict[row['serial']] = estabelecimento
                            
            
            if row['serial'] in serial_set:
                # O serial já existe, então pule para a próxima iteração
                continue
            
            
            # Adiciona o serial ao conjunto
            serial_set.add(row['serial'])

            # Verifica se o serial já existe no dicionário
            if row['serial'] in maquina_dict:
                # A máquina já existe, então atualize as informações dela
                estabelecimento = maquina_dict[row['serial']]
                estabelecimento.id_vendas = row['id']
                estabelecimento.modelo = modelo
                estabelecimento.ultima_venda = created
            else:
                # A máquina não existe, então crie uma nova e adicione ao dicionário
                estabelecimento = Estabelecimento(maquina=row['serial'], modelo=modelo, ultima_venda=created)
                if pd.notna(row['estabelecimento']):
                    estabelecimento.id_vendas = row['id']
                    estabelecimento.nome = row['estabelecimento']['nome_fantasia']
                    estabelecimento.representante =row['representante'] 
                maquina_dict[row['serial']] = estabelecimento
            
            data_de_30dias = (datetime.now() - timedelta(days=30)).date()
            data_de_16dias = (datetime.now() - timedelta(days=16)).date()
            data_de_15dias = (datetime.now() - timedelta(days=15)).date()
            data_ultima_venda = datetime.strptime(created, '%d/%m/%Y').date()

            if data_ultima_venda >= data_de_15dias:
                estabelecimento.status = " ATIVO (Últimos 15 dias)"
                
            elif   data_de_16dias <= data_ultima_venda < data_de_30dias:
                estabelecimento.status = "PARADO (16 à 30 dias)"                
                
            elif  data_ultima_venda < data_de_30dias :
                estabelecimento.status = " RETIRAR (Acima de 31 dias)"                
            
       
            estabelecimento.save()
    return HttpResponse( print ('tabela feita' ) )

def api_older(request):    
    
    TOKEN_BEARER = os.environ.get('TOKEN_BEARER')
    
    
    
    api_vendas = f"https://api.zsystems.com.br/vendas?page=1&limit=999999&startDate=2023-03-01T03:00:00.000Z&endDate=2023-03-01T03:00:00.000Z&date1=2022-07-28T17:24:13.326Z&date=%7B%22start%22:%222022-11-01T03:00:00.000Z%22,%22end%22:%222022-12-31T03:00:00.000Z%22%7D&omniEstabelecimento&pos&loading=false"

    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(TOKEN_BEARER)}
   
    vendas_response = requests.request("GET", api_vendas, headers=headers)

    dados_vendas = vendas_response.json()
    df_vendas = pd.DataFrame(dados_vendas['vendas'])
    
    ######
    df_excel = pd.read_excel('bond_estabelecimento.xlsx', sheet_name='bond_estabelecimento')
    
    maquina_dict = {}
    serial_set = set()
    for _, row in df_excel.iterrows():
        estabelecimento = Estabelecimento()
        estabelecimento.nome = row['estabelecimento']
        estabelecimento.representante = row['representante']
        estabelecimento.maquina = row['maquina']
        maquina_dict[row['maquina']] = estabelecimento
        serial_set.add(row['maquina'])

    for _, row in df_vendas.iterrows():
        
        if pd.isnull(row['serial']):
            continue
        if Estabelecimento.objects.filter(id_vendas=row['id']).exists():
            continue
        else:
            modelo = 'D195' if str(row['serial']).startswith('1470') else 'S920' if str(row['serial']).startswith('6') else 'Link Pagamento / PIX'
            created = datetime.strptime(row['created'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y')
            estabelecimento_banco = Estabelecimento.objects.filter(maquina=row['serial']).first()
        
            # Verifica se o serial já existe no conjunto
            if estabelecimento_banco:
                
                estabelecimento.ultima_venda = created  # Atualize a última venda para a data atual
                estabelecimento.save()

            else:
                # A máquina não existe, então crie uma nova e adicione ao dicionário e ao conjunto
                estabelecimento = Estabelecimento(maquina=row['serial'], modelo=modelo, ultima_venda=created)
                if pd.notna(row['estabelecimento']):
                    estabelecimento.id_vendas = row['id']
                    estabelecimento.nome = row['estabelecimento']['nome_fantasia']
                    estabelecimento.representante =row['representante'] 
                maquina_dict[row['serial']] = estabelecimento
                            
            
            if row['serial'] in serial_set:
                # O serial já existe, então pule para a próxima iteração
                continue
            
            
            # Adiciona o serial ao conjunto
            serial_set.add(row['serial'])

            # Verifica se o serial já existe no dicionário
            if row['serial'] in maquina_dict:
                # A máquina já existe, então atualize as informações dela
                estabelecimento = maquina_dict[row['serial']]
                estabelecimento.id_vendas = row['id']
                estabelecimento.modelo = modelo
                estabelecimento.ultima_venda = created
            else:
                # A máquina não existe, então crie uma nova e adicione ao dicionário
                estabelecimento = Estabelecimento(maquina=row['serial'], modelo=modelo, ultima_venda=created)
                if pd.notna(row['estabelecimento']):
                    estabelecimento.id_vendas = row['id']
                    estabelecimento.nome = row['estabelecimento']['nome_fantasia']
                    estabelecimento.representante =row['representante'] 
                maquina_dict[row['serial']] = estabelecimento
            
            data_de_30dias = (datetime.now() - timedelta(days=30)).date()
            data_de_16dias = (datetime.now() - timedelta(days=16)).date()
            data_de_15dias = (datetime.now() - timedelta(days=15)).date()
            data_ultima_venda = datetime.strptime(created, '%d/%m/%Y').date()

            if data_ultima_venda >= data_de_15dias:
                estabelecimento.status = " ATIVO (Últimos 15 dias)"
                
            elif   data_de_16dias <= data_ultima_venda < data_de_30dias:
                estabelecimento.status = "PARADO (16 à 30 dias)"                
                
            elif  data_ultima_venda < data_de_30dias :
                estabelecimento.status = " RETIRAR (Acima de 31 dias)"                
            
       
            estabelecimento.save()
    return redirect( "index" )
         

# Modelagem de dados no Modelo Estabelecimento 
def atualizar_status():
    # Verificar se passaram mais de 15 dias desde a última venda

    estabelecimentos = Estabelecimento.objects.all()

    data_de_30dias = timezone.now() - timedelta(days=30)
    data_de_16dias = timezone.now() - timedelta(days=16)
    data_de_15dias = timezone.now() - timedelta(days=15)

    for estabelecimento in estabelecimentos:
        ultima_venda = datetime.strptime(estabelecimento.ultima_venda, '%d/%m/%Y').date()


        if ultima_venda >= data_de_15dias.date():
            estabelecimento.status = "ATIVO (Últimos 15 dias)"
        elif ultima_venda < data_de_16dias.date() and ultima_venda > data_de_30dias.date():
            estabelecimento.status = "PARADO (16 à 30 dias)"
        elif ultima_venda < data_de_30dias.date():
            estabelecimento.status = "RETIRAR (Acima de 31 dias)"
            
        estabelecimento.save()
    
    return HttpResponse ( print('datas atualizadas') )
   

def limpeza ():
       
    estabelecimento_delete = Estabelecimento.objects.order_by('maquina', 'ultima_venda')

    maquinas_repetidas = []
    maquina_anterior = None

    for estabelecimento in estabelecimento_delete:
        if estabelecimento.maquina == maquina_anterior:
            maquinas_repetidas.append(estabelecimento.maquina)
        maquina_anterior = estabelecimento.maquina

    for maquina in maquinas_repetidas:
        entradas_repetidas = Estabelecimento.objects.filter(maquina=maquina).order_by('ultima_venda')
        entrada_antiga = entradas_repetidas.first()
        entradas_repetidas.exclude(id=entrada_antiga.id).delete()
        
    # Identifique os registros duplicados
    duplicados = Estabelecimento.objects.values('id_vendas').annotate(Count('id_vendas')).filter(id_vendas__count__gt=1)

    # Remova os registros duplicados, mantendo apenas um deles
    for duplicado in duplicados:
        registros_duplicados = Vendas.objects.filter(id_vendas=duplicado['id_vendas']).distinct()
        registros_duplicados.delete()
    return HttpResponse ( print('dados limpos') )
    




def importar_dados():
    estabelecimentos = Estabelecimento.objects.all()  # Obtém todos os dados do modelo de origem
    
    # Itera sobre os dados e cria ou atualiza os registros no modelo de destino
    for estabelecimento in estabelecimentos:
        # Filtra os registros existentes com base no campo id_vendas
        vendas = Vendas.objects.filter(id_vendas=estabelecimento.id_vendas)
        
        if vendas.exists():
            # Atualiza os campos do modelo de destino com os valores do modelo de origem
            vendas.update(
                nome=estabelecimento.nome,
                representante=estabelecimento.representante,
                modelo=estabelecimento.modelo,
                maquina=estabelecimento.maquina,
                status=estabelecimento.status,
                ultima_venda=estabelecimento.ultima_venda,
                # Mapeie todos os campos que você deseja importar
            )
        else:
            # Cria um novo registro no modelo de destino
            Vendas.objects.create(
                id_vendas=estabelecimento.id_vendas,
                nome=estabelecimento.nome,
                representante=estabelecimento.representante,
                modelo=estabelecimento.modelo,
                maquina=estabelecimento.maquina,
                status=estabelecimento.status,
                ultima_venda=estabelecimento.ultima_venda,
                # Mapeie todos os campos que você deseja importar
            )
    
    return HttpResponse ( print('dados importados') )


@login_required 
def delete (request):
    
    objetos    = Vendas.objects.all()    
   
    for objeto in objetos:
        objeto.delete()
    return HttpResponse ('Tabela apagada ')

 



