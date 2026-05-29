"""
ReviewAgent
───────────
Responsabilidade: Avaliar a qualidade do copy gerado com base em
uma rubrica profissional e decidir: aprovar ou solicitar revisão.

Critérios de avaliação (0–10 cada):
  - Clareza: fácil de entender?
  - Relevância: alinhado ao briefing e estratégia?
  - Persuasão: convence e engaja?
  - Tom de voz: segue o tom definido?
  - CTA: a ação pedida é clara e atraente?

Score final >= 7 → aprovado
Score final < 7  → solicita revisão (máx 2 revisões)
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgencyState

MAX_REVISIONS = 2

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

REVIEW_SYSTEM_PROMPT = """
Você é um Diretor de Criação experiente revisando copy de marketing.

Sua função é avaliar objetivamente e dar feedback ESPECÍFICO e ACIONÁVEL.

Nunca aprove copy que:
- Usa clichês como "solução inovadora", "qualidade inigualável"
- Não menciona o público-alvo explicitamente
- Tem CTA vago como "Clique aqui" ou "Saiba mais"
- Está desalinhado com o tom de voz definido

Seja direto: diga EXATAMENTE o que precisa mudar e como melhorar.
Responda em português brasileiro.
IMPORTANTE: Retorne SEMPRE um JSON válido.
"""

def review_node(state: AgencyState) -> AgencyState:
    """
    Nó do grafo responsável pela revisão do copy.
    Avalia o copy e decide se aprova ou solicita revisão.
    """
    print(f"🔎 [ReviewAgent] Revisando copy (tentativa {state.revision_count + 1}/{MAX_REVISIONS + 1})...")

    # Proteção contra loop infinito
    if state.revision_count >= MAX_REVISIONS:
        print(f"⚠️  [ReviewAgent] Máximo de revisões atingido. Aprovando com ressalvas.")
        return state.model_copy(update={
            "approved": True,
            "review_score": state.review_score or 6,
            "review_feedback": "Aprovado após máximo de revisões. Revise manualmente.",
            "status": "approved",
        })

    llm = get_llm()

    prompt =f"""
Avalie a seguinte copy de marketing:

━━━ CONTEXTO ━━━
Briefing: {state.briefing}
Público-alvo: {state.target_audience}
Tom de voz: {state.tone_of_voice}
USP: {state.usp}

━━━ COPY GERADO ━━━
Headline: {state.headline}
Tagline: {state.tagline}

Instagram Post:
{state.instagram_post}

LinkedIn Post:
{state.linkedin_post}

Email - Assunto: {state.email_subject}
Email - Corpo:
{state.email_body}

CTA: {state.cta}

━━━ AVALIE ━━━
Retorne EXATAMENTE este JSON:
{{
  "scores": {{
    "clareza": <0-10>,
    "relevancia": <0-10>,
    "persuasao": <0-10>,
    "tom_de_voz": <0-10>,
    "cta": <0-10>
  }},
  "score_final": <média dos 5 critérios, uma casa decimal>,
  "pontos_fortes": ["ponto 1", "ponto 2"],
  "pontos_a_melhorar": ["melhoria específica 1", "melhoria específica 2"],
  "approved": <true se score_final >= 7, senão false>,
  "feedback_para_copywriter": "Instrução clara e específica do que reescrever e como melhorar"
}}
"""
    
    messages = [
        SystemMessage(content=REVIEW_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]
    
    response = llm.invoke(messages)
    review = _parse_review(response.content)

    score = review.get("score_final", 5)
    approved = review.get("approved", score >= 7)

    if approved:
        print(f"✅ [ReviewAgent] Copy APROVADA! Score: {score}/10")
        new_status = "approved"
    else:
        print(f"🔄 [ReviewAgent] Copy Reprovada! Score: {score}/10. Solicitando revisão..")
        new_status = "writing"

    return state.model_copy(update={
        "approved": approved,
        "review_score": int(round(float(score))),
        "review_feedback": review.get("feedback_para_copywriter", ""),
        "revision_count": state.revision_count + (0 if approved else 1),
        "status": new_status,
    })


def _parse_review(raw: str) -> dict:
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
            "score_final": 7,
            "approved": True,
            "feedback_para_copywriter": "Aprovado (erro no parse da avaliação).",
        }
