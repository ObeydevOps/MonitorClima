import requests
import sqlite3
from datetime import datetime, timedelta
import time
import os

# --- CONFIGURAÇÕES DA API ---
# A chave é lida de forma segura da variável de ambiente CLIMATE_API_KEY
API_KEY = os.environ.get("CLIMATE_API_KEY") 
CIDADE = "Sua_cidade_aqui" 
URL_BASE = f"https://api.hgbrasil.com/weather?format=json&city_name={CIDADE}&key={API_KEY}"

ID_TEMP = 1 
ID_UMIDADE = 2
# 8640 segundos = 2 horas e 24 minutos (Garante 10 consultas em 24h)
INTERVALO_COLETA_SEGUNDOS = 8640 

if not API_KEY:
    # Levanta um erro se a variável de ambiente não estiver definida
    raise ValueError("A chave da API não foi encontrada. Defina a variável de ambiente 'CLIMATE_API_KEY'.")

# --- FUNÇÕES DE SUPORTE ---

def get_db_connection():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect('monitoramento.db')

def get_last_timestamp(conn):
    """Obtém o carimbo de data/hora da última coleta bem-sucedida no DB."""
    cursor = conn.cursor()
    # Pega o timestamp mais recente em toda a tabela de leituras
    cursor.execute("SELECT MAX(timestamp_leitura) FROM leituras") 
    last_time_str = cursor.fetchone()[0]
    
    if last_time_str:
        # Converte a string do DB para um objeto datetime
        return datetime.strptime(last_time_str, '%Y-%m-%d %H:%M:%S')
    return None

# --- FUNÇÃO PRINCIPAL DE COLETA (MODIFICADA E ROBUSTA) ---

def buscar_e_salvar_dados():
    """Faz a requisição à API, processa e insere no DB."""
    try:
        # 1. EXTRAÇÃO (E)
        response = requests.get(URL_BASE)
        response.raise_for_status()
        dados = response.json()
        
        # --- TRATAMENTO ROBUSTO DE EXTRAÇÃO DO JSON ---
        try:
            # Tenta acessar o campo 'results'. Se falhar, é um erro de API/limite.
            clima = dados['results'] 
            
            # 2. TRANSFORMAÇÃO (T) - Extração dos valores
            temp = clima['temp']
            umidade = clima['humidity']
            status_clima = clima['description']
            
        except KeyError:
            # Captura a exceção se a chave 'results' não existir (erro de API, limite excedido, etc.)
            mensagem_erro = dados.get('message', 'Estrutura JSON Inesperada ou Limite Excedido. Verifique o JSON retornado.')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 Falha na Extração. API retornou: {mensagem_erro}")
            return
        # --- FIM DO TRATAMENTO ROBUSTO ---

        timestamp_leitura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Lógica de Alerta
        status_temp = "Normal"
        if temp > 30.0:
            status_temp = "Alerta: Temperatura Elevada!"
        elif temp < 15.0:
            status_temp = "Aviso: Baixa Temperatura"

        # 3. CARGA (L)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Inserção da Temperatura
        cursor.execute('''
            INSERT INTO leituras (sensor_id, timestamp_leitura, valor, status)
            VALUES (?, ?, ?, ?)
        ''', (ID_TEMP, timestamp_leitura, temp, status_temp))
        
        # Inserção da Umidade
        cursor.execute('''
            INSERT INTO leituras (sensor_id, timestamp_leitura, valor, status)
            VALUES (?, ?, ?, ?)
        ''', (ID_UMIDADE, timestamp_leitura, umidade, f"Clima: {status_clima}"))

        conn.commit()
        conn.close()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ HG OK. Sua_cidade_aqui: Temp={temp}°C, Umidade={umidade}%.")

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão HTTP: {e}")
    except Exception as e:
        print(f"Erro geral durante a execução: {e}")

if __name__ == '__main__':
    print(f"Coletor de Dados de Clima HG Brasil para {CIDADE} rodando...")
    print(f"Intervalo de Coleta: {timedelta(seconds=INTERVALO_COLETA_SEGUNDOS)}")

    while True:
        
        # --- LÓGICA DE VERIFICAÇÃO DE TEMPO (TOLERÂNCIA A FALHAS) ---
        conn = get_db_connection()
        ultimo_timestamp = get_last_timestamp(conn)
        conn.close()
        
        deve_coletar_agora = True
        
        if ultimo_timestamp:
            delta = datetime.now() - ultimo_timestamp
            segundos_desde_ultima = delta.total_seconds()
            
            if segundos_desde_ultima < INTERVALO_COLETA_SEGUNDOS:
                tempo_restante = INTERVALO_COLETA_SEGUNDOS - segundos_desde_ultima
                print(f"⏳ Esperando. Ainda faltam {timedelta(seconds=tempo_restante)} para a próxima coleta permitida.")
                
                # Dorme pelo tempo restante + 5s de margem
                time.sleep(tempo_restante + 5) 
                
                deve_coletar_agora = False
        # --- FIM DA LÓGICA DE VERIFICAÇÃO ---

        if deve_coletar_agora:
            buscar_e_salvar_dados()
            
        # Dorme pelo intervalo total após a coleta (ou se a lógica de verificação
        # esperou o suficiente para passar o ponto de coleta)
        time.sleep(INTERVALO_COLETA_SEGUNDOS)