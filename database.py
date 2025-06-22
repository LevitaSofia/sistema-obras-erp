# database.py
import sqlite3

DATABASE_PATH = 'database.db'


def get_db_connection():
    """
    Cria e retorna uma nova conexão com o banco de dados.
    Habilita o acesso por nome de coluna (row_factory) e chaves estrangeiras.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Adicionar coluna 'valor_contrato' à tabela 'obras' se não existir
    try:
        cursor.execute("PRAGMA table_info(obras)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'valor_contrato' not in columns:
            cursor.execute(
                'ALTER TABLE obras ADD COLUMN valor_contrato REAL DEFAULT 0.0')
            print("INFO: Coluna 'valor_contrato' adicionada à tabela 'obras'.")
    except Exception as e:
        print(
            f"WARNING: Não foi possível adicionar a coluna 'valor_contrato': {e}")

    # Criar tabela de medicoes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            data_medicao DATE NOT NULL,
            valor REAL NOT NULL,
            nota_fiscal TEXT,
            observacoes TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
