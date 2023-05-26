
from apscheduler.schedulers.background import BackgroundScheduler
from .views import api_estabelecimento, limpeza , atualizar_status , importar_dados
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def start():
    print('Starting background scheduler')
    
now = datetime.now()

# Definir o próximo horário de execução para cada tarefa em sequência
next_run_api_estabelecimento = now + timedelta(minutes=10)
next_run_limpeza = next_run_api_estabelecimento + timedelta(minutes=13)
next_run_atualizar_status = next_run_limpeza + timedelta(minutes=14)
next_run_importar_dados = next_run_atualizar_status + timedelta(minutes=15)

# Agendar as tarefas com os próximos horários de execução
scheduler.add_job(api_estabelecimento, 'date', run_date=next_run_api_estabelecimento)
scheduler.add_job(limpeza, 'date', run_date=next_run_limpeza)
scheduler.add_job(atualizar_status, 'date', run_date=next_run_atualizar_status)
scheduler.add_job(importar_dados, 'date', run_date=next_run_importar_dados)

scheduler.start()

