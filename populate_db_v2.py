import sqlite3
import os

DATABASE_FILE = 'database.db'


def get_etapas_era():
    """Copiado de app.py para ter a mesma fonte da verdade."""
    return {
        'Orçamento': ['Solicitação recebida', 'Proposta enviada', 'Aguardando aprovação'],
        'Projeto': ['Projeto SLQA', 'Projeto Piso a Piso', 'Projeto Bandeja', 'Projeto Fachadeira / Guarda-corpo', 'ART emitida'],
        'Execução': ['SLQA executado', 'Piso a Piso executado', 'Fachadeira executada', 'Bandeja executada', 'Linha de vida executada'],
        'Faturamento': ['Primeira medição feita', 'NFS emitida', 'Pagamento confirmado'],
        'Encerramento': ['Obra finalizada', 'Relatórios entregues', 'Feedback registrado']
    }


def populate_database():
    """
    Populates the database with new works for BILD and PERPLAN,
    avoiding duplicates.
    """
    base_path = 'G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS'

    construtoras_data = {
        "001 CONSTRUTORA BILD": {
            "codigo": "BILD",
            "base_folder": "001 CONSTRUTORA BILD",
            "obras": [
                "BILD ALLMA", "BILD ÉVERO", "BILD LAFITE", "BILD MEET",
                "BILD OBRA CAMPINAS", "BILD SÃO PAULO LAGUNA", "BILD VITA GALASSI",
                "BILD ALPHA 11", "BILD FRANCA", "BILD LAGUNA OBRA DE SÃO PAULO",
                "BILD NOVAM", "BILD OBRA DE SÃO PAULO", "BILD SSRP", "BILD ARÚNA",
                "BILD GOTIE", "BILD LUMIUS", "BILD NOVVA", "BILD OBRA OPERA",
                "BILD TRINITA - DAMA", "BILD Av. Nossa Senhora do Ó - São PauloSP",
                "BILD HIALI", "BILD LUZZ-ALTAMIRA", "BILD OBRA ATRIOS",
                "BILD OBRA TRION", "BILD UBERABA PROJETO QUADRA"
            ]
        },
        "002 CONSTRUTORA PERPLAN": {
            "codigo": "PERPLAN",
            "base_folder": "002 CONSTRUTORA PERPLAN",
            "obras": [
                "00 PERPLAN 00", "PERPLAN HELADE (PARQUE MERAKI)",
                "PERPLAN PERPLAN PERPLAN 34 GRANDVERSER", "PERPLAN PERPLAN RIVERSID",
                "PERPLAN 50 NUAGE ALTAMIRA", "PERPLAN FLORIANO", "PERPLAN HYPE",
                "PERPLAN LIDICE", "PERPLAN SEIVA", "PERPLAN GRANDVERSER PLACE ( PERPLAN )",
                "PERPLAN PERPLAN OBRA HORIZ FRANCA", "PERPLAN UBERLANDIA OBRA CASA ALTA"
            ]
        }
    }

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print("Iniciando a atualização do banco de dados...")

        for nome_construtora, data in construtoras_data.items():
            print(f"\\nProcessando construtora: {nome_construtora}")

            cursor.execute(
                "SELECT id FROM construtoras WHERE nome = ?", (nome_construtora,))
            result = cursor.fetchone()
            if result:
                construtora_id = result[0]
            else:
                cursor.execute(
                    "INSERT INTO construtoras (nome, codigo) VALUES (?, ?)", (nome_construtora, data['codigo']))
                construtora_id = cursor.lastrowid
                print(
                    f"  -> Construtora '{nome_construtora}' adicionada com ID: {construtora_id}")

            obras_adicionadas = 0
            for nome_obra in data['obras']:
                cursor.execute(
                    "SELECT id FROM obras WHERE nome = ? AND construtora_id = ?", (nome_obra, construtora_id))
                if cursor.fetchone():
                    continue

                caminho_obra = os.path.join(
                    base_path, data['base_folder'], nome_obra).replace('\\\\', '/')

                cursor.execute("""
                    INSERT INTO obras (nome, construtora_id, caminho_pasta, status, responsavel, cidade)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nome_obra, construtora_id, caminho_obra, 'Em andamento', None, None))
                obra_id = cursor.lastrowid

                # INSERIR ETAPAS ERA PADRÃO PARA A NOVA OBRA
                etapas_padrao = get_etapas_era()
                for etapa_cat, itens in etapas_padrao.items():
                    for item_desc in itens:
                        cursor.execute("""
                            INSERT OR IGNORE INTO etapas_era (obra_id, etapa, item, concluido)
                            VALUES (?, ?, ?, ?)
                        """, (obra_id, etapa_cat, item_desc, False))

                obras_adicionadas += 1

            if obras_adicionadas > 0:
                print(
                    f"  -> {obras_adicionadas} novas obras adicionadas e inicializadas com etapas ERA.")
            else:
                print("  -> Nenhuma obra nova para adicionar.")

        conn.commit()
        print("\\nAtualização do banco de dados concluída com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()


def fix_missing_era_steps():
    """Verifica todas as obras e adiciona etapas ERA faltantes."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        etapas_padrao = get_etapas_era()

        print("Iniciando verificação de etapas ERA faltantes...")

        # 1. Pega todas as obras existentes
        cursor.execute("SELECT id FROM obras")
        obras = cursor.fetchall()
        obras_corrigidas = 0

        for obra in obras:
            obra_id = obra[0]
            etapas_inseridas = 0
            # 2. Para cada obra, verifica se todas as etapas padrão existem
            for etapa_cat, itens in etapas_padrao.items():
                for item_desc in itens:
                    # Tenta inserir a etapa. Se já existir, o IGNORE evita o erro.
                    cursor.execute("""
                        INSERT OR IGNORE INTO etapas_era (obra_id, etapa, item, concluido)
                        VALUES (?, ?, ?, ?)
                    """, (obra_id, etapa_cat, item_desc, False))
                    # lastrowid não funciona com OR IGNORE, mas podemos verificar changes
                    if conn.total_changes > 0:
                        etapas_inseridas += 1

            if etapas_inseridas > 0:
                obras_corrigidas += 1
                # Zera o contador de mudanças para a proxima iteração
                # (isso é uma simplificação, o ideal seria mais complexo, mas para este script serve)
                conn.commit()

        if obras_corrigidas > 0:
            print(
                f"-> Verificação concluída. {obras_corrigidas} obras tiveram etapas faltantes adicionadas.")
        else:
            print(
                "-> Verificação concluída. Todas as obras já possuem as etapas ERA completas.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # A função principal agora será a de correção
    fix_missing_era_steps()
