import sqlite3
from database import get_db_connection


class Obra:
    """
    Classe que representa uma obra, encapsulando os dados e interações
    com o banco de dados.
    """

    @staticmethod
    def get_etapas_era():
        """Retorna a estrutura padrão das etapas ERA."""
        return {
            'Orçamento': ['Solicitação recebida', 'Proposta enviada', 'Aguardando aprovação'],
            'Projeto': ['Projeto SLQA', 'Projeto Piso a Piso', 'Projeto Bandeja', 'Projeto Fachadeira / Guarda-corpo', 'ART emitida'],
            'Execução': ['SLQA executado', 'Piso a Piso executado', 'Fachadeira executada', 'Bandeja executada', 'Linha de vida executada'],
            'Faturamento': ['Primeira medição feita', 'NFS emitida', 'Pagamento confirmado'],
            'Encerramento': ['Obra finalizada', 'Relatórios entregues', 'Feedback registrado']
        }

    def __init__(self, id=None, nome=None, construtora_id=None, cidade=None, status=None, responsavel=None, caminho_pasta=None, etapa_atual=None, anotacoes=None, data_criacao=None, data_atualizacao=None, cnpj=None, endereco=None, numero=None, bairro=None, cep=None, estado=None, nome_fantasia=None, razao_social=None, valor_contrato=0.0, construtora_nome=None, construtora_razao_social=None, **kwargs):
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
        self.estado = estado
        self.construtora_razao_social = construtora_razao_social
        self.nome_fantasia = nome_fantasia
        self.razao_social = razao_social
        self.valor_contrato = valor_contrato
        self.construtora_nome = construtora_nome

    def save(self):
        """Salva uma nova obra no banco de dados."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO obras (nome, construtora_id, cidade, status, responsavel, caminho_pasta, etapa_atual, anotacoes, cnpj, endereco, numero, bairro, cep, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.nome, self.construtora_id, self.cidade, self.status, self.responsavel, self.caminho_pasta, self.etapa_atual, self.anotacoes, self.cnpj, self.endereco, self.numero, self.bairro, self.cep, self.estado))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def find_by_id(obra_id):
        """Busca uma obra pelo ID, incluindo o nome da construtora."""
        conn = get_db_connection()
        query = """
            SELECT o.*, c.nome as construtora_nome
            FROM obras o
            JOIN construtoras c ON o.construtora_id = c.id
            WHERE o.id = ?
        """
        obra_row = conn.execute(query, (obra_id,)).fetchone()
        conn.close()
        if obra_row:
            return Obra(**obra_row)
        return None
