# 📋 Instruções Rápidas - Sistema de Obras

## 🚀 Como Usar o Sistema

### 1. **Abrir o Sistema**
```bash
python app.py
```
Acesse: http://127.0.0.1:5000

### 2. **Navegação Principal**
- **Página Inicial**: Lista todas as obras com filtros
- **Construtoras**: Gerencia as empresas construtoras
- **Adicionar Obra**: Cria nova obra
- **Visualizar Arquivos**: Acessa arquivos da obra

### 3. **🖱️ Como Abrir Arquivos e Pastas**

#### **Para Arquivos:**
- **Clique simples** no botão "Abrir" → Abre o arquivo com o programa padrão
- **Clique duplo** na linha do arquivo → Mesmo efeito
- **Botão "Copiar"** → Copia o caminho para área de transferência

#### **Para Pastas:**
- **Clique simples** no botão "Abrir" → Abre a pasta no Windows Explorer
- **Clique duplo** na linha da pasta → Mesmo efeito
- **Botão "Copiar"** → Copia o caminho para área de transferência

#### **Para Links do Google Drive:**
- **Clique simples** no botão "Abrir" → Abre no navegador
- **Botão "Copiar"** → Copia o link para área de transferência

### 4. **🔧 Funcionalidades Especiais**

#### **Filtros na Página Inicial:**
- **Por Construtora**: Selecione uma empresa específica
- **Por Status**: Em andamento, Finalizado, Atrasado
- **Por Cidade**: Digite o nome da cidade
- **Busca Geral**: Procura em nome, responsável, cidade

#### **Ações Rápidas:**
- **Editar Obra**: Clique no ícone de lápis
- **Visualizar Arquivos**: Clique no ícone de pasta
- **Excluir Obra**: Clique no ícone de lixeira (com confirmação)

### 5. **📁 Estrutura de Pastas**

O sistema suporta:
- **Pastas Locais**: `G:/Meu Drive/...` (seu drive)
- **Links do Google Drive**: URLs compartilhadas
- **Arquivos**: PDFs, imagens, documentos, etc.

### 6. **⚠️ Dicas Importantes**

#### **Para Arquivos Locais:**
- Certifique-se de que o caminho está correto
- O arquivo deve existir no sistema
- Use o botão "Copiar" se o arquivo não abrir automaticamente

#### **Para Pastas Locais:**
- A pasta deve existir no Windows
- O sistema tentará abrir no Windows Explorer
- Se não funcionar, use o caminho copiado

#### **Para Links:**
- Links do Google Drive devem ser públicos ou compartilhados
- Use o formato: `https://drive.google.com/drive/folders/...`

### 7. **🔄 Recarregar Dados**

Se você adicionar novos arquivos nas pastas:
1. Volte para a página inicial
2. Clique novamente em "Visualizar Arquivos"
3. O sistema atualizará a lista automaticamente

### 8. **📊 Estatísticas**

Na página de arquivos, você verá:
- Total de itens encontrados
- Quantidade de arquivos vs pastas
- Tamanho dos arquivos (quando disponível)

### 9. **🎨 Interface**

- **Azul**: Pastas e ações principais
- **Verde**: Links e ações positivas
- **Amarelo**: Avisos e edições
- **Vermelho**: Exclusões e erros
- **Cinza**: Informações secundárias

### 10. **🆘 Solução de Problemas**

#### **Arquivo não abre:**
1. Verifique se o caminho está correto
2. Use o botão "Copiar" e cole no Windows Explorer
3. Verifique se o arquivo existe

#### **Pasta não abre:**
1. Verifique se a pasta existe
2. Use o caminho copiado no Windows Explorer
3. Verifique permissões de acesso

#### **Link não funciona:**
1. Verifique se o link está correto
2. Teste o link diretamente no navegador
3. Verifique se o Google Drive está compartilhado

---

**💡 Dica**: Use **clique duplo** nas linhas dos arquivos/pastas para abrir rapidamente!

## 📊 Dados de Exemplo

O sistema já vem com dados prontos:

### Construtoras
- 001 CONSTRUTORA BILD
- 002 CONSTRUTORA SILVA

### Obras
- **BILD ALLMA** (Ribeirão Preto, Em andamento)
- **BILD CENTER** (São Paulo, Finalizado)
- **SILVA RESIDENCIAL** (Campinas, Em andamento)
- **SILVA COMERCIAL** (Santos, Atrasado)

## 🎯 Funcionalidades Principais

1. **Página Inicial**: Lista todas as obras com filtros
2. **Nova Obra**: Cadastro completo de obras
3. **Editar Obra**: Modificar dados existentes
4. **Visualizar Arquivos**: Listar conteúdo das pastas
5. **Gerenciar Construtoras**: CRUD de construtoras

## 🔧 Configuração

- **Porta**: 5000 (padrão)
- **Banco**: SQLite (database.db)
- **Interface**: Bootstrap 5 + CSS personalizado

## 🆘 Solução de Problemas

### Erro de Porta
```python
# Em app.py, linha 295, mude para:
app.run(debug=True, port=5001)
```

### Recriar Banco
```bash
# Delete o arquivo database.db e execute novamente
rm database.db
python app.py
```

### Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📱 Acesso

- **URL**: http://localhost:5000
- **Navegador**: Chrome, Firefox, Edge, Safari
- **Responsivo**: Funciona em desktop e mobile

---

**✅ Sistema pronto para uso!** 