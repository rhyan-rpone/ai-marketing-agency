from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class AgencyState(BaseModel):
    """
    Estado compartilhado entre todos os agentes do Marketing AI Agency.
    O LangGraph passa este objeto de nó em nó, cada agente lê e escreve
    apenas nos campos de sua responsabilidade.
    """

    # ── INPUT ──────────────────────────────────────────────────────────────
    briefing: str = Field(..., description="Briefing da campanha fornecido pelo usuário")

    # ── RESEARCH AGENT ─────────────────────────────────────────────────────
    market_trends: Optional[List[str]] = Field(
        default=None, description="Tendências de mercado identificadas"
    )
    competitors: Optional[List[dict]] = Field(
        default=None, description="Concorrentes encontrados (nome, posicionamento)"
    )
    target_insights: Optional[str] = Field(
        default=None, description="Insights sobre o público-alvo"
    )

    # ── STRATEGY AGENT ─────────────────────────────────────────────────────
    target_audience: Optional[str] = Field(
        default=None, description="Público-alvo definido"
    )
    tone_of_voice: Optional[str] = Field(
        default=None, description="Tom de voz da campanha"
    )
    channels: Optional[List[str]] = Field(
        default=None, description="Canais de distribuição"
    )
    campaign_goals: Optional[List[str]] = Field(
        default=None, description="Objetivos da campanha"
    )
    usp: Optional[str] = Field(
        default=None, description="Unique Selling Proposition"
    )

    # ── COPYWRITER AGENT ───────────────────────────────────────────────────
    headline: Optional[str] = Field(default=None, description="Headline principal")
    tagline: Optional[str] = Field(default=None, description="Tagline da campanha")
    instagram_post: Optional[str] = Field(default=None, description="Post para Instagram")
    linkedin_post: Optional[str] = Field(default=None, description="Post para LinkedIn")
    email_subject: Optional[str] = Field(default=None, description="Assunto do email marketing")
    email_body: Optional[str] = Field(default=None, description="Corpo do email marketing")
    cta: Optional[str] = Field(default=None, description="Call-to-action principal")

    # ── REVIEW AGENT ───────────────────────────────────────────────────────
    approved: bool = Field(default=False, description="Copy aprovado pelo revisor")
    review_score: Optional[int] = Field(
        default=None, description="Score de qualidade (0-10)"
    )
    review_feedback: Optional[str] = Field(
        default=None, description="Feedback detalhado do revisor"
    )
    revision_count: int = Field(
        default=0, description="Número de revisões realizadas"
    )

    # ── CONTROL ────────────────────────────────────────────────────────────
    status: Literal[
        "started", "researching", "strategizing",
        "writing", "reviewing", "approved", "failed"
    ] = Field(default="started")
    error: Optional[str] = Field(default=None, description="Mensagem de erro, se houver")
