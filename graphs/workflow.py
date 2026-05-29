from langgraph.graph import StateGraph, START, END

from graph.state import AgencySttate
from agents.research_agent import research_node
from agents.strategy_agent import strategy_node
from agents.copywritter_agent import copywritter_node
from agents.review_agent import review_node

def decide_after_review(state: AgencyState)   -> str:
    """
    Edge condicional validando logo após o ReviewAgent
    - Se aprovado, END
    - Se for reprovado vai pro copywritter, nova escrita com feedback ate 2x
    """
    if state.approved:
        return "end"
    return "copywriter"

def build_graph() -> StateGraph:
    """
    Constrói e compula o grafo de agentes.
    Retorna o grafo compilado, pronto para ser invocado"""

    graph = StateGraph(AgencyState)

    ## Adicionando os nós
    graph.add_node("research",    research_node)
    graph.add_node("strategy",    strategy_node)
    graph.add_node("copywriter",  copywriter_node)
    graph.add_node("review",     review_node)

    ## Fluxo principal
    graph.add_edge(START, "research")
    graph.add_edge("research", "strategy")
    graph.add_edge("strategy", "copywriter")
    graph.add_edge("copywriter", "review")



    ## Edge condicional pro review
    graph.add_conditional_edges(
        "review",
        decide_after_review,
        {
            "end":            END,
            "copywriter":     "copywriter", ## Loop da revisão
        }
    )

    return graph.compile()

# Instância global do grafo
agency_graph = build_graph()

f __name__ == "__main__":
    import json

# Execução direta pra teste local

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
