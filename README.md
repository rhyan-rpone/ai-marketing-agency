# 🚀 Marketing AI Agency

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-MultiAgent-green)
![FastAPI](https://img.shields.io/badge/FastAPI-API-success)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![License](https://img.shields.io/badge/license-MIT-black)

Sistema Multi-Agente construído com LangGraph que simula um departamento completo de marketing.

O usuário fornece um briefing e múltiplos agentes especializados colaboram para pesquisar mercado, criar estratégia, gerar copy, revisar qualidade e entregar campanhas completas.

---

# 🎯 Problema

Criar campanhas completas normalmente exige:

- Pesquisa de mercado
- Estratégia
- Copywriting
- Revisões
- Aprovação

Este projeto automatiza esse fluxo utilizando múltiplos agentes especializados trabalhando juntos.

---

# ✨ Features

✅ Arquitetura Multi-Agent com LangGraph

✅ State Management compartilhado

✅ Orquestração via grafo de estados

✅ Pesquisa automática de mercado

✅ Estratégia de marketing automatizada

✅ Geração de copy

✅ Sistema de revisão automática

✅ Human-in-the-loop

✅ API REST

✅ Interface Web

✅ Dockerizado

✅ Testes automatizados

---

# 🏗 Arquitetura

```text
                    +----------------+
                    |    User Input  |
                    +--------+-------+
                             |
                             v

                  +--------------------+
                  | Orchestrator Agent |
                  +---------+----------+
                            |
                            v

                    +---------------+
                    | ResearchAgent |
                    +-------+-------+
                            |
                            v

                    +---------------+
                    | StrategyAgent |
                    +-------+-------+
                            |
                            v

                    +----------------+
                    | CopywriterAgent|
                    +--------+-------+
                             |
                             v

                     +--------------+
                     | ReviewAgent  |
                     +------+-------+
                            |

                 Approved? ---- NO
                      |            ^
                      |            |
                     YES           |
                      |____________|

                            |
                            v

                     +--------------+
                     | Final Output |
                     +--------------+
```

---

# 📂 Estrutura do Projeto

```text
marketing-ai-agency/

├── agents/
│   ├── orchestrator.py
│   ├── research_agent.py
│   ├── strategy_agent.py
│   ├── copywriter_agent.py
│   └── review_agent.py

├── graph/
│   ├── state.py
│   └── workflow.py

├── api/
│   └── main.py

├── tools/

├── ui/
│   └── app.py

├── tests/

├── requirements.txt

├── Dockerfile

└── README.md
```

---

# 🧠 Tecnologias

| Tecnologia | Uso |
|----------|----------|
| Python | Core |
| LangGraph | Orquestração Multi-Agent |
| LangChain | Abstrações LLM |
| FastAPI | API |
| Streamlit | Interface |
| Tavily | Pesquisa |
| Docker | Deploy |
| Pytest | Testes |

---

# ⚙️ Instalação

Clone o projeto:

```bash
git clone https://github.com/SEU_USER/marketing-ai-agency.git

cd marketing-ai-agency
```

Crie ambiente virtual:

```bash
python -m venv venv
```

Ative:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

Instale dependências:

```bash
pip install -r requirements.txt
```

---

# 🔑 Variáveis de Ambiente

Crie:

```text
.env
```

Adicione:

```env
OPENAI_API_KEY=

TAVILY_API_KEY=
```

---

# 🚀 Rodando API

```bash
uvicorn api.main:app --reload
```

API disponível:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 🖥 Rodando Interface

```bash
streamlit run ui/app.py
```

---

# 🐳 Docker

Build:

```bash
docker compose up --build
```

---

# 📬 Exemplo de Request

POST:

```json
{
   "briefing":"Lançar marca de tênis sustentável para jovens"
}
```

Resposta:

```json
{

"research_data":{

"market":"Growing",

"competitors":[...]

},

"strategy":{

"target":"18-30",

"tone":"modern"

},

"copy":{

"headline":"Move the Future",

"cta":"Shop Now"

}

}
```

---

# 🔄 Workflow

```text
Briefing

↓

Research

↓

Strategy

↓

Copy Generation

↓

Review

↓

Approved?

↓

Output
```

---

# 🧪 Rodando Testes

```bash
pytest
```

---

# 📈 Roadmap

- [ ] Persistent Memory
- [ ] Redis Checkpointer
- [ ] Multi-LLM Support
- [ ] Campaign PDF Export
- [ ] Metrics Dashboard
- [ ] Observability

---

# 📸 Screenshots

Adicionar:

- Interface Streamlit

- Graph visualization

- Output example

- API Swagger

---

# 💡 Possíveis Aplicações

- Marketing Agencies

- Growth Teams

- Startups

- Content Teams

- Digital Products

- Consultants

---

# 👨‍💻 Autor

Rhyan Pablo

AI Engineer • Automation • Multi-Agent Systems • Applied AI

LinkedIn:

[SEU LINK]

---

# ⭐ Gostou?

Se esse projeto foi útil:

Star ⭐ no repositório