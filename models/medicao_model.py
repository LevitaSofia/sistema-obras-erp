# models/medicao_model.py
from database import get_db_connection
from datetime import datetime

DATABASE = 'database.db'


class Medicao:
    """
    Representa uma medição de uma obra.
    """

    def __init__(self, obra_id, data_medicao, valor, nota_fiscal=None, observacoes=None, id=None, data_criacao=None):
        self.id = id
        self.obra_id = obra_id
        self.data_medicao = data_medicao
        self.valor = valor
        self.nota_fiscal = nota_fiscal
        self.observacoes = observacoes
        self.data_criacao = data_criacao

    @staticmethod
    def get_by_obra(obra_id):
        """
        Retorna todas as medições de uma obra específica, ordenadas pela data.

        Args:
            obra_id (int): O ID da obra.

        Returns:
            list[Medicao]: Uma lista de objetos Medicao.
        """
        conn = get_db_connection()
        medicoes_rows = conn.execute(
            'SELECT * FROM medicoes WHERE obra_id = ? ORDER BY data_medicao DESC', (
                obra_id,)
        ).fetchall()
        conn.close()

        return [Medicao(**row) for row in medicoes_rows]

    @staticmethod
    def create(obra_id, data_medicao_str, valor, nota_fiscal, observacoes):
        """
        Cria um novo registro de medição no banco de dados.

        Args:
            obra_id (int): O ID da obra.
            data_medicao_str (str): A data da medição no formato 'YYYY-MM-DD'.
            valor (float): O valor da medição.
            nota_fiscal (str): O número da nota fiscal.
            observacoes (str): Observações sobre a medição.

        Returns:
            Medicao: O objeto Medicao recém-criado.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO medicoes (obra_id, data_medicao, valor, nota_fiscal, observacoes)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (obra_id, data_medicao_str, valor, nota_fiscal, observacoes)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return Medicao(
            id=new_id,
            obra_id=obra_id,
            data_medicao=datetime.strptime(
                data_medicao_str, "%Y-%m-%d").date(),
            valor=valor,
            nota_fiscal=nota_fiscal,
            observacoes=observacoes
        )

    @staticmethod
    def calcular_total_medido(obra_id):
        """
        Calcula a soma de todas as medições de uma obra.

        Args:
            obra_id (int): O ID da obra.

        Returns:
            float: O valor total medido.
        """
        conn = get_db_connection()
        total_row = conn.execute(
            'SELECT SUM(valor) FROM medicoes WHERE obra_id = ?', (obra_id,)
        ).fetchone()
        conn.close()

        return total_row[0] if total_row and total_row[0] is not None else 0.0


def registrar_medicao(medicao):
    """Insere uma nova medição no banco de dados.

    Args:
        medicao (Medicao): Um objeto da classe Medicao.

    Returns:
        int: O ID da medição inserida.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO medicoes (obra_id, valor, data_medicao, nota_fiscal, observacoes) VALUES (?, ?, ?, ?, ?)',
            (medicao.obra_id, medicao.valor, medicao.data_medicao,
             medicao.nota_fiscal, medicao.observacoes)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def listar_medicoes_por_obra(obra_id):
    """Retorna todas as medições de uma obra, ordenadas por data.

    Args:
        obra_id (int): O ID da obra.

    Returns:
        list: Uma lista de objetos Medicao.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'SELECT * FROM medicoes WHERE obra_id = ? ORDER BY data_medicao DESC', (
                obra_id,)
        )
        medicoes_rows = cursor.fetchall()
        medicoes = [Medicao(**row) for row in medicoes_rows]
        return medicoes
    finally:
        conn.close()


def resumo_mensal_geral(ano, mes):
    """Retorna o faturamento total por obra para um determinado mês e ano.

    Args:
        ano (int): O ano do resumo.
        mes (int): O mês do resumo.

    Returns:
        list: Uma lista de dicionários, cada um contendo nome da obra, 
              nome da construtora e o total faturado no mês.
    """
    data_filtro = f"{ano}-{str(mes).zfill(2)}"
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                o.nome as obra_nome, 
                c.nome as construtora_nome, 
                SUM(m.valor) as total_mes
            FROM medicoes m
            JOIN obras o ON m.obra_id = o.id
            JOIN construtoras c ON o.construtora_id = c.id
            WHERE strftime('%Y-%m', m.data_medicao) = ?
            GROUP BY o.id
            ORDER BY c.nome, o.nome
        """
        cursor = conn.execute(query, (data_filtro,))
        return cursor.fetchall()
    finally:
        conn.close()
