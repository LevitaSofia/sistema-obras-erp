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

    def __iter__(self):
        """Permite a conversão do objeto em um dicionário."""
        yield 'id', self.id
        yield 'nome', self.nome
        yield 'construtora_id', self.construtora_id
        yield 'cidade', self.cidade
        yield 'status', self.status
        yield 'responsavel', self.responsavel
        yield 'caminho_pasta', self.caminho_pasta
        yield 'etapa_atual', self.etapa_atual
        yield 'anotacoes', self.anotacoes
        yield 'data_criacao', self.data_criacao
        yield 'data_atualizacao', self.data_atualizacao
        yield 'cnpj', self.cnpj
        yield 'endereco', self.endereco
        yield 'numero', self.numero
        yield 'bairro', self.bairro
        yield 'cep', self.cep
        yield 'estado', self.estado
        yield 'construtora_razao_social', self.construtora_razao_social
        yield 'nome_fantasia', self.nome_fantasia
        yield 'razao_social', self.razao_social
        yield 'valor_contrato', self.valor_contrato
        yield 'construtora_nome', self.construtora_nome

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

    @staticmethod
    def update(data):
        """Atualiza uma obra existente no banco de dados."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE obras SET
                    nome = ?,
                    construtora_id = ?,
                    responsavel = ?,
                    status = ?,
                    etapa_atual = ?,
                    anotacoes = ?,
                    caminho_pasta = ?,
                    cnpj = ?,
                    endereco = ?,
                    numero = ?,
                    bairro = ?,
                    cidade = ?,
                    uf = ?,
                    cep = ?
                WHERE id = ?
            """, (
                data['nome'],
                data['construtora_id'],
                data['responsavel'],
                data['status'],
                data['etapa_atual'],
                data['anotacoes'],
                data['caminho_pasta'],
                data.get('cnpj'),
                data.get('endereco'),
                data.get('numero'),
                data.get('bairro'),
                data.get('cidade'),
                data.get('uf'),
                data.get('cep'),
                data['id']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar obra: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def find_by_filters(filters):
        """
        Busca obras no banco de dados com base em um dicionário de filtros.
        """
        conn = get_db_connection()
        
        base_query = """
            SELECT o.*, c.nome as construtora_nome
            FROM obras o
            LEFT JOIN construtoras c ON o.construtora_id = c.id
        """
        
        where_clauses = []
        params = []

        if filters.get('construtora_id'):
            where_clauses.append("o.construtora_id = ?")
            params.append(filters['construtora_id'])
            
        if filters.get('busca'):
            term = f"%{filters['busca']}%"
            where_clauses.append("(o.nome LIKE ? OR o.cidade LIKE ? OR o.responsavel LIKE ?)")
            params.extend([term, term, term])
            
        if filters.get('etapa'):
            where_clauses.append("o.etapa_atual = ?")
            params.append(filters['etapa'])

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
            
        base_query += " ORDER BY construtora_nome, o.nome"
        
        obras_rows = conn.execute(base_query, params).fetchall()
        conn.close()
        
        return [Obra(**row) for row in obras_rows]

    @staticmethod
    def find_all():
        """Busca todas as obras no banco de dados com o nome da construtora."""
        conn = get_db_connection()
        query = """
            SELECT o.*, COALESCE(c.nome, 'Construtora Não Associada') as construtora_nome
            FROM obras o
            LEFT JOIN construtoras c ON o.construtora_id = c.id
            ORDER BY construtora_nome, o.nome
        """
        obras_rows = conn.execute(query).fetchall()
        conn.close()
        return [Obra(**row) for row in obras_rows]
