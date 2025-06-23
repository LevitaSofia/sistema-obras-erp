# Documentação Técnica - Sistema de Gestão de Obras

**Data de Geração:** 22/06/2025 14:35

## 1. Visão Geral

Este documento detalha a arquitetura e os componentes do Sistema de Gestão de Obras, uma aplicação web desenvolvida com Flask para o backend e Bootstrap para o frontend. O sistema permite o cadastro, visualização, edição e filtragem de obras e construtoras, além de funcionalidades como consulta de CNPJ e abertura de pastas locais.

A aplicação segue uma estrutura modular, utilizando Blueprints do Flask para organizar as rotas e controladores, e um padrão de modelo de dados (Model) para interagir com o banco de dados SQLite.

## 2. Estrutura do Projeto

```
/
|-- app.py                    # Ponto de entrada principal da aplicação Flask
|-- database.db               # Arquivo do banco de dados SQLite
|-- database.py               # Módulo para gerenciamento da conexão com o BD
|-- requirements.txt          # Dependências do projeto Python
|-- run.bat / run.sh          # Scripts para iniciar a aplicação
|-- DOCUMENTACAO_PROJETO.md   # Este arquivo
|
|-- controllers/              # Blueprints e lógica das rotas (Controladores)
|   |-- cadastro_obra_controller.py
|
|-- database/                 # Scripts SQL para inicialização
|   |-- init_medicoes.sql
|
|-- models/                   # Classes que representam os dados (Modelos)
|   |-- obra_model.py
|
|-- modules/                  # Módulos de funcionalidades específicas (Blueprints)
|   |-- orcamento/
|   |-- medicoes/
|
|-- routes/                   # Definições de rotas (Blueprints mais antigos)
|   |-- medicoes.py
|
|-- static/                   # Arquivos estáticos (CSS, JavaScript, Imagens)
|   |-- js/
|   |   |-- auto_cadastro.js
|   |-- style.css
|
|-- templates/                # Arquivos de template HTML (Jinja2)
|   |-- base.html             # Template base para todas as páginas
|   |-- index.html            # Dashboard principal com lista de obras
|   |-- cadastrar_obra.html   # Formulário para nova obra
|   |-- editar.html           # Formulário para edição de obra
|   |-- visualizar_obra.html  # Detalhes de uma obra
|   |-- construtoras.html     # Gerenciamento de construtoras
|   |-- ...
```

## 3. Backend (Flask)

### 3.1. `app.py`
É o coração da aplicação. Suas responsabilidades incluem:
-   **Inicialização do Flask:** Cria a instância da aplicação.
-   **Configuração:** Define a chave secreta (`secret_key`).
-   **Inicialização do Banco de Dados (`init_db`)**: Função crucial que verifica a existência das tabelas (`obras`, `construtoras`, etc.) e colunas necessárias a cada inicialização, adicionando colunas faltantes (`ALTER TABLE`). Atua como um sistema de migração simples.
-   **Registro de Blueprints:** Importa e registra os módulos de rotas (`medicoes_bp`, `cadastro_obra_bp`, `orcamento_bp`).
-   **Filtros Jinja Customizados:** Define e registra o filtro `format_date` para formatar datas nos templates.
-   **Rotas Principais:**
    -   `@app.route('/')`: Rota do dashboard principal. Processa os filtros (construtora, busca, etc.), busca os dados filtrados através de `Obra.find_by_filters()` e renderiza `index.html`.
    -   `@app.route('/obra/<int:id>')`: Exibe a página de detalhes de uma obra.
    -   `@app.route('/editar_obra/<int:id>')`: Exibe e processa o formulário de edição de uma obra.
    -   `@app.route('/construtoras', methods=['GET', 'POST'])`: Gerencia o cadastro e listagem de construtoras.
    -   `@app.route('/abrir_pasta', methods=['POST'])`: Endpoint que recebe um caminho de pasta via POST e utiliza `os.startfile()` para abri-lo no sistema (Windows).

### 3.2. `database.py`
-   **`get_db_connection()`**: Função centralizadora que cria e retorna uma conexão com o banco de dados SQLite (`database.db`). Configura o `row_factory` para `sqlite3.Row`, o que permite acessar os resultados das consultas como dicionários (ex: `row['coluna']`).

### 3.3. Modelos (`models/`)
-   **`models/obra_model.py`**:
    -   **Classe `Obra`**: Representa uma obra no sistema. O construtor (`__init__`) aceita `**kwargs` para mapear dinamicamente as colunas do banco de dados para os atributos do objeto.
    -   **`find_by_id(id)`**: Busca uma obra pelo seu ID.
    -   **`find_all()`**: Busca todas as obras.
    -   **`find_by_filters(filters)`**: Método estático que constrói uma consulta SQL dinâmica com base nos filtros fornecidos (construtora, busca, etapa), permitindo a filtragem no dashboard.
    -   **`update(dados)`**: Atualiza os dados de uma obra no banco de dados.

### 3.4. Controladores (`controllers/`)
-   **`controllers/cadastro_obra_controller.py`**:
    -   Define um **Blueprint** (`cadastro_obra_bp`) para agrupar as rotas relacionadas ao cadastro de obras.
    -   **`/cadastrar_obra`**: Rota para adicionar uma nova obra.
    -   **`/api/consultar_cnpj`**: Endpoint que recebe um CNPJ, consulta uma API externa (`https://www.receitaws.com.br`) e retorna os dados da empresa em formato JSON.

## 4. Frontend (Templates e Arquivos Estáticos)

### 4.1. Templates (`templates/`)
-   **`base.html`**: Estrutura HTML principal que é estendida por todos os outros templates. Inclui a navbar, o rodapé, e a importação de arquivos CSS e JS globais. Contém a lógica de exibição de mensagens "flash".
-   **`index.html`**: A página mais complexa.
    -   **Formulário de Filtros**: Envia os dados via `GET` para a própria rota `/`, recarregando a página com os resultados filtrados.
    -   **Listagem de Obras**: Itera sobre a variável `obras` (passada pelo `app.py`) e renderiza um "card" para cada obra.
    -   **Botão "Abrir Pasta"**: Possui um atributo `data-caminho` com o caminho da pasta. A função `onclick` chama o JavaScript `abrirPasta(this)`.
    -   **JavaScript Local**: Contém as funções `showAlert()`, `abrirPasta()` e `confirmarExclusao()`.
-   **`editar.html` / `cadastrar_obra.html`**: Contêm os formulários para gerenciar os dados das obras, incluindo o campo para o `caminho_pasta`.

### 4.2. Arquivos Estáticos (`static/`)
-   **`static/js/auto_cadastro.js`**: Script utilizado nas páginas de cadastro/edição de obras.
    -   Monitora o campo de CNPJ e, quando um CNPJ válido é digitado, faz uma requisição `fetch` para a API interna (`/api/consultar_cnpj`).
    -   Ao receber a resposta, preenche automaticamente os campos do formulário (razão social, endereço, etc.).
-   **`static/style.css`**: Contém estilos customizados para refinar a aparência do Bootstrap e garantir a consistência visual.

## 5. Banco de Dados

-   **Tecnologia:** SQLite 3.
-   **Arquivo:** `database.db`.
-   **Esquema Principal:**
    -   **`construtoras`**: Armazena os dados das empresas construtoras (id, nome, codigo, cnpj, etc.).
    -   **`obras`**: Tabela principal que armazena todas as informações de uma obra, incluindo chaves estrangeiras para `construtoras` e campos como `nome`, `cidade`, `status`, `etapa_atual`, e `caminho_pasta`.
    -   **Tabelas de Medição:** Definidas em `database/init_medicoes.sql`, relacionadas a medições financeiras e de progresso.

## 6. Como Executar o Projeto

1.  **Pré-requisitos:**
    -   Python 3.x instalado.
    -   `pip` (gerenciador de pacotes do Python).

2.  **Instalação de Dependências:**
    -   Abra um terminal na raiz do projeto.
    -   Execute o comando:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Inicialização e Execução:**
    -   No mesmo terminal, execute o script principal do Flask:
        ```bash
        python app.py
        ```
    -   O script `init_db()` será executado automaticamente, criando e/ou verificando o banco de dados.
    -   A aplicação estará disponível em `http://127.0.0.1:5000`. 