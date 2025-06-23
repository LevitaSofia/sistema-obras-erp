def calcular_totais(itens):
    """
    Calcula os totais para uma lista de itens medidos.
    Retorna um dicionário com os totais.
    """
    if not itens:
        return {
            'valor_orcado_total': 0,
            'valor_medido_total': 0,
            'saldo_total': 0,
            'porcentagem_media': 0
        }

    valor_orcado_total = sum(item['valor_orcado'] for item in itens)
    valor_medido_total = sum(item['valor_medido'] for item in itens)
    saldo_total = valor_orcado_total - valor_medido_total

    porcentagem_media = (valor_medido_total / valor_orcado_total) * \
        100 if valor_orcado_total > 0 else 0

    return {
        'valor_orcado_total': valor_orcado_total,
        'valor_medido_total': valor_medido_total,
        'saldo_total': saldo_total,
        'porcentagem_media': porcentagem_media
    }


def gerar_relatorio_pdf(medicao_id):
    """
    Esqueleto da função para gerar um relatório em PDF de uma medição.
    No futuro, esta função usará uma biblioteca como FPDF ou ReportLab.
    """
    print(f"Futuramente, um PDF para a medição {medicao_id} será gerado aqui.")
    # Exemplo de lógica futura:
    # 1. Buscar dados da medição e itens do banco.
    # 2. Criar um objeto PDF.
    # 3. Adicionar cabeçalho, detalhes da obra, tabela de itens e totais.
    # 4. Salvar ou retornar o arquivo PDF.
    return None
