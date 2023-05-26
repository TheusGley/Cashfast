
from django.urls import path 
from .views import *



urlpatterns = [
    path('',  login_view,  name='login'),
    path('index', index, name='index'),
    
    path('estabelecimento', listar_vendas, name='estabelecimento'),
    path('lista_estabelecimento', lista_estabelecimentos, name='lista'),
    
    
    
    path('maquinas', maquina, name='maquinas'),
    path('representantes', representantes, name='representantes'),
    
    
    path('estabelecimento_novo', estabelecimento_redirect ,  name='estabelecimento_novo'),
    path('estabelecimento-update/<id>/', update_estabelecimento, name='bond_update'),
    path('api_older/', api_older, name='api_older'),
    
    
    
    path('exportcsv', export_csv, name='exportcsv'),

    
    # path('api', api_estabelecimento, name='api'),
    # path('atualizar', atualizar_status, name='atualizar'),
    # path('limpeza', limpeza, name='limpeza'),
    # path ('importar', importar_dados, name='importar'),

    
    
    path('delete', delete, name='delete'),
    
    

    
    
    

    
    # path('cadastrar/', cadastrar , name='bond_cadastro'),
    # path('cadastrar-confirm/', cadastrar_confirm , name='bond_cadastro_con'),
    
    

]
