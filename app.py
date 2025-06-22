from models.obra_model import Obra
from database import get_db_connection
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import json
from datetime import datetime
import sys
from itertools import groupby
from operator import itemgetter
# Importações do novo módulo
from controllers import medicao_controller
from models.medicao_model import Medicao
import requests
from utils.empresa_api import EmpresaAPI
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123'

# Filtro personalizado para formatar data


@app.template_filter('format_date')
def format_date(value, format='%d/%m/%Y'):
    """Formata uma string de data para o formato brasileiro."""
    if value:
        try:
            # Tenta converter a string para um objeto de data
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime(format)
        except (ValueError, TypeError):
            # Se falhar ou o valor for inválido, retorna o valor original
            return value
    return ""


# Configuração do banco de dados
DATABASE = 'database.db'


def init_db():
    """Inicializa o banco de dados com as tabelas necessárias e adiciona colunas se não existirem."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # --- Verificação e adição de colunas na tabela obras ---
    cursor.execute("PRAGMA table_info(obras)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    new_columns = {
        'cnpj': 'TEXT',
        'endereco': 'TEXT',
        'numero': 'TEXT',
        'bairro': 'TEXT',
        'cep': 'TEXT',
        'uf': 'TEXT',
        'cidade': 'TEXT',
        'razao_social': 'TEXT'
    }

    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            print(f"Adicionando coluna '{col_name}' à tabela 'obras'...")
            cursor.execute(
                f"ALTER TABLE obras ADD COLUMN {col_name} {col_type}")

    # --- Verificação e adição de colunas na tabela construtoras ---
    cursor.execute("PRAGMA table_info(construtoras)")
    construtoras_cols = [column[1] for column in cursor.fetchall()]
    if 'razao_social' not in construtoras_cols:
        print("Adicionando coluna 'razao_social' à tabela 'construtoras'...")
        cursor.execute("ALTER TABLE construtoras ADD COLUMN razao_social TEXT")
    if 'cnpj' not in construtoras_cols:
        print("Adicionando coluna 'cnpj' à tabela 'construtoras'...")
        cursor.execute("ALTER TABLE construtoras ADD COLUMN cnpj TEXT")

    # Criar tabela de construtoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS construtoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            codigo TEXT NOT NULL UNIQUE,
            razao_social TEXT,
            cnpj TEXT UNIQUE
        )
    ''')

    # Criar tabela de obras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            construtora_id INTEGER NOT NULL,
            cnpj TEXT,
            razao_social TEXT,
            nome_fantasia TEXT,
            cidade TEXT,
            estado TEXT,
            endereco TEXT,
            numero TEXT,
            bairro TEXT,
            cep TEXT,
            status TEXT NOT NULL DEFAULT 'Em andamento',
            responsavel TEXT,
            caminho_pasta TEXT NOT NULL,
            etapa_atual TEXT DEFAULT 'Orçamento',
            anotacoes TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (construtora_id) REFERENCES construtoras (id)
        )
    ''')

    # Criar tabela de etapas ERA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etapas_era (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            etapa TEXT NOT NULL,
            item TEXT NOT NULL,
            concluido BOOLEAN DEFAULT FALSE,
            data_conclusao TIMESTAMP,
            responsavel TEXT,
            observacoes TEXT,
            FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE,
            UNIQUE(obra_id, etapa, item)
        )
    ''')

    # Criar tabela de sistemas de proteção
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sistemas_protecao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    ''')

    # Criar tabela de relação obra-sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obra_sistemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            sistema_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pendente',
            FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE,
            FOREIGN KEY (sistema_id) REFERENCES sistemas_protecao (id),
            UNIQUE(obra_id, sistema_id)
        )
    ''')

    # Criar tabela de medicoes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            nota_fiscal TEXT,
            FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE
        )
    ''')

    # Inserir dados iniciais se as tabelas estiverem vazias
    cursor.execute('SELECT COUNT(*) FROM construtoras')
    if cursor.fetchone()[0] == 0:
        # Inserir construtoras
        construtoras = [
            ('001 CONSTRUTORA BILD', '001'),
            ('002 CONSTRUTORA PERPLAN', '002')
        ]
        cursor.executemany(
            'INSERT INTO construtoras (nome, codigo) VALUES (?, ?)', construtoras)

        # Inserir sistemas de proteção
        sistemas = [
            ('SLQA', 'Sistema de Linha de Vida e Ancoragem'),
            ('Piso a Piso', 'Proteção Piso a Piso'),
            ('Fachadeira', 'Fachadeira / Guarda-corpo'),
            ('Bandeja', 'Bandeja de Proteção'),
            ('Linha de Vida', 'Linha de Vida Horizontal/Vertical')
        ]
        cursor.executemany(
            'INSERT INTO sistemas_protecao (nome, descricao) VALUES (?, ?)', sistemas)

        # Inserir obras de exemplo
        obras_exemplo = [
            ('BILD ALLMA', 1, 'Ribeirão Preto', 'Em andamento', 'João Silva',
             'G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/001 CONSTRUTORA BILD/BILD ALLMA', 'Projeto'),
            ('BILD ÉVERO', 1, 'São Paulo', 'Em andamento', 'Maria Santos',
             'G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/001 CONSTRUTORA BILD/BILD ÉVERO', 'Execução'),
            ('PERPLAN HYPE', 2, 'Campinas', 'Em andamento', 'Pedro Oliveira',
             'G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/002 CONSTRUTORA PERPLAN/PERPLAN HYPE', 'Orçamento'),
            ('PERPLAN SEIVA', 2, 'Santos', 'Concluído', 'Ana Costa',
             'G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/002 CONSTRUTORA PERPLAN/PERPLAN SEIVA', 'Encerramento')
        ]
        cursor.executemany('''
            INSERT INTO obras (nome, construtora_id, cidade, status, responsavel, caminho_pasta, etapa_atual)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', obras_exemplo)

        # Inserir algumas etapas ERA de exemplo
        etapas_exemplo = [
            # BILD ALLMA - Orçamento
            (1, 'Orçamento', 'Solicitação recebida', True, 'João Silva'),
            (1, 'Orçamento', 'Proposta enviada', True, 'João Silva'),
            (1, 'Orçamento', 'Aguardando aprovação', False, None),
            # BILD ALLMA - Projeto
            (1, 'Projeto', 'Projeto SLQA', True, 'João Silva'),
            (1, 'Projeto', 'Projeto Piso a Piso', False, None),
            (1, 'Projeto', 'ART emitida', False, None),
            # BILD ÉVERO - Execução
            (2, 'Execução', 'SLQA executado', True, 'Maria Santos'),
            (2, 'Execução', 'Piso a Piso executado', True, 'Maria Santos'),
            (2, 'Execução', 'Fachadeira executada', False, None),
            # PERPLAN HYPE - Orçamento
            (3, 'Orçamento', 'Solicitação recebida', True, 'Pedro Oliveira'),
            (3, 'Orçamento', 'Proposta enviada', False, None),
            # PERPLAN SEIVA - Concluído
            (4, 'Encerramento', 'Obra finalizada', True, 'Ana Costa'),
            (4, 'Encerramento', 'Relatórios entregues', True, 'Ana Costa'),
            (4, 'Encerramento', 'Feedback registrado', True, 'Ana Costa')
        ]

        for obra_id, etapa, item, concluido, responsavel in etapas_exemplo:
            cursor.execute('''
                INSERT INTO etapas_era (obra_id, etapa, item, concluido, responsavel)
                VALUES (?, ?, ?, ?, ?)
            ''', (obra_id, etapa, item, concluido, responsavel))

        # Inserir sistemas por obra
        sistemas_obra = [
            (1, 1, 'Em andamento'),  # BILD ALLMA - SLQA
            (1, 2, 'Pendente'),      # BILD ALLMA - Piso a Piso
            (2, 1, 'Concluído'),     # BILD ÉVERO - SLQA
            (2, 2, 'Concluído'),     # BILD ÉVERO - Piso a Piso
            (2, 3, 'Em andamento'),  # BILD ÉVERO - Fachadeira
            (3, 1, 'Pendente'),      # PERPLAN HYPE - SLQA
            (4, 1, 'Concluído'),     # PERPLAN SEIVA - SLQA
            (4, 2, 'Concluído'),     # PERPLAN SEIVA - Piso a Piso
        ]
        cursor.executemany('''
            INSERT INTO obra_sistemas (obra_id, sistema_id, status)
            VALUES (?, ?, ?)
        ''', sistemas_obra)

    conn.commit()
    conn.close()


def sanitize_foldername(name):
    """Remove caracteres inválidos para nomes de pastas."""
    if not name:
        return ""
    # Remove caracteres inválidos do Windows e outros comuns
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()


def gerar_caminho_pasta(construtora_codigo, construtora_nome, cnpj, nome_obra, caminho_personalizado=None):
    """
    Gera o caminho da pasta seguindo a estrutura:
    G:/Meu Drive/000 ALTA TELAS/{CODIGO} CONSTRUTORA {NOME_CONSTRUTORA}/{CNPJ} - {NOME_FANTASIA}

    Regras:
    - O nome da pasta da obra é "{CNPJ} - {NOME_FANTASIA}".
    - Nomes são sanitizados para remover caracteres inválidos.
    """
    if caminho_personalizado and caminho_personalizado.strip():
        return caminho_personalizado.strip().replace('\\', '/')

    base_path = "G:/Meu Drive/000 ALTA TELAS"

    # Sanitiza e formata o nome da construtora
    nome_sem_codigo = construtora_nome
    if construtora_codigo and construtora_nome.startswith(construtora_codigo):
        nome_sem_codigo = construtora_nome[len(construtora_codigo):].strip()
    if nome_sem_codigo.upper().startswith("CONSTRUTORA "):
        nome_sem_codigo = nome_sem_codigo[12:].strip()

    codigo_formatado = construtora_codigo.zfill(
        3) if construtora_codigo else "000"
    pasta_construtora = sanitize_foldername(
        f"{codigo_formatado} CONSTRUTORA {nome_sem_codigo.upper()}")

    # Sanitiza e formata o nome da obra
    cnpj_sanitizado = ''.join(
        filter(str.isdigit, cnpj)) if cnpj else "SEM_CNPJ"
    nome_obra_sanitizado = sanitize_foldername(
        nome_obra.upper()) if nome_obra else "OBRA SEM NOME"

    pasta_obra = f"{cnpj_sanitizado} - {nome_obra_sanitizado}"

    return f"{base_path}/{pasta_construtora}/{pasta_obra}"


def get_etapas_era():
    """Retorna a estrutura padrão das etapas ERA"""
    return {
        'Orçamento': [
            'Solicitação recebida',
            'Proposta enviada',
            'Aguardando aprovação'
        ],
        'Projeto': [
            'Projeto SLQA',
            'Projeto Piso a Piso',
            'Projeto Bandeja',
            'Projeto Fachadeira / Guarda-corpo',
            'ART emitida'
        ],
        'Execução': [
            'SLQA executado',
            'Piso a Piso executado',
            'Fachadeira executada',
            'Bandeja executada',
            'Linha de vida executada'
        ],
        'Faturamento': [
            'Primeira medição feita',
            'NFS emitida',
            'Pagamento confirmado'
        ],
        'Encerramento': [
            'Obra finalizada',
            'Relatórios entregues',
            'Feedback registrado'
        ]
    }


@app.route('/')
def index():
    """Página inicial - lista todas as obras agrupadas por construtora"""
    conn = get_db_connection()

    # Parâmetros de filtro
    construtora_id = request.args.get('construtora_id', '')
    busca = request.args.get('busca', '')
    etapa = request.args.get('etapa', '')
    sistema = request.args.get('sistema', '')

    # Query base
    query = '''
        SELECT o.*, c.nome as construtora_nome, c.codigo as construtora_codigo
        FROM obras o 
        JOIN construtoras c ON o.construtora_id = c.id
        WHERE 1=1
    '''
    params = []

    # Aplicar filtros
    if construtora_id:
        query += ' AND o.construtora_id = ?'
        params.append(construtora_id)

    if busca:
        query += ' AND (o.nome LIKE ? OR o.cidade LIKE ? OR o.responsavel LIKE ?)'
        params.extend([f'%{busca}%', f'%{busca}%', f'%{busca}%'])

    if etapa:
        query += ' AND o.etapa_atual = ?'
        params.append(etapa)

    if sistema:
        query += ''' AND o.id IN (
            SELECT os.obra_id FROM obra_sistemas os 
            JOIN sistemas_protecao sp ON os.sistema_id = sp.id 
            WHERE sp.nome LIKE ?
        )'''
        params.append(f'%{sistema}%')

    query += ' ORDER BY c.nome, o.nome'

    obras_list = conn.execute(query, params).fetchall()

    # Buscar dados adicionais para cada obra
    obras_completas = []
    for obra in obras_list:
        # Buscar sistemas da obra
        sistemas = conn.execute('''
            SELECT sp.nome, os.status
            FROM obra_sistemas os
            JOIN sistemas_protecao sp ON os.sistema_id = sp.id
            WHERE os.obra_id = ?
        ''', (obra['id'],)).fetchall()

        # Buscar progresso das etapas ERA
        etapas_progresso = conn.execute('''
            SELECT etapa, COUNT(*) as total, SUM(CASE WHEN concluido THEN 1 ELSE 0 END) as concluidos
            FROM etapas_era
            WHERE obra_id = ?
            GROUP BY etapa
        ''', (obra['id'],)).fetchall()

        obra_dict = dict(obra)
        obra_dict['sistemas'] = sistemas
        obra_dict['etapas_progresso'] = etapas_progresso
        obras_completas.append(obra_dict)

    # Agrupar obras por construtora
    obras_agrupadas = {}
    if obras_completas:
        for key, group in groupby(obras_completas, key=lambda x: x['construtora_nome']):
            obras_agrupadas[key] = list(group)

    # Buscar dados para filtros
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    sistemas_protecao = conn.execute(
        'SELECT * FROM sistemas_protecao ORDER BY nome').fetchall()
    etapas = ['Orçamento', 'Projeto', 'Execução',
              'Faturamento', 'Encerramento']

    # Estatísticas
    total_obras = conn.execute('SELECT COUNT(*) FROM obras').fetchone()[0]
    obras_andamento = conn.execute(
        "SELECT COUNT(*) FROM obras WHERE status = 'Em andamento'").fetchone()[0]
    obras_concluidas = conn.execute(
        "SELECT COUNT(*) FROM obras WHERE status = 'Concluído'").fetchone()[0]

    conn.close()

    return render_template('index.html',
                           obras_agrupadas=obras_agrupadas,
                           construtoras=construtoras,
                           sistemas_protecao=sistemas_protecao,
                           etapas=etapas,
                           filtros={'construtora_id': construtora_id,
                                    'busca': busca, 'etapa': etapa, 'sistema': sistema},
                           stats={'total': total_obras, 'andamento': obras_andamento, 'concluidas': obras_concluidas})


@app.route('/obra/<int:id>')
def visualizar_obra(id):
    """Visualizar detalhes da obra com painel ERA"""
    conn = get_db_connection()

    # Buscar obra
    obra = conn.execute('''
        SELECT o.*, c.nome as construtora_nome 
        FROM obras o 
        JOIN construtoras c ON o.construtora_id = c.id 
        WHERE o.id = ?
    ''', (id,)).fetchone()

    if obra is None:
        flash('Obra não encontrada!', 'error')
        return redirect(url_for('index'))

    # Buscar etapas ERA da obra
    etapas_obra = conn.execute('''
        SELECT etapa, item, concluido, data_conclusao, responsavel, observacoes
        FROM etapas_era
        WHERE obra_id = ?
        ORDER BY etapa, item
    ''', (id,)).fetchall()

    # Buscar sistemas da obra
    sistemas_obra = conn.execute('''
        SELECT sp.nome, sp.descricao, os.status
        FROM obra_sistemas os
        JOIN sistemas_protecao sp ON os.sistema_id = sp.id
        WHERE os.obra_id = ?
        ORDER BY sp.nome
    ''', (id,)).fetchall()

    # Organizar etapas por categoria
    etapas_organizadas = {}
    etapas_padrao = get_etapas_era()

    for etapa_cat, itens in etapas_padrao.items():
        etapas_organizadas[etapa_cat] = []
        for item in itens:
            # Buscar se existe na obra
            etapa_obra = next(
                (e for e in etapas_obra if e['etapa'] == etapa_cat and e['item'] == item), None)
            if etapa_obra:
                etapas_organizadas[etapa_cat].append(dict(etapa_obra))
            else:
                # Criar item padrão não concluído
                etapas_organizadas[etapa_cat].append({
                    'etapa': etapa_cat,
                    'item': item,
                    'concluido': False,
                    'data_conclusao': None,
                    'responsavel': None,
                    'observacoes': None
                })

    conn.close()

    return render_template('visualizar_obra.html',
                           obra=obra,
                           etapas_organizadas=etapas_organizadas,
                           sistemas_obra=sistemas_obra)


@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_obra():
    """Página para adicionar nova obra"""
    if request.method == 'POST':
        # 1. Obter dados do formulário
        nome_obra = request.form['nome_fantasia']
        construtora_id = request.form['construtora_id']
        cidade = request.form['cidade']
        estado = request.form.get('uf')
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cep = request.form.get('cep')
        status = request.form['status']
        responsavel = request.form['responsavel']
        etapa_atual = request.form['etapa_atual']
        anotacoes = request.form['anotacoes']
        cnpj = request.form.get('cnpj')
        razao_social = request.form.get('razao_social')
        nome_fantasia = request.form.get('nome_fantasia')

        # 2. Se CNPJ foi fornecido, consultar API para pegar dados completos
        if cnpj:
            api = EmpresaAPI()
            dados_empresa = api.get_dados_cnpj(cnpj)
            if not dados_empresa.get("erro"):
                # Prioriza NOME FANTASIA, senão RAZÃO SOCIAL
                nome_obra = dados_empresa.get('nome_fantasia') or dados_empresa.get(
                    'razao_social') or nome_obra
                razao_social = dados_empresa.get('razao_social', razao_social)
                nome_fantasia = dados_empresa.get(
                    'nome_fantasia', nome_fantasia)

                # Preencher dados de endereço se não foram fornecidos
                if not endereco:
                    endereco = dados_empresa.get('logradouro', '')
                if not numero:
                    numero = dados_empresa.get('numero', '')
                if not bairro:
                    bairro = dados_empresa.get('bairro', '')
                if not cidade:
                    cidade = dados_empresa.get('municipio', '')
                if not estado:
                    estado = dados_empresa.get('uf', '')
                if not cep:
                    cep = dados_empresa.get('cep', '')

        # 3. Validar dados obrigatórios
        if not all([nome_obra, construtora_id, status, etapa_atual]):
            flash('Nome, construtora, status e etapa são obrigatórios!', 'error')
            return redirect(url_for('adicionar_obra'))

        # 4. Gerar caminho da pasta
        conn = get_db_connection()
        construtora = conn.execute(
            'SELECT codigo, nome FROM construtoras WHERE id = ?', (construtora_id,)).fetchone()

        caminho_pasta = gerar_caminho_pasta(
            construtora_codigo=construtora['codigo'],
            construtora_nome=construtora['nome'],
            cnpj=cnpj,
            nome_obra=nome_obra
        )

        # 5. Criar obra no banco e pasta no disco
        try:
            # Criar diretório
            os.makedirs(caminho_pasta, exist_ok=True)

            # Inserir obra com todos os campos
            cursor = conn.execute('''
                INSERT INTO obras (
                    nome, construtora_id, cnpj, razao_social, nome_fantasia,
                    cidade, estado, endereco, numero, bairro, cep,
                    status, responsavel, caminho_pasta, etapa_atual, anotacoes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nome_obra, construtora_id, cnpj, razao_social, nome_fantasia,
                cidade, estado, endereco, numero, bairro, cep,
                status, responsavel, caminho_pasta, etapa_atual, anotacoes
            ))

            obra_id = cursor.lastrowid

            # Criar etapas ERA padrão
            etapas_padrao = get_etapas_era()
            for etapa, itens in etapas_padrao.items():
                for item in itens:
                    conn.execute('''
                        INSERT INTO etapas_era (obra_id, etapa, item, concluido)
                        VALUES (?, ?, ?, ?)
                    ''', (obra_id, etapa, item, False))

            # Criar sistemas de proteção padrão
            sistemas = conn.execute(
                'SELECT id FROM sistemas_protecao').fetchall()
            for sistema in sistemas:
                conn.execute('''
                    INSERT INTO obra_sistemas (obra_id, sistema_id, status)
                    VALUES (?, ?, ?)
                ''', (obra_id, sistema['id'], 'Pendente'))

            conn.commit()
            flash('Obra adicionada com sucesso!', 'success')
            return redirect(url_for('visualizar_obra', id=obra_id))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar obra. Verifique os dados.', 'error')
        finally:
            conn.close()

    # LÓGICA DE VISUALIZAÇÃO (GET)
    conn = get_db_connection()
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    sistemas_protecao = conn.execute(
        'SELECT * FROM sistemas_protecao ORDER BY nome').fetchall()
    etapas = ['Orçamento', 'Projeto', 'Execução',
              'Faturamento', 'Encerramento']
    conn.close()

    return render_template('adicionar.html',
                           construtoras=construtoras,
                           sistemas_protecao=sistemas_protecao,
                           etapas=etapas)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_obra(id):
    """Página para editar uma obra existente."""
    conn = get_db_connection()

    if request.method == 'POST':
        # 1. Obter dados antigos da obra
        obra_antiga = conn.execute(
            'SELECT * FROM obras WHERE id = ?', (id,)).fetchone()
        if obra_antiga is None:
            flash('Obra não encontrada.', 'danger')
            conn.close()
            return redirect(url_for('index'))

        caminho_antigo = obra_antiga['caminho_pasta']

        # 2. Obter novos dados do formulário
        novo_nome = request.form['nome_fantasia']
        nova_construtora_id = int(request.form['construtora_id'])
        novo_cnpj = request.form.get('cnpj')
        nova_razao_social = request.form.get('razao_social')
        novo_nome_fantasia = request.form.get('nome_fantasia')
        nova_cidade = request.form.get('cidade')
        novo_estado = request.form.get('uf')
        novo_endereco = request.form.get('endereco')
        novo_numero = request.form.get('numero')
        novo_bairro = request.form.get('bairro')
        novo_cep = request.form.get('cep')

        # 3. Se o CNPJ mudou, consultar API e atualizar dados da obra
        if novo_cnpj and novo_cnpj != obra_antiga['cnpj']:
            api = EmpresaAPI()
            dados_empresa = api.get_dados_cnpj(novo_cnpj)
            if not dados_empresa.get("erro"):
                # Prioriza NOME FANTASIA, senão RAZÃO SOCIAL
                novo_nome = dados_empresa.get('nome_fantasia') or dados_empresa.get(
                    'razao_social') or novo_nome
                nova_razao_social = dados_empresa.get(
                    'razao_social', nova_razao_social)
                novo_nome_fantasia = dados_empresa.get(
                    'nome_fantasia', novo_nome_fantasia)

                # Preencher dados de endereço se não foram fornecidos
                if not novo_endereco:
                    novo_endereco = dados_empresa.get('logradouro', '')
                if not novo_numero:
                    novo_numero = dados_empresa.get('numero', '')
                if not novo_bairro:
                    novo_bairro = dados_empresa.get('bairro', '')
                if not nova_cidade:
                    nova_cidade = dados_empresa.get('municipio', '')
                if not novo_estado:
                    novo_estado = dados_empresa.get('uf', '')
                if not novo_cep:
                    novo_cep = dados_empresa.get('cep', '')

                flash('CNPJ consultado e dados da obra atualizados.', 'info')

        # 4. Gerar novo caminho da pasta
        try:
            # Buscar dados da construtora selecionada
            construtora_info = conn.execute(
                'SELECT codigo, nome FROM construtoras WHERE id = ?', (nova_construtora_id,)).fetchone()

            # Gerar novo caminho
            novo_caminho = gerar_caminho_pasta(
                construtora_codigo=construtora_info['codigo'],
                construtora_nome=construtora_info['nome'],
                cnpj=novo_cnpj,
                nome_obra=novo_nome,
                caminho_personalizado=request.form.get('caminho_personalizado')
            )

            # 5. Mover pasta se necessário
            if novo_caminho != caminho_antigo:
                # Criar diretórios se não existirem
                os.makedirs(os.path.dirname(novo_caminho), exist_ok=True)

                # Mover pasta se existir
                if os.path.exists(caminho_antigo):
                    print(
                        f"DEBUG: Movendo pasta de '{caminho_antigo}' para '{novo_caminho}'")
                    os.rename(caminho_antigo, novo_caminho)
                else:
                    print(f"DEBUG: Criando nova pasta em '{novo_caminho}'")
                    os.makedirs(novo_caminho, exist_ok=True)

        except Exception as e:
            flash(f"Erro ao processar pasta: {e}", "danger")
            novo_caminho = caminho_antigo

        # 6. Atualizar banco de dados
        try:
            conn.execute('''
                UPDATE obras SET
                    nome = ?, construtora_id = ?, cidade = ?, status = ?, responsavel = ?,
                    caminho_pasta = ?, etapa_atual = ?, anotacoes = ?, data_atualizacao = CURRENT_TIMESTAMP,
                    cnpj = ?, endereco = ?, numero = ?, bairro = ?, cep = ?, estado = ?, razao_social = ?,
                    nome_fantasia = ?
                WHERE id = ?
            ''', (
                novo_nome, nova_construtora_id, nova_cidade, request.form.get(
                    'status'), request.form.get('responsavel'),
                novo_caminho, request.form.get('etapa_atual'),
                request.form.get('anotacoes'), novo_cnpj,
                novo_endereco, novo_numero,
                novo_bairro, novo_cep,
                novo_estado, nova_razao_social, novo_nome_fantasia, id
            ))
            conn.commit()
            flash('Obra atualizada com sucesso!', 'success')
        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Erro ao atualizar banco: {e}", "danger")
        finally:
            conn.close()

        return redirect(url_for('visualizar_obra', id=id))

    else:
        # LÓGICA DE VISUALIZAÇÃO (GET)
        query = """
            SELECT o.*, c.nome as construtora_nome, c.razao_social as construtora_razao_social
            FROM obras o
            LEFT JOIN construtoras c ON o.construtora_id = c.id
            WHERE o.id = ?
        """
        obra = conn.execute(query, (id,)).fetchone()

        if obra is None:
            flash('Obra não encontrada.', 'danger')
            conn.close()
            return redirect(url_for('index'))

        construtoras_list = conn.execute(
            'SELECT * FROM construtoras ORDER BY nome').fetchall()
        etapas_era_list = get_etapas_era().keys()
        conn.close()

        return render_template('editar.html',
                               obra=obra,
                               construtoras=construtoras_list,
                               etapas_era=etapas_era_list)


@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_obra(id):
    """Excluir obra"""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM obras WHERE id = ?', (id,))
        conn.commit()
        flash('Obra excluída com sucesso!', 'success')
    except:
        flash('Erro ao excluir obra!', 'error')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/atualizar_etapa', methods=['POST'])
def atualizar_etapa():
    """Atualizar status de uma etapa ERA"""
    data = request.get_json()
    obra_id = data.get('obra_id')
    etapa = data.get('etapa')
    item = data.get('item')
    concluido = data.get('concluido')
    responsavel = data.get('responsavel')
    observacoes = data.get('observacoes')

    conn = get_db_connection()
    try:
        if concluido:
            conn.execute('''
                UPDATE etapas_era 
                SET concluido = ?, data_conclusao = CURRENT_TIMESTAMP, responsavel = ?, observacoes = ?
                WHERE obra_id = ? AND etapa = ? AND item = ?
            ''', (True, responsavel, observacoes, obra_id, etapa, item))
        else:
            conn.execute('''
                UPDATE etapas_era 
                SET concluido = ?, data_conclusao = NULL, responsavel = ?, observacoes = ?
                WHERE obra_id = ? AND etapa = ? AND item = ?
            ''', (False, responsavel, observacoes, obra_id, etapa, item))

        conn.commit()
        return jsonify({'success': True, 'message': 'Etapa atualizada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar etapa: {str(e)}'}), 500
    finally:
        conn.close()


@app.route('/atualizar_sistema', methods=['POST'])
def atualizar_sistema():
    """Atualizar status de um sistema de proteção"""
    data = request.get_json()
    obra_id = data.get('obra_id')
    sistema_id = data.get('sistema_id')
    status = data.get('status')

    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE obra_sistemas 
            SET status = ?
            WHERE obra_id = ? AND sistema_id = ?
        ''', (status, obra_id, sistema_id))

        conn.commit()
        return jsonify({'success': True, 'message': 'Sistema atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar sistema: {str(e)}'}), 500
    finally:
        conn.close()


@app.route('/abrir_pasta', methods=['POST'])
def abrir_pasta():
    """Abrir pasta da obra no sistema operacional"""
    data = request.get_json()
    caminho = data.get('caminho')
    print(f"--- DEBUG: Abrir Pasta ---")
    print(f"Caminho recebido: {caminho}")

    if not caminho:
        print("DEBUG: Caminho não fornecido.")
        return jsonify({'success': False, 'message': 'Caminho não fornecido.'}), 400

    try:
        # Normalizar o caminho para o padrão do SO
        caminho_normalizado = os.path.normpath(caminho)
        print(f"Caminho normalizado: {caminho_normalizado}")

        if not os.path.exists(caminho_normalizado):
            print(f"DEBUG: Pasta não encontrada em '{caminho_normalizado}'")
            return jsonify({'success': False, 'message': f'Pasta não encontrada: {caminho_normalizado}'}), 404

        print("DEBUG: Pasta encontrada. Executando os.startfile...")
        os.startfile(caminho_normalizado)
        print("--- DEBUG: Comando os.startfile executado com sucesso ---")
        return jsonify({'success': True, 'message': 'Pasta aberta com sucesso!'})
    except Exception as e:
        print(f"DEBUG: Erro ao abrir pasta: {e}")
        return jsonify({'success': False, 'message': f'Erro ao abrir pasta: {str(e)}'}), 500


@app.route('/construtoras')
def construtoras():
    """Página para gerenciar construtoras"""
    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form.get('nome')
        codigo = request.form.get('codigo')
        if nome and codigo:
            try:
                conn.execute(
                    'INSERT INTO construtoras (nome, codigo) VALUES (?, ?)', (nome, codigo))
                conn.commit()
                flash('Construtora adicionada com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash('Construtora já existe!', 'error')

    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    conn.close()

    return render_template('construtoras.html', construtoras=construtoras)


# --- ROTAS DO MÓDULO DE MEDIÇÕES ---

@app.route("/obra/<int:obra_id>/medicoes")
def listar_medicoes(obra_id):
    """Carrega e renderiza a lista de medições da obra."""
    conn = get_db_connection()
    obra = conn.execute(
        'SELECT o.*, c.nome as construtora_nome FROM obras o JOIN construtoras c ON o.construtora_id = c.id WHERE o.id = ?', (obra_id,)).fetchone()
    conn.close()

    if obra is None:
        flash('Obra não encontrada!', 'error')
        return redirect(url_for('index'))

    medicoes = medicao_controller.obter_medicoes_obra(obra_id)
    return render_template('medicoes/listar_medicoes.html', medicoes=medicoes, obra=obra)


@app.route("/obra/<int:obra_id>/medicoes/nova", methods=["GET", "POST"])
def nova_medicao(obra_id):
    """Formulário para registrar uma nova medição."""
    conn = get_db_connection()
    obra = conn.execute(
        'SELECT o.*, c.nome as construtora_nome FROM obras o JOIN construtoras c ON o.construtora_id = c.id WHERE o.id = ?', (obra_id,)).fetchone()
    conn.close()

    if obra is None:
        flash('Obra não encontrada!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        sucesso, mensagem = medicao_controller.processar_nova_medicao(
            obra_id=obra_id,
            valor_str=request.form.get('valor'),
            data_str=request.form.get('data'),
            nota_fiscal=request.form.get('nota_fiscal')
        )
        if sucesso:
            flash('Medição registrada com sucesso!', 'success')
            return redirect(url_for('listar_medicoes', obra_id=obra_id))
        else:
            flash(f'Erro ao registrar medição: {mensagem}', 'error')

    return render_template('medicoes/nova_medicao.html', obra=obra)


@app.route("/faturamento/mensal")
def faturamento_mensal():
    """Página de faturamento mensal"""
    conn = get_db_connection()

    # Obter dados das medições
    medicoes = conn.execute('''
        SELECT m.*, o.nome as obra_nome, o.construtora_id
        FROM medicoes m
        JOIN obras o ON m.obra_id = o.id
        ORDER BY m.data_medicao DESC
    ''').fetchall()

    # Obter construtoras
    construtoras = conn.execute(
        'SELECT * FROM construtoras ORDER BY nome').fetchall()
    conn.close()

    # Processar dados para o gráfico
    dados = {
        'medicoes': medicoes,
        'construtoras': construtoras,
        'meses': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    }

    return render_template('medicoes/resumo_mensal.html', **dados)


# --- NOVAS ROTAS DE API ---

@app.route('/api/consultar_cnpj', methods=['POST'])
def api_consultar_cnpj():
    """Endpoint da API para consultar dados de um CNPJ."""
    data = request.get_json()
    cnpj = data.get('cnpj')
    if not cnpj:
        return jsonify({"erro": "CNPJ não fornecido."}), 400

    api = EmpresaAPI()
    resultado = api.get_dados_cnpj(cnpj)
    return jsonify(resultado)


@app.route('/api/consultar_cep', methods=['POST'])
def api_consultar_cep():
    """Endpoint da API para consultar dados de um CEP."""
    data = request.get_json()
    cep = data.get('cep')
    if not cep:
        return jsonify({"erro": "CEP não fornecido."}), 400

    api = EmpresaAPI()
    resultado = api.get_endereco_cep(cep)
    return jsonify(resultado)


if __name__ == '__main__':
    # Garante que o banco de dados seja inicializado antes de rodar a app
    init_db()

    # Importação e registro do Blueprint aqui para evitar importação circular
    from controllers.cadastro_obra_controller import cadastro_obra_bp

    app.register_blueprint(cadastro_obra_bp)

    app.run(debug=True)
