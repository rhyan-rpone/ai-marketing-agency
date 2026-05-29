import json
import time
from html import escape
from typing import Any

import httpx
import streamlit as st


API_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 120
SAMPLE_BRIEFING = (
    "Lancar uma linha de cosmeticos veganos para mulheres de 25 a 40 anos "
    "que buscam beleza consciente. Preco medio: R$120. Objetivo: gerar leads "
    "e vender kits no lancamento de marco de 2025."
)

st.set_page_config(
    page_title="Marketing AI Agency",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #f6f7fb;
                --panel: #ffffff;
                --ink: #17202a;
                --muted: #667085;
                --line: #e6e8ef;
                --brand: #275efe;
                --brand-2: #00a676;
                --brand-3: #ffb020;
                --danger: #d92d20;
                --shadow: 0 18px 45px rgba(16, 24, 40, 0.08);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(39, 94, 254, 0.10), transparent 28rem),
                    linear-gradient(180deg, #fbfcff 0%, var(--bg) 48%, #ffffff 100%);
                color: var(--ink);
            }

            .block-container {
                max-width: 1240px;
                padding-top: 2.2rem;
                padding-bottom: 4rem;
            }

            [data-testid="stSidebar"] {
                background: #101828;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #f2f4f7;
            }

            [data-testid="stSidebar"] .stCaptionContainer,
            [data-testid="stSidebar"] p {
                color: #cbd5e1;
            }

            .hero {
                border: 1px solid rgba(39, 94, 254, 0.12);
                background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(242,246,255,0.92));
                border-radius: 8px;
                box-shadow: var(--shadow);
                padding: 2.1rem 2.2rem;
                margin-bottom: 1.4rem;
            }

            .eyebrow {
                color: var(--brand);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
            }

            .hero h1 {
                font-size: clamp(2.25rem, 5vw, 4.7rem);
                line-height: 0.96;
                margin: 0;
                letter-spacing: 0;
                color: #111827;
            }

            .hero p {
                max-width: 760px;
                color: var(--muted);
                font-size: 1.04rem;
                line-height: 1.65;
                margin: 1rem 0 0;
            }

            .chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 1.35rem;
            }

            .chip {
                border: 1px solid var(--line);
                border-radius: 999px;
                background: rgba(255,255,255,0.82);
                color: #344054;
                padding: 0.46rem 0.78rem;
                font-size: 0.84rem;
                font-weight: 700;
            }

            .panel {
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.94);
                border-radius: 8px;
                padding: 1.2rem;
                box-shadow: 0 10px 30px rgba(16, 24, 40, 0.06);
                height: 100%;
            }

            .panel-title {
                color: #101828;
                font-size: 0.92rem;
                font-weight: 800;
                margin-bottom: 0.35rem;
            }

            .panel-copy {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.55;
                margin-bottom: 0.8rem;
            }

            .step-card {
                border: 1px solid var(--line);
                border-radius: 8px;
                background: #ffffff;
                padding: 0.95rem;
                margin-bottom: 0.7rem;
            }

            .step-label {
                color: #101828;
                font-weight: 800;
                font-size: 0.92rem;
            }

            .step-desc {
                color: var(--muted);
                font-size: 0.84rem;
                line-height: 1.45;
                margin-top: 0.2rem;
            }

            .metric-card {
                border: 1px solid var(--line);
                background: #ffffff;
                border-radius: 8px;
                padding: 1rem;
                min-height: 108px;
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.78rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0;
            }

            .metric-value {
                color: #101828;
                font-size: 1.7rem;
                font-weight: 900;
                line-height: 1.1;
                margin-top: 0.35rem;
                overflow-wrap: anywhere;
            }

            .metric-note {
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.35rem;
            }

            .result-hero {
                border: 1px solid rgba(39, 94, 254, 0.16);
                background: linear-gradient(135deg, #111827, #1d2939);
                border-radius: 8px;
                padding: 1.5rem;
                color: #ffffff;
                margin: 1.1rem 0 1rem;
            }

            .result-hero .label {
                color: #98a2b3;
                font-size: 0.78rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0;
            }

            .result-hero h2 {
                color: #ffffff;
                font-size: clamp(1.55rem, 3vw, 2.4rem);
                line-height: 1.06;
                margin: 0.35rem 0 0.7rem;
                letter-spacing: 0;
            }

            .result-hero p {
                color: #d0d5dd;
                margin: 0.15rem 0;
                line-height: 1.55;
            }

            .content-card {
                border: 1px solid var(--line);
                background: #ffffff;
                border-radius: 8px;
                padding: 1.1rem;
                margin-bottom: 0.8rem;
            }

            .content-card h3 {
                color: #101828;
                font-size: 1.02rem;
                margin: 0 0 0.55rem;
                letter-spacing: 0;
            }

            .content-card p, .content-card li {
                color: #475467;
                line-height: 1.6;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.34rem 0.65rem;
                font-size: 0.8rem;
                font-weight: 800;
                border: 1px solid rgba(255,255,255,0.16);
                background: rgba(255,255,255,0.10);
            }

            .stTextArea textarea {
                border-radius: 8px;
                border: 1px solid #d0d5dd;
                box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
                font-size: 0.98rem;
                line-height: 1.55;
            }

            .stButton > button {
                border-radius: 8px;
                min-height: 3rem;
                font-weight: 850;
                border: 0;
                box-shadow: 0 12px 24px rgba(39, 94, 254, 0.22);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.35rem;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 8px;
                padding: 0.55rem 0.85rem;
                font-weight: 800;
            }

            div[data-testid="stAlert"] {
                border-radius: 8px;
            }

            @media (max-width: 760px) {
                .block-container {
                    padding-top: 1rem;
                }

                .hero {
                    padding: 1.25rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_health() -> tuple[bool, str]:
    try:
        response = httpx.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, "API online"
        return False, f"API respondeu {response.status_code}"
    except httpx.HTTPError:
        return False, "API offline"


def call_campaign_api(briefing: str) -> dict[str, Any]:
    response = httpx.post(
        f"{API_URL}/campaign",
        json={"briefing": briefing.strip()},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def safe_get(data: dict[str, Any], *keys: str, default: Any = "-") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current in (None, ""):
            return default
    return current


def html_text(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "-"))


def render_metric(label: str, value: Any, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html_text(label)}</div>
            <div class="metric-value">{html_text(value)}</div>
            <div class="metric-note">{html_text(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_content_card(title: str, body: Any) -> None:
    text = body if body not in (None, "") else "Nao informado pela API."
    safe_body = html_text(text).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="content-card">
            <h3>{html_text(title)}</h3>
            <p>{safe_body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list_card(title: str, items: Any) -> None:
    if not items:
        render_content_card(title, "Nao informado pela API.")
        return

    if isinstance(items, list):
        list_items = "".join(f"<li>{html_text(item)}</li>" for item in items)
    else:
        list_items = f"<li>{html_text(items)}</li>"

    st.markdown(
        f"""
        <div class="content-card">
            <h3>{html_text(title)}</h3>
            <ul>{list_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_competitors(items: Any) -> None:
    if not items:
        render_content_card("Concorrentes", "Nao informado pela API.")
        return

    rows = []
    for item in items:
        if isinstance(item, dict):
            name = html_text(item.get("name", "Concorrente"))
            positioning = html_text(item.get("positioning", "Posicionamento nao informado"))
            rows.append(f"<li><strong>{name}</strong>: {positioning}</li>")
        else:
            rows.append(f"<li>{html_text(item)}</li>")

    st.markdown(
        f"""
        <div class="content-card">
            <h3>Concorrentes</h3>
            <ul>{''.join(rows)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    online, message = api_health()
    status_color = "#12b76a" if online else "#f04438"

    with st.sidebar:
        st.markdown("## Marketing AI Agency")
        st.caption("Painel executivo para gerar campanhas multi-agente.")
        st.markdown(
            f"""
            <span class="status-pill">
                <span style="width:8px;height:8px;border-radius:50%;background:{status_color};display:inline-block;margin-right:8px;"></span>
                {message}
            </span>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("### Stack")
        st.caption("FastAPI")
        st.caption("LangGraph")
        st.caption("OpenAI")
        st.caption("Tavily API")
        st.caption("Streamlit")

        st.divider()
        st.markdown("### Pipeline")
        st.caption("1. Pesquisa de mercado")
        st.caption("2. Estrategia de campanha")
        st.caption("3. Copy para canais")
        st.caption("4. Revisao de qualidade")

        st.divider()
        st.caption(f"Endpoint: {API_URL}")


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">AI marketing operating system</div>
            <h1>Marketing AI Agency</h1>
            <p>
                Um cockpit de campanha com agentes especializados para pesquisa,
                estrategia, copywriting e revisao. Feito para mostrar arquitetura,
                produto e acabamento visual em uma unica demo.
            </p>
            <div class="chip-row">
                <span class="chip">Multi-agent workflow</span>
                <span class="chip">FastAPI backend</span>
                <span class="chip">Tavily research</span>
                <span class="chip">Recruiter-ready demo</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def load_sample_briefing() -> None:
    st.session_state["briefing"] = SAMPLE_BRIEFING


def render_input_area() -> str:
    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        st.markdown(
            """
            <div class="panel-title">Briefing da campanha</div>
            <div class="panel-copy">
                Descreva produto, publico, preco, canais e objetivo. Quanto melhor o briefing,
                mais forte fica a estrategia.
            </div>
            """,
            unsafe_allow_html=True,
        )

        briefing = st.text_area(
            "Briefing da campanha",
            label_visibility="collapsed",
            placeholder=(
                "Ex: Lancar tenis sustentavel para jovens de 18 a 30 anos. "
                "Preco: R$350. Objetivo: gerar awareness e pre-venda em Instagram, LinkedIn e email."
            ),
            height=180,
            key="briefing",
        )

        st.button(
            "Usar briefing de exemplo",
            use_container_width=True,
            on_click=load_sample_briefing,
        )

    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Como a campanha nasce</div>
                <div class="panel-copy">
                    O fluxo orquestra agentes com responsabilidades claras e devolve um pacote
                    pronto para apresentacao.
                </div>
                <div class="step-card">
                    <div class="step-label">Research Agent</div>
                    <div class="step-desc">Busca tendencias, concorrentes e insights de publico.</div>
                </div>
                <div class="step-card">
                    <div class="step-label">Strategy Agent</div>
                    <div class="step-desc">Define publico, tom, canais, objetivos e USP.</div>
                </div>
                <div class="step-card">
                    <div class="step-label">Copywriter Agent</div>
                    <div class="step-desc">Cria headline, posts, email e CTA.</div>
                </div>
                <div class="step-card">
                    <div class="step-label">Review Agent</div>
                    <div class="step-desc">Avalia qualidade e pede revisao quando necessario.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return briefing


def render_results(data: dict[str, Any], elapsed: float) -> None:
    score = safe_get(data, "review", "review_score", default="N/A")
    status = safe_get(data, "status", default="finalizado")
    revisions = safe_get(data, "review", "revision_count", default=0)
    generated_at = safe_get(data, "generated_at", default="-")

    st.markdown("## Resultado da campanha")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric("Score", f"{score}/10", "Qualidade final")
    with m2:
        render_metric("Status", status, "Estado do workflow")
    with m3:
        render_metric("Revisoes", revisions, "Iteracoes do copy")
    with m4:
        render_metric("Tempo", f"{elapsed:.1f}s", "Tempo desta execucao")

    headline = safe_get(data, "copy", "headline")
    tagline = safe_get(data, "copy", "tagline")
    cta = safe_get(data, "copy", "cta")

    st.markdown(
        f"""
        <section class="result-hero">
            <div class="label">Campanha final</div>
            <h2>{html_text(headline)}</h2>
            <p><strong>Tagline:</strong> {html_text(tagline)}</p>
            <p><strong>CTA:</strong> {html_text(cta)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    strategy_tab, copy_tab, research_tab, export_tab = st.tabs(
        ["Estrategia", "Pecas de copy", "Pesquisa", "Exportar"]
    )

    with strategy_tab:
        c1, c2 = st.columns(2)
        with c1:
            render_content_card("Publico-alvo", safe_get(data, "strategy", "target_audience"))
            render_content_card("Tom de voz", safe_get(data, "strategy", "tone_of_voice"))
        with c2:
            render_content_card("Proposta unica de valor", safe_get(data, "strategy", "usp"))
            render_list_card("Objetivos", safe_get(data, "strategy", "campaign_goals", default=[]))
        render_list_card("Canais recomendados", safe_get(data, "strategy", "channels", default=[]))

    with copy_tab:
        instagram, linkedin, email = st.tabs(["Instagram", "LinkedIn", "Email"])
        with instagram:
            render_content_card("Post para Instagram", safe_get(data, "copy", "instagram_post"))
        with linkedin:
            render_content_card("Post para LinkedIn", safe_get(data, "copy", "linkedin_post"))
        with email:
            render_content_card("Assunto", safe_get(data, "copy", "email_subject"))
            render_content_card("Corpo do email", safe_get(data, "copy", "email_body"))

    with research_tab:
        c1, c2 = st.columns(2)
        with c1:
            render_list_card("Tendencias de mercado", safe_get(data, "research", "market_trends", default=[]))
        with c2:
            render_competitors(safe_get(data, "research", "competitors", default=[]))
        render_content_card("Insights de publico", safe_get(data, "research", "target_insights"))

    with export_tab:
        st.markdown("### Pacote gerado")
        st.caption(f"Gerado em: {generated_at}")
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            "Baixar JSON da campanha",
            data=payload,
            file_name="marketing-ai-agency-campaign.json",
            mime="application/json",
            use_container_width=True,
        )
        st.code(payload, language="json")


def main() -> None:
    inject_css()
    render_sidebar()
    render_hero()

    briefing = render_input_area()

    generate = st.button(
        "Gerar campanha completa",
        type="primary",
        use_container_width=True,
        disabled=not briefing or len(briefing.strip()) < 20,
    )

    if generate:
        progress = st.progress(0)
        status = st.empty()

        try:
            started_at = time.perf_counter()
            for value, message in [
                (18, "Conectando com a API..."),
                (34, "Research Agent analisando mercado..."),
                (52, "Strategy Agent estruturando a campanha..."),
                (70, "Copywriter Agent criando as pecas..."),
                (86, "Review Agent avaliando qualidade..."),
            ]:
                progress.progress(value)
                status.caption(message)
                time.sleep(0.08)

            data = call_campaign_api(briefing)
            elapsed = time.perf_counter() - started_at
            progress.progress(100)
            status.success("Campanha gerada com sucesso.")

            st.session_state["last_campaign"] = data
            st.session_state["last_elapsed"] = elapsed

        except httpx.ConnectError:
            status.empty()
            progress.empty()
            st.error(
                "Nao consegui conectar na API. Inicie o backend FastAPI em http://localhost:8000 e tente novamente."
            )
        except httpx.HTTPStatusError as exc:
            status.empty()
            progress.empty()
            detail = exc.response.text
            st.error(f"A API retornou erro {exc.response.status_code}: {detail}")
        except httpx.TimeoutException:
            status.empty()
            progress.empty()
            st.error("A geracao demorou demais e atingiu o tempo limite. Tente um briefing menor.")
        except Exception as exc:
            status.empty()
            progress.empty()
            st.error(f"Erro inesperado: {exc}")

    if "last_campaign" in st.session_state:
        render_results(
            st.session_state["last_campaign"],
            st.session_state.get("last_elapsed", 0.0),
        )


if __name__ == "__main__":
    main()
