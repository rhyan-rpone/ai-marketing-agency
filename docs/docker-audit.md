# Docker Audit

Auditoria realizada para tornar o Marketing AI Agency executavel via Docker.

## Ajustes Necessarios Identificados

- Criar `Dockerfile` e `docker-compose.yml` na raiz do projeto.
- Remover `tests/Dockerfile` e `tests/docker-compose.yml`, pois estavam vazios.
- Tornar `API_URL` configuravel na UI via variavel de ambiente.
- Validar `OPENAI_API_KEY` e `TAVILY_API_KEY` antes de executar agentes.
- Manter `/health` independente das chaves para healthchecks de container.
- Remover dependencias nao utilizadas do `requirements.txt`.
- Adicionar dependencias importadas diretamente e antes implicitas:
  `langchain-community`, `langchain-core`, `tavily-python` e `httpx`.
- Ignorar caches temporarios criados por pytest no Windows.
- Documentar o fluxo Docker-first no README.

## Dependencias Diretas

As dependencias diretas usadas pelo projeto estao fixadas em `requirements.txt`:

- `fastapi`
- `httpx`
- `langchain-community`
- `langchain-core`
- `langchain-openai`
- `langgraph`
- `openai`
- `pydantic`
- `python-dotenv`
- `streamlit`
- `tavily-python`
- `uvicorn`
- `pytest`

## Compatibilidade Entre Modulos

- `api.main` importa `graph.workflow` e expõe FastAPI.
- `graph.workflow` orquestra agentes em `agents/`.
- Agentes compartilham o estado em `graph.state`.
- `ui.app` chama a API por `API_URL`, usando `http://localhost:8000` fora do Docker
  e `http://api:8000` dentro do Compose.

## Validacoes Executadas

- `python -m py_compile api/main.py ui/app.py`
- `python -m pytest tests -v`
- `pip install --dry-run --ignore-installed -r requirements.txt`
- Parser YAML em `docker-compose.yml`
- `/health` sem chaves obrigatorias
- `POST /campaign` sem chaves obrigatorias retornando erro claro

Docker nao estava instalado no ambiente local desta auditoria, entao `docker compose up --build`
precisa ser executado em uma maquina com Docker disponivel.
