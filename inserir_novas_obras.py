import sqlite3
import os

# Define o caminho do banco de dados na raiz do projeto
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Lista de novas obras (nome_obra, caminho_pasta, nome_construtora)
obras_para_inserir = [
    # Obras BILD
    ("BILD ALPHA 11", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD ALPHA 11", "BILD"),
    ("BILD AV. NOSSA SENHORA DO Ó - SÃO PAULOSP",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD AV. NOSSA SENHORA DO Ó - SÃO PAULOSP", "BILD"),
    ("BILD FRANCA", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD FRANCA", "BILD"),
    ("BILD GOTIE", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD GOTIE", "BILD"),
    ("BILD LAGUNA OBRA DE SÃO PAULO",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD LAGUNA OBRA DE SÃO PAULO", "BILD"),
    ("BILD MEET", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD MEET", "BILD"),
    ("BILD NOVAM", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD NOVAM", "BILD"),
    ("BILD OBRA ATRIOS",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD OBRA ATRIOS", "BILD"),
    ("BILD OBRA CAMPINAS",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD OBRA CAMPINAS", "BILD"),
    ("BILD OBRA DE SÃO PAULO",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD OBRA DE SÃO PAULO", "BILD"),
    ("BILD OBRA TRION",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTora BILD\BILD OBRA TRION", "BILD"),
    ("BILD SÃO PAULO LAGUNA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD SÃO PAULO LAGUNA", "BILD"),
    ("BILD SSRP", r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD SSRP", "BILD"),
    ("BILD TRINITA - DAMA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD TRINITA - DAMA", "BILD"),
    ("BILD UBERABA PROJETO QUADRA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD UBERABA PROJETO QUADRA", "BILD"),
    ("BILD VITA GALASSI",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\BILD VITA GALASSI", "BILD"),
    ("26722705000106 - OLHOS D'AGUA Q5 L10 RPO DESENVOLVIMENTO IMOBILIARIO SPE LTDA - OBRA EVERO",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\26722705000106 - OLHOS D'AGUA Q5 L10 RPO DESENVOLVIMENTO IMOBILIARIO SPE LTDA - OBRA EVERO", "BILD"),
    ("40049024000150 - PIR BILD DESENVOLVIMENTO IMOBILIARIO 51 SPE LTDA - OBRA LUMIUS",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\40049024000150 - PIR BILD DESENVOLVIMENTO IMOBILIARIO 51 SPE LTDA - OBRA LUMIUS", "BILD"),
    ("42545480000116 - UBR BILD DESENVOLVIMENTO IMOBILIARIO 72 SPE LTDA. - OBRA HIALI",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\42545480000116 - UBR BILD DESENVOLVIMENTO IMOBILIARIO 72 SPE LTDA. - OBRA HIALI", "BILD"),
    ("43286494000125 - UDI BILD DESENVOLVIMENTO IMOBILIARIO 80 SPE LTDA. OBRA LUZ ALTAIMIRA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\43286494000125 - UDI BILD DESENVOLVIMENTO IMOBILIARIO 80 SPE LTDA. OBRA LUZ ALTAIMIRA", "BILD"),
    ("44918286000164 - RPO BILD DESENVOLVimento IMOBILIARIO 90 SPE LTDA - OBRA NOVVA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\44918286000164 - RPO BILD DESENVOLVIMENTO IMOBILIARIO 90 SPE LTDA - OBRA NOVVA", "BILD"),
    ("45098729000180 - UDI BILD DESENVOLVIMENTO IMOBILIARIO 88 SPE LTDA - OBRA ALLMA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\45098729000180 - UDI BILD DESENVOLVIMENTO IMOBILIARIO 88 SPE LTDA - OBRA ALLMA", "BILD"),
    ("45349540000113 - UBR BILD DESENVOLVIMENTO IMOBILIARIO 87 SPE LTDA - OBRA ARÚNA",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\45349540000113 - UBR BILD DESENVOLVIMENTO IMOBILIARIO 87 SPE LTDA - OBRA ARÚNA", "BILD"),
    ("45727197000115 - BRU BILD DESENVOLVIMENTO IMOBILIARIO 95 SPE LTDA - OBRA LAFITE",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\45727197000115 - BRU BILD DESENVOLVIMENTO IMOBILIARIO 95 SPE LTDA - OBRA LAFITE", "BILD"),
    ("46670984000119 - UDI 101 BILD DESENVOLVIMENTO IMOBILIARIO SPE LTDA - OBRA OPERA HAUS",
     r"G:\Meu Drive\000 ALTA TELAS\001 CONSTRUTORA BILD\46670984000119 - UDI 101 BILD DESENVOLVIMENTO IMOBILIARIO SPE LTDA - OBRA OPERA HAUS", "BILD"),

    # Obras PERPLAN
    ("00 PERPLAN 00", r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\00 PERPLAN 00", "PERPLAN"),
    ("41343431000138 - PERPLAN 37 EMPREENDIMENTO IMOBILIARIO SPE LTDA",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\41343431000138 - PERPLAN 37 EMPREENDIMENTO IMOBILIARIO SPE LTDA", "PERPLAN"),
    ("42786769000127 - PERPLAN 51 EMPREENDIMENTO IMOBILIARIO SPE LTDA",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\42786769000127 - PERPLAN 51 EMPREENDIMENTO IMOBILIARIO SPE LTDA", "PERPLAN"),
    ("42789236000107 - NUAGE ALTAIMIRA",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\42789236000107 - NUAGE ALTAIMIRA", "PERPLAN"),
    ("PERPLAN FLORIANO", r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN FLORIANO", "PERPLAN"),
    ("PERPLAN HYPE", r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN HYPE", "PERPLAN"),
    ("PERPLAN LIDICE", r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN LIDICE", "PERPLAN"),
    ("PERPLAN PERPLAN OBRA HORIZ FRANCA",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN PERPLAN OBRA HORIZ FRANCA", "PERPLAN"),
    ("PERPLAN PERPLAN PERPLAN 34 GRANDVERSE GARDEN EMPREENDIMENTOS IMOBILIARIOS SPE LTDA (GAVEA)",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN PERPLAN PERPLAN 34 GRANDVERSE GARDEN EMPREENDIMENTOS IMOBILIARIOS SPE LTDA (GAVEA)", "PERPLAN"),
    ("PERPLAN PERPLAN RIVERSID",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN PERPLAN RIVERSID", "PERPLAN"),
    ("PERPLAN SEIVA", r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN SEIVA", "PERPLAN"),
    ("PERPLAN UBERLANDIA OBRA CASA ALTA",
     r"G:\Meu Drive\000 ALTA TELAS\002 CONSTRUTORA PERPLAN\PERPLAN UBERLANDIA OBRA CASA ALTA", "PERPLAN"),
]


def inserir_obras():
    """
    Conecta ao banco de dados e insere novas obras a partir da lista,
    verificando duplicatas antes da inserção.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"Conectado ao banco de dados: {db_path}")

    contadores = {"BILD": 0, "PERPLAN": 0, "existentes": 0}

    for nome_obra, caminho_pasta, nome_construtora in obras_para_inserir:
        try:
            # 1. Verifica se a obra já existe (pelo nome OU caminho)
            cursor.execute(
                "SELECT 1 FROM obras WHERE nome = ? OR caminho_pasta = ?", (nome_obra, caminho_pasta))
            if cursor.fetchone():
                print(f"-> Obra já existe, pulando: '{nome_obra[:40]}...'")
                contadores["existentes"] += 1
                continue

            # 2. Busca o ID da construtora pelo nome
            cursor.execute(
                "SELECT id FROM construtoras WHERE nome = ?", (nome_construtora,))
            result = cursor.fetchone()
            if not result:
                print(
                    f"[ERRO] Construtora não encontrada: '{nome_construtora}'. Pule esta obra.")
                continue

            construtora_id = result[0]

            # 3. Insere a nova obra com os valores padrão para outras colunas
            cursor.execute(
                """
                INSERT INTO obras (nome, caminho_pasta, construtora_id, cidade, status, etapa_atual) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nome_obra, caminho_pasta, construtora_id,
                 "Não definida", "Em andamento", "Orçamento")
            )
            print(
                f"[SUCESSO] Obra inserida ({nome_construtora}): '{nome_obra[:40]}...'")
            if nome_construtora in contadores:
                contadores[nome_construtora] += 1

        except sqlite3.Error as e:
            print(
                f"[ERRO FATAL] Ocorreu um erro de banco de dados com a obra '{nome_obra}': {e}")
            conn.rollback()  # Desfaz a transação atual em caso de erro
            break

    conn.commit()
    conn.close()

    print("\n" + "="*40)
    print("      Relatório de Inserção de Obras")
    print("="*40)
    print(
        f"Total de Novas Obras Inseridas: {contadores['BILD'] + contadores['PERPLAN']}")
    print(f"  - Obras BILD Adicionadas:     {contadores['BILD']}")
    print(f"  - Obras PERPLAN Adicionadas:  {contadores['PERPLAN']}")
    print(
        f"\nTotal de Obras Já Existentes (ignoradas): {contadores['existentes']}")
    print("="*40)
    print("O banco de dados foi atualizado com sucesso.")


if __name__ == "__main__":
    inserir_obras()
