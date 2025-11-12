# MonitorClima
Dashboard de Monitoramento Climático!

Visão Geral do Projeto

Este projeto consiste em um sistema de monitoramento climático que coleta dados de Temperatura e Umidade de uma cidade específica através de uma API externa (HG Brasil), armazena esses dados localmente em um banco de dados SQLite e os visualiza em tempo real usando um Dashboard interativo construído com Streamlit.

O objetivo principal é oferecer uma visualização histórica e em tempo real das tendências climáticas, permitindo identificar padrões e alertas.

Desenvolvido por: Igor H. Marques

🛠️ Arquitetura e Componentes

O projeto é dividido em três componentes principais:

Componente

Linguagem/Tecnologia

Descrição

coletor_api.py

Python

Script responsável por fazer requisições HTTP à API, extrair os dados de temperatura e umidade, e persistir as leituras no banco de dados. O coletor é configurado para rodar em intervalos longos (2h24min) para economizar recursos e respeitar limites de API.

monitoramento.db

SQLite3

Banco de dados leve e local que armazena todas as leituras históricas dos sensores (temperatura e umidade) e metadados.

dashboard_app.py

Python (Streamlit, Pandas, Matplotlib)

Aplicação web interativa que se conecta ao banco de dados, processa os dados brutos e os apresenta em forma de KPIs (Indicadores Chave de Performance), gráfico de tendência e tabela de dados brutos.

⚙️ Configuração e Instalação

Para configurar e executar o projeto, siga os passos abaixo.

1. Pré-requisitos (Conda)

É altamente recomendado o uso do gerenciador de ambientes Anaconda ou Miniconda para evitar conflitos de dependências (especialmente o famoso conflito com o NumPy).

2. Criação do Ambiente Isolado

Crie e ative um ambiente Conda isolado para garantir a compatibilidade das versões:

# Crie o ambiente (usando Python 3.10 para maior compatibilidade)
conda create -n monitor-env python=3.10

# Ative o ambiente
conda activate monitor-env


3. Instalação das Dependências

Com o ambiente ativado, instale todas as bibliotecas necessárias:

conda install streamlit pandas matplotlib sqlite


(Se preferir usar pip: pip install streamlit pandas matplotlib)

4. Estrutura de Pastas

Certifique-se de que seus arquivos estejam na mesma pasta:

MonitorTemp/
├── coletor_api.py
├── dashboard_app.py
├── monitoramento.db (será criado na primeira execução do coletor)
└── README.md (este arquivo)


▶️ Como Executar

O sistema deve ser executado em dois terminais separados e simultâneos.

Terminal 1: Coletor de Dados

Este terminal fica responsável pela ingestão de dados. Ele deve ser mantido rodando em segundo plano.

Ative o Ambiente:

conda activate monitor-env


Inicie o Coletor:

python coletor_api.py


O coletor irá inicializar o banco de dados e começar a registrar as leituras de clima no intervalo programado.

Terminal 2: Dashboard (Visualização)

Este terminal hospeda a aplicação web Streamlit.

Ative o Ambiente:

conda activate monitor-env


Inicie o Dashboard:

streamlit run dashboard_app.py


Após a execução, o Streamlit fornecerá um link (Local URL: http://localhost:8501) para acessar o dashboard no seu navegador. O gráfico será populado e atualizado automaticamente à medida que o coletor de dados registrar novas leituras.

📈 Funcionalidades do Dashboard

KPIs em Tempo Real: Exibe a Temperatura e Umidade mais recentes, incluindo o status (se houver alerta).

Gráfico de Tendência: Utiliza Matplotlib para plotar a evolução da Temperatura e Umidade nos últimos 6 dias.

Eixo X Otimizado: O eixo de tempo é formatado para evitar sobreposição de rótulos, mesmo com muitos pontos de dados.

Tabela de Dados Brutos: Apresenta a lista completa de leituras do banco de dados para verificação.

Atualização Automática: Os dados do dashboard são recarregados a cada 60 segundos.

🚨 Troubleshooting Comum

Problema

Solução

AttributeError: _ARRAY_API not found

O problema é a versão do NumPy. Execute conda activate monitor-env antes de rodar qualquer script.

"Nenhum dado encontrado" no Dashboard

O script coletor_api.py não está rodando. Inicie-o em um terminal separado.

Gráfico aparece VAZIO (só pontos)

Deixe o coletor_api.py rodar por mais tempo. O gráfico precisa de pelo menos dois pontos por sensor para desenhar a linha de tendência.

Gráfico Ilegível / Rótulos Sobrepostos

Certifique-se de que a última versão do dashboard_app.py foi salva e está sendo executada (ela contém os ajustes de escala e rótulos do eixo X).