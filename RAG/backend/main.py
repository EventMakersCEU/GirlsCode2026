"""
main.py
=======

Servidor FastAPI que conecta o frontend (HTML/JS) com o motor de RAG
(rag_engine.py). Este é o "porteiro" da nossa aplicação: recebe a pergunta
do navegador, chama o motor de IA e devolve a resposta em JSON.

Endpoints disponíveis:
  POST /perguntar   -> Recebe uma pergunta e devolve a resposta da IA.
  POST /reindexar   -> Força a releitura da pasta /documentos.

Para rodar o servidor (de dentro da pasta backend/):
  uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from rag_engine import RAGEngine

load_dotenv()


# Variável global que guarda o motor de RAG já inicializado.
# Será preenchida quando o servidor subir (no "lifespan").
engine: RAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda na hora que o servidor sobe e na hora que ele desliga.

    Aqui a gente cria o RAGEngine UMA VEZ só e já roda a indexação
    automática da pasta /documentos. Isso evita pagar o custo de
    indexar em cada pergunta.
    """
    global engine
    print("[Girls Code RAG] Inicializando motor de IA ...")
    engine = RAGEngine()

    print("[Girls Code RAG] Indexando documentos ...")
    try:
        relatorio = engine.indexar()
        print(
            "[Girls Code RAG] Indexação concluída: "
            f"{len(relatorio['arquivos_lidos'])} arquivo(s), "
            f"{len(relatorio['urls_lidas'])} URL(s), "
            f"{relatorio['total_chunks']} pedaço(s) de texto."
        )
        if relatorio["erros"]:
            print("[Girls Code RAG] Alguns itens deram erro:")
            for erro in relatorio["erros"]:
                print(f"  - {erro}")
    except Exception as erro:
        print(f"[Girls Code RAG] ERRO ao indexar: {erro}")

    yield

    print("[Girls Code RAG] Encerrando servidor ...")


app = FastAPI(
    title="Girls Code 2026 - RAG API",
    description=(
        "API caixa-preta do desafio de RAG do hackathon Girls Code 2026 "
        "(CEU/Unifei). Foco do desafio: construir o frontend e a estilização."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# CORS - libera o acesso a partir do navegador (frontend local).
# ------------------------------------------------------------------
# Em produção isso seria mais restrito, mas como o hackathon roda
# tudo na máquina das participantes, liberamos qualquer origem.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# MODELOS DE DADOS (o que o frontend manda e o que devolvemos)
# ------------------------------------------------------------------
class PerguntaRequest(BaseModel):
    """JSON esperado em POST /perguntar."""

    pergunta: str = Field(..., min_length=1, description="Pergunta da usuária")


class RespostaResponse(BaseModel):
    """JSON devolvido por POST /perguntar."""

    resposta: str
    fontes: list[str]


@app.post("/perguntar", response_model=RespostaResponse)
def perguntar(req: PerguntaRequest) -> RespostaResponse:
    """Recebe uma pergunta e devolve a resposta gerada pelo RAG."""
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="O motor de IA ainda está inicializando. Tente novamente em instantes.",
        )

    try:
        resultado = engine.responder(req.pergunta)
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar a IA: {erro}",
        )

    return RespostaResponse(
        resposta=resultado["resposta"],
        fontes=resultado["fontes"],
    )


@app.post("/reindexar")
def reindexar() -> dict:
    """Lê tudo de novo na pasta /documentos sem precisar reiniciar o servidor.

    Útil quando você adicionar um novo arquivo durante o desenvolvimento.
    """
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="O motor de IA ainda não terminou de subir.",
        )

    try:
        relatorio = engine.indexar()
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reindexar: {erro}",
        )

    return {
        "mensagem": "Indexação concluída.",
        "relatorio": relatorio,
    }


# ------------------------------------------------------------------
# TRATAMENTO GLOBAL DE ERROS (mensagens sempre em português)
# ------------------------------------------------------------------
@app.exception_handler(Exception)
async def tratador_geral_excecoes(request, exc: Exception):  # noqa: ANN001
    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "Ocorreu um erro inesperado no servidor. "
                f"Detalhe técnico: {exc}"
            )
        },
    )
