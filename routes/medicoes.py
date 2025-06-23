import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from models.medicao import Medicao
from models.obra_model import Obra
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from database import get_db_connection
import sqlite3
from models.medicao import MedicaoItem
from models.cadastro_avancado import CadastroAvancado

medicoes_bp = Blueprint('medicoes', __name__, template_folder='templates')

BASE_UPLOAD_FOLDER = "G:/Meu Drive/000 ALTA TELAS/"


@medicoes_bp.route('/medicoes/obra/<int:obra_id>', methods=['GET', 'POST'])
def listar_e_adicionar(obra_id):
    """
    Exibe a lista de medições de uma obra e permite adicionar novas.
    """
    obra = Obra.find_by_id(obra_id)
    if not obra:
        abort(404)

    if request.method == 'POST':
        # --- Lógica de Adicionar Nova Medição ---
        valor_str = request.form.get('valor', '0').replace(
            '.', '').replace(',', '.')
        valor = float(valor_str)
        data_medicao = request.form.get('data_medicao')
        nota_fiscal = request.form.get('nota_fiscal')
        etapa_obra = request.form.get('etapa_obra')
        observacoes = request.form.get('observacoes')
        arquivo = request.files.get('arquivo')

        if not all([valor > 0, data_medicao, etapa_obra]):
            flash('Valor, Data e Etapa da Obra são obrigatórios.', 'danger')
        else:
            arquivo_path = None
            if arquivo and arquivo.filename != '':
                # --- Lógica de Salvamento de Arquivo ---
                if not obra.caminho_pasta or not os.path.isdir(obra.caminho_pasta):
                    flash(
                        f"Caminho da pasta da obra não configurado ou inválido: '{obra.caminho_pasta}'", 'danger')
                    return redirect(url_for('medicoes.listar_e_adicionar', obra_id=obra.id))

                medicoes_dir = os.path.join(obra.caminho_pasta, 'MEDICOES')
                os.makedirs(medicoes_dir, exist_ok=True)

                # Gera nome de arquivo seguro e único
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = secure_filename(
                    f"MEDICAO_{data_medicao}_NF-{nota_fiscal or 'SN'}_{timestamp}.pdf")
                arquivo_path = os.path.join(medicoes_dir, filename)
                arquivo.save(arquivo_path)

            nova_medicao = Medicao(
                obra_id=obra.id,
                valor=valor,
                data_medicao=data_medicao,
                nota_fiscal=nota_fiscal,
                etapa_obra=etapa_obra,
                observacoes=observacoes,
                arquivo_path=arquivo_path
            )
            nova_medicao.save()
            flash('Medição adicionada com sucesso!', 'success')

        return redirect(url_for('medicoes.listar_e_adicionar', obra_id=obra.id))

    # --- Lógica de Exibir a Página (GET) ---
    medicoes = Medicao.find_all_by_obra(obra_id)
    total_medido = Medicao.get_total_medido_by_obra(obra_id)
    valor_contrato = obra.valor_contrato or 0
    saldo_contrato = valor_contrato - total_medido

    etapas_exemplo = ['Fundações', 'Estrutura', 'Alvenaria',
                      'Instalações Elétricas', 'Instalações Hidráulicas', 'Acabamento']

    return render_template(
        'medicoes/medicoes.html',
        obra=obra,
        medicoes=medicoes,
        total_medido=total_medido,
        saldo_contrato=saldo_contrato,
        valor_contrato=valor_contrato,
        etapas_obra=etapas_exemplo
    )


@medicoes_bp.route('/nova', methods=['POST'])
def adicionar_medicao(obra_id):
    """Processa o formulário para adicionar uma nova medição com itens."""
    try:
        # Dados da medição principal
        medicao_data = {
            'referencia': request.form.get('referencia'),
            'data_medicao': request.form.get('data_medicao'),
            'nota_fiscal': request.form.get('nota_fiscal'),
            'observacoes': request.form.get('observacoes')
        }

        # Dados dos itens (vem como string JSON)
        itens_json_str = request.form.get('itens_medicao')
        if not itens_json_str:
            flash('A medição deve ter pelo menos um item.', 'danger')
            return redirect(url_for('medicoes.listar_e_adicionar', obra_id=obra_id))

        itens_data = json.loads(itens_json_str)

        if not all(medicao_data.values()) or not itens_data:
            flash(
                'Todos os campos da medição e pelo menos um item são obrigatórios.', 'danger')
        else:
            Medicao.create(obra_id, medicao_data, itens_data)
            flash('Medição adicionada com sucesso!', 'success')

    except json.JSONDecodeError:
        flash('Erro ao processar os itens da medição. Formato inválido.', 'danger')
    except Exception as e:
        flash(f'Erro ao salvar medição: {e}', 'danger')

    return redirect(url_for('medicoes.listar_e_adicionar', obra_id=obra_id))


@medicoes_bp.route('/<int:medicao_id>', methods=['GET'])
def visualizar_medicao(obra_id, medicao_id):
    """Endpoint para buscar os detalhes de uma medição (seus itens) via API."""
    medicao, itens = Medicao.find_by_id_with_items(medicao_id)
    if not medicao:
        return jsonify({"erro": "Medição não encontrada"}), 404

    return jsonify({
        "medicao": medicao,
        "itens": itens
    })


@medicoes_bp.route('/medicao/criar', methods=['POST'])
def criar_medicao():
    """
    Cria um novo cabeçalho de medição para uma obra.
    """
    obra_id = request.form.get('obra_id', type=int)
    # O campo 'periodo_referencia' do formulário corresponde à coluna 'referencia' na tabela
    referencia = request.form.get('periodo_referencia')
    data_medicao = request.form.get('data_medicao')

    if not all([obra_id, referencia, data_medicao]):
        flash('Todos os campos são obrigatórios para iniciar uma medição.', 'danger')
        return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))

    conn = get_db_connection()
    try:
        # Descobre o número da última medição para incrementar
        last_medicao_num = conn.execute(
            "SELECT MAX(numero_medicao) FROM medicoes WHERE obra_id = ?",
            (obra_id,)
        ).fetchone()[0]

        next_medicao_num = (last_medicao_num or 0) + 1

        # Insere o novo cabeçalho de medição
        conn.execute(
            """
            INSERT INTO medicoes (obra_id, numero_medicao, referencia, data_medicao, criacao_usuario, valor)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (obra_id, next_medicao_num, referencia,
             data_medicao, "USUARIO_ATUAL", 0.0)
        )
        conn.commit()
        flash(
            f'Medição Nº {next_medicao_num} ({referencia}) iniciada com sucesso!', 'success')
    except sqlite3.Error as e:
        flash(f'Erro ao criar medição: {e}', 'danger')
        # Log do erro para depuração
        print(f"Erro no banco de dados: {e}")
    finally:
        conn.close()

    return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))


@medicoes_bp.route('/<int:medicao_id>/detalhar', methods=['GET', 'POST'])
def detalhar_medicao(medicao_id):
    """
    Exibe uma visão detalhada de uma medição específica, permitindo a edição
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Acessar colunas pelo nome

    try:
        medicao = conn.execute(
            "SELECT * FROM medicoes WHERE id = ?", (medicao_id,)).fetchone()
        if not medicao:
            abort(404, description="Medição não encontrada")

        obra_id = medicao['obra_id']
        obra_query = "SELECT o.*, c.nome as construtora_nome FROM obras o JOIN construtoras c ON o.construtora_id = c.id WHERE o.id = ?"
        obra = conn.execute(obra_query, (obra_id,)).fetchone()

        orcamento = conn.execute(
            "SELECT * FROM orcamentos WHERE obra_id = ?", (obra_id,)).fetchone()
        if not orcamento:
            abort(404, description="Orçamento não encontrado para esta obra")

        if request.method == 'POST':
            # --- Lógica POST (Salvar os dados) ---
            try:
                itens_orcamento = conn.execute(
                    "SELECT id FROM orcamento_itens WHERE orcamento_id = ?", (orcamento['id'],)).fetchall()
                for item in itens_orcamento:
                    orcamento_item_id = item['id']
                    form_key = f"quantidade_medida_{orcamento_item_id}"

                    try:
                        quantidade_medida_str = request.form.get(
                            form_key, '0').replace(',', '.')
                        quantidade_medida = float(
                            quantidade_medida_str) if quantidade_medida_str else 0.0
                    except (ValueError, TypeError):
                        quantidade_medida = 0.0

                    item_existente = conn.execute(
                        "SELECT id FROM medicao_itens WHERE medicao_id = ? AND orcamento_item_id = ?",
                        (medicao_id, orcamento_item_id)
                    ).fetchone()

                    # Lógica para salvar justificativa
                    justificativa = request.form.get(
                        f"justificativa_aditivo_{orcamento_item_id}", None)

                    if quantidade_medida > 0:
                        if item_existente:
                            conn.execute("UPDATE medicao_itens SET quantidade_medida = ?, justificativa_aditivo = ? WHERE id = ?",
                                         (quantidade_medida, justificativa, item_existente['id']))
                        else:
                            conn.execute("INSERT INTO medicao_itens (medicao_id, orcamento_item_id, quantidade_medida, justificativa_aditivo) VALUES (?, ?, ?, ?)",
                                         (medicao_id, orcamento_item_id, quantidade_medida, justificativa))
                    elif item_existente:
                        conn.execute(
                            "DELETE FROM medicao_itens WHERE id = ?", (item_existente['id'],))

                conn.commit()
                flash('Medição salva com sucesso!', 'success')
            except sqlite3.Error as e:
                conn.rollback()
                flash(f'Erro ao salvar a medição: {e}', 'danger')

            return redirect(url_for('medicoes.detalhar_medicao', medicao_id=medicao_id))

        # --- Lógica GET (Exibir a página com todos os cálculos) ---
        itens_orcamento = conn.execute(
            "SELECT * FROM orcamento_itens WHERE orcamento_id = ? ORDER BY id", (orcamento['id'],)).fetchall()
        itens_medidos_atuais_raw = conn.execute(
            "SELECT * FROM medicao_itens WHERE medicao_id = ?", (medicao_id,)).fetchall()
        itens_medidos_atuais = {
            item['orcamento_item_id']: item for item in itens_medidos_atuais_raw}

        query_anterior = """
            SELECT mi.orcamento_item_id, SUM(mi.quantidade_medida) as total_anterior
            FROM medicao_itens mi
            JOIN medicoes m ON mi.medicao_id = m.id
            WHERE m.obra_id = ? AND m.data_medicao < ?
            GROUP BY mi.orcamento_item_id
        """
        medido_anterior_result = conn.execute(
            query_anterior, (obra_id, medicao['data_medicao'])).fetchall()
        total_medido_anterior = {
            row['orcamento_item_id']: row['total_anterior'] for row in medido_anterior_result}

        processed_itens = []
        total_orcado_geral = 0
        total_anterior_geral = 0
        total_atual_geral = 0

        for item in itens_orcamento:
            item_id = item['id']
            valor_unitario = item['valor_unitario'] or 0
            qtd_contrato = item['quantidade'] or 0

            # --- Valores do Contrato ---
            valor_contrato = qtd_contrato * valor_unitario
            total_orcado_geral += valor_contrato

            # --- Valores Anteriores ---
            qtd_anterior = total_medido_anterior.get(item_id, 0)
            valor_anterior = qtd_anterior * valor_unitario
            total_anterior_geral += valor_anterior

            # --- Valores Atuais ---
            item_medido_atual = itens_medidos_atuais.get(item_id)
            qtd_atual = item_medido_atual['quantidade_medida'] if item_medido_atual else 0.0
            valor_atual = qtd_atual * valor_unitario
            total_atual_geral += valor_atual

            # --- Acumulados ---
            qtd_acumulada = qtd_anterior + qtd_atual
            valor_acumulado = qtd_acumulada * valor_unitario

            # --- Saldos ---
            qtd_saldo = qtd_contrato - qtd_acumulada
            valor_saldo = valor_contrato - valor_acumulado

            # --- Flag para Aditivo ---
            is_extrapolated = qtd_acumulada > qtd_contrato

            # --- Percentuais (Item) ---
            perc_contrato = 100.0 if valor_contrato > 0 else 0
            perc_anterior = (valor_anterior / valor_contrato *
                             100) if valor_contrato > 0 else 0
            perc_atual = (valor_atual / valor_contrato *
                          100) if valor_contrato > 0 else 0
            perc_acumulado = (valor_acumulado / valor_contrato *
                              100) if valor_contrato > 0 else 0
            perc_saldo = (valor_saldo / valor_contrato *
                          100) if valor_contrato > 0 else 0

            processed_itens.append({
                'id': item_id, 'descricao': item['descricao'], 'unidade': item['unidade'], 'valor_unitario': valor_unitario,
                # Quantidades
                'qtd_contrato': qtd_contrato, 'qtd_anterior': qtd_anterior, 'qtd_atual': qtd_atual, 'qtd_acumulada': qtd_acumulada, 'qtd_saldo': qtd_saldo,
                # Valores
                'valor_contrato': valor_contrato, 'valor_anterior': valor_anterior, 'valor_atual': valor_atual, 'valor_acumulado': valor_acumulado, 'valor_saldo': valor_saldo,
                # Percentuais
                'perc_contrato': perc_contrato, 'perc_anterior': perc_anterior, 'perc_atual': perc_atual, 'perc_acumulado': perc_acumulado, 'perc_saldo': perc_saldo,
                # Aditivo
                'is_extrapolated': is_extrapolated,
                'justificativa_aditivo': item_medido_atual['justificativa_aditivo'] if item_medido_atual else None
            })

        # --- Totais e Percentuais Gerais ---
        total_acumulado_geral = total_anterior_geral + total_atual_geral
        total_saldo_geral = total_orcado_geral - total_acumulado_geral

        perc_total_orcado = 100.0 if total_orcado_geral > 0 else 0
        perc_total_anterior = (
            total_anterior_geral / total_orcado_geral * 100) if total_orcado_geral > 0 else 0
        perc_total_atual = (
            total_atual_geral / total_orcado_geral * 100) if total_orcado_geral > 0 else 0
        perc_total_acumulado = (
            total_acumulado_geral / total_orcado_geral * 100) if total_orcado_geral > 0 else 0
        perc_total_saldo = (
            total_saldo_geral / total_orcado_geral * 100) if total_orcado_geral > 0 else 0

        totais = {
            # Valores
            'orcado': total_orcado_geral, 'anterior': total_anterior_geral, 'atual': total_atual_geral,
            'acumulado': total_acumulado_geral, 'saldo': total_saldo_geral,
            # Percentuais
            'perc_orcado': perc_total_orcado, 'perc_anterior': perc_total_anterior, 'perc_atual': perc_total_atual,
            'perc_acumulado': perc_total_acumulado, 'perc_saldo': perc_total_saldo
        }

        return render_template('medicoes/detalhar_medicao.html',
                               medicao=medicao,
                               obra=obra,
                               orcamento=orcamento,
                               itens=processed_itens,
                               totais=totais)
    except sqlite3.Error as e:
        flash(f"Erro de banco de dados: {e}", "danger")
        return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=medicao['obra_id'] if 'medicao' in locals() and medicao else 0))
    finally:
        if 'conn' in locals() and conn:
            conn.close()


@medicoes_bp.route('/medicao/<int:medicao_id>/formulario', methods=['GET'])
def carregar_formulario_medicao(medicao_id):
    """
    Retorna apenas o HTML do formulário de detalhe da medição, para ser carregado via AJAX.
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        # Reutiliza a mesma lógica de busca e cálculo de detalhar_medicao (GET)
        medicao = conn.execute(
            "SELECT * FROM medicoes WHERE id = ?", (medicao_id,)).fetchone()
        if not medicao:
            return "<p>Medição não encontrada.</p>", 404

        obra_id = medicao['obra_id']
        orcamento = conn.execute(
            "SELECT * FROM orcamentos WHERE obra_id = ?", (obra_id,)).fetchone()
        itens_orcamento = conn.execute(
            "SELECT * FROM orcamento_itens WHERE orcamento_id = ? ORDER BY id", (orcamento['id'],)).fetchall()
        itens_medidos_atuais = {item['orcamento_item_id']: item for item in conn.execute(
            "SELECT * FROM medicao_itens WHERE medicao_id = ?", (medicao_id,)).fetchall()}

        query_anterior = """
            SELECT mi.orcamento_item_id, SUM(mi.quantidade_medida) as total_anterior
            FROM medicao_itens mi
            JOIN medicoes m ON mi.medicao_id = m.id
            WHERE m.obra_id = ? AND m.data_medicao < ?
            GROUP BY mi.orcamento_item_id
        """
        total_medido_anterior = {row['orcamento_item_id']: row['total_anterior'] for row in conn.execute(
            query_anterior, (obra_id, medicao['data_medicao'])).fetchall()}

        processed_itens = []
        total_orcado_geral = total_anterior_geral = total_atual_geral = 0

        for item in itens_orcamento:
            item_id = item['id']
            valor_unitario = item['valor_unitario'] or 0
            qtd_contrato = item['quantidade'] or 0
            valor_contrato = qtd_contrato * valor_unitario
            total_orcado_geral += valor_contrato
            qtd_anterior = total_medido_anterior.get(item_id, 0)
            valor_anterior = qtd_anterior * valor_unitario
            total_anterior_geral += valor_anterior
            item_medido_atual = itens_medidos_atuais.get(item_id)
            qtd_atual = item_medido_atual['quantidade_medida'] if item_medido_atual else 0.0
            valor_atual = qtd_atual * valor_unitario
            total_atual_geral += valor_atual
            qtd_acumulada = qtd_anterior + qtd_atual
            valor_acumulado = qtd_acumulada * valor_unitario
            qtd_saldo = qtd_contrato - qtd_acumulada
            valor_saldo = valor_contrato - valor_acumulado
            processed_itens.append({'id': item_id, 'descricao': item['descricao'], 'unidade': item['unidade'], 'qtd_contrato': qtd_contrato, 'valor_contrato': valor_contrato, 'qtd_anterior': qtd_anterior,
                                   'valor_anterior': valor_anterior, 'qtd_atual': qtd_atual, 'valor_atual': valor_atual, 'qtd_acumulada': qtd_acumulada, 'valor_acumulado': valor_acumulado, 'qtd_saldo': qtd_saldo, 'valor_saldo': valor_saldo})

        totais = {'orcado': total_orcado_geral, 'anterior': total_anterior_geral, 'atual': total_atual_geral,
                  'acumulado': total_anterior_geral + total_atual_geral, 'saldo': total_orcado_geral - (total_anterior_geral + total_atual_geral)}

        # Renderiza um template parcial, sem o layout base
        return render_template('medicoes/_form_detalhar.html', medicao=medicao, orcamento=orcamento, itens=processed_itens, totais=totais)
    finally:
        if conn:
            conn.close()


@medicoes_bp.route('/medicao/<int:medicao_id>/excluir', methods=['POST'])
def excluir_medicao(medicao_id):
    """
    Exclui uma medição e todos os seus itens.
    """
    conn = get_db_connection()
    try:
        # Primeiro, precisamos do obra_id para o redirecionamento
        medicao = conn.execute(
            "SELECT obra_id FROM medicoes WHERE id = ?", (medicao_id,)).fetchone()
        if not medicao:
            flash('Medição não encontrada.', 'danger')
            # Redireciona para a home se não encontrar
            return redirect(url_for('index'))

        obra_id = medicao['obra_id']

        # Excluir os itens da medição primeiro para manter a integridade
        conn.execute(
            "DELETE FROM medicao_itens WHERE medicao_id = ?", (medicao_id,))

        # Excluir o cabeçalho da medição
        conn.execute("DELETE FROM medicoes WHERE id = ?", (medicao_id,))

        conn.commit()
        flash('Medição excluída com sucesso!', 'success')

        # Redireciona de volta para a página do orçamento da obra
        return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))

    except sqlite3.Error as e:
        conn.rollback()
        flash(f'Erro ao excluir a medição: {e}', 'danger')
        # Tenta redirecionar de volta se possível
        if 'obra_id' in locals():
            return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))
        else:
            return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()


@medicoes_bp.route('/<int:medicao_id>/fechar', methods=['POST'])
def fechar_medicao(medicao_id):
    """
    Finaliza uma medição, calcula seu valor total final e altera seu status para 'Fechada'.
    Uma vez fechada, a medição não pode mais ser alterada.
    """
    conn = get_db_connection()
    try:
        # Verificar se a medição já não está fechada
        medicao = conn.execute(
            "SELECT obra_id, status FROM medicoes WHERE id = ?", (medicao_id,)).fetchone()
        if not medicao:
            flash('Medição não encontrada.', 'danger')
            return redirect(url_for('index'))

        obra_id = medicao['obra_id']
        if medicao['status'] == 'Fechada':
            flash('Esta medição já está fechada e não pode ser alterada.', 'warning')
            return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))

        # Calcular o valor final da medição somando os valores dos seus itens
        query_valor_total = """
            SELECT SUM(mi.quantidade_medida * oi.valor_unitario)
            FROM medicao_itens mi
            JOIN orcamento_itens oi ON mi.orcamento_item_id = oi.id
            WHERE mi.medicao_id = ?
        """
        valor_final = conn.execute(
            query_valor_total, (medicao_id,)).fetchone()[0] or 0.0

        # Atualizar a medição com o valor final e o novo status
        conn.execute(
            "UPDATE medicoes SET valor = ?, status = 'Fechada' WHERE id = ?",
            (valor_final, medicao_id)
        )
        conn.commit()
        flash('Medição fechada e faturada com sucesso!', 'success')
        # Redireciona de volta para a mesma página para mostrar o status atualizado
        return redirect(url_for('.detalhar_medicao', medicao_id=medicao_id))

    except sqlite3.Error as e:
        conn.rollback()
        flash(f'Erro ao fechar a medição: {e}', 'danger')
        if 'obra_id' in locals():
            return redirect(url_for('orcamento_bp.detalhar_orcamento', obra_id=obra_id))
        else:
            return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()


@medicoes_bp.route('/<int:medicao_id>/reabrir', methods=['POST'])
def reabrir_medicao(medicao_id):
    """
    Reabre uma medição que foi fechada, alterando seu status para 'Em Aberto'.
    """
    conn = get_db_connection()
    try:
        # Apenas altera o status e anula o valor finalizado
        conn.execute(
            "UPDATE medicoes SET status = 'Em Aberto', valor = NULL WHERE id = ?",
            (medicao_id,)
        )
        conn.commit()
        flash('Medição reaberta com sucesso! Agora você pode editá-la novamente.', 'info')
        return redirect(url_for('.detalhar_medicao', medicao_id=medicao_id))

    except sqlite3.Error as e:
        conn.rollback()
        flash(f'Erro ao reabrir a medição: {e}', 'danger')
        return redirect(url_for('.detalhar_medicao', medicao_id=medicao_id))
    finally:
        if conn:
            conn.close()
