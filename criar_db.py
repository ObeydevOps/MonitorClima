import sqlite3

def criar_tabelas():
    DB_NAME = 'monitoramento.db'
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criação da Tabela Sensores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensores (
            sensor_id INTEGER PRIMARY KEY,
            nome_sensor TEXT NOT NULL,
            unidade TEXT NOT NULL,
            localizacao TEXT,
            linguagem_implementacao TEXT NOT NULL
        )
    ''')
    
    # Criação da Tabela Leituras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            leitura_id INTEGER PRIMARY KEY,
            sensor_id INTEGER NOT NULL,
            timestamp_leitura TIMESTAMP NOT NULL,
            valor REAL NOT NULL,
            status TEXT,
            FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
        )
    ''')

    # --- Inserção dos Sensores ---
    LOCAL = 'Sua_cidade_aqui'

    # 1. Sensor de Temperatura (ID 1)
    cursor.execute("INSERT OR IGNORE INTO sensores (sensor_id, nome_sensor, unidade, localizacao, linguagem_implementacao) VALUES (1, 'Temperatura - HG Brasil', 'ºC', ?, 'Python/API')", (LOCAL,))
    
    # 2. Sensor de Umidade (ID 2)
    cursor.execute("INSERT OR IGNORE INTO sensores (sensor_id, nome_sensor, unidade, localizacao, linguagem_implementacao) VALUES (2, 'Umidade - HG Brasil', '%', ?, 'Python/API')", (LOCAL,))

    conn.commit()
    conn.close()
    print("✅ Banco de dados, tabelas e sensores base criados com sucesso!")

if __name__ == '__main__':
    criar_tabelas()