"""
api/main.py
───────────
API REST do Marketing AI Agency usando FastAPI.

Endpoints:
  POST /campaign         → Executa a campanha completa (síncrono)
  POST /campaign/stream  → Executa com streaming de progresso (Server-Sent Events)
  GET  /health           → Health check
  GET  /docs             → Swagger UI (automático pelo FastAPI)
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from graph.state import AgencyState
from graph.workflow import agency_graph
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = ("OPENAI_API_KEY", "TAVILY_API_KEY")


def validate_required_env() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Variaveis de ambiente obrigatorias ausentes: "
                f"{', '.join(missing)}. Copie .env.example para .env e configure valores validos."
            ),
        )


# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Marketing AI Agency",
    description="Sistema multi-agente para geração de campanhas de marketing com IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (permite chamadas do frontend/Streamlit) ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Em produção, restrinja aos seus domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas de Request / Response ─────────────────────────────────────────

class CampaignRequest(BaseModel):
    briefing: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Briefing detalhado da campanha",
        example="Lançar tênis sustentável para jovens de 18-30 anos. Preço: R$350. Jan/2025.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "briefing": (
                    "Lançar uma linha de cosméticos veganos para mulheres de 25-40 anos "
                    "que buscam beleza consciente. Preço médio: R$120. Março de 2025."
                )
            }
        }


class ResearchOutput(BaseModel):
    market_trends: Optional[list] = None
    competitors: Optional[list] = None
    target_insights: Optional[str] = None


class StrategyOutput(BaseModel):
    target_audience: Optional[str] = None
    tone_of_voice: Optional[str] = None
    channels: Optional[list] = None
    campaign_goals: Optional[list] = None
    usp: Optional[str] = None


class CopyOutput(BaseModel):
    headline: Optional[str] = None
    tagline: Optional[str] = None
    instagram_post: Optional[str] = None
    linkedin_post: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    cta: Optional[str] = None


class ReviewOutput(BaseModel):
    approved: bool
    review_score: Optional[int] = None
    review_feedback: Optional[str] = None
    revision_count: int = 0


class CampaignResponse(BaseModel):
    status: str
    briefing: str
    research: ResearchOutput
    strategy: StrategyOutput
    copy: CopyOutput
    review: ReviewOutput
    generated_at: str
    duration_seconds: Optional[float] = None


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verifica se a API está no ar."""
    return {
        "status": "ok",
        "service": "Marketing AI Agency",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/campaign", response_model=CampaignResponse, tags=["Campanha"])
async def generate_campaign(request: CampaignRequest):
    """
    Executa o pipeline completo de geração de campanha.

    O sistema passa pelo fluxo:
    **Pesquisa → Estratégia → Copywriting → Revisão**

    Se o copy não passar na revisão (score < 7), o copywriter é acionado
    novamente com o feedback, até no máximo 2 revisões.

    Tempo estimado: 30–90 segundos dependendo do LLM e da complexidade.
    """
    validate_required_env()
    start_time = datetime.utcnow()

    try:
        # Executa o grafo de agentes
        initial_state = AgencyState(briefing=request.briefing)
        result = agency_graph.invoke(initial_state)

        duration = (datetime.utcnow() - start_time).total_seconds()

        return CampaignResponse(
            status=result.get("status", "unknown"),
            briefing=result.get("briefing", request.briefing),
            research=ResearchOutput(
                market_trends=result.get("market_trends"),
                competitors=result.get("competitors"),
                target_insights=result.get("target_insights"),
            ),
            strategy=StrategyOutput(
                target_audience=result.get("target_audience"),
                tone_of_voice=result.get("tone_of_voice"),
                channels=result.get("channels"),
                campaign_goals=result.get("campaign_goals"),
                usp=result.get("usp"),
            ),
            copy=CopyOutput(
                headline=result.get("headline"),
                tagline=result.get("tagline"),
                instagram_post=result.get("instagram_post"),
                linkedin_post=result.get("linkedin_post"),
                email_subject=result.get("email_subject"),
                email_body=result.get("email_body"),
                cta=result.get("cta"),
            ),
            review=ReviewOutput(
                approved=result.get("approved", False),
                review_score=result.get("review_score"),
                review_feedback=result.get("review_feedback"),
                revision_count=result.get("revision_count", 0),
            ),
            generated_at=datetime.utcnow().isoformat(),
            duration_seconds=round(duration, 2),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar o pipeline: {str(e)}"
        )


@app.post("/campaign/stream", tags=["Campanha"])
async def generate_campaign_stream(request: CampaignRequest):
    """
    Executa o pipeline com streaming de progresso via Server-Sent Events (SSE).

    O cliente recebe eventos em tempo real conforme cada agente conclui sua etapa.
    Útil para mostrar progresso na UI sem bloquear a interface.

    Use o header: Accept: text/event-stream
    """

    async def event_generator():
        """Gera eventos SSE para cada etapa do pipeline."""

        def send_event(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

        try:
            missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
            if missing:
                yield send_event("error", {
                    "message": (
                        "Variaveis de ambiente obrigatorias ausentes: "
                        f"{', '.join(missing)}. Copie .env.example para .env e configure valores validos."
                    )
                })
                return

            yield send_event("started", {
                "message": "Pipeline iniciado",
                "briefing": request.briefing[:100] + "...",
            })

            initial_state = AgencyState(briefing=request.briefing)

            # Stream passo a passo usando .stream() do LangGraph
            async for event in agency_graph.astream(
                initial_state,
                stream_mode="updates",
            ):
                for node_name, node_output in event.items():
                    status_map = {
                        "research":   ("🔍 Pesquisa concluída", "research_done"),
                        "strategy":   ("🧠 Estratégia definida", "strategy_done"),
                        "copywriter": ("✍️  Copy gerado", "copy_done"),
                        "review":     ("🔎 Revisão concluída", "review_done"),
                    }

                    if node_name in status_map:
                        message, event_type = status_map[node_name]
                        payload = {"message": message, "node": node_name}

                        # Adiciona preview dos dados relevantes
                        if node_name == "review":
                            payload["approved"] = node_output.get("approved", False)
                            payload["score"] = node_output.get("review_score")
                        elif node_name == "copywriter":
                            payload["headline"] = node_output.get("headline", "")

                        yield send_event(event_type, payload)
                        await asyncio.sleep(0.1)  # Pequena pausa para flush

            # Evento final com o resultado completo
            final_result = agency_graph.invoke(
                AgencyState(briefing=request.briefing)
            )
            yield send_event("completed", {
                "message": "Campanha gerada com sucesso!",
                "status": final_result.get("status"),
                "headline": final_result.get("headline"),
                "score": final_result.get("review_score"),
            })

        except Exception as e:
            yield send_event("error", {"message": str(e)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ── Execução local ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,       # Hot reload em desenvolvimento
        log_level="info",
    )
