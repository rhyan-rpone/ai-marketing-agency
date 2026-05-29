"""
ResearchAgent
─────────────
Responsabilidade: Pesquisar tendências de mercado, concorrentes e
insights sobre o público-alvo a partir do briefing da campanha.

Ferramentas: TavilySearchResults (busca web em tempo real)
"""

import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgencyState

# Configuração da LLM
def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

# Ferramenta de Web Search
def get_search_tool() -> TavilySearchResults:
    return TavilySearchResults(
    max_results=5,
    api_key=os.getenv("TAVILY_API_KEY"),
    include_answer=True,
    include_raw_content=False,
    )

# Prompt do sistema de WebSearch
RESEARCH_SYSTEM_PROMPT = """
Você é um Analista de Mercado especializado em pesquisa para campanhas de marketing.

Sua função é transformar um briefing de campanha em insights acionáveis de mercado.

Para cada briefing, você deve identificar:
1. TENDÊNCIAS DE MERCADO: 3-5 tendências relevantes do setor
2. CONCORRENTES: 2-3 concorrentes diretos com seu posicionamento
3. INSIGHTS DE PÚBLICO: Comportamentos, dores e desejos do público-alvo

Seja específico, baseado em dados reais e direto ao ponto.
Responda sempre em português brasileiro.
"""

# Função principal do node
def research_node(state: AgencyState) -> AgencyState:
    """
    Nó do grafo responsável pela pesquisa de mercado.
    Recebe o estado com o briefing e popula os campos de pesquisa.
    """
    print("🔍 [ResearchAgent] Iniciando pesquisa de mercado...")

    llm = get_llm()
    search = get_search_tool()

  # 1. Busca web baseada no briefing
    search_query = f"tendências mercado {state.briefing} 2024 marketing"
    search_results = search.invoke(search_query)

  # Formata os resultados de busca para o LLM
    search_context = "\n".join([
        f"- {r.get('title', '')}: {r.get('content', '')[:300]}"
        for r in search_results
        if isinstance(r, dict)
    ])

    # 2. LLM analisa os resultados e extrai insights estruturados
    prompt = f"""
Briefing da campanha:
{state.briefing}

Resultados da pesquisa encontrados:
{search_context}

Com base no briefing e nos resultados de pesquisa, forneça:

TENDÊNCIAS (liste 4 tendências relevantes, uma por linha, começando com •):

CONCORRENTES (liste 2-3 concorrentes no formato "Nome: Posicionamento"):

INSIGHTS DE PÚBLICO (parágrafo único com os principais insights):
"""
    
    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    raw_output = response.content

   # 3. Parseia a resposta do LLM
    trends, competitors, insights = _parse_research_output(raw_output)

    print(f"✅ [ResearchAgent] Pesquisa concluída. {len(trends)} tendências, {len(competitors)} concorrentes.")

    return state.model_copy(update={
        "market_trends": trends,
        "competitors": competitors,
        "target_insights": insights,
        "status": "strategizing",
    })


def _parse_research_output(raw: str) -> tuple[list, list, str]:
    """Extrai tendências, concorrentes e insights da repsosta do LLM"""
    lines = raw.strinp().split("\n")
    trends, competitors, insights = [], [], ""

    section = None
    insight_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "TENDÊNCIAS" in line.upper():
            section = "trends"
        elif "CONCORRENTES" in line.upper():
            section = "competitors"
        elif "INSIGHTS" in line.upper():
            section = "insights"
        elif section == "trends" and line.startswith("•"):
            trends.append(line[1:].strip())
        elif section == "competitors" and ":" in line:
            parts = line.split(":", 1)
            competitors.append({
                "name": parts[0].strip().lstrip("-").strip(),
                "positioning": parts[1].strip() if len(parts) > 1 else ""
            })
        elif section == "insights":
            insight_lines.append(line)

    insights = " ".join(insight_lines).strip()

    # Fallback se o parse falhar
    if not trends:
        trends = ["Tendência não identificada — revise o briefing"]
    if not insights:
        insights = raw[:500]

    return trends, competitors, insights
