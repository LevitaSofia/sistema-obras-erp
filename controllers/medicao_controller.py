from models import medicao_model
from datetime import datetime


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
