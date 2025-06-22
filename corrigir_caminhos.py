#!/usr/bin/env python3
"""
Script para corrigir todos os caminhos de pastas no banco de dados
Aplica a nova função gerar_caminho_pasta para todas as obras existentes
"""

import sqlite3
import os


def gerar_caminho_pasta(construtora_codigo, construtora_nome, cnpj, razao_social, nome_obra, caminho_personalizado=None):
    """
    Gera o caminho da pasta seguindo a estrutura:
    G:/Meu Drive/000 ALTA TELAS/{CODIGO} CONSTRUTORA {NOME_CONSTRUTORA}/{NOME_OBRA}
    """

    # Se há caminho personalizado, retorna ele diretamente
    if caminho_personalizado and caminho_personalizado.strip():
        return caminho_personalizado.strip()

    # Caminho base
    base_path = "G:/Meu Drive/000 ALTA TELAS"

    # Extrair apenas o nome da construtora (sem o código)
    nome_sem_codigo = construtora_nome
    if construtora_codigo and construtora_nome.startswith(construtora_codigo):
        nome_sem_codigo = construtora_nome[len(construtora_codigo):].strip()

    # Remover "CONSTRUTORA" se estiver no nome
    if nome_sem_codigo.upper().startswith("CONSTRUTORA "):
        nome_sem_codigo = nome_sem_codigo[12:].strip()

    # Garantir que o código tenha 3 dígitos
    codigo_formatado = construtora_codigo.zfill(
        3) if construtora_codigo else "000"

    # Criar pasta da construtora: "002 CONSTRUTORA PERPLAN"
    pasta_construtora = f"{codigo_formatado} CONSTRUTORA {nome_sem_codigo.upper()}"

    # Nome da obra em maiúsculas
    nome_obra_upper = nome_obra.upper() if nome_obra else "OBRA SEM NOME"

    # Montar caminho completo
    caminho_completo = f"{base_path}/{pasta_construtora}/{nome_obra_upper}"

    return caminho_completo


def corrigir_caminhos():
    """Corrige todos os caminhos de pastas no banco de dados"""

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    try:
        # Buscar todas as obras com dados da construtora
        obras = conn.execute('''
            SELECT o.*, c.codigo as construtora_codigo, c.nome as construtora_nome
            FROM obras o
            JOIN construtoras c ON o.construtora_id = c.id
        ''').fetchall()

        print(f"Encontradas {len(obras)} obras para corrigir...")

        for obra in obras:
            # Gerar novo caminho
            novo_caminho = gerar_caminho_pasta(
                construtora_codigo=obra['construtora_codigo'],
                construtora_nome=obra['construtora_nome'],
                cnpj=obra['cnpj'],
                razao_social=obra['razao_social'],
                nome_obra=obra['nome']
            )

            caminho_antigo = obra['caminho_pasta']

            print(f"\nObra: {obra['nome']}")
            print(f"Caminho antigo: {caminho_antigo}")
            print(f"Caminho novo: {novo_caminho}")

            # Atualizar no banco de dados
            conn.execute('''
                UPDATE obras 
                SET caminho_pasta = ? 
                WHERE id = ?
            ''', (novo_caminho, obra['id']))

            # Tentar mover a pasta se ela existir
            if os.path.exists(caminho_antigo) and caminho_antigo != novo_caminho:
                try:
                    # Criar diretório de destino se não existir
                    os.makedirs(os.path.dirname(novo_caminho), exist_ok=True)

                    # Mover a pasta
                    os.rename(caminho_antigo, novo_caminho)
                    print(f"✅ Pasta movida com sucesso!")
                except Exception as e:
                    print(f"⚠️ Erro ao mover pasta: {e}")
            elif not os.path.exists(caminho_antigo):
                try:
                    # Criar nova pasta se não existir
                    os.makedirs(novo_caminho, exist_ok=True)
                    print(f"✅ Nova pasta criada!")
                except Exception as e:
                    print(f"⚠️ Erro ao criar pasta: {e}")
            else:
                print(f"ℹ️ Pasta já está no local correto")

        # Commit das mudanças
        conn.commit()
        print(
            f"\n✅ Todas as {len(obras)} obras foram atualizadas no banco de dados!")

    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("🔧 Iniciando correção de caminhos de pastas...")
    corrigir_caminhos()
    print("✅ Processo concluído!")
