# Funcionalidade de Consulta de CNPJ

## Visão Geral

O sistema agora possui integração completa com a API BrasilAPI para consulta automática de dados de empresas através do CNPJ. Quando um CNPJ é digitado no formulário, o sistema consulta automaticamente a API e preenche todos os campos relevantes.

## Como Funciona

### 1. Consulta da API
- **Endpoint**: `https://brasilapi.com.br/api/cnpj/v1/{cnpj}`
- **Trigger**: Quando o usuário sai do campo CNPJ (evento `blur`)
- **Validação**: O CNPJ deve ter exatamente 14 dígitos

### 2. Dados Retornados pela API
A API BrasilAPI retorna os seguintes dados que são utilizados pelo sistema:

```json
{
  "cnpj": "20017812000157",
  "razao_social": "BILD DESENVOLVIMENTO IMOBILIÁRIO S.A.",
  "nome_fantasia": "BILD ALLMA",
  "descricao_porte": "DEMAIS",
  "logradouro": "AVENIDA PRESIDENTE VARGAS",
  "numero": "1.357",
  "bairro": "VILA SEIXAS",
  "municipio": "Ribeirão Preto",
  "uf": "SP",
  "cep": "14056878"
}
```

### 3. Preenchimento Automático dos Campos

#### Prioridade de Preenchimento do Nome da Obra:
1. **Nome Fantasia** (prioridade máxima)
2. **Razão Social** (fallback se não houver nome fantasia)

#### Campos Preenchidos Automaticamente:
- **CNPJ**: Número do CNPJ consultado
- **Razão Social**: Nome legal da empresa
- **Nome da Obra**: Nome Fantasia (ou Razão Social como fallback)
- **Endereço**: Logradouro da empresa
- **Número**: Número do endereço
- **Bairro**: Bairro da empresa
- **Cidade**: Município da empresa
- **Estado**: UF da empresa
- **CEP**: CEP da empresa

### 4. Armazenamento no Banco de Dados

Os dados são salvos na tabela `obras` com os seguintes campos:

```sql
CREATE TABLE obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,                    -- Nome da obra (nome_fantasia ou razao_social)
    construtora_id INTEGER NOT NULL,
    cnpj TEXT,                            -- CNPJ da empresa
    razao_social TEXT,                    -- Razão social da empresa
    nome_fantasia TEXT,                   -- Nome fantasia da empresa
    cidade TEXT,                          -- Cidade da empresa
    estado TEXT,                          -- Estado da empresa
    endereco TEXT,                        -- Logradouro
    numero TEXT,                          -- Número do endereço
    bairro TEXT,                          -- Bairro
    cep TEXT,                             -- CEP
    status TEXT NOT NULL DEFAULT 'Em andamento',
    responsavel TEXT,
    caminho_pasta TEXT NOT NULL,
    etapa_atual TEXT DEFAULT 'Orçamento',
    anotacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (construtora_id) REFERENCES construtoras (id)
)
```

## Arquivos Modificados

### Backend
- `app.py`: Rotas de API e processamento de formulários
- `utils/empresa_api.py`: Classe para consulta das APIs externas
- `migrate_database.py`: Script de migração do banco de dados

### Frontend
- `static/js/auto_cadastro.js`: JavaScript para consulta automática
- `templates/adicionar.html`: Formulário de adição de obras
- `templates/editar.html`: Formulário de edição de obras

## Fluxo de Funcionamento

1. **Usuário digita CNPJ** no campo correspondente
2. **Sistema aguarda** o usuário sair do campo (evento `blur`)
3. **Validação** do CNPJ (14 dígitos)
4. **Consulta à API** BrasilAPI
5. **Processamento** dos dados retornados
6. **Preenchimento automático** dos campos do formulário
7. **Feedback visual** de sucesso para o usuário
8. **Salvamento** dos dados no banco quando o formulário for enviado

## Tratamento de Erros

- **CNPJ inválido**: Mensagem de erro se não tiver 14 dígitos
- **API indisponível**: Mensagem de erro se a API não responder
- **CNPJ não encontrado**: Mensagem de erro se o CNPJ não existir
- **Campos vazios**: Sistema usa dados fornecidos manualmente como fallback

## Exemplo de Uso

1. Acesse a página "Adicionar Obra"
2. Digite o CNPJ: `20017812000157`
3. Saia do campo CNPJ
4. Aguarde a consulta automática
5. Observe o preenchimento automático:
   - **Nome da Obra**: "BILD ALLMA" (nome fantasia)
   - **Razão Social**: "BILD DESENVOLVIMENTO IMOBILIÁRIO S.A."
   - **Endereço**: "AVENIDA PRESIDENTE VARGAS"
   - **Número**: "1.357"
   - **Bairro**: "VILA SEIXAS"
   - **Cidade**: "Ribeirão Preto"
   - **Estado**: "SP"
   - **CEP**: "14056878"

## Benefícios

- **Redução de erros**: Dados padronizados da Receita Federal
- **Agilidade**: Preenchimento automático de múltiplos campos
- **Confiabilidade**: Dados oficiais e atualizados
- **Experiência do usuário**: Interface mais fluida e intuitiva 