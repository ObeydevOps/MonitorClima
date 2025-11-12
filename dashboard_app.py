import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

DB_NAME = 'monitoramento.db'

@st.cache_data(ttl=60)
def get_data_from_db():
    conn = sqlite3.connect(DB_NAME)
    # Consulta SQL filtrando apenas os dados dos últimos 6 dias
    query = """
    SELECT 
        l.timestamp_leitura, 
        s.nome_sensor, 
        l.valor, 
        s.unidade,
        l.status
    FROM leituras l
    JOIN sensores s ON l.sensor_id = s.sensor_id
    WHERE 
        -- FILTRO OBRIGATÓRIO: Garante que NENHUM dado anterior a 2025 seja incluído
        l.timestamp_leitura >= '2025-01-01 00:00:00' 
        -- FILTRO TEMPORAL: Limita a exibição aos últimos 6 dias no banco de dados
        AND l.timestamp_leitura >= DATETIME('now', '-6 days')
    ORDER BY l.timestamp_leitura DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return pd.DataFrame()
        
    df['timestamp_leitura'] = pd.to_datetime(df['timestamp_leitura'])
    
    # Se houver strings, elas são convertidas para NaN (que é ignorado na plotagem).
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

    return df

# --- ESTRUTURA DO DASHBOARD ---
st.set_page_config(layout="wide")
st.title("☁️ Monitoramento de Clima: Sua_cidade_aqui")
st.caption("Histórico de 6 dias, dados via HG Brasil API.")
st.markdown("---") # Adiciona uma linha divisória visual
st.subheader("Projeto Desenvolvido por Igor H Marques!") 
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# O DF agora tem 'timestamp_leitura' como DATETIME 
df = get_data_from_db() 

if df.empty:
    st.warning("Nenhum dado encontrado. O coletor (coletor_api.py) precisa rodar por pelo menos um intervalo para coletar dados.")
    st.stop()

# Visão Geral e KPIs 
st.header("Indicadores Chave (KPIs)")
df_ultimas = df.sort_values(by='timestamp_leitura', ascending=False).drop_duplicates(subset=['nome_sensor'])

col1, col2 = st.columns(2)

# Garante que a linha existe antes de acessar iloc[0]
if not df_ultimas[df_ultimas['nome_sensor'].str.contains('Temperatura', case=False)].empty:
    temp_value = df_ultimas[df_ultimas['nome_sensor'].str.contains('Temperatura', case=False)].iloc[0]
    # Usamos o método isna() para garantir que o valor não seja NaN antes de formatar
    temp_display = f"{temp_value['valor']:.1f} {temp_value['unidade']}" if not pd.isna(temp_value['valor']) else f"N/A {temp_value['unidade']}"
    col1.metric("Temperatura Atual", temp_display, temp_value['status'])

if not df_ultimas[df_ultimas['nome_sensor'].str.contains('Umidade', case=False)].empty:
    umidade_value = df_ultimas[df_ultimas['nome_sensor'].str.contains('Umidade', case=False)].iloc[0]
    umidade_display = f"{umidade_value['valor']:.0f} {umidade_value['unidade']}" if not pd.isna(umidade_value['valor']) else f"N/A {umidade_value['unidade']}"
    col2.metric("Umidade Atual", umidade_display, umidade_value['status'])


# Gráfico de Tendência de Temperatura
st.header("📉 Tendência de Temperatura e Umidade")

# --- NOVO BLOCO TRY/EXCEPT PARA DIAGNÓSTICO ---
try:
    # 1. Filtra dados de Temperatura (Eixo Y Primário)
    df_temp = df[df['nome_sensor'].str.contains('Temperatura', case=False)].sort_values('timestamp_leitura', ascending=True)

    # 2. Filtra dados de Umidade (Eixo Y Secundário)
    df_umidade = df[df['nome_sensor'].str.contains('Umidade', case=False)].sort_values('timestamp_leitura', ascending=True)
    
    # Adicionando uma verificação adicional de segurança
    if df_temp.empty or df_umidade.empty:
        st.warning("Dados insuficientes para gerar o gráfico de tendência. Certifique-se de que o coletor rodou por pelo menos dois intervalos para cada sensor.")
        # Se estiver vazio, pulamos o resto da seção do gráfico e vamos para a tabela
        raise ValueError("Dados de temperatura ou umidade vazios para o gráfico.")


    # Define o tamanho do gráfico
    fig, ax = plt.subplots(figsize=(10, 4))

    # --- AJUSTES DO EIXO X PARA HORÁRIOS DE LEITURA (2h24min) ---

    #Permite que o Matplotlib defina os rótulos principais (dias)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1)) # Rótulo para cada dia
    
    #Mantenha os minor_locator para a grade em intervalos de 2h24m, mas sem texto
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 2))) 

    #Define o formato para exibir Data e Hora
    date_format = mdates.DateFormatter('%d/%m %H:%M') 
    ax.xaxis.set_major_formatter(date_format)

    # --- FIM DOS AJUSTES DO EIXO X ---

    # Plota a Temperatura (Eixo Y Primário)
    ax.set_title('Histórico de Temperatura e Umidade de 6 Dias')
    ax.set_xlabel("Data e Hora da Leitura")
    #Marcador 'o'
    ax.plot(df_temp['timestamp_leitura'], df_temp['valor'], label='Temperatura (°C)', color='blue', marker='o', markersize=4)
    ax.set_ylabel("Temperatura (°C)", color='blue')
    ax.tick_params(axis='y', labelcolor='blue')
    ax.grid(True, linestyle='--', alpha=0.6)

    # Plota os pontos de alerta da Temperatura
    alertas = df_temp[df_temp['status'].str.contains('Alerta', na=False)]
    if not alertas.empty:
        ax.plot(alertas['timestamp_leitura'], alertas['valor'], 'ro', markersize=8, label='Alerta de Temperatura')

    # EIXO Y SECUNDÁRIO (UMIDADE) - Linha contínua
    ax2 = ax.twinx() 
    #Marcador 'o' 
    ax2.plot(df_umidade['timestamp_leitura'], df_umidade['valor'], label='Umidade (%)', color='green', marker='o', markersize=4) 
    ax2.set_ylabel("Umidade (%)", color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.set_ylim(0, 100)

    # Combina as legendas
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc='upper left')

    # Rotação e Tamanho da Fonte
    plt.xticks(rotation=45)
    ax.tick_params(axis='x', labelsize=8) 

    st.pyplot(fig)
    
except ValueError as ve: # Capture ValueError especificamente para a nossa verificação de dados vazios
    st.error(f"Erro nos dados para o gráfico: {ve}")
    st.info("O gráfico não pode ser gerado porque faltam dados de temperatura ou umidade. Verifique se o coletor de dados está funcionando.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao gerar o gráfico: {e}")
    st.info("Por favor, verifique a integridade dos seus dados no banco de dados e as configurações do script.")
# --- FIM DO BLOCO TRY/EXCEPT ---


# Tabela de Dados Brutos
st.header("Tabela de Dados Brutos")

#Cria uma cópia do DF e aplica a formatação de string SÓ na cópia para a tabela.
df_display = df.copy()
df_display['timestamp_leitura'] = df_display['timestamp_leitura'].dt.strftime('%d/%m/%Y %H:%M:%S')

st.dataframe(df_display) # Exibe o DF formatado

