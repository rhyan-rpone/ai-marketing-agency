"""
StrategyAgent
─────────────
Responsabilidade: Com base nos dados de pesquisa, definir:
  - Público-alvo detalhado
  - Tom de voz
  - Canais de distribuição
  - Objetivos da campanha
  - USP (Unique Selling Proposition)
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgencyState


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.5,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


STRATEGY_SYSTEM_PROMPT = """
Você é um Estrategista de Marketing Sênior com 15 anos de experiência em branding e campanhas digitais.

Seu trabalho é transformar pesquisas de mercado em estratégias claras e acionáveis.

Você pensa em:
- Posicionamento diferenciado (não genérico)
- Públicos com dores específicas (não "todos os adultos")
- Tons de voz que criam conexão real
- Canais onde o público de fato está
- Propostas de valor únicas e memoráveis

Responda sempre em português brasileiro.
IMPORTANTE: Retorne sua resposta SEMPRE em formato JSON válido, sem markdown.
"""


def strategy_node(state: AgencyState) -> AgencyState:
    """
    Nó do grafo responsável pela estratégia da campanha.
    Lê os dados de pesquisa e produz a estratégia completa.
    """
    print("🧠 [StrategyAgent] Desenvolvendo estratégia da campanha...")

    llm = get_llm()

    # Monta contexto com os dados de pesquisa
    trends_text = "\n".join([f"  • {t}" for t in (state.market_trends or [])])
    competitors_text = "\n".join([
        f"  • {c.get('name', '')}: {c.get('positioning', '')}"
        for c in (state.competitors or [])
    ])

    prompt = f"""
Briefing original:
{state.briefing}

Tendências de mercado identificadas:
{trends_text or "Não disponível"}

Concorrentes:
{competitors_text or "Não disponível"}

Insights do público:
{state.target_insights or "Não disponível"}

Crie a estratégia completa retornando EXATAMENTE este JSON (sem nenhum texto antes ou depois):

{{
  "target_audience": "Descrição detalhada do público-alvo (idade, comportamentos, dores, desejos)",
  "tone_of_voice": "Como a marca deve se comunicar (ex: inspirador e direto, técnico e confiável)",
  "channels": ["canal1", "canal2", "canal3"],
  "campaign_goals": ["objetivo1", "objetivo2", "objetivo3"],
  "usp": "Uma frase que captura o diferencial único da oferta frente aos concorrentes"
}}
"""

    messages = [
        SystemMessage(content=STRATEGY_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    strategy = _parse_strategy(response.content)

    print(f"✅ [StrategyAgent] Estratégia definida. Canais: {strategy.get('channels', [])}")

    return state.model_copy(update={
        "target_audience": strategy.get("target_audience", ""),
        "tone_of_voice": strategy.get("tone_of_voice", ""),
        "channels": strategy.get("channels", []),
        "campaign_goals": strategy.get("campaign_goals", []),
        "usp": strategy.get("usp", ""),
        "status": "writing",
    })


def _parse_strategy(raw: str) -> dict:
    """Parseia o JSON da resposta do LLM com fallback seguro."""
    try:
        # Remove blocos de markdown se houver
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except (json.JSONDecodeError, IndexError):
        # Fallback: retorna estrutura mínima
        return {
            "target_audience": raw[:200],
            "tone_of_voice": "Profissional e próximo",
            "channels": ["Instagram", "Email", "LinkedIn"],
            "campaign_goals": ["Aumentar awareness", "Gerar leads"],
            "usp": "Produto diferenciado para o mercado",
        }
