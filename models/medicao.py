from database import get_db_connection
from datetime import datetime
import sqlite3


class MedicaoItem:
    """Modelo para os itens individuais de uma medição."""

    def __init__(self, id=None, medicao_id=None, orcamento_item_id=None, quantidade_medida=0.0, valor_unitario=0.0, **kwargs):
        self.id = id
        self.medicao_id = medicao_id
        self.orcamento_item_id = orcamento_item_id
        self.quantidade_medida = float(quantidade_medida)
        self.valor_unitario = float(valor_unitario)
        self.valor_total = self.quantidade_medida * self.valor_unitario

    @staticmethod
    def find_by_medicao(medicao_id):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        items = conn.execute(
            "SELECT * FROM medicao_itens WHERE medicao_id = ?", (medicao_id,)).fetchall()
        conn.close()
        return [MedicaoItem(**item) for item in items]


class Medicao:
    """Classe que representa uma medição de obra."""

    def __init__(self, id=None, obra_id=None, numero_medicao=None, referencia=None, nota_fiscal=None,
                 data_medicao=None, valor=0.0, status=None, observacoes=None, arquivo_path=None,
                 criacao_usuario=None, data_criacao=None, **kwargs):
        self.id = id
        self.obra_id = obra_id
        self.numero_medicao = numero_medicao
        self.referencia = referencia
        self.nota_fiscal = nota_fiscal
        self.data_medicao = data_medicao
        self.valor = valor
        self.status = status
        self.observacoes = observacoes
        self.arquivo_path = arquivo_path
        self.criacao_usuario = criacao_usuario
        self.data_criacao = data_criacao
        # Para aceitar outros campos que venham do banco e não estão no construtor
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        """Salva uma nova medição no banco de dados."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # O campo 'etapa_obra' foi removido da tabela, então é removido daqui também.
        cursor.execute(
            """
            INSERT INTO medicoes (obra_id, valor, data_medicao, nota_fiscal, referencia, observacoes, arquivo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (self.obra_id, self.valor, self.data_medicao, self.nota_fiscal,
             self.referencia, self.observacoes, self.arquivo_path)
        )
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def get_total_medido_by_obra(obra_id):
        """Calcula o valor total já medido para uma obra a partir do cabeçalho da medição."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Usando a coluna 'valor' da tabela 'medicoes'
        cursor.execute(
            "SELECT SUM(valor) FROM medicoes WHERE obra_id = ?", (obra_id,))
        total = cursor.fetchone()[0]
        conn.close()
        return total if total is not None else 0.0

    @staticmethod
    def create(obra_id, medicao_data, itens_data):
        """Cria uma nova medição e todos os seus itens atomicamente."""
        conn = get_db_connection()
        try:
            # Insere a medição principal
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medicoes (obra_id, referencia, nota_fiscal, data_medicao, observacoes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                obra_id,
                medicao_data['referencia'],
                medicao_data.get('nota_fiscal'),
                medicao_data['data_medicao'],
                medicao_data.get('observacoes')
            ))
            medicao_id = cursor.lastrowid

            # Esta parte precisaria ser adaptada para usar MedicaoItem se fosse chamada
            # Por enquanto, a lógica de criação de itens está na rota.
            # for item in itens_data:
            #     MedicaoItem.create(medicao_id, item, conn)

            conn.commit()
            return medicao_id
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar medição: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def find_all_by_obra(obra_id):
        """Busca todas as medições de uma obra."""
        conn = get_db_connection()
        # Retorna dicionários para facilitar o uso no template
        conn.row_factory = sqlite3.Row
        medicoes = conn.execute("""
            SELECT 
                m.*,
                strftime('%d/%m/%Y', m.data_medicao) as data_formatada
            FROM medicoes m
            WHERE m.obra_id = ? 
            ORDER BY m.data_medicao DESC
        """, (obra_id,)).fetchall()
        conn.close()
        return [dict(row) for row in medicoes]

    @staticmethod
    def find_by_id_with_items(medicao_id):
        """Busca uma medição específica com todos os seus itens."""
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        try:
            medicao = conn.execute(
                "SELECT * FROM medicoes WHERE id = ?", (medicao_id,)).fetchone()
            if not medicao:
                return None, []

            itens = conn.execute(
                "SELECT * FROM medicao_itens WHERE medicao_id = ?", (medicao_id,)).fetchall()
            return dict(medicao), [dict(item) for item in itens]
        finally:
            conn.close()

    @staticmethod
    def get_grand_total_by_obra(obra_id):
        """Calcula o valor total acumulado de todas as medições de uma obra."""
        conn = get_db_connection()
        try:
            total = conn.execute("""
                SELECT SUM(im.valor_total) as grand_total
                FROM medicao_itens im
                JOIN medicoes m ON im.medicao_id = m.id
                WHERE m.obra_id = ?
            """, (obra_id,)).fetchone()['grand_total']
            return total if total is not None else 0
        finally:
            conn.close()
