"""
rag_engine.py
=============

Coração do RAG (Retrieval-Augmented Generation) deste projeto.

Este arquivo lê tudo o que está na pasta /documentos
(textos, PDFs, planilhas Excel e páginas da web listadas em links.txt),
transforma esse conteúdo em "vetores" (números que representam o significado
do texto) e guarda esses vetores em um banco local (ChromaDB).

Quando uma pergunta chega do frontend, a gente:
  1. Transforma a pergunta em um vetor.
  2. Procura no banco os pedaços de texto mais parecidos com a pergunta.
  3. Junta esses pedaços como "contexto" e pede para a IA (Llama 3.3 70B
     via Groq) responder.

Stack escolhida para o hackathon:
  - Embeddings: fastembed (100% local, sem limite, sem chave de API).
  - LLM: Groq + llama-3.3-70b-versatile (free tier MUITO generoso).

Você NÃO precisa mexer aqui para fazer o desafio funcionar. Mas se quiser
mudar a PERSONALIDADE da IA, edite a variável PROMPT_TEMPLATE logo abaixo.
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path

# Desativa a telemetria do ChromaDB ANTES de importar a biblioteca.
# Isso evita warnings inofensivos do tipo "Failed to send telemetry event"
# que aparecem por incompatibilidade entre versoes de chromadb e posthog.
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Silencia tambem os loggers internos de telemetria do ChromaDB.
# Mesmo com a variavel de ambiente acima, algumas versoes ainda logam
# o erro de incompatibilidade do posthog - aqui matamos esses loggers.
for _nome_logger in (
    "chromadb.telemetry.product.posthog",
    "chromadb.telemetry",
    "chromadb",
    "posthog",
):
    logging.getLogger(_nome_logger).setLevel(logging.CRITICAL)

import chromadb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fastembed import TextEmbedding
from groq import Groq
from pypdf import PdfReader


# ============================================================
#                                                              
#   PERSONALIDADE DA IA                      
#   --------------------------------------------------------   
#   Esta string controla o tom, o estilo e as instruções que   
#   a IA segue para responder. Você pode mudar tudo o que      
#   está entre as três aspas abaixo.                           
#                                                              
#   IMPORTANTE: mantenha as marcações {contexto} e {pergunta}  
#   no texto. Elas são "espaços reservados" que serão          
#   trocados automaticamente pelo conteúdo da sua base de      
#   conhecimento e pela pergunta da usuária.                   
#                                                              
#   Exemplos de personalidade que você pode tentar:            
#     - "Você é uma assistente animada e usa emojis..."        
#     - "Você é uma cientista séria e cita estudos..."         
#     - "Você é uma mentora carinhosa para meninas em TI..."   
#                                                              
# ============================================================
# Alterar a personalidade da IA aqui
PROMPT_TEMPLATE = """Você é uma assistente virtual focada em apoiar mulheres e meninas da área de tecnologia. Responda sempre em português do Brasil, de forma acolhedora, clara e encorajadora!

Contexto:
{contexto}

Pergunta da usuária:
{pergunta}

Resposta:"""


# ============================================================
# CONFIGURAÇÕES GERAIS DO RAG
# ------------------------------------------------------------
# CHUNK_SIZE   = tamanho de cada pedaço de texto (em caracteres).
# CHUNK_OVERLAP = quantos caracteres se repetem entre pedaços
#                 vizinhos (ajuda a não "cortar" frases no meio).
# TOP_K        = quantos pedaços similares a IA usa como contexto.
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTOS_DIR = BASE_DIR.parent / "documentos"
CHROMA_DIR = BASE_DIR / "chroma_db"
LINKS_FILE = DOCUMENTOS_DIR / "links.txt"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4

# Modelo de geração (resposta em linguagem natural) via Groq.
# Free tier: ~14.400 requisições por dia, 30 por minuto.
MODELO_GERACAO = "llama-3.3-70b-versatile"

# Modelo de embedding LOCAL (multilingual, suporta português).
# Baixado automaticamente na primeira execução (~220MB) e fica em cache.
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

COLECAO_NOME = "base_conhecimento"


class RAGEngine:
    """Classe que cuida de toda a lógica do RAG.

    Uso típico:
        engine = RAGEngine()
        engine.indexar()                   # lê os documentos e cria o banco
        resposta = engine.responder("...")  # responde uma pergunta
    """

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada. Crie um arquivo .env na pasta "
                "backend/ com o conteúdo: GROQ_API_KEY=sua_chave_aqui. "
                "Obtenha uma chave gratis em https://console.groq.com/keys"
            )

        # Cliente do Groq (LLM que vai gerar as respostas em portugues).
        self.cliente_groq = Groq(api_key=api_key)

        # Modelo de embedding local (fastembed). Na primeira vez baixa o
        # modelo (~220MB) e guarda em cache - depois fica offline e rapido.
        print(f"[RAGEngine] Carregando modelo de embedding local: {MODELO_EMBEDDING}")
        self.embedder = TextEmbedding(model_name=MODELO_EMBEDDING)

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        # anonymized_telemetry=False evita warnings inofensivos do ChromaDB
        # sobre envio de telemetria - só deixa o log mais limpo.
        self.cliente_chroma = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self.colecao = self.cliente_chroma.get_or_create_collection(
            name=COLECAO_NOME,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # LEITORES DE CADA TIPO DE ARQUIVO
    # ------------------------------------------------------------------
    # Cada método abaixo abre um tipo diferente de arquivo e devolve
    # uma string com o texto puro, pronto para ser dividido em chunks.

    def _carregar_txt(self, caminho: Path) -> str:
        """Lê um arquivo .txt comum (UTF-8)."""
        return caminho.read_text(encoding="utf-8", errors="ignore")

    def _carregar_pdf(self, caminho: Path) -> str:
        """Lê um arquivo .pdf usando o pypdf.

        Junta o texto de todas as páginas em uma string só.
        """
        leitor = PdfReader(str(caminho))
        partes: list[str] = []
        for numero, pagina in enumerate(leitor.pages, start=1):
            texto_pagina = pagina.extract_text() or ""
            if texto_pagina.strip():
                partes.append(f"[Página {numero}]\n{texto_pagina}")
        return "\n\n".join(partes)

    def _carregar_xlsx(self, caminho: Path) -> str:
        """Lê uma planilha Excel (.xlsx) e converte em texto.

        Estratégia simples e didática:
          - Para CADA aba da planilha, percorre linha por linha.
          - Cada linha vira uma frase no formato:
                "coluna1: valor1 | coluna2: valor2 | ..."
          - Isso faz a IA "entender" tabela como texto normal.
        """
        partes: list[str] = []
        planilhas = pd.read_excel(caminho, sheet_name=None, dtype=str)

        for nome_aba, df in planilhas.items():
            df = df.fillna("")
            partes.append(f"[Planilha: {nome_aba}]")

            for _, linha in df.iterrows():
                campos = [
                    f"{coluna}: {valor}".strip()
                    for coluna, valor in linha.items()
                    if str(valor).strip()
                ]
                if campos:
                    partes.append(" | ".join(campos))

        return "\n".join(partes)

    def _carregar_url(self, url: str) -> str:
        """Baixa uma página da web e extrai apenas o texto visível.

        Remove tags <script> e <style> (que são código, não conteúdo)
        e devolve o texto limpo.
        """
        resposta = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "GirlsCodeRAG/1.0"},
        )
        resposta.raise_for_status()

        sopa = BeautifulSoup(resposta.text, "lxml")
        for tag in sopa(["script", "style", "noscript"]):
            tag.decompose()

        texto = sopa.get_text(separator="\n")
        linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
        return "\n".join(linhas)

    def _ler_links_txt(self) -> list[str]:
        """Lê o arquivo documentos/links.txt e devolve a lista de URLs válidas.

        Ignora linhas em branco e linhas que começam com '#' (comentários).
        """
        if not LINKS_FILE.exists():
            return []

        urls: list[str] = []
        for linha in LINKS_FILE.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            urls.append(linha)
        return urls

    # ------------------------------------------------------------------
    # CHUNKING (DIVISÃO DO TEXTO EM PEDAÇOS)
    # ------------------------------------------------------------------
    def _dividir_em_chunks(self, texto: str) -> list[str]:
        """Divide um texto grande em pedaços menores com sobreposição.

        Por que isso? Modelos de IA tem limite de tamanho. E busca por
        similaridade funciona melhor com pedaços pequenos e focados.
        """
        texto = re.sub(r"\s+\n", "\n", texto).strip()
        if not texto:
            return []

        chunks: list[str] = []
        inicio = 0
        passo = max(1, CHUNK_SIZE - CHUNK_OVERLAP)

        while inicio < len(texto):
            fim = min(inicio + CHUNK_SIZE, len(texto))
            chunk = texto[inicio:fim].strip()
            if chunk:
                chunks.append(chunk)
            if fim == len(texto):
                break
            inicio += passo

        return chunks

    # ------------------------------------------------------------------
    # EMBEDDINGS (TRANSFORMAR TEXTO EM VETORES DE NÚMEROS)
    # ------------------------------------------------------------------
    def _gerar_embeddings(self, textos: list[str]) -> list[list[float]]:
        """Transforma uma lista de textos em vetores usando o fastembed.

        Roda 100% local - sem chave de API, sem limites e sem internet
        (após o primeiro download do modelo).
        """
        # fastembed devolve um generator de numpy arrays - convertemos
        # para list[list[float]] para o ChromaDB conseguir armazenar.
        vetores = list(self.embedder.embed(textos))
        return [v.tolist() for v in vetores]

    # ------------------------------------------------------------------
    # INDEXAÇÃO (LÊ TUDO -> CHUNKS -> VETORES -> BANCO)
    # ------------------------------------------------------------------
    def indexar(self) -> dict:
        """Lê toda a pasta /documentos e reconstrói o banco de vetores.

        Devolve um pequeno relatório (dicionário) com o que foi carregado.
        """
        DOCUMENTOS_DIR.mkdir(parents=True, exist_ok=True)

        # Apaga a coleção antiga e cria uma nova - assim a indexação
        # sempre começa do zero (evita conteúdo duplicado).
        try:
            self.cliente_chroma.delete_collection(COLECAO_NOME)
        except Exception:
            pass
        self.colecao = self.cliente_chroma.get_or_create_collection(
            name=COLECAO_NOME,
            metadata={"hnsw:space": "cosine"},
        )

        relatorio = {
            "arquivos_lidos": [],
            "urls_lidas": [],
            "erros": [],
            "total_chunks": 0,
        }

        fontes: list[tuple[str, str]] = []

        for arquivo in sorted(DOCUMENTOS_DIR.iterdir()):
            if not arquivo.is_file():
                continue

            nome = arquivo.name
            if nome.lower() == "links.txt":
                continue

            try:
                extensao = arquivo.suffix.lower()
                if extensao == ".txt":
                    texto = self._carregar_txt(arquivo)
                elif extensao == ".pdf":
                    texto = self._carregar_pdf(arquivo)
                elif extensao == ".xlsx":
                    texto = self._carregar_xlsx(arquivo)
                else:
                    continue

                if texto.strip():
                    fontes.append((nome, texto))
                    relatorio["arquivos_lidos"].append(nome)
            except Exception as erro:
                relatorio["erros"].append(f"{nome}: {erro}")

        for url in self._ler_links_txt():
            try:
                texto = self._carregar_url(url)
                if texto.strip():
                    fontes.append((url, texto))
                    relatorio["urls_lidas"].append(url)
            except Exception as erro:
                relatorio["erros"].append(f"{url}: {erro}")

        if not fontes:
            return relatorio

        documentos: list[str] = []
        metadados: list[dict] = []
        ids: list[str] = []

        for nome_fonte, texto in fontes:
            for chunk in self._dividir_em_chunks(texto):
                documentos.append(chunk)
                metadados.append({"fonte": nome_fonte})
                ids.append(str(uuid.uuid4()))

        if not documentos:
            return relatorio

        # Com embeddings locais nao ha mais limite de API - podemos
        # processar lotes maiores. O fastembed ja paraleliza internamente.
        TAMANHO_LOTE = 64
        for inicio in range(0, len(documentos), TAMANHO_LOTE):
            lote_textos = documentos[inicio : inicio + TAMANHO_LOTE]
            lote_meta = metadados[inicio : inicio + TAMANHO_LOTE]
            lote_ids = ids[inicio : inicio + TAMANHO_LOTE]
            lote_embeddings = self._gerar_embeddings(lote_textos)

            self.colecao.add(
                documents=lote_textos,
                embeddings=lote_embeddings,
                metadatas=lote_meta,
                ids=lote_ids,
            )

        relatorio["total_chunks"] = len(documentos)
        return relatorio

    # ------------------------------------------------------------------
    # RESPONDER UMA PERGUNTA (RETRIEVAL + GERAÇÃO)
    # ------------------------------------------------------------------
    def responder(self, pergunta: str) -> dict:
        """Responde uma pergunta usando o conteúdo indexado.

        Passos:
          1. Transforma a pergunta em vetor (fastembed local).
          2. Busca no ChromaDB os chunks mais parecidos.
          3. Monta o prompt usando PROMPT_TEMPLATE.
          4. Pede uma resposta ao Llama 3.3 via Groq.
        """
        pergunta = (pergunta or "").strip()
        if not pergunta:
            return {
                "resposta": "Por favor, escreva uma pergunta antes de enviar.",
                "fontes": [],
            }

        total_indexado = self.colecao.count()
        if total_indexado == 0:
            return {
                "resposta": (
                    "A base de conhecimento está vazia. Adicione arquivos "
                    "(.txt, .pdf ou .xlsx) na pasta /documentos ou cole URLs "
                    "no arquivo /documentos/links.txt e reinicie o servidor."
                ),
                "fontes": [],
            }

        embedding_pergunta = self._gerar_embeddings([pergunta])[0]

        resultado = self.colecao.query(
            query_embeddings=[embedding_pergunta],
            n_results=min(TOP_K, total_indexado),
        )

        documentos = (resultado.get("documents") or [[]])[0]
        metadados = (resultado.get("metadatas") or [[]])[0]

        contexto = "\n\n---\n\n".join(documentos) if documentos else "(sem contexto)"
        fontes = sorted({meta.get("fonte", "?") for meta in metadados})

        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)

        # Chamada ao Groq - usa a interface estilo OpenAI (chat completions).
        resposta_modelo = self.cliente_groq.chat.completions.create(
            model=MODELO_GERACAO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        texto_resposta = (resposta_modelo.choices[0].message.content or "").strip()
        if not texto_resposta:
            texto_resposta = (
                "Não consegui gerar uma resposta no momento. Tente reformular "
                "a pergunta ou verifique se há conteúdo relevante em /documentos."
            )

        return {"resposta": texto_resposta, "fontes": fontes}


# ============================================================
# EXECUÇÃO DIRETA: permite reindexar pelo terminal com
#     python rag_engine.py
# ============================================================
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    engine = RAGEngine()
    print("Iniciando indexação da pasta /documentos ...")
    relatorio = engine.indexar()
    print("Indexação concluída!")
    print(f"  Arquivos lidos : {relatorio['arquivos_lidos']}")
    print(f"  URLs lidas     : {relatorio['urls_lidas']}")
    print(f"  Total de chunks: {relatorio['total_chunks']}")
    if relatorio["erros"]:
        print("  Erros encontrados:")
        for erro in relatorio["erros"]:
            print(f"    - {erro}")
