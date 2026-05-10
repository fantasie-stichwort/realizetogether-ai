# PROJECT.md — Permanent Project Context

> This file describes stable, long-lived project facts.
> Update it when the stack, architecture, or conventions change.
> Do NOT use it for current working state — use `CURRENT.md` for that.

---

## Project Overview

**Name:** sinan-ucar-portfolio
**Purpose:** Sinans persönliches KI-Portfolio — FastAPI-Backend (4 AI-Endpunkte) + Astro-Frontend als Showcase auf sinanucar.com. Kein Produktivcode für RealizeTogether.
**Status:** active / production
**Primary users:** Visitors of sinanucar.com; potential employers / collaborators
**Repository:** TODO: confirm exact GitHub URL

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.12 (backend) | |
| Framework | FastAPI | 4 endpoints, LangChain orchestration |
| LLM Orchestration | LangChain | langchain-core, -google-genai, -openai, -groq, -anthropic |
| Validation | Pydantic BaseModel | `with_structured_output()` for structured LLM output |
| Frontend | Astro.js | Separate deployment in frontend/ |
| Hosting | Render | realizetogether-ai.onrender.com |
| Dev environment | Google Firebase Studio | .idx/dev.nix |
| Monitoring | Sentry | SENTRY_DSN via .env |

---

## Package Manager & Tooling

| Tool | Command | Notes |
|---|---|---|
| Package manager | pip | requirements.txt |
| Dev server | `bash start.sh` | from backend/, after activating venv |
| Dev server (alt) | `uvicorn main:app --reload --port 8000` | |
| Dependencies | `pip install -r requirements.txt` | |
| Model check | `python check_models.py` | verify all LLM providers respond |

---

## Repository Structure

```
backend/
  main.py          — FastAPI app, 4 endpoints
  start.sh         — dev server startup script
  check_models.py  — multi-provider connectivity test
  data/
    cv.md          — Sinan's CV (context for /api/chat)
frontend/          — Astro.js frontend (separate deployment)
.idx/
  dev.nix          — Firebase Studio dev environment config
```

---

## Architecture Notes

### Multi-Provider LLM Fallback

`invoke_resiliently()` tries providers in order, falls through on quota error / timeout:

1. `google:gemini-flash-latest`
2. `google:gemini-2.0-flash`
3. `openai:gpt-4o-mini`
4. `groq:llama-3.3-70b-versatile`

### API Endpoints

| Endpoint | Task | Notes |
|---|---|---|
| `POST /api/chat` | CV-Assistent — answers questions about Sinan's background | Context: `data/cv.md` |
| `POST /api/vision` | UX-Screenshot-Analyse → `VisionAnalysis` Pydantic model | |
| `POST /api/analyze` | Sentiment-Analyse → `SentimentAnalysis` Pydantic model | |
| `POST /api/agent` | Agent with tools (calculator, web_search, etc.) | Manual tool loop, no LangGraph |

---

## Coding Conventions

- **Structured Output:** always `llm.with_structured_output(PydanticModel)` — no manual JSON parsing
- **Errors:** LLM calls in try/except; use fallback actively — no silent catch without logging
- **Agent:** manual tool loop (no LangGraph) — keep as-is while it suffices
- **CORS:** maintain allowlist in `main.py` — no wildcard `*`
- **Secrets:** only via `.env` + `python-dotenv` — never hardcode
- **Uploads:** max 4 MB, only JPEG/PNG/WebP/GIF — type-check before processing

---

## Known Constraints & Fragile Areas

- Multi-provider fallback depends on all 4 provider API keys being valid
- `data/cv.md` is the single source of truth for the chat endpoint — keep it updated
- Frontend (Astro) is a separate deployment — changes there don't affect backend

---

## Environment Variables (names only)

```
SENTRY_DSN
GOOGLE_API_KEY
OPENAI_API_KEY
GROQ_API_KEY
ANTHROPIC_API_KEY
```

---

## External Dependencies & Integrations

| Service | Purpose | Notes |
|---|---|---|
| Google Gemini | Primary LLM provider | gemini-flash-latest, gemini-2.0-flash |
| OpenAI | Fallback LLM provider | gpt-4o-mini |
| Groq | Fallback LLM provider | llama-3.3-70b-versatile |
| Render | Backend hosting | realizetogether-ai.onrender.com |
| Sentry | Error monitoring | SENTRY_DSN required |
| Firebase Studio | Dev environment | .idx/dev.nix |

---

## Last Updated

- Date: 2026-05-10
- Updated by: Claude Code (migration from legacy CLAUDE.md)
- Reason: Initial migration into docs/ai/ structure via ai-dev-workflow-template
