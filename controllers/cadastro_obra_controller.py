from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import requests
import os
import re
from werkzeug.utils import secure_filename
import sqlite3

from database import get_db_connection
from models.obra_model import Obra
from utils.empresa_api import EmpresaAPI

# Cria um Blueprint para o cadastro de obras
cadastro_obra_bp = Blueprint(
    'cadastro_obra_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# --- Rotas da API Interna ---


@cadastro_obra_bp.route("/api/consultar_cnpj", methods=['GET'])
def consultar_cnpj():
    """Consulta um CNPJ na BrasilAPI, recebido via query string."""
    cnpj = request.args.get('cnpj')  # Pega o CNPJ da query string
    if not cnpj:
        return jsonify({"erro": "Parâmetro CNPJ não encontrado"}), 400

    cnpj_limpo = re.sub(r'\D', '', cnpj)
    if len(cnpj_limpo) != 14:
        return jsonify({"erro": "CNPJ inválido"}), 400
    try:
        response = requests.get(
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Falha ao consultar API de CNPJ: {e}"}), 500


@cadastro_obra_bp.route("/api/consultar_cep/<cep>")
def consultar_cep(cep):
    """Consulta um CEP na ViaCEP."""
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) != 8:
        return jsonify({"erro": "CEP inválido"}), 400
    try:
        response = requests.get(
            f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Falha ao consultar API de CEP: {e}"}), 500


@cadastro_obra_bp.route("/api/get_or_create_construtora", methods=["POST"])
def get_or_create_construtora():
    """
    Verifica se uma construtora existe pelo CNPJ.
    Se não existir, cria uma nova.
    Retorna os dados da construtora em JSON.
    """
    data = request.get_json()
    cnpj = data.get('cnpj')
    razao_social = data.get('razao_social')
    nome_fantasia = data.get('nome_fantasia')

    if not cnpj:
        return jsonify({"erro": "CNPJ é obrigatório"}), 400

    cnpj_limpo = re.sub(r'\\D', '', cnpj)

    conn = get_db_connection()
    try:
        # 1. Verifica se a construtora já existe
        construtora = conn.execute(
            "SELECT * FROM construtoras WHERE cnpj = ?", (cnpj_limpo,)).fetchone()

        if construtora:
            conn.close()
            return jsonify(dict(construtora))

        # 2. Se não existe, cria uma nova
        else:
            # Gera um novo código para a construtora
            last_code_row = conn.execute(
                "SELECT MAX(CAST(codigo AS INTEGER)) FROM construtoras").fetchone()
            last_code = last_code_row[0] if last_code_row and last_code_row[0] is not None else 0
            new_code = f"{last_code + 1:03d}"

            # Usa o nome fantasia como nome principal, se não houver, usa a razão social
            nome_principal = nome_fantasia if nome_fantasia else razao_social

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO construtoras (nome, codigo, razao_social, cnpj)
                VALUES (?, ?, ?, ?)
            """, (nome_principal, new_code, razao_social, cnpj_limpo))

            new_id = cursor.lastrowid
            conn.commit()

            nova_construtora = conn.execute(
                "SELECT * FROM construtoras WHERE id = ?", (new_id,)).fetchone()
            conn.close()

            return jsonify(dict(nova_construtora))

    except sqlite3.IntegrityError:
        conn.close()
        # Caso raro de condição de corrida ou se o nome não for único
        return jsonify({"erro": f"Já existe uma construtora com o nome '{nome_fantasia}' ou CNPJ '{cnpj_limpo}'."}), 409
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"erro": f"Erro interno do servidor: {e}"}), 500


# --- Rota Principal de Cadastro ---


@cadastro_obra_bp.route("/obras/cadastrar", methods=["GET", "POST"])
def cadastrar_obra():
    """Exibe o formulário e processa o cadastro de uma nova obra."""
    conn = get_db_connection()
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()

    if request.method == "POST":
        # 1. Obter dados do formulário
        nome_obra = request.form.get(
            'nome_fantasia') or request.form.get('razao_social')
        construtora_id = request.form.get('construtora_id')
        cnpj = re.sub(r'\D', '', request.form.get('cnpj', ''))

        # Validação básica
        if not nome_obra or not construtora_id:
            flash('Nome da Obra e Construtora são obrigatórios!', 'danger')
            return render_template("obras/cadastrar_obra.html", construtoras=construtoras)

        # 2. Obter ou criar caminho da pasta
        caminho_pasta_form = request.form.get('caminho_pasta')
        if caminho_pasta_form:
            # Usa o caminho informado pelo usuário se ele existir
            caminho_pasta = caminho_pasta_form
        else:
            # Se não, cria um caminho padrão (fallback)
            construtora = conn.execute(
                'SELECT codigo, nome FROM construtoras WHERE id = ?', (construtora_id,)).fetchone()
            base_path = f"G:/Meu Drive/000 ALTA TELAS"
            # Monta o nome da pasta da construtora
            nome_pasta_construtora = f"{construtora['codigo']} CONSTRUTORA {construtora['nome'].upper()}"
            # Garante que o nome da obra é seguro para ser um nome de pasta
            nome_obra_seguro = secure_filename(nome_obra)
            caminho_pasta = os.path.join(
                base_path, nome_pasta_construtora, nome_obra_seguro)

        # 3. Inserir no banco de dados
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO obras (nome, construtora_id, cidade, status, responsavel, caminho_pasta, etapa_atual, anotacoes, cnpj, endereco, numero, bairro, cep, uf)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome_obra,
                construtora_id,
                request.form.get('cidade'),
                'Em andamento',
                request.form.get('responsavel'),
                caminho_pasta,
                'Orçamento',
                request.form.get('anotacoes'),
                cnpj,
                request.form.get('endereco'),
                request.form.get('numero'),
                request.form.get('bairro'),
                re.sub(r'\D', '', request.form.get('cep', '')),
                request.form.get('uf')
            ))
            obra_id = cursor.lastrowid

            # 4. Criar etapas ERA padrão para a nova obra
            etapas_padrao = Obra.get_etapas_era()
            for etapa, itens in etapas_padrao.items():
                for item in itens:
                    cursor.execute("""
                        INSERT OR IGNORE INTO etapas_era (obra_id, etapa, item, concluido)
                        VALUES (?, ?, ?, ?)
                    """, (obra_id, etapa, item, False))

            conn.commit()

            # 5. Criar a pasta no sistema de arquivos
            os.makedirs(caminho_pasta, exist_ok=True)

            flash(f'Obra "{nome_obra}" cadastrada com sucesso!', 'success')
            return redirect(url_for('visualizar_obra', id=obra_id))

        except sqlite3.IntegrityError as e:
            conn.rollback()
            flash(f'Erro de integridade ao salvar a obra: {e}', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Ocorreu um erro inesperado: {e}', 'danger')
        finally:
            conn.close()

    return render_template("obras/cadastrar_obra.html", construtoras=construtoras)


@cadastro_obra_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_obra():
    # ... (código da rota) ...
    # LÓGICA DE VISUALIZAÇÃO (GET)
    conn = get_db_connection()
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    sistemas_protecao = conn.execute(
        'SELECT * FROM sistemas_protecao ORDER BY nome').fetchall()
    etapas = list(Obra.get_etapas_era().keys())
    conn.close()

    return render_template('adicionar.html',
                           construtoras=construtoras,
                           sistemas_protecao=sistemas_protecao,
                           etapas=etapas)
