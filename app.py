from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import json
from datetime import datetime
from itertools import groupby
from collections import defaultdict

# Modelos
from models.obra_model import Obra
from database import get_db_connection, init_db

# Blueprints
from controllers.cadastro_obra_controller import cadastro_obra_bp
from routes.cadastro_avancado import cadastro_bp as cadastro_avancado_bp
from routes.medicoes import medicoes_bp
from modules.orcamento.routes import orcamento_bp

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123'
DATABASE = 'database.db'

# --- Filtros Customizados para o Jinja ---


def format_date_filter(value, fmt='%d/%m/%Y'):
    """Formata uma string de data (ex: '2023-12-31') para o formato brasileiro."""
    if value is None:
        return ""
    try:
        # Converte a string para objeto datetime e depois para o formato desejado
        date_obj = datetime.strptime(str(value), '%Y-%m-%d')
        return date_obj.strftime(fmt)
    except ValueError:
        # Se a data já estiver em um formato diferente ou for inválida, retorna o valor original
        return value


# Registrar o filtro no ambiente Jinja do Flask
app.jinja_env.filters['format_date'] = format_date_filter


# --- Inicialização do Banco de Dados ---
def init_db():
    """
    Cria e/ou atualiza o banco de dados, garantindo que todas as tabelas e
    colunas necessárias existam.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # --- 1. Garante que a tabela 'construtoras' exista ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS construtoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                codigo TEXT NOT NULL UNIQUE,
                razao_social TEXT,
                cnpj TEXT UNIQUE,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --- 2. Garante que a tabela 'obras' exista ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS obras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                construtora_id INTEGER NOT NULL,
                FOREIGN KEY (construtora_id) REFERENCES construtoras (id)
            )
        ''')

        # --- 3. Verifica e adiciona colunas ausentes na tabela 'obras' ---
        cursor.execute("PRAGMA table_info(obras)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        # Dicionário de colunas que a tabela DEVE ter [Nome da Coluna: Tipo de Dados]
        required_columns = {
            "cidade": "TEXT",
            "estado": "TEXT",
            "endereco": "TEXT",
            "responsavel": "TEXT",
            "telefone_responsavel": "TEXT",
            "email_responsavel": "TEXT",
            "data_inicio": "DATE",
            "data_prevista_fim": "DATE",
            "status": "TEXT DEFAULT 'Em andamento'",
            "caminho_pasta": "TEXT",
            "observacoes": "TEXT",  # Coluna do erro anterior
            "data_cadastro": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "etapa_atual": "TEXT DEFAULT 'Orçamento'",  # Coluna do erro anterior
            "anotacoes": "TEXT",  # Coluna do erro atual
            "cnpj": "TEXT",
            "numero": "TEXT",
            "bairro": "TEXT",
            "cep": "TEXT",
            "uf": "TEXT",
            "cno": "TEXT"  # Adicionando a coluna CNO que faltava
        }

        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE obras ADD COLUMN {col_name} {col_type}")
                print(f"Coluna '{col_name}' adicionada à tabela 'obras'.")

        # --- 4. Garante que a tabela 'orcamentos' exista ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                obra_id INTEGER NOT NULL UNIQUE,
                codigo TEXT,
                tipo TEXT DEFAULT 'Orçamento Principal',
                valor_custo REAL DEFAULT 0.0,
                valor_venda REAL DEFAULT 0.0,
                criacao_usuario TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE
            )
        ''')

        # --- 5. Trigger para criar um orçamento padrão para cada nova obra ---
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS criar_orcamento_default
            AFTER INSERT ON obras
            FOR EACH ROW
            BEGIN
                INSERT INTO orcamentos (obra_id, codigo, criacao_usuario)
                VALUES (NEW.id, 'ORC-' || substr('000000' || NEW.id, -6), 'SISTEMA');
            END;
        ''')

        # --- 6. Back-fill: Garante que obras antigas tenham um orçamento ---
        cursor.execute("""
            INSERT INTO orcamentos (obra_id, codigo, criacao_usuario)
            SELECT o.id, 'ORC-' || substr('000000' || o.id, -6), 'SISTEMA_BACKFILL'
            FROM obras o
            LEFT JOIN orcamentos orc ON o.id = orc.obra_id
            WHERE orc.id IS NULL
        """)

        # --- 7. Garante que a tabela de itens de orçamento exista ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orcamento_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                item_num TEXT,
                descricao TEXT NOT NULL,
                unidade TEXT,
                quantidade REAL DEFAULT 0,
                valor_unitario REAL DEFAULT 0,
                valor_total REAL GENERATED ALWAYS AS (quantidade * valor_unitario) STORED,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id) ON DELETE CASCADE
            )
        ''')

        # --- 8. Garante que a tabela de medicoes (cabeçalho) exista ---
        # Unificando a estrutura nova e legada para ser a fonte única da verdade.

        # --- 8.1 Verificação e Correção da Estrutura da Tabela 'medicoes' ---
        # Verificamos se a coluna 'valor' permite nulos. Se não, recriamos a tabela.
        cursor.execute("PRAGMA table_info(medicoes)")
        columns_info = {col[1]: col for col in cursor.fetchall()}

        # A coluna 'valor' (índice 3) não deve ser 'NOT NULL' (índice 3 == 1)
        valor_is_not_null = 'valor' in columns_info and columns_info['valor'][3] == 1

        if valor_is_not_null:
            print(
                "Aplicando migração: Corrigindo 'NOT NULL' na coluna 'valor' da tabela 'medicoes'...")
            # Renomeia a tabela antiga
            cursor.execute('ALTER TABLE medicoes RENAME TO medicoes_old;')
            # Cria a nova tabela com a estrutura correta (valor REAL, sem NOT NULL)
            cursor.execute('''
                CREATE TABLE medicoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    obra_id INTEGER NOT NULL,
                    numero_medicao INTEGER,
                    referencia TEXT,
                    nota_fiscal TEXT,
                    data_medicao DATE NOT NULL,
                    valor REAL, 
                    status TEXT NOT NULL DEFAULT 'Em Aberto',
                    observacoes TEXT,
                    arquivo_path TEXT,
                    criacao_usuario TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE
                )
            ''')
            # Copia os dados da tabela antiga para a nova, garantindo um status padrão
            cursor.execute('''
                INSERT INTO medicoes (id, obra_id, numero_medicao, referencia, nota_fiscal, data_medicao, valor, status, observacoes, arquivo_path, criacao_usuario, data_criacao)
                SELECT id, obra_id, numero_medicao, referencia, nota_fiscal, data_medicao, valor, COALESCE(status, 'Em Aberto'), observacoes, arquivo_path, criacao_usuario, data_criacao FROM medicoes_old;
            ''')
            # Remove a tabela antiga
            cursor.execute('DROP TABLE medicoes_old;')
            print("Tabela 'medicoes' corrigida com sucesso.")
        else:
            # Se a tabela ainda não existe ou já está correta, cria com a estrutura certa.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    obra_id INTEGER NOT NULL,
                    numero_medicao INTEGER,
                    referencia TEXT,
                    nota_fiscal TEXT,
                    data_medicao DATE NOT NULL,
                    valor REAL,
                    status TEXT NOT NULL DEFAULT 'Em Aberto',
                    observacoes TEXT,
                    arquivo_path TEXT,
                    criacao_usuario TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE
                )
            ''')

        # --- 8.2. Garante que colunas ausentes na tabela 'medicoes' sejam adicionadas ---
        cursor.execute("PRAGMA table_info(medicoes)")
        medicoes_columns = {column[1] for column in cursor.fetchall()}

        required_medicoes_columns = {
            "numero_medicao": "INTEGER",
            "referencia": "TEXT",
            "nota_fiscal": "TEXT",
            "valor": "REAL",
            "status": "TEXT",
            "observacoes": "TEXT",
            "arquivo_path": "TEXT",
            "criacao_usuario": "TEXT"
        }

        for col_name, col_type in required_medicoes_columns.items():
            if col_name not in medicoes_columns:
                cursor.execute(
                    f"ALTER TABLE medicoes ADD COLUMN {col_name} {col_type}")
                print(f"Coluna '{col_name}' adicionada à tabela 'medicoes'.")

        # Adicionar a coluna 'numero_medicao' à tabela 'medicoes' se não existir
        if 'numero_medicao' not in medicoes_columns:
            print("Aplicando migração: Adicionando 'numero_medicao' a 'medicoes'...")
            cursor.execute(
                'ALTER TABLE medicoes ADD COLUMN numero_medicao INTEGER;')
            conn.commit()
            print("'numero_medicao' adicionada com sucesso.")

        # --- 9. Garante que a tabela de medicao_itens (detalhes) exista ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicao_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicao_id INTEGER NOT NULL,
                orcamento_item_id INTEGER NOT NULL,
                quantidade_medida REAL NOT NULL DEFAULT 0,
                justificativa_aditivo TEXT,
                FOREIGN KEY (medicao_id) REFERENCES medicoes (id) ON DELETE CASCADE,
                FOREIGN KEY (orcamento_item_id) REFERENCES orcamento_itens (id) ON DELETE CASCADE
            )
        ''')

        # Adicionar a coluna 'justificativa_aditivo' à tabela 'medicao_itens' se não existir
        cursor.execute("PRAGMA table_info(medicao_itens)")
        columns_medicao_itens = [column[1] for column in cursor.fetchall()]
        if 'justificativa_aditivo' not in columns_medicao_itens:
            print(
                "Aplicando migração: Adicionando 'justificativa_aditivo' a 'medicao_itens'...")
            cursor.execute(
                'ALTER TABLE medicao_itens ADD COLUMN justificativa_aditivo TEXT;')
            conn.commit()
            print("'justificativa_aditivo' adicionada com sucesso.")

        # --- 10. REMOVIDO: Execução do script SQL legado ---
        # A estrutura legada foi mesclada na definição acima para evitar conflitos.

        conn.commit()
        print("Banco de dados verificado e atualizado com sucesso.")

    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Conexão com o banco de dados fechada.")


# --- Registro dos Blueprints ---
app.register_blueprint(cadastro_obra_bp)
app.register_blueprint(cadastro_avancado_bp)
app.register_blueprint(medicoes_bp, url_prefix='/medicao')
app.register_blueprint(orcamento_bp)


# --- Rotas Principais ---
@app.route('/')
def index():
    """Página inicial - lista todas as obras, com filtros."""
    # 1. Obter parâmetros de filtro da URL
    filtros = {
        'construtora_id': request.args.get('construtora_id', ''),
        'busca': request.args.get('busca', ''),
        'etapa': request.args.get('etapa', ''),
        'sistema': request.args.get('sistema', '')
    }

    # 2. Buscar obras com base nos filtros
    obras = Obra.find_by_filters(filtros)

    # 3. Calcular estatísticas com base nos resultados filtrados
    total_obras = len(obras) if obras else 0
    obras_em_andamento = len(
        [o for o in obras if o.status == 'Em andamento']) if obras else 0
    obras_concluidas = len(
        [o for o in obras if o.status == 'Concluído']) if obras else 0

    stats = {
        'total': total_obras,
        'andamento': obras_em_andamento,
        'concluidas': obras_concluidas
    }

    # 4. Buscar dados para preencher os menus de filtro
    conn = get_db_connection()
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    conn.close()

    etapas = list(Obra.get_etapas_era().keys())
    sistemas_protecao = [
        {'nome': 'SLQA'}, {'nome': 'Piso a Piso'}, {'nome': 'Fachadeira'},
        {'nome': 'Bandeja'}, {'nome': 'Linha de Vida'}
    ]

    # 5. Renderizar o template com os dados corretos
    return render_template('index.html',
                           obras=obras,  # Envia a lista de obras filtradas
                           stats=stats,
                           construtoras=construtoras,
                           filtros=filtros,  # Envia os filtros atuais para preencher o form
                           etapas=etapas,
                           sistemas_protecao=sistemas_protecao)


@app.route('/obra/<int:id>')
def visualizar_obra(id):
    """Exibe os detalhes de uma obra específica."""
    obra = Obra.find_by_id(id)
    if not obra:
        flash('Obra não encontrada.', 'danger')
        return redirect(url_for('index'))

    # Dados fictícios para as etapas organizadas
    etapas_organizadas = {
        'Orçamento': [
            {'item': 'Solicitação recebida', 'concluido': True,
                'data_conclusao': '2023-01-10', 'responsavel': 'Admin', 'observacoes': ''},
            {'item': 'Proposta enviada', 'concluido': True, 'data_conclusao': '2023-01-15',
                'responsavel': 'Admin', 'observacoes': 'Aguardando feedback.'},
            {'item': 'Aguardando aprovação', 'concluido': False,
                'data_conclusao': None, 'responsavel': '', 'observacoes': ''}
        ],
        'Projeto': [
            {'item': 'Projeto SLQA', 'concluido': False,
                'data_conclusao': None, 'responsavel': '', 'observacoes': ''},
            {'item': 'Projeto Piso a Piso', 'concluido': False,
                'data_conclusao': None, 'responsavel': '', 'observacoes': ''}
        ],
        'Execução': [
            {'item': 'SLQA executado', 'concluido': False,
                'data_conclusao': None, 'responsavel': '', 'observacoes': ''}
        ]
    }

    # Dados fictícios para sistemas da obra
    sistemas_obra = [
        {'id': 1, 'nome': 'SLQA', 'descricao': 'Sistema de Linhas de Ancoragem',
            'status': 'Em andamento'},
        {'id': 2, 'nome': 'Piso a Piso',
            'descricao': 'Proteção de vãos entre pavimentos', 'status': 'Pendente'}
    ]

    return render_template('visualizar_obra.html',
                           obra=dict(obra),
                           etapas_organizadas=etapas_organizadas,
                           sistemas_obra=sistemas_obra)


@app.route('/construtoras', methods=['GET', 'POST'])
def construtoras():
    """Página de gerenciamento de construtoras."""
    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        codigo = request.form['codigo']
        razao_social = request.form.get('razao_social')
        cnpj = request.form.get('cnpj')

        if not nome or not codigo:
            flash('Nome e Código são campos obrigatórios.', 'danger')
        else:
            try:
                conn.execute(
                    'INSERT INTO construtoras (nome, codigo, razao_social, cnpj) VALUES (?, ?, ?, ?)',
                    (nome, codigo, razao_social, cnpj)
                )
                conn.commit()
                flash('Construtora adicionada com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash(
                    'Já existe uma construtora com esse Nome, Código ou CNPJ.', 'danger')
            except Exception as e:
                flash(
                    f'Ocorreu um erro ao adicionar a construtora: {e}', 'danger')

        conn.close()
        return redirect(url_for('construtoras'))

    # Se for GET, apenas exibe a lista
    construtoras_list = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    conn.close()
    return render_template('construtoras.html', construtoras=construtoras_list)


@app.route('/construtoras/<int:id>/editar', methods=['GET', 'POST'])
def editar_construtora(id):
    """Edita uma construtora existente."""
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        try:
            conn.execute(
                'UPDATE construtoras SET nome = ? WHERE id = ?', (nome, id))
            conn.commit()
            flash('Construtora atualizada com sucesso!', 'success')
            return redirect(url_for('construtoras'))
        except Exception as e:
            flash(f"Erro ao atualizar construtora: {e}", "danger")

    construtora = conn.execute(
        'SELECT * FROM construtoras WHERE id = ?', (id,)).fetchone()
    conn.close()
    if construtora:
        # A resposta para GET pode ser um JSON para preencher um modal via JS
        return jsonify(dict(construtora))
    return redirect(url_for('construtoras'))


@app.route('/construtora/excluir/<int:id>', methods=['POST'])
def excluir_construtora(id):
    """Exclui uma construtora, com verificação de integridade."""
    conn = get_db_connection()
    try:
        # Tenta excluir a construtora
        conn.execute('DELETE FROM construtoras WHERE id = ?', (id,))
        conn.commit()
        flash('Construtora excluída com sucesso!', 'success')
    except sqlite3.IntegrityError:
        # Captura o erro que ocorre se houver obras vinculadas (foreign key constraint)
        flash('Não é possível excluir esta construtora, pois ela possui obras associadas. Por favor, reatribua ou delete as obras primeiro.', 'danger')
    except Exception as e:
        # Captura quaisquer outros erros
        flash(
            f'Ocorreu um erro inesperado ao excluir a construtora: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('construtoras'))


@app.route('/obra/excluir/<int:id>', methods=['POST'])
def excluir_obra(id):
    """Exclui uma obra específica."""
    try:
        Obra.delete(id)
        flash('Obra excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir obra: {e}', 'danger')
    return redirect(url_for('index'))


@app.route('/editar_obra/<int:id>', methods=['GET', 'POST'])
def editar_obra(id):
    """Exibe o formulário e processa a edição de uma obra."""
    if request.method == 'POST':
        # Obter os dados do formulário
        dados = {
            'id': id,
            'nome': request.form['nome_fantasia'],
            'construtora_id': request.form['construtora_id'],
            'responsavel': request.form['responsavel'],
            'status': request.form['status'],
            'etapa_atual': request.form['etapa_atual'],
            'anotacoes': request.form['anotacoes'],
            'caminho_pasta': request.form['caminho_pasta'],
            'cnpj': request.form.get('cnpj'),
            'endereco': request.form.get('endereco'),
            'numero': request.form.get('numero'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'uf': request.form.get('uf'),
            'cep': request.form.get('cep')
        }

        # Lógica para atualizar a obra no banco de dados
        if Obra.update(dados):
            flash('Obra atualizada com sucesso!', 'success')
        else:
            flash('Erro ao atualizar a obra.', 'danger')

        return redirect(url_for('visualizar_obra', id=id))

    # Se for GET, busca os dados e exibe o formulário
    obra = Obra.find_by_id(id)
    if not obra:
        flash('Obra não encontrada.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    conn.close()

    # Obter a lista de etapas para popular o dropdown
    etapas_era = list(Obra.get_etapas_era().keys())

    return render_template('editar.html',
                           obra=dict(obra),
                           construtoras=construtoras,
                           etapas_era=etapas_era)

# Adicione outras rotas principais aqui (editar, excluir, etc.) se elas não estiverem em blueprints.


@app.route('/abrir_pasta', methods=['POST'])
def abrir_pasta():
    """Abre o diretório da obra no gerenciador de arquivos do sistema."""
    data = request.get_json()
    caminho = data.get('caminho_pasta')

    if not caminho:
        return jsonify({'error': 'Caminho da pasta não fornecido.'}), 400

    # Normaliza o caminho para o sistema operacional atual
    caminho_normalizado = os.path.normpath(caminho)

    if not os.path.isdir(caminho_normalizado):
        return jsonify({'error': f'O caminho não existe ou não é um diretório: {caminho_normalizado}'}), 404

    try:
        # os.startfile() é específico para Windows.
        # Para outros sistemas (Linux, macOS), você usaria outras abordagens
        # como subprocess.run(['xdg-open', caminho]) ou subprocess.run(['open', caminho])
        if os.name == 'nt':  # Windows
            os.startfile(caminho_normalizado)
            return jsonify({'message': 'O diretório da obra foi aberto.'}), 200
        else:
            return jsonify({'error': 'Funcionalidade disponível apenas para Windows.'}), 400

    except Exception as e:
        app.logger.error(
            f"Erro ao tentar abrir a pasta '{caminho_normalizado}': {e}")
        return jsonify({'error': f'Ocorreu um erro no servidor ao tentar abrir a pasta: {e}'}), 500


@app.route('/faturamento_geral')
def faturamento_geral():
    """Página que exibe um resumo de todas as medições fechadas, agrupadas por mês."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    query = """
        SELECT
            strftime('%Y-%m', m.data_medicao) as mes_ano,
            c.nome as construtora_nome,
            o.nome as obra_nome,
            m.numero_medicao,
            m.referencia,
            m.data_medicao,
            m.valor as valor_faturado,
            o.id as obra_id
        FROM medicoes m
        JOIN obras o ON m.obra_id = o.id
        JOIN construtoras c ON o.construtora_id = c.id
        WHERE m.status = 'Fechada'
        ORDER BY mes_ano DESC, c.nome, o.nome, m.numero_medicao;
    """
    medicoes_fechadas = conn.execute(query).fetchall()

    # Agrupar por mês
    faturamento_por_mes = []
    for mes, grupo in groupby(medicoes_fechadas, key=lambda x: x['mes_ano']):
        medicoes_do_mes = list(grupo)
        total_mes = sum(item['valor_faturado'] for item in medicoes_do_mes)
        faturamento_por_mes.append({
            'mes_ano': mes,
            'medicoes': medicoes_do_mes,
            'total_mes': total_mes
        })

    total_geral = sum(item['valor_faturado'] for item in medicoes_fechadas)

    conn.close()

    return render_template('faturamento_geral.html',
                           faturamento_por_mes=faturamento_por_mes,
                           total_geral=total_geral)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
