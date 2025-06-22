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
