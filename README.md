# Zank - Assistente Financeiro via WhatsApp

## 📋 Sobre o Projeto

O **Zank** é um assistente financeiro inteligente desenvolvido para WhatsApp que ajuda usuários a gerenciar suas finanças pessoais de forma simples e intuitiva. Utilizando inteligência artificial para processar linguagem natural, o bot permite registrar gastos, criar e acompanhar metas financeiras, e consultar relatórios detalhados através de conversas simples no WhatsApp.

O sistema processa mensagens em linguagem natural, categorizando automaticamente os gastos e fornecendo respostas contextuais. Usuários podem interagir de forma natural, sem precisar memorizar comandos complexos.

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework moderno e assíncrono para construção de APIs em Python
- **PostgreSQL** - Banco de dados relacional para armazenamento de dados
- **SQLAlchemy** - ORM para interação com o banco de dados
- **Alembic** - Ferramenta de migração de banco de dados
- **Pydantic** - Validação de dados e configurações

### Integração WhatsApp
- **WAHA (WhatsApp HTTP API)** - Serviço para integração com WhatsApp via API REST
- **Docker** - Containerização do serviço WAHA

### Inteligência Artificial
- **LangChain** - Framework para construção de aplicações com LLMs
- **LangGraph** - Construção de agentes com fluxos de estado
- **Groq** - Provedor de API para processamento com LLMs
- **OpenAI** - Integração com modelos GPT

### Autenticação e Segurança
- **JWT (PyJWT)** - Autenticação baseada em tokens
- **Argon2 (pwdlib)** - Hash seguro de senhas

### Ferramentas de Desenvolvimento
- **Poetry** - Gerenciamento de dependências Python
- **Ruff** - Linter e formatador de código
- **Pytest** - Framework de testes
- **Pytest-asyncio** - Suporte para testes assíncronos
- **Factory Boy** - Geração de dados de teste

### Outras Dependências
- **httpx** - Cliente HTTP assíncrono
- **slowapi** - Rate limiting para APIs
- **freezegun** - Mocking de datas em testes

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.13+**
- **Poetry** (para gerenciamento de dependências)
- **Docker** e **Docker Compose** (para executar o WAHA)
- **PostgreSQL** (banco de dados)
- **Git** (para clonar o repositório)

## 🚀 Como Rodar o Projeto

### 1. Clonar o Repositório

```bash
git clone <url-do-repositório>
cd Backend
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/nome_do_banco

# Autenticação
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WAHA (WhatsApp HTTP API)
WAHA_API_KEY=e1a77c55ba564d18ab6fb9a9bc67a11c
WAHA_BASE_URL=http://localhost:3000
WAHA_SESSION_NAME=default

# IA e Chatbot
GROQ_API_KEY=sua_chave_groq_aqui
BOT_API_KEY=sua_chave_bot_aqui
OPENAI_KEY=sua_chave_openai_aqui
```

**Importante:** Substitua os valores pelos seus próprios tokens e credenciais.

### 3. Instalar Dependências

```bash
pip install poetry
```

Com o Poetry instalado, execute:

```bash
poetry install
```

### 4. Configurar o Banco de Dados

Certifique-se de que o PostgreSQL está rodando e crie o banco de dados:

```bash
createdb nome_do_banco
```

Execute as migrações do Alembic:

```bash
alembic upgrade head
```

### 5. Rodar a Aplicação FastAPI

Inicie o servidor FastAPI:

```bash
poetry run fastapi dev app.py
```

Ou usando o taskipy:

```bash
poetry run task run
```

A API estará disponível em `http://localhost:8000`.

A documentação interativa estará disponível em:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📱 Configuração do WAHA (WhatsApp HTTP API)

O WAHA é o serviço responsável pela integração com o WhatsApp. Ele funciona como uma ponte entre sua aplicação e a API do WhatsApp Web.

### 1. Rodar a Imagem Docker do WAHA

No diretório raiz do projeto, execute:

```bash
docker-compose up -d
```

Este comando irá:
- Baixar a imagem `devlikeapro/waha:latest`
- Criar um container chamado `wpp_bot_waha`
- Expor a porta 3000 para acesso ao dashboard e API
- Configurar as variáveis de ambiente necessárias

Para verificar se o container está rodando:

```bash
docker ps
```

Você deve ver o container `wpp_bot_waha` na lista.

### 2. Acessar o Dashboard do WAHA

Após o container iniciar, acesse o dashboard do WAHA:

```
http://localhost:3000
```

**Importante:** Ao iniciar o WAHA pela primeira vez, uma senha de acesso é gerada automaticamente e exibida nos logs. Você precisará dessa senha para fazer login no dashboard.

Para encontrar a senha, execute um dos comandos abaixo:

```bash
# Opção 1: Ver logs do container diretamente
docker logs wpp_bot_waha

# Opção 2: Ver logs usando docker-compose (mais completo)
docker-compose logs waha

# Opção 3: Acompanhar logs em tempo real (útil para ver a senha quando o container iniciar)
docker logs -f wpp_bot_waha
```

Procure por uma linha similar a:

```
WAHA Dashboard password: <sua_senha_aqui>
```

ou

```
Dashboard password: <sua_senha_aqui>
```

**Dica:** Se a senha não aparecer nos logs, aguarde alguns segundos após o container iniciar. A senha é gerada durante a inicialização do WAHA. Você também pode filtrar os logs procurando pela palavra "password":

```bash
docker logs wpp_bot_waha | grep -i password
```

Copie a senha encontrada e use-a para fazer login no dashboard quando solicitado.

### 3. Cadastrar um Número de Telefone

No dashboard do WAHA (após fazer login):

1. Vá para a seção **"Sessions"** ou **"Sessões"**
2. Clique em **"Create Session"** ou **"Criar Sessão"**
3. Escolha o nome da sessão (deve corresponder ao valor de `WAHA_SESSION_NAME` no seu `.env`, por exemplo: `default`)
4. Após criar a sessão, você verá um QR Code na tela
5. **Abra o WhatsApp no seu celular**
6. Vá em **Configurações > Aparelhos conectados > Conectar um aparelho**
7. **Escaneie o QR Code** exibido no dashboard
8. Aguarde a conexão ser estabelecida (o status deve mudar para "Connected" ou "Conectado")

**Nota:** O número conectado será usado para enviar e receber mensagens do bot. É recomendado usar um número dedicado para o bot, não seu número pessoal.

### 4. Configurar o Webhook

Após conectar o número, é necessário configurar o webhook para que o WAHA envie as mensagens recebidas para sua API FastAPI:

1. No dashboard do WAHA, vá para a seção **"Webhooks"** ou **"Webhooks"**
2. Clique em **"Add Webhook"** ou **"Adicionar Webhook"**
3. Configure o webhook com os seguintes dados:

   - **URL do Webhook**: 
     - **Para desenvolvimento local**: `http://localhost:8000/webhook` ou `http://host.docker.internal:8000/webhook` (veja detalhes abaixo)
     - **Para produção**: `https://api.seudominio.com/webhook` (substitua pelo domínio do seu servidor)
     - ⚠️ **Importante**: A rota é `/webhook` (sem barra final). Certifique-se de que sua API FastAPI está rodando na porta 8000 ou ajuste conforme necessário.
   
   - **Eventos para escutar**: Selecione os eventos que deseja receber:
     - ✅ `message` - Mensagens recebidas (obrigatório)
     - ✅ `message.any` - Todas as mensagens
     - Opcionalmente, outros eventos conforme necessário
   
   - **Método HTTP**: `POST`

4. Salve o webhook e verifique se está ativo (status deve aparecer como "Active" ou "Ativo")

**Importante para desenvolvimento local:**

Se estiver testando localmente e o FastAPI estiver rodando na sua máquina, mas o WAHA está em um container Docker, você pode precisar:

- Usar `host.docker.internal` (se estiver no Windows/Mac):
  - URL: `http://host.docker.internal:8000/webhook`

- Ou usar o IP da sua máquina na rede Docker:
  - Descubra o IP: `docker network inspect bridge`
  - Use: `http://<seu-ip>:8000/webhook`

- Ou usar `http://<ip-da-sua-maquina>:8000/webhook` (substitua pelo seu IP local)

**Alternativa usando ngrok (para desenvolvimento):**

Para testar webhooks localmente sem configurar a rede Docker, você pode usar o ngrok:

1. Instale o ngrok: https://ngrok.com/download
2. Inicie um tunnel:
   ```bash
   ngrok http 8000
   ```
3. Use a URL fornecida pelo ngrok no webhook:
   ```
   https://<sua-url-ngrok>.ngrok.io/webhook
   ```

### 5. Verificar a Configuração

Para testar se tudo está funcionando:

1. Envie uma mensagem para o número conectado no WhatsApp
2. Verifique os logs do FastAPI para ver se a mensagem foi recebida
3. O bot deve processar a mensagem e responder automaticamente

Para ver os logs do container WAHA:

```bash
docker logs -f wpp_bot_waha
```

Para ver os logs do FastAPI, observe o terminal onde a aplicação está rodando.

## 🔧 Comandos Úteis

### Gerenciamento do Docker

```bash
# Iniciar o WAHA
docker-compose up -d

# Parar o WAHA
docker-compose down

# Ver logs do WAHA
docker logs -f wpp_bot_waha

# Reiniciar o WAHA
docker-compose restart waha
```

### Desenvolvimento

```bash
# Rodar a aplicação em modo desenvolvimento
poetry run fastapi dev app.py

# Executar testes
poetry run pytest

# Executar testes com cobertura
poetry run task test

# Formatar código
poetry run task format

# Verificar lint
poetry run task lint
```

### Migrações de Banco de Dados

```bash
# Criar uma nova migração
alembic revision --autogenerate -m "descricao da migracao"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

## 📁 Estrutura do Projeto

```
Backend/
├── agents/              # Agentes de IA (LangChain/LangGraph)
│   ├── context.py      # Contexto e variáveis globais
│   ├── finance_agent.py # Agente principal de finanças
│   └── tools.py        # Ferramentas do agente
├── core/               # Configurações centrais
│   ├── database.py     # Configuração do banco de dados
│   ├── mensagens.py    # Mensagens do bot
│   └── settings.py     # Configurações e variáveis de ambiente
├── middleware/         # Middlewares (autenticação, segurança)
├── migrations/         # Migrações do Alembic
├── models/             # Modelos SQLAlchemy e Schemas Pydantic
├── routers/            # Rotas da API FastAPI
│   ├── auth.py        # Autenticação
│   ├── bot.py         # Rotas do bot
│   ├── categorias.py  # Categorias de gastos
│   ├── gastos.py      # Gastos financeiros
│   ├── metas.py       # Metas financeiras
│   ├── stripe.py      # Integração Stripe
│   ├── users.py       # Usuários
│   └── webhook.py     # Webhook do WAHA
├── services/           # Serviços auxiliares
│   ├── mapping_service.py    # Mapeamento de usuários
│   └── whatsapp_service.py   # Serviço WhatsApp
├── tests/              # Testes automatizados
├── utils/              # Utilitários
├── app.py             # Aplicação principal FastAPI
├── docker-compose.yml # Configuração do WAHA
├── pyproject.toml     # Configuração Poetry
└── README.md          # Este arquivo
```

## 🔐 Segurança

- As senhas são hasheadas usando Argon2
- Tokens JWT são usados para autenticação
- Variáveis sensíveis devem estar no arquivo `.env` (não commitar no Git)
- Rate limiting está configurado via slowapi
- CORS está configurado para permitir apenas origens específicas

## 📝 Notas Importantes

- O WAHA precisa de uma conexão ativa com o WhatsApp Web. Se a sessão cair, será necessário escanear o QR Code novamente.
- Para produção, considere usar um serviço de túnel estável ou configurar um domínio próprio para os webhooks.
- Mantenha o arquivo `.env` seguro e nunca o commite no repositório.
- O banco de dados PostgreSQL deve estar acessível antes de iniciar a aplicação.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 👤 Autor

**Du** - duducostalobo10@gmail.com

---

**Dúvidas ou problemas?** Abra uma issue no repositório ou entre em contato com o desenvolvedor.

