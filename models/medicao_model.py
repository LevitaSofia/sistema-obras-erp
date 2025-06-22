# models/medicao_model.py
from database import get_db_connection
from datetime import datetime

DATABASE = 'database.db'


class Medicao:
    """Classe que representa uma medição financeira de uma obra."""

    def __init__(self, obra_id, valor, data, nota_fiscal=None, id=None):
        self.id = id
        self.obra_id = obra_id
        self.valor = valor
        self.data = data
        self.nota_fiscal = nota_fiscal


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
            'INSERT INTO medicoes (obra_id, valor, data, nota_fiscal) VALUES (?, ?, ?, ?)',
            (medicao.obra_id, medicao.valor, medicao.data, medicao.nota_fiscal)
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
            'SELECT * FROM medicoes WHERE obra_id = ? ORDER BY data DESC', (
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
            WHERE strftime('%Y-%m', m.data) = ?
            GROUP BY o.id
            ORDER BY c.nome, o.nome
        """
        cursor = conn.execute(query, (data_filtro,))
        return cursor.fetchall()
    finally:
        conn.close()
