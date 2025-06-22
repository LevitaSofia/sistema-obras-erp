#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar e popular o banco de dados com dados de exemplo
Sistema de Gerenciamento de Obras de Construção
"""

import sqlite3
import os
from datetime import datetime


def criar_tabelas(cursor):
    """Cria as tabelas do banco de dados"""

    # Tabela de construtoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS construtoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de obras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            construtora_id INTEGER NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT,
            endereco TEXT,
            responsavel TEXT,
            telefone_responsavel TEXT,
            email_responsavel TEXT,
            data_inicio DATE,
            data_prevista_fim DATE,
            status TEXT DEFAULT 'Em andamento',
            caminho_pasta TEXT,
            observacoes TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (construtora_id) REFERENCES construtoras (id)
        )
    ''')

    print("✅ Tabelas criadas com sucesso!")


def inserir_construtoras(cursor):
    """Insere as construtoras de exemplo"""

    construtoras = [
        ('Construtora ABC Ltda', '12.345.678/0001-90', '(11) 9999-8888',
         'contato@abc.com.br', 'Rua das Construções, 123 - São Paulo/SP'),
        ('Empresa XYZ Construções', '98.765.432/0001-10', '(21) 8888-7777',
         'contato@xyz.com.br', 'Av. das Obras, 456 - Rio de Janeiro/RJ')
    ]

    cursor.executemany('''
        INSERT INTO construtoras (nome, cnpj, telefone, email, endereco)
        VALUES (?, ?, ?, ?, ?)
    ''', construtoras)

    print(f"✅ {len(construtoras)} construtoras inseridas!")


def inserir_obras(cursor):
    """Insere as obras de exemplo com a estrutura de pastas correta"""

    # Base path correto
    base_path = r"G:\Meu Drive\000 ALTA TELAS\01 PROJETOS EMRESA"

    obras = [
        # Construtora ABC Ltda (ID 1)
        ('Residencial Solar', 1, 'São Paulo', 'SP', 'Rua das Flores, 100', 'João Silva', '(11) 9999-1111',
         'joao@abc.com.br', '2024-01-15', '2024-12-31', 'Em andamento', f'{base_path}\\ABC\\Residencial Solar'),
        ('Shopping Center Plaza', 1, 'São Paulo', 'SP', 'Av. Paulista, 1000', 'Maria Santos', '(11) 9999-2222',
         'maria@abc.com.br', '2024-02-01', '2025-06-30', 'Em andamento', f'{base_path}\\ABC\\Shopping Center Plaza'),
        ('Condomínio Verde', 1, 'Campinas', 'SP', 'Rua das Palmeiras, 200', 'Pedro Costa', '(19) 9999-3333',
         'pedro@abc.com.br', '2024-03-10', '2025-03-10', 'Em andamento', f'{base_path}\\ABC\\Condomínio Verde'),
        ('Hospital Municipal', 1, 'Santos', 'SP', 'Av. da Saúde, 500', 'Ana Oliveira', '(13) 9999-4444',
         'ana@abc.com.br', '2024-01-20', '2025-01-20', 'Em andamento', f'{base_path}\\ABC\\Hospital Municipal'),
        ('Escola Técnica', 1, 'Ribeirão Preto', 'SP', 'Rua da Educação, 300', 'Carlos Lima', '(16) 9999-5555',
         'carlos@abc.com.br', '2024-02-15', '2024-11-15', 'Em andamento', f'{base_path}\\ABC\\Escola Técnica'),
        ('Residencial Horizonte', 1, 'São Paulo', 'SP', 'Rua do Horizonte, 150', 'Lucia Ferreira', '(11) 9999-6666',
         'lucia@abc.com.br', '2024-04-01', '2025-04-01', 'Em andamento', f'{base_path}\\ABC\\Residencial Horizonte'),
        ('Centro Comercial Norte', 1, 'São Paulo', 'SP', 'Av. Santana, 800', 'Roberto Alves', '(11) 9999-7777',
         'roberto@abc.com.br', '2024-03-01', '2025-03-01', 'Em andamento', f'{base_path}\\ABC\\Centro Comercial Norte'),
        ('Condomínio Luxo', 1, 'São Paulo', 'SP', 'Rua Oscar Freire, 1000', 'Fernanda Rocha', '(11) 9999-8888',
         'fernanda@abc.com.br', '2024-05-01', '2025-05-01', 'Em andamento', f'{base_path}\\ABC\\Condomínio Luxo'),
        ('Prédio Corporativo', 1, 'São Paulo', 'SP', 'Av. Brigadeiro Faria Lima, 2000', 'Ricardo Mendes', '(11) 9999-9999',
         'ricardo@abc.com.br', '2024-06-01', '2025-06-01', 'Em andamento', f'{base_path}\\ABC\\Prédio Corporativo'),
        ('Residencial Parque', 1, 'São Paulo', 'SP', 'Rua do Parque, 400', 'Sandra Costa', '(11) 9999-0000',
         'sandra@abc.com.br', '2024-07-01', '2025-07-01', 'Em andamento', f'{base_path}\\ABC\\Residencial Parque'),
        ('Shopping Sul', 1, 'São Paulo', 'SP', 'Av. Santo Amaro, 1500', 'Marcelo Silva', '(11) 9999-1111',
         'marcelo@abc.com.br', '2024-08-01', '2025-08-01', 'Em andamento', f'{base_path}\\ABC\\Shopping Sul'),
        ('Hospital Privado', 1, 'São Paulo', 'SP', 'Av. Morumbi, 3000', 'Patricia Lima', '(11) 9999-2222',
         'patricia@abc.com.br', '2024-09-01', '2025-09-01', 'Em andamento', f'{base_path}\\ABC\\Hospital Privado'),
        ('Escola Internacional', 1, 'São Paulo', 'SP', 'Rua das Nações, 600', 'Daniel Santos', '(11) 9999-3333',
         'daniel@abc.com.br', '2024-10-01', '2025-10-01', 'Em andamento', f'{base_path}\\ABC\\Escola Internacional'),
        ('Residencial Mar', 1, 'Santos', 'SP', 'Av. da Praia, 700', 'Camila Alves', '(13) 9999-4444',
         'camila@abc.com.br', '2024-11-01', '2025-11-01', 'Em andamento', f'{base_path}\\ABC\\Residencial Mar'),
        ('Centro Empresarial', 1, 'São Paulo', 'SP', 'Av. Engenheiro Caetano Álvares, 1000', 'Thiago Rocha', '(11) 9999-5555',
         'thiago@abc.com.br', '2024-12-01', '2025-12-01', 'Em andamento', f'{base_path}\\ABC\\Centro Empresarial'),
        ('Condomínio Família', 1, 'São Paulo', 'SP', 'Rua da Família, 250', 'Juliana Mendes', '(11) 9999-6666',
         'juliana@abc.com.br', '2025-01-01', '2026-01-01', 'Em andamento', f'{base_path}\\ABC\\Condomínio Família'),
        ('Hotel Executivo', 1, 'São Paulo', 'SP', 'Av. São João, 1200', 'Andre Costa', '(11) 9999-7777',
         'andre@abc.com.br', '2025-02-01', '2026-02-01', 'Em andamento', f'{base_path}\\ABC\\Hotel Executivo'),
        ('Residencial Vista', 1, 'São Paulo', 'SP', 'Rua da Vista, 350', 'Vanessa Silva', '(11) 9999-8888',
         'vanessa@abc.com.br', '2025-03-01', '2026-03-01', 'Em andamento', f'{base_path}\\ABC\\Residencial Vista'),
        ('Shopping Leste', 1, 'São Paulo', 'SP', 'Av. Radial Leste, 2000', 'Felipe Lima', '(11) 9999-9999',
         'felipe@abc.com.br', '2025-04-01', '2026-04-01', 'Em andamento', f'{base_path}\\ABC\\Shopping Leste'),
        ('Hospital Especializado', 1, 'São Paulo', 'SP', 'Av. Jabaquara, 1500', 'Gabriela Santos', '(11) 9999-0000',
         'gabriela@abc.com.br', '2025-05-01', '2026-05-01', 'Em andamento', f'{base_path}\\ABC\\Hospital Especializado'),

        # Empresa XYZ Construções (ID 2)
        ('Residencial Copacabana', 2, 'Rio de Janeiro', 'RJ', 'Av. Atlântica, 1000', 'Roberto Silva', '(21) 8888-1111',
         'roberto@xyz.com.br', '2024-01-10', '2024-12-10', 'Em andamento', f'{base_path}\\XYZ\\Residencial Copacabana'),
        ('Shopping Leblon', 2, 'Rio de Janeiro', 'RJ', 'Av. Ataulfo de Paiva, 500', 'Carla Santos', '(21) 8888-2222',
         'carla@xyz.com.br', '2024-02-05', '2025-02-05', 'Em andamento', f'{base_path}\\XYZ\\Shopping Leblon'),
        ('Condomínio Ipanema', 2, 'Rio de Janeiro', 'RJ', 'Rua Visconde de Pirajá, 800', 'Marcos Costa', '(21) 8888-3333',
         'marcos@xyz.com.br', '2024-03-15', '2025-03-15', 'Em andamento', f'{base_path}\\XYZ\\Condomínio Ipanema'),
        ('Hotel Luxo', 2, 'Rio de Janeiro', 'RJ', 'Av. Vieira Souto, 200', 'Fernanda Lima', '(21) 8888-4444',
         'fernanda@xyz.com.br', '2024-04-01', '2025-04-01', 'Em andamento', f'{base_path}\\XYZ\\Hotel Luxo'),
        ('Centro Empresarial Barra', 2, 'Rio de Janeiro', 'RJ', 'Av. das Américas, 3000', 'Ricardo Alves', '(21) 8888-5555',
         'ricardo@xyz.com.br', '2024-05-10', '2025-05-10', 'Em andamento', f'{base_path}\\XYZ\\Centro Empresarial Barra'),
        ('Residencial Botafogo', 2, 'Rio de Janeiro', 'RJ', 'Rua Voluntários da Pátria, 600', 'Patricia Rocha', '(21) 8888-6666',
         'patricia@xyz.com.br', '2024-06-01', '2025-06-01', 'Em andamento', f'{base_path}\\XYZ\\Residencial Botafogo'),
        ('Shopping Tijuca', 2, 'Rio de Janeiro', 'RJ', 'Av. Maracanã, 1000', 'Thiago Mendes', '(21) 8888-7777',
         'thiago@xyz.com.br', '2024-07-15', '2025-07-15', 'Em andamento', f'{base_path}\\XYZ\\Shopping Tijuca'),
        ('Hospital Sul', 2, 'Rio de Janeiro', 'RJ', 'Av. das Américas, 5000', 'Juliana Costa', '(21) 8888-8888',
         'juliana@xyz.com.br', '2024-08-01', '2025-08-01', 'Em andamento', f'{base_path}\\XYZ\\Hospital Sul'),
        ('Escola Particular', 2, 'Rio de Janeiro', 'RJ', 'Rua das Laranjeiras, 400', 'Andre Silva', '(21) 8888-9999',
         'andre@xyz.com.br', '2024-09-10', '2025-09-10', 'Em andamento', f'{base_path}\\XYZ\\Escola Particular'),
        ('Condomínio Flamengo', 2, 'Rio de Janeiro', 'RJ', 'Av. Rui Barbosa, 700', 'Vanessa Lima', '(21) 8888-0000',
         'vanessa@xyz.com.br', '2024-10-01', '2025-10-01', 'Em andamento', f'{base_path}\\XYZ\\Condomínio Flamengo'),
        ('Residencial Lagoa', 2, 'Rio de Janeiro', 'RJ', 'Av. Epitácio Pessoa, 900', 'Felipe Santos', '(21) 8888-1111',
         'felipe@xyz.com.br', '2024-11-15', '2025-11-15', 'Em andamento', f'{base_path}\\XYZ\\Residencial Lagoa'),
        ('Shopping Norte', 2, 'Rio de Janeiro', 'RJ', 'Av. Dom Helder Câmara, 2000', 'Gabriela Alves', '(21) 8888-2222',
         'gabriela@xyz.com.br', '2024-12-01', '2025-12-01', 'Em andamento', f'{base_path}\\XYZ\\Shopping Norte'),
        ('Hotel Executivo Centro', 2, 'Rio de Janeiro', 'RJ', 'Rua do Ouvidor, 300', 'Carlos Rocha', '(21) 8888-3333',
         'carlos@xyz.com.br', '2025-01-01', '2026-01-01', 'Em andamento', f'{base_path}\\XYZ\\Hotel Executivo Centro'),
        ('Centro Médico', 2, 'Rio de Janeiro', 'RJ', 'Av. Nilo Peçanha, 800', 'Lucia Mendes', '(21) 8888-4444',
         'lucia@xyz.com.br', '2025-02-01', '2026-02-01', 'Em andamento', f'{base_path}\\XYZ\\Centro Médico'),
        ('Residencial Centro', 2, 'Rio de Janeiro', 'RJ', 'Rua da Carioca, 500', 'Roberto Costa', '(21) 8888-5555',
         'roberto@xyz.com.br', '2025-03-01', '2026-03-01', 'Em andamento', f'{base_path}\\XYZ\\Residencial Centro'),
        ('Shopping Oeste', 2, 'Rio de Janeiro', 'RJ', 'Av. das Américas, 7000', 'Carla Silva', '(21) 8888-6666',
         'carla@xyz.com.br', '2025-04-01', '2026-04-01', 'Em andamento', f'{base_path}\\XYZ\\Shopping Oeste'),
        ('Condomínio Praia', 2, 'Rio de Janeiro', 'RJ', 'Av. Atlântica, 2000', 'Marcos Lima', '(21) 8888-7777',
         'marcos@xyz.com.br', '2025-05-01', '2026-05-01', 'Em andamento', f'{base_path}\\XYZ\\Condomínio Praia'),
        ('Hotel Resort', 2, 'Rio de Janeiro', 'RJ', 'Av. Sernambetiba, 3000', 'Fernanda Santos', '(21) 8888-8888',
         'fernanda@xyz.com.br', '2025-06-01', '2026-06-01', 'Em andamento', f'{base_path}\\XYZ\\Hotel Resort'),
        ('Residencial Montanha', 2, 'Rio de Janeiro', 'RJ', 'Rua das Paineiras, 400', 'Ricardo Alves', '(21) 8888-9999',
         'ricardo@xyz.com.br', '2025-07-01', '2026-07-01', 'Em andamento', f'{base_path}\\XYZ\\Residencial Montanha')
    ]

    cursor.executemany('''
        INSERT INTO obras (nome, construtora_id, cidade, estado, endereco, responsavel, 
                          telefone_responsavel, email_responsavel, data_inicio, data_prevista_fim, 
                          status, caminho_pasta)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', obras)

    print(f"✅ {len(obras)} obras inseridas!")
    print(f"📁 Estrutura base: {base_path}")


def verificar_dados(cursor):
    """Verifica se os dados foram inseridos corretamente"""

    # Contar construtoras
    cursor.execute('SELECT COUNT(*) FROM construtoras')
    num_construtoras = cursor.fetchone()[0]

    # Contar obras
    cursor.execute('SELECT COUNT(*) FROM obras')
    num_obras = cursor.fetchone()[0]

    # Mostrar algumas obras de exemplo
    cursor.execute('''
        SELECT o.nome, c.nome as construtora, o.cidade, o.caminho_pasta 
        FROM obras o 
        JOIN construtoras c ON o.construtora_id = c.id 
        LIMIT 5
    ''')
    obras_exemplo = cursor.fetchall()

    print(f"\n📊 Verificação dos dados:")
    print(f"   • Construtoras: {num_construtoras}")
    print(f"   • Obras: {num_obras}")
    print(f"\n📋 Exemplos de obras criadas:")

    for obra in obras_exemplo:
        print(f"   • {obra[0]} ({obra[1]}) - {obra[2]}")
        print(f"     📁 {obra[3]}")


def main():
    """Função principal"""

    print("🏗️  Sistema de Gerenciamento de Obras")
    print("=" * 50)

    # Conectar ao banco de dados
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        print("📦 Criando tabelas...")
        criar_tabelas(cursor)

        print("\n🏢 Inserindo construtoras...")
        inserir_construtoras(cursor)

        print("\n🏗️  Inserindo obras...")
        inserir_obras(cursor)

        print("\n✅ Verificando dados...")
        verificar_dados(cursor)

        # Commit das alterações
        conn.commit()

        print(f"\n🎉 Banco de dados criado com sucesso!")
        print(f"📁 Arquivo: database.db")
        print(f"🌐 Execute 'python app.py' para iniciar o sistema web")

    except sqlite3.Error as e:
        print(f"❌ Erro no banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
