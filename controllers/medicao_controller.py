"""
Módulo Controller de Medições
-----------------------------

Este módulo utiliza um Blueprint do Flask para agrupar as rotas relacionadas
ao gerenciamento de medições de uma obra. Ele lida com a lógica de negócio
para exibir a página de medições e processar o formulário de adição de novas
medições.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.obra_model import Obra
from models.medicao_model import Medicao
from models import medicao_model
from datetime import datetime

# Criação do Blueprint para as rotas de medição
medicoes_bp = Blueprint(
    'medicoes',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@medicoes_bp.route('/obra/<int:obra_id>/medicoes', methods=['GET', 'POST'])
def listar_e_adicionar(obra_id):
    """
    Exibe a lista de medições de uma obra e permite adicionar novas.
    """
    obra = Obra.find_by_id(obra_id)
    if not obra:
        flash('Obra não encontrada.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Processar formulário de nova medição
        data_medicao = request.form.get('data_medicao')
        valor_str = request.form.get('valor', '0').replace(
            '.', '').replace(',', '.')
        nota_fiscal = request.form.get('nota_fiscal')
        observacoes = request.form.get('observacoes')

        try:
            valor = float(valor_str)
            if valor <= 0:
                flash('O valor da medição deve ser um número positivo.', 'warning')
            elif not data_medicao:
                flash('A data da medição é obrigatória.', 'warning')
            else:
                Medicao.create(
                    obra_id=obra_id,
                    data_medicao_str=data_medicao,
                    valor=valor,
                    nota_fiscal=nota_fiscal,
                    observacoes=observacoes
                )
                flash('Medição adicionada com sucesso!', 'success')
        except ValueError:
            flash('Valor da medição inválido. Use o formato 1.234,56.', 'danger')

        return redirect(url_for('medicoes.listar_e_adicionar', obra_id=obra_id))

    # Lógica para GET
    medicoes = Medicao.get_by_obra(obra_id)
    total_medido = Medicao.calcular_total_medido(obra_id)

    valor_contrato = obra.valor_contrato if obra.valor_contrato else 0.0
    saldo_restante = valor_contrato - total_medido

    return render_template(
        'medicoes/medicoes.html',
        obra=obra,
        medicoes=medicoes,
        total_medido=total_medido,
        valor_contrato=valor_contrato,
        saldo_restante=saldo_restante
    )


@medicoes_bp.route('/medicoes/resumo', methods=['GET'])
def resumo_mensal():
    """
    Exibe o resumo mensal de faturamento de todas as obras.
    """
    hoje = datetime.now()
    ano = request.args.get('ano', default=hoje.year, type=int)
    mes = request.args.get('mes', default=hoje.month, type=int)

    dados_resumo = obter_resumo_mensal(ano, mes)

    # Gera uma lista de anos para o dropdown
    anos_disponiveis = range(2020, hoje.year + 2)

    return render_template(
        'medicoes/resumo_mensal.html',
        resumo=dados_resumo['resumo'],
        total_geral=dados_resumo['total_geral'],
        ano_selecionado=dados_resumo['ano_selecionado'],
        mes_selecionado=dados_resumo['mes_selecionado'],
        anos_disponiveis=anos_disponiveis
    )


def processar_nova_medicao(obra_id, valor_str, data_str, nota_fiscal):
    """Valida os dados e registra uma nova medição.

    Returns:
        tuple: (sucesso, mensagem_ou_id)
    """
    if not all([valor_str, data_str]):
        return False, "Valor e data são obrigatórios."

    try:
        valor = float(valor_str)
        # Validar data
        datetime.strptime(data_str, '%Y-%m-%d')
    except ValueError:
        return False, "Formato de valor ou data inválido. Use AAAA-MM-DD para a data."

    medicao = medicao_model.Medicao(
        obra_id=obra_id,
        valor=valor,
        data=data_str,
        nota_fiscal=nota_fiscal
    )

    medicao_id = medicao_model.registrar_medicao(medicao)
    return True, medicao_id


def obter_medicoes_obra(obra_id):
    """Obtém a lista de medições para uma obra específica."""
    return medicao_model.listar_medicoes_por_obra(obra_id)


def obter_resumo_mensal(ano, mes):
    """Obtém os dados para o resumo mensal de faturamento."""
    if ano is None or mes is None:
        hoje = datetime.now()
        ano, mes = hoje.year, hoje.month

    resumo = medicao_model.resumo_mensal_geral(int(ano), int(mes))
    total_geral = sum(item['total_mes'] for item in resumo)

    return {
        'resumo': resumo,
        'total_geral': total_geral,
        'ano_selecionado': int(ano),
        'mes_selecionado': int(mes)
    }
