"""
CopywriterAgent
───────────────
Responsabilidade: Produzir todos os textos da campanha:
  - Headline e tagline
  - Post para Instagram
  - Post para LinkedIn
  - Email marketing (assunto + corpo)
  - CTA principal
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgencyState


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.8,   # Mais criativo para copy
        api_key=os.getenv("OPENAI_API_KEY"),
    )


COPYWRITER_SYSTEM_PROMPT = """
Você é um Copywriter Sênior especializado em marketing digital e conversão.

Seu copy é:
- ESPECÍFICO: evita clichês como "solução inovadora" ou "qualidade premium"
- ORIENTADO À DOR: fala sobre o problema real do público antes da solução
- COM VOZ PRÓPRIA: adota o tom de voz definido na estratégia
- ACIONÁVEL: todo texto termina com uma ação clara

Para cada peça:
- Headlines: máx 10 palavras, impacto imediato
- Instagram: engajante, usa emojis com moderação, hashtags ao final
- LinkedIn: profissional, storytelling, sem emojis excessivos
- Email: assunto curioso (max 50 chars), corpo que conta história antes da oferta
- CTA: verbo de ação + benefício (ex: "Quero meu acesso gratuito")

IMPORTANTE: Responda SEMPRE em JSON válido, sem markdown.
Responda em português brasileiro.
"""


def copywriter_node(state: AgencyState) -> AgencyState:
    """
    Nó do grafo responsável pela produção de copy.
    Se for uma revisão, o feedback do revisor é incluído no prompt.
    """
    is_revision = state.revision_count > 0
    revision_label = f" (Revisão #{state.revision_count})" if is_revision else ""
    print(f"✍️  [CopywriterAgent] Escrevendo copy{revision_label}...")

    llm = get_llm()

    channels_text = ", ".join(state.channels or ["Instagram", "Email", "LinkedIn"])
    goals_text = "\n".join([f"  • {g}" for g in (state.campaign_goals or [])])

    # Inclui feedback do revisor se for revisão
    feedback_section = ""
    if is_revision and state.review_feedback:
        feedback_section = f"""
⚠️  ESTA É UMA REVISÃO. O revisor pediu as seguintes melhorias:
{state.review_feedback}

Corrija especificamente os pontos acima mantendo o que estava bom.
"""

    prompt = f"""
Briefing: {state.briefing}

Público-alvo: {state.target_audience or "Não definido"}
Tom de voz: {state.tone_of_voice or "Profissional e próximo"}
USP: {state.usp or "Não definido"}
Canais: {channels_text}
Objetivos:
{goals_text}
{feedback_section}

Gere o copy completo retornando EXATAMENTE este JSON:

{{
  "headline": "Headline principal da campanha (máx 10 palavras)",
  "tagline": "Tagline memorável (máx 8 palavras)",
  "instagram_post": "Post completo para Instagram com emojis e hashtags",
  "linkedin_post": "Post completo para LinkedIn (tom profissional, storytelling)",
  "email_subject": "Assunto do email (máx 50 caracteres)",
  "email_body": "Corpo do email completo (saudação, problema, solução, oferta, CTA)",
  "cta": "Call-to-action principal (verbo + benefício)"
}}
"""

    messages = [
        SystemMessage(content=COPYWRITER_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    copy_data = _parse_copy(response.content)

    print(f"✅ [CopywriterAgent] Copy gerado. Headline: \"{copy_data.get('headline', '')}\"")

    return state.model_copy(update={
        "headline": copy_data.get("headline", ""),
        "tagline": copy_data.get("tagline", ""),
        "instagram_post": copy_data.get("instagram_post", ""),
        "linkedin_post": copy_data.get("linkedin_post", ""),
        "email_subject": copy_data.get("email_subject", ""),
        "email_body": copy_data.get("email_body", ""),
        "cta": copy_data.get("cta", ""),
        "status": "reviewing",
        # Reseta aprovação para nova rodada de review
        "approved": False,
        "review_feedback": None,
    })


def _parse_copy(raw: str) -> dict:
    """Parseia JSON com fallback."""
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except (json.JSONDecodeError, IndexError):
        return {
            "headline": "Copy não pôde ser gerado",
            "tagline": "Tente novamente",
            "instagram_post": raw[:500],
            "linkedin_post": "",
            "email_subject": "Nova campanha",
            "email_body": raw[:800],
            "cta": "Saiba mais",
        }
