# Girls Code 2026 - Desafio RAG (CEU / Unifei)

Desafio de **RAG (Retrieval-Augmented Generation)** do **Girls Code 2026**, organizado pelo CEU - Centro de Empreendedorismo Unifei.

> **Foco do desafio:** construir o **frontend (HTML)** e toda a **estilização (CSS)** do zero! O backend ja vem pronto, funcional e comentado em português - você só precisa conversar com ele.

---

## O que esse projeto faz?

É um chat com uma assistente de IA que responde perguntas com base em documentos que **você** coloca na pasta `documentos/`. A IA usa o modelo **Llama 3.3 70B** (gratuito) via [Groq](https://groq.com) e busca informações em arquivos `.txt`, `.pdf`, `.xlsx` e até em páginas da web que você listar.

## Estrutura do projeto

```
girls-code-rag/
├── backend/                    # O Cérebro da IA / Servidor Python (pronto para usar)
│   ├── main.py                 # API FastAPI
│   ├── rag_engine.py           # Logica do RAG (com PROMPT_TEMPLATE editavel)
│   ├── requirements.txt        # Dependencias do Python
│   └── .env.example            # Modelo do arquivo de chave de API
├── documentos/                 # BASE DE CONHECIMENTO
│   └── links.txt               # Cole URLs (uma por linha) para a IA ler (opcional)
├── frontend/                   # A Casa da IA
│   ├── index.html              # HTML base do chat
│   ├── style.css               # CSS vazio
│   └── script.js               # Logica do envio (ja pronta)
└── README.md
```

---

## Pré-requisitos

- **Python 3.10 - 3.12** instalado.
- Uma **chave gratuita do Groq**, obtida em [https://console.groq.com/keys](https://console.groq.com/keys) (basta criar uma conta gratis).

---

## Como rodar o projeto

### 1) Configurar o backend (Python)

Abra um terminal **dentro da pasta `backend/`** e execute:

```bash
# Cria um ambiente virtual para nao bagunçar o Python da sua maquina
python -m venv .venv

# Ativa o ambiente virtual
source .venv/bin/activate          # Linux / macOS
.venv\Scripts\activate             # Windows (PowerShell ou CMD)

# Instala todas as bibliotecas necessarias
pip install -r requirements.txt

# Cria seu arquivo .env a partir do exemplo
cp .env.example .env               # Linux / macOS
copy .env.example .env             # Windows
```

Agora **abra o arquivo `backend/.env`** em qualquer editor de texto e cole sua chave do Groq:

```env
GROQ_API_KEY=cole_sua_chave_aqui
```

Em seguida, ainda dentro de `backend/`, suba o servidor:

```bash
uvicorn main:app
```

Se tudo deu certo, você verá algo como:

```
[Girls Code RAG] Inicializando motor de IA ...
[RAGEngine] Carregando modelo de embedding local: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
[Girls Code RAG] Indexando documentos ...
[Girls Code RAG] Indexação concluída: 0 arquivo(s), 0 URL(s), 0 pedaço(s) de texto.
Uvicorn running on http://127.0.0.1:8000
```

> Na primeira execução o `fastembed` vai baixar o modelo de embedding (cerca de 220 MB). Isso pode levar alguns minutos dependendo da sua internet. Nas próximas vezes ele inicia em poucos segundos.

Deixe esse terminal aberto - ele é o coração da aplicação.

### 2) Abrir o frontend

Abra **outro terminal**, vá até a pasta `frontend/` e suba um servidor de arquivos estáticos:

```bash
cd frontend
python -m http.server 5500
```

Depois, no navegador, acesse [http://localhost:5500](http://localhost:5500). Pronto! O chat está no ar.

> Dica: você também pode usar a extensão **Live Server** do VS Code se preferir.

---

## Como adicionar conteúdo na base de conhecimento

Coloque arquivos dentro da pasta `**documentos/`**:

- `.txt` (texto puro)
- `.pdf` (documentos em PDF)
- `.xlsx` (planilhas do Excel)
- URLs → cole cada link em uma linha do arquivo `documentos/links.txt`

Depois de adicionar/remover algo:

- Reinicie o servidor (Ctrl+C e suba de novo), **ou**
- Chame `POST http://localhost:8000/reindexar` (pelo terminal: `curl -X POST http://localhost:8000/reindexar`).

---

## Como mudar a PERSONALIDADE da IA

Abra o arquivo `**backend/rag_engine.py`** e procure pelo bloco bem destacado `**PERSONALIDADE DA IA - EDITE AQUI!`**. Lá dentro existe uma variável chamada `PROMPT_TEMPLATE`.

Basta editar o texto entre as três aspas para mudar o tom da assistente:

```python
PROMPT_TEMPLATE = """Voce e uma mentora carinhosa para meninas em TI...
Contexto: {contexto}
Pergunta: {pergunta}
Resposta:"""
```

**Importante:** mantenha os marcadores `{contexto}` e `{pergunta}` em algum lugar do texto - eles são substituídos automaticamente.

---

## Dicas para o desafio

1. **Classes prontas no JS** - o `script.js` já cria as mensagens com:
  - `.mensagem` (todas)
  - `.mensagem-usuario` (mensagem da pessoa)
  - `.mensagem-bot` (resposta da IA)
  - `.mensagem-erro` (mensagens de erro)
2. **Acessibilidade conta pontos!** Pense em contraste, foco visível em botões, tamanho de fonte adequado.
3. **Conteúdo de qualidade** - quanto mais relevante for o que você colocar em `documentos/`, melhores serão as respostas da IA.

---

## Endpoints do backend (caso queira testar com curl/Postman)

- `POST /perguntar` → corpo `{ "pergunta": "..." }`, devolve `{ "resposta": "...", "fontes": [...] }`.
- `POST /reindexar` → relê tudo dentro de `documentos/`.

---

## Problemas comuns


| Sintoma                                         | Possível causa                            | Solução                                                   |
| ----------------------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| "Não foi possível conectar ao servidor" no chat | O backend não está rodando                | Suba o `uvicorn` no terminal do backend                   |
| Erro `GROQ_API_KEY não encontrada`              | Arquivo `.env` faltando ou vazio          | Crie `backend/.env` com `GROQ_API_KEY=...`                |
| Servidor demora para subir na 1ª vez            | Download do modelo de embedding (~220 MB) | Aguarde - é único, fica em cache em `~/.cache/fastembed/` |
| Erro 429 / `rate_limit_exceeded` no Groq        | Muitas perguntas em poucos segundos       | Aguarde 60s - o limite por minuto se renova rápido        |
| PDF não foi lido                                | PDF de imagem (escaneado)                 | Use PDFs com texto selecionável                           |


Boa sorte, equipe! 💜

> Girls Code 2026 - CEU / Unifei

