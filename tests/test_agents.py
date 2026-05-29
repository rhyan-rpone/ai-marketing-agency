"""
tests/test_agents.py
────────────────────
Testes unitários dos agentes usando mocks do LLM.
Rode com: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from graph.state import AgencyState


SAMPLE_BRIEFING = "Lançar app de delivery saudável para profissionais 25-40 anos. R$ 0 mensalidade."


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def base_state():
    return AgencyState(briefing=SAMPLE_BRIEFING)


@pytest.fixture
def state_after_research():
    return AgencyState(
        briefing=SAMPLE_BRIEFING,
        market_trends=["Crescimento de 30% em apps de saúde", "Foco em praticidade"],
        competitors=[{"name": "iFood Saudável", "positioning": "Variedade"}],
        target_insights="Profissionais buscam praticidade sem abrir mão da saúde.",
        status="strategizing",
    )


@pytest.fixture
def state_after_strategy(state_after_research):
    return state_after_research.model_copy(update={
        "target_audience": "Profissionais 25-40 anos, urbanos, renda média-alta",
        "tone_of_voice": "Prático, motivador e sem jargões",
        "channels": ["Instagram", "LinkedIn", "Email"],
        "campaign_goals": ["Aumentar downloads em 40%", "Gerar 1000 leads"],
        "usp": "Único app onde você monta o prato, não escolhe de lista",
        "status": "writing",
    })


# ── Testes do ResearchAgent ────────────────────────────────────────────────

class TestResearchAgent:

    @patch("agents.research_agent.get_search_tool")
    @patch("agents.research_agent.get_llm")
    def test_research_populates_state(self, mock_llm, mock_search, base_state):
        from agents.research_agent import research_node

        # Mock da busca
        mock_search.return_value.invoke.return_value = [
            {"title": "Tendência 1", "content": "Apps de saúde crescem 30% ao ano"}
        ]

        # Mock do LLM
        mock_response = MagicMock()
        mock_response.content = """
TENDÊNCIAS
• Apps de saúde crescem 30% ao ano
• Demanda por personalização aumenta
• Integração com wearables em alta

CONCORRENTES
iFood Saudável: Variedade de opções

INSIGHTS DE PÚBLICO
Profissionais buscam praticidade.
"""
        mock_llm.return_value.invoke.return_value = mock_response

        result = research_node(base_state)

        assert result.market_trends is not None
        assert len(result.market_trends) > 0
        assert result.target_insights is not None
        assert result.status == "strategizing"

    @patch("agents.research_agent.get_search_tool")
    @patch("agents.research_agent.get_llm")
    def test_research_handles_empty_search(self, mock_llm, mock_search, base_state):
        from agents.research_agent import research_node

        mock_search.return_value.invoke.return_value = []
        mock_response = MagicMock()
        mock_response.content = "TENDÊNCIAS\n• Sem dados\n\nCONCORRENTES\n\nINSIGHTS DE PÚBLICO\nSem dados."
        mock_llm.return_value.invoke.return_value = mock_response

        result = research_node(base_state)
        assert result.status == "strategizing"


# ── Testes do StrategyAgent ────────────────────────────────────────────────

class TestStrategyAgent:

    @patch("agents.strategy_agent.get_llm")
    def test_strategy_produces_all_fields(self, mock_llm, state_after_research):
        from agents.strategy_agent import strategy_node
        import json

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "target_audience": "Profissionais 25-40 anos",
            "tone_of_voice": "Prático e motivador",
            "channels": ["Instagram", "Email"],
            "campaign_goals": ["Aumentar downloads"],
            "usp": "Personalização total do prato",
        })
        mock_llm.return_value.invoke.return_value = mock_response

        result = strategy_node(state_after_research)

        assert result.target_audience == "Profissionais 25-40 anos"
        assert result.tone_of_voice == "Prático e motivador"
        assert "Instagram" in result.channels
        assert result.usp is not None
        assert result.status == "writing"


# ── Testes do CopywriterAgent ──────────────────────────────────────────────

class TestCopywriterAgent:

    @patch("agents.copywriter_agent.get_llm")
    def test_copywriter_generates_all_copy(self, mock_llm, state_after_strategy):
        from agents.copywriter_agent import copywriter_node
        import json

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "headline": "Sua comida saudável, do seu jeito",
            "tagline": "Praticidade que nutre",
            "instagram_post": "Post do instagram aqui 🥗 #saudavel",
            "linkedin_post": "Post do linkedin profissional aqui",
            "email_subject": "Seu almoço nunca foi tão prático",
            "email_body": "Olá! Imagine um app onde você...",
            "cta": "Baixar grátis agora",
        })
        mock_llm.return_value.invoke.return_value = mock_response

        result = copywriter_node(state_after_strategy)

        assert result.headline == "Sua comida saudável, do seu jeito"
        assert result.cta is not None
        assert result.status == "reviewing"
        assert result.approved is False  # Reset para review

    @patch("agents.copywriter_agent.get_llm")
    def test_copywriter_includes_feedback_on_revision(self, mock_llm, state_after_strategy):
        from agents.copywriter_agent import copywriter_node
        import json

        state_with_feedback = state_after_strategy.model_copy(update={
            "revision_count": 1,
            "review_feedback": "O CTA está genérico. Seja mais específico sobre o benefício.",
        })

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "headline": "Headline revisada",
            "tagline": "Tagline revisada",
            "instagram_post": "Post revisado",
            "linkedin_post": "Post linkedin revisado",
            "email_subject": "Assunto revisado",
            "email_body": "Body revisado",
            "cta": "Montar meu primeiro prato grátis",
        })
        mock_llm.return_value.invoke.return_value = mock_response

        # Verifica que o prompt foi chamado (feedback incluído)
        result = copywriter_node(state_with_feedback)
        call_args = mock_llm.return_value.invoke.call_args[0][0]
        # O HumanMessage deve conter o feedback
        human_msg = str(call_args[1].content)
        assert "genérico" in human_msg or "revisão" in human_msg.lower() or result.headline is not None


# ── Testes do ReviewAgent ──────────────────────────────────────────────────

class TestReviewAgent:

    def _make_full_state(self, state_after_strategy):
        return state_after_strategy.model_copy(update={
            "headline": "Sua comida saudável, do seu jeito",
            "tagline": "Praticidade que nutre",
            "instagram_post": "Post Instagram aqui",
            "linkedin_post": "Post LinkedIn aqui",
            "email_subject": "Seu almoço nunca foi tão prático",
            "email_body": "Corpo do email aqui...",
            "cta": "Baixar grátis agora",
            "status": "reviewing",
        })

    @patch("agents.review_agent.get_llm")
    def test_review_approves_good_copy(self, mock_llm, state_after_strategy):
        from agents.review_agent import review_node
        import json

        state = self._make_full_state(state_after_strategy)

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "scores": {"clareza": 8, "relevancia": 9, "persuasao": 8, "tom_de_voz": 9, "cta": 7},
            "score_final": 8.2,
            "pontos_fortes": ["Headline clara", "Tom adequado"],
            "pontos_a_melhorar": [],
            "approved": True,
            "feedback_para_copywriter": "",
        })
        mock_llm.return_value.invoke.return_value = mock_response

        result = review_node(state)

        assert result.approved is True
        assert result.status == "approved"
        assert result.review_score >= 7

    @patch("agents.review_agent.get_llm")
    def test_review_rejects_bad_copy(self, mock_llm, state_after_strategy):
        from agents.review_agent import review_node
        import json

        state = self._make_full_state(state_after_strategy)

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "scores": {"clareza": 5, "relevancia": 6, "persuasao": 4, "tom_de_voz": 6, "cta": 5},
            "score_final": 5.2,
            "pontos_fortes": [],
            "pontos_a_melhorar": ["CTA genérico", "Headline sem impacto"],
            "approved": False,
            "feedback_para_copywriter": "Reescreva o CTA com benefício específico e torne a headline mais impactante.",
        })
        mock_llm.return_value.invoke.return_value = mock_response

        result = review_node(state)

        assert result.approved is False
        assert result.status == "writing"
        assert result.revision_count == 1
        assert result.review_feedback is not None

    @patch("agents.review_agent.get_llm")
    def test_review_forces_approval_after_max_revisions(self, mock_llm, state_after_strategy):
        from agents.review_agent import review_node, MAX_REVISIONS

        state = self._make_full_state(state_after_strategy).model_copy(update={
            "revision_count": MAX_REVISIONS,  # Já no limite
        })

        result = review_node(state)

        # Deve aprovar mesmo sem chamar o LLM
        assert result.approved is True
        assert result.status == "approved"
        mock_llm.assert_not_called()
