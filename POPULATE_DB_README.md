# 📊 Script de População do Banco de Dados

## 🎯 Objetivo

O script `populate_db.py` foi criado para popular automaticamente o banco de dados do Sistema de Obras com todas as obras das construtoras BILD e PERPLAN.

## 🚀 Como Usar

### Execução Simples
```bash
python populate_db.py
```

### O que o script faz:
1. ✅ Remove o banco existente (se houver)
2. ✅ Cria as tabelas `construtoras` e `obras`
3. ✅ Insere 2 construtoras
4. ✅ Insere 37 obras (25 BILD + 12 PERPLAN)
5. ✅ Verifica e exibe estatísticas
6. ✅ Confirma sucesso da operação

## 📋 Dados Inseridos

### 🏢 Construtoras
1. **001 CONSTRUTORA BILD** (ID: 1)
2. **002 CONSTRUTORA PERPLAN** (ID: 2)

### 🏗️ Obras BILD (25 obras)
- BILD ALLMA
- BILD ÉVERO
- BILD LAFITE
- BILD MEET
- BILD OBRA CAMPINAS
- BILD SÃO PAULO LAGUNA
- BILD VITA GALASSI
- BILD ALPHA 11
- BILD FRANCA
- BILD LAGUNA OBRA DE SÃO PAULO
- BILD NOVAM
- BILD OBRA DE SÃO PAULO
- BILD SSRP
- BILD ARÚNA
- BILD GOTIE
- BILD LUMIUS
- BILD NOVVA
- BILD OBRA OPERA
- BILD TRINITA - DAMA
- BILD Av. Nossa Senhora do Ó - São PauloSP
- BILD HIALI
- BILD LUZZ-ALTAMIRA
- BILD OBRA ATRIOS
- BILD OBRA TRION
- BILD UBERABA PROJETO QUADRA

### 🏗️ Obras PERPLAN (12 obras)
- 00 PERPLAN 00
- PERPLAN 50 NUAGE ALTAMIRA
- PERPLAN FLORIANO
- PERPLAN HELADE (PARQUE MERAKI)
- PERPLAN HYPE
- PERPLAN LIDICE
- PERPLAN SEIVA
- PERPLAN GRANDVERSER PLACE ( PERPLAN )
- PERPLAN PERPLAN OBRA HORIZ FRANCA
- PERPLAN PERPLAN PERPLAN 34 GRANDVERS...
- PERPLAN PERPLAN RIVERSID
- PERPLAN UBERLANDIA OBRA CASA ALTA

## 📁 Estrutura dos Caminhos

### Caminhos BILD
```
G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/001 CONSTRUTORA BILD/[NOME_OBRA]
```

### Caminhos PERPLAN
```
G:/Meu Drive/000 ALTA TELAS/CONSTRUTORA EMP ALTA TELAS/002 CONSTRUTORA PERPLAN/[NOME_OBRA]
```

## 🔧 Configurações dos Dados

### Campos das Obras:
- **nome**: Nome completo da obra
- **construtora_id**: ID da construtora (1 = BILD, 2 = PERPLAN)
- **cidade**: `None` (pode ser preenchido posteriormente)
- **status**: `'Em andamento'` (padrão)
- **responsavel**: `None` (pode ser preenchido posteriormente)
- **caminho_pasta**: Caminho completo da pasta no Google Drive (Drive G:)

## 📊 Saída do Script

Ao executar o script, você verá:

```
🚀 Iniciando população do banco de dados...
==================================================
Removendo banco existente: database.db
Criando tabela construtoras...
Criando tabela obras...
Inserindo construtoras...
Inserindo obras da CONSTRUTORA BILD...
Inserindo obras da CONSTRUTORA PERPLAN...
✅ Construtoras inseridas: 2
✅ Obras inseridas: 37

📊 Estatísticas por construtora:
   • 001 CONSTRUTORA BILD: 25 obras
   • 002 CONSTRUTORA PERPLAN: 12 obras

🎉 Banco de dados populado com sucesso!
📁 Banco de dados salvo em: database.db

==================================================
🔍 Verificando dados inseridos...

📋 Tabelas criadas: ['construtoras', 'obras', 'sqlite_sequence']

🏢 Construtoras:
   ID 1: 001 CONSTRUTORA BILD
   ID 2: 002 CONSTRUTORA PERPLAN

🏗️ Primeiras 5 obras:
   • BILD ALLMA (001 CONSTRUTORA BILD)
   • BILD ÉVERO (001 CONSTRUTORA BILD)
   • BILD LAFITE (001 CONSTRUTORA BILD)
   • BILD MEET (001 CONSTRUTORA BILD)
   • BILD OBRA CAMPINAS (001 CONSTRUTORA BILD)

✅ Script executado com sucesso!
🌐 Agora você pode executar: python app.py
```

## 🔄 Reexecução

Para reexecutar o script e recriar o banco:

```bash
python populate_db.py
```

O script automaticamente:
- Remove o banco existente
- Cria um novo banco limpo
- Insere todos os dados novamente

## 🛠️ Funções do Script

### `criar_e_popular_banco()`
- Função principal que executa toda a lógica
- Pode ser importada e chamada de outros scripts

### `verificar_banco()`
- Verifica se os dados foram inseridos corretamente
- Exibe estatísticas e amostras dos dados

## ⚠️ Importante

- O script usa `sqlite3` nativo (sem SQLAlchemy)
- Usa `executemany()` para inserção eficiente
- Inclui tratamento de erros completo
- Remove o banco existente antes de criar um novo
- Todos os caminhos seguem o padrão do Google Drive (Drive G:)
- **Obras separadas por construtora** para melhor organização

## 🎉 Resultado

Após executar o script:
- Banco `database.db` criado e populado
- 37 obras disponíveis no sistema
- Sistema Flask pronto para uso
- Acesse: http://localhost:5000

---

**✅ Script testado e funcionando perfeitamente!** 