from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from database import get_db_connection
import sqlite3

# Criação do Blueprint para o módulo de orçamento
orcamento_bp = Blueprint('orcamento_bp', __name__,
                         template_folder='templates',
                         static_folder='static',
                         static_url_path='/modules/orcamento/static')


@orcamento_bp.route('/orcamento/obra/<int:obra_id>', methods=['GET', 'POST'])
def detalhar_orcamento(obra_id):
    """
    Exibe os detalhes de um orçamento e permite adicionar novos itens.
    """
    conn = get_db_connection()

    # Lógica para adicionar um novo item ao orçamento
    if request.method == 'POST':
        orcamento_id = request.form.get('orcamento_id', type=int)
        descricao = request.form.get('descricao')
        unidade = request.form.get('unidade')
        quantidade = request.form.get('quantidade', type=float)
        valor_unitario = request.form.get('valor_unitario', type=float)

        if not all([orcamento_id, descricao, unidade, quantidade, valor_unitario]):
            flash('Todos os campos para adicionar um item são obrigatórios.', 'danger')
        else:
            try:
                conn.execute(
                    """
                    INSERT INTO orcamento_itens (orcamento_id, descricao, unidade, quantidade, valor_unitario)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (orcamento_id, descricao, unidade, quantidade, valor_unitario)
                )
                conn.commit()
                flash('Item adicionado ao orçamento com sucesso!', 'success')
            except sqlite3.Error as e:
                flash(f'Erro ao adicionar item: {e}', 'danger')

        conn.close()
        return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))

    # --- BUSCA DADOS REAIS PARA GET ---

    # 1. Busca os dados principais do orçamento
    query_orcamento = """
        SELECT
            o.id as obra_id, o.nome as obra_nome, o.cnpj as obra_cnpj, o.cno as cno,
            strftime('%d/%m/%Y', o.data_inicio) || ' - ' || strftime('%d/%m/%Y', o.data_prevista_fim) as periodo_obra,
            orc.id, orc.codigo, orc.tipo, orc.criacao_usuario,
            strftime('%d/%m/%Y %H:%M:%S', orc.data_criacao) as criacao_data,
            c.nome as cliente_nome
        FROM orcamentos orc
        JOIN obras o ON orc.obra_id = o.id
        JOIN construtoras c ON o.construtora_id = c.id
        WHERE orc.obra_id = ?
    """
    orcamento_data = conn.execute(query_orcamento, (obra_id,)).fetchone()

    if not orcamento_data:
        conn.close()
        abort(404, "Orçamento não encontrado para a obra especificada.")

    # 2. Busca os itens do orçamento
    orcamento_id = orcamento_data['id']
    query_itens = "SELECT * FROM orcamento_itens WHERE orcamento_id = ? ORDER BY id"
    itens_orcamento = conn.execute(query_itens, (orcamento_id,)).fetchall()

    # 3. Busca as medições existentes, já calculando o valor total de cada uma
    query_medicoes = """
        SELECT
            m.id,
            m.numero_medicao,
            m.referencia,
            strftime('%d/%m/%Y', m.data_medicao) as data_formatada,
            m.status,
            COALESCE(SUM(mi.quantidade_medida * oi.valor_unitario), 0.0) as valor_medido
        FROM medicoes m
        LEFT JOIN medicao_itens mi ON m.id = mi.medicao_id
        LEFT JOIN orcamento_itens oi ON mi.orcamento_item_id = oi.id
        WHERE m.obra_id = ?
        GROUP BY m.id, m.numero_medicao, m.referencia, m.data_medicao, m.status
        ORDER BY m.numero_medicao DESC;
    """
    medicoes = conn.execute(query_medicoes, (obra_id,)).fetchall()

    # 4. Calcula o valor total do contrato a partir dos itens
    total_orcamento = sum(item['valor_total'] for item in itens_orcamento)

    # 5. Calcula o valor total medido acumulado e o saldo
    total_medido_geral = sum(m['valor_medido'] for m in medicoes)
    saldo_a_medir_valor = total_orcamento - total_medido_geral

    # 6. Calcula o percentual medido, tratando o caso de divisão por zero
    if total_orcamento > 0:
        percentual_medido = (total_medido_geral / total_orcamento) * 100
    else:
        percentual_medido = 0

    conn.close()

    return render_template('orcamento/detalhe_orcamento.html',
                           orcamento=orcamento_data,
                           itens=itens_orcamento,
                           medicoes=medicoes,
                           total_orcamento=total_orcamento,
                           total_medido_geral=total_medido_geral,
                           saldo_a_medir_valor=saldo_a_medir_valor,
                           percentual_medido=percentual_medido)
