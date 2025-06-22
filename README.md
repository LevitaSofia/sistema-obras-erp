# Sistema de Gestão de Obras - Painel ERA

## 1. Visão Geral

Este é um sistema web desenvolvido em Python com o microframework Flask, projetado para a gestão detalhada de obras, com foco em sistemas de proteção coletiva. A aplicação permite o acompanhamento de múltiplos projetos, agrupados por construtora, e oferece um painel de status interativo inspirado na metodologia "ERA" (Estudo, Rastreamento, Ação).

O principal diferencial do sistema é a integração com o sistema de arquivos local, permitindo que os usuários abram as pastas de uma obra diretamente pelo navegador, facilitando o acesso a documentos, projetos e outros arquivos importantes.

---

## 2. Funcionalidades Principais

*   **Dashboard Centralizado:** A página inicial exibe todas as obras em formato de "cards", fornecendo uma visão rápida do status, construtora, e progresso de cada uma.
*   **Filtros Avançados:** Permite filtrar as obras por:
    *   Construtora
    *   Etapa principal (Orçamento, Projeto, Execução, etc.)
    *   Sistema de Proteção (SLQA, Piso a Piso, etc.)
    *   Busca por texto livre (nome da obra, cidade, responsável).
*   **Painel de Detalhes da Obra (ERA):** Cada obra possui uma página de visualização detalhada que inclui:
    *   **Checklist Interativo:** Um checklist completo dividido por categorias (Orçamento, Projeto, Execução, Faturamento, Encerramento). O status de cada item é salvo automaticamente no banco de dados sem a necessidade de recarregar a página.
    *   **Gestão de Sistemas de Proteção:** Controle do status ('Pendente', 'Em Andamento', 'Concluído') para cada tipo de sistema de proteção associado à obra.
    *   **Informações Gerais:** Exibição de todos os dados da obra, como responsável, anotações, e status geral.
*   **Integração com Sistema de Arquivos Local:** A funcionalidade "Abrir Pasta" permite abrir o diretório da obra no Windows Explorer (ou gerenciador de arquivos padrão) com um único clique.
*   **Gestão de Dados (CRUD):** A aplicação suporta operações completas de Criar, Ler, Atualizar e Excluir (CRUD) para Obras e Construtoras.
*   **Banco de Dados Robusto:** Utiliza SQLite com um esquema bem definido para armazenar e relacionar todas as informações de forma eficiente.
*   **Scripts de Apoio:** Inclui um script (`populate_db_v2.py`) para popular o banco de dados em massa com uma lista pré-definida de obras, evitando inserções duplicadas.

---

## 3. Pilha Tecnológica

*   **Backend:** Python 3, Flask
*   **Frontend:** HTML5, CSS3, JavaScript
*   **Framework CSS:** Bootstrap 5 (para layout responsivo e componentes de UI)
*   **Banco de Dados:** SQLite 3
*   **Bibliotecas Python:**
    *   `Flask`: Núcleo da aplicação web.
    *   `sqlite3`: Para interação com o banco de dados.

---

## 4. Estrutura do Projeto

```
/
├── app.py                      # Arquivo principal da aplicação Flask (rotas e lógica)
├── database.db                 # Arquivo do banco de dados SQLite
├── populate_db_v2.py           # Script para popular o banco com as obras
├── requirements.txt            # Lista de dependências Python
├── static/
│   └── style.css               # Folha de estilos customizada
└── templates/
    ├── base.html               # Template base com a estrutura HTML principal
    ├── index.html              # Página inicial (dashboard de obras)
    ├── visualizar_obra.html    # Página de detalhes da obra (Painel ERA)
    ├── adicionar.html          # Formulário para adicionar nova obra
    ├── editar.html             # Formulário para editar uma obra existente
    └── construtoras.html       # Página para gerenciar as construtoras
```

---

## 5. Esquema do Banco de Dados

O banco de dados (`database.db`) é composto por 5 tabelas inter-relacionadas:

1.  **`construtoras`**: Armazena as empresas construtoras.
    *   `id` (INTEGER, PK): Identificador único.
    *   `nome` (TEXT, UNIQUE): Nome da construtora.
    *   `codigo` (TEXT, UNIQUE): Código ou sigla da construtora.

2.  **`obras`**: Tabela central que armazena as informações de cada obra.
    *   `id` (INTEGER, PK): Identificador único.
    *   `nome` (TEXT): Nome da obra.
    *   `construtora_id` (INTEGER, FK): Chave estrangeira para a tabela `construtoras`.
    *   `cidade` (TEXT): Cidade da obra.
    *   `status` (TEXT): Status geral (ex: "Em andamento", "Concluído").
    *   `responsavel` (TEXT): Nome do responsável pela obra.
    *   `caminho_pasta` (TEXT): Caminho completo para a pasta local da obra.
    *   `etapa_atual` (TEXT): Etapa principal do projeto.
    *   `anotacoes` (TEXT): Campo para anotações gerais.
    *   `data_criacao` / `data_atualizacao` (TIMESTAMP): Datas de controle.

3.  **`etapas_era`**: Armazena o status de cada item do checklist ERA para cada obra.
    *   `id` (INTEGER, PK): Identificador único.
    *   `obra_id` (INTEGER, FK): Chave estrangeira para `obras`.
    *   `etapa` (TEXT): A categoria da etapa (ex: "Projeto").
    *   `item` (TEXT): A descrição do item do checklist (ex: "ART emitida").
    *   `concluido` (BOOLEAN): `True` se o item foi concluído.
    *   `data_conclusao`, `responsavel`, `observacoes`: Campos adicionais para detalhamento.

4.  **`sistemas_protecao`**: Tabela de apoio com os tipos de sistemas de proteção.
    *   `id` (INTEGER, PK): Identificador único.
    *   `nome` (TEXT, UNIQUE): Nome do sistema (ex: "SLQA").
    *   `descricao` (TEXT): Descrição completa.

5.  **`obra_sistemas`**: Tabela de junção que relaciona obras e sistemas, definindo o status de cada sistema para cada obra.
    *   `id` (INTEGER, PK): Identificador único.
    *   `obra_id` (INTEGER, FK): Chave estrangeira para `obras`.
    *   `sistema_id` (INTEGER, FK): Chave estrangeira para `sistemas_protecao`.
    *   `status` (TEXT): Status do sistema na obra (ex: "Pendente", "Concluído").

---

## 6. Como Instalar e Executar

1.  **Pré-requisitos:**
    *   Python 3 instalado.

2.  **Clone o Repositório:**
    *   Baixe e descompacte os arquivos do projeto em uma pasta de sua escolha.

3.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    ```
    *   Ative o ambiente:
        *   No Windows: `venv\\Scripts\\activate`
        *   No macOS/Linux: `source venv/bin/activate`

4.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Inicialize e Execute a Aplicação:**
    ```bash
    python app.py
    ```
    *   Na primeira execução, o arquivo `app.py` chamará a função `init_db()` automaticamente, que criará o arquivo `database.db` e as tabelas com dados de exemplo.

6.  **Acesse a Aplicação:**
    *   Abra seu navegador e acesse `http://127.0.0.1:5000`.

7.  **Popule com Dados em Massa (Opcional):**
    *   Para adicionar a lista completa de obras BILD e PERPLAN, execute o script:
    ```bash
    python populate_db_v2.py
    ```
    *   O script foi projetado para não inserir obras duplicadas.

---

## 7. Detalhes de Implementação

### Funcionalidade "Abrir Pasta"

Esta funcionalidade é crucial e foi implementada para contornar as restrições de segurança dos navegadores, que não permitem que o JavaScript do lado do cliente acesse o sistema de arquivos local.

**Fluxo de Execução:**

1.  **Frontend:** Na página de detalhes da obra, o botão "Abrir Pasta" possui um evento de clique (`onclick`) que chama uma função JavaScript.
2.  **Requisição AJAX:** A função JavaScript envia uma requisição `POST` via AJAX para a rota `/abrir_pasta` no servidor Flask. O corpo da requisição contém o caminho da pasta da obra, que está armazenado no banco de dados (ex: `{"caminho": "G:/Meu Drive/..."}`).
3.  **Backend (Flask):** A rota `/abrir_pasta` em `app.py` recebe a requisição.
4.  **Validação e Normalização:** O código Python extrai o caminho, normaliza-o usando `os.path.normpath()` para garantir a compatibilidade com o sistema operacional (convertendo `/` em `\\` no Windows) e verifica se o diretório realmente existe com `os.path.exists()`.
5.  **Execução do Comando:** Se a pasta existir, o comando `os.startfile(caminho_normalizado)` é executado. Este comando é específico do Python no Windows e instrui o sistema operacional a abrir o caminho especificado com o programa padrão (neste caso, o Windows Explorer).
6.  **Retorno:** O servidor retorna uma resposta JSON ao frontend, indicando sucesso ou falha.

Este método é seguro porque a ação de abrir a pasta é executada pelo servidor (o processo Python), que tem as permissões necessárias para acessar o sistema de arquivos, e não pelo navegador.

### Painel ERA Interativo

A interatividade do painel ERA é alcançada usando JavaScript para se comunicar com o backend sem a necessidade de recarregar a página.

**Fluxo de Atualização:**

1.  **Evento de Clique:** Um listener de eventos em JavaScript monitora os cliques em qualquer checkbox com a classe `.etapa-checkbox`.
2.  **Coleta de Dados:** Quando um checkbox é alterado, o script coleta os dados relevantes dos atributos `data-*` do elemento, como `data-obra-id` e `data-etapa-id`.
3.  **Requisição AJAX:** Uma requisição `POST` é enviada para a rota `/atualizar_etapa` com os dados da etapa e seu novo status (marcado/desmarcado).
4.  **Backend (Flask):** A rota `/atualizar_etapa` recebe os dados, atualiza a linha correspondente na tabela `etapas_era` (alterando o campo `concluido` e a `data_conclusao`), e commita a transação no banco de dados.
5.  **Feedback Visual:** A aplicação poderia ser estendida para fornecer um feedback visual imediato (como um ícone de "salvando..."), mas atualmente a confirmação vem através da persistência do estado do checkbox quando a página é recarregada.

---

**Desenvolvido para gestão eficiente de obras de proteção coletiva com foco em usabilidade e organização.** 