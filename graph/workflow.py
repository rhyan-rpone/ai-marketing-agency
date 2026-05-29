"""
workflow.py
───────────
Define o grafo de estados (StateGraph) do Marketing AI Agency.

Fluxo:
  START
    └─► research ──► strategy ──► copywriter ──► review
                                       ▲               │
                                       └── (revisão) ──┘
                                                       │
                                                     (aprovado)
                                                       │
                                                     END
"""

from langgraph.graph import StateGraph, START, END

from graph.state import AgencyState
from agents.research_agent import research_node
from agents.strategy_agent import strategy_node
from agents.copywriter_agent import copywriter_node
from agents.review_agent import review_node


def decide_after_review(state: AgencyState) -> str:
    """
    Edge condicional após o ReviewAgent.
    - Se aprovado → END
    - Se reprovado → copywriter (nova rodada de escrita com feedback)
    """
    if state.approved:
        return "end"
    return "copywriter"


def build_graph() -> StateGraph:
    """
    Constrói e compila o grafo de agentes.
    Retorna o grafo compilado, pronto para ser invocado.
    """
    graph = StateGraph(AgencyState)

    # ── Adiciona os nós ────────────────────────────────────────────────────
    graph.add_node("research",    research_node)
    graph.add_node("strategy",    strategy_node)
    graph.add_node("copywriter",  copywriter_node)
    graph.add_node("review",      review_node)

    # ── Define o fluxo principal ───────────────────────────────────────────
    graph.add_edge(START,        "research")
    graph.add_edge("research",   "strategy")
    graph.add_edge("strategy",   "copywriter")
    graph.add_edge("copywriter", "review")

    # ── Edge condicional no review ─────────────────────────────────────────
    graph.add_conditional_edges(
        "review",
        decide_after_review,
        {
            "end":        END,
            "copywriter": "copywriter",   # Loop de revisão
        }
    )

    return graph.compile()


# ── Instância global do grafo (singleton) ─────────────────────────────────
agency_graph = build_graph()


# ── Execução direta para teste local ──────────────────────────────────────
if __name__ == "__main__":
    import json

    test_briefing = """
    Lançar um tênis sustentável feito de materiais reciclados para jovens de 18 a 30 anos
    que se preocupam com meio ambiente e moda ao mesmo tempo. Preço: R$ 350. 
    Lançamento: Janeiro de 2025.
    """

    print("=" * 60)
    print("🚀 Marketing AI Agency — Execução de Teste")
    print("=" * 60)

    initial_state = AgencyState(briefing=test_briefing.strip())
    result = agency_graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Score de qualidade: {result.get('review_score', 'N/A')}/10")
    print(f"Revisões realizadas: {result.get('revision_count', 0)}")
    print(f"\n🎯 Headline: {result.get('headline', '')}")
    print(f"💬 Tagline:  {result.get('tagline', '')}")
    print(f"📣 CTA:      {result.get('cta', '')}")
    print(f"\n📱 Instagram:\n{result.get('instagram_post', '')}")
    print(f"\n📧 Email (assunto): {result.get('email_subject', '')}")
