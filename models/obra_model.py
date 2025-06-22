import sqlite3
from database import get_db_connection


class Obra:
    def __init__(self, id=None, nome=None, construtora_id=None, cidade=None, status=None, responsavel=None, caminho_pasta=None, etapa_atual=None, anotacoes=None, data_criacao=None, data_atualizacao=None, cnpj=None, endereco=None, numero=None, bairro=None, cep=None, uf=None):
        self.id = id
        self.nome = nome
        self.construtora_id = construtora_id
        self.cidade = cidade
        self.status = status
        self.responsavel = responsavel
        self.caminho_pasta = caminho_pasta
        self.etapa_atual = etapa_atual
        self.anotacoes = anotacoes
        self.data_criacao = data_criacao
        self.data_atualizacao = data_atualizacao
        self.cnpj = cnpj
        self.endereco = endereco
        self.numero = numero
        self.bairro = bairro
        self.cep = cep
        self.uf = uf

    def save(self):
        """Salva uma nova obra no banco de dados."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO obras (nome, construtora_id, cidade, status, responsavel, caminho_pasta, etapa_atual, anotacoes, cnpj, endereco, numero, bairro, cep, uf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.nome, self.construtora_id, self.cidade, self.status, self.responsavel, self.caminho_pasta, self.etapa_atual, self.anotacoes, self.cnpj, self.endereco, self.numero, self.bairro, self.cep, self.uf))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def find_by_id(obra_id):
        """Busca uma obra pelo ID."""
        conn = get_db_connection()
        obra = conn.execute(
            'SELECT * FROM obras WHERE id = ?', (obra_id,)).fetchone()
        conn.close()
        if obra:
            return Obra(**obra)
        return None
