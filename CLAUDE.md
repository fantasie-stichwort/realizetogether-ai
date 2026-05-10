# CLAUDE.md — Claude Code Configuration

@AGENTS.md

---

## Claude Code — Specific Instructions

This file configures Claude Code for this project.
The central rule file is `AGENTS.md`. All rules defined there apply here in full.

---

## Project Identity

**Name:** sinan-ucar-portfolio
**URL:** sinanucar.com
**Purpose:** Sinans persönliches KI-Portfolio-Backend. FastAPI-Backend (4 Endpunkte) + Astro-Frontend (Showcase).

---

## Stack

### Migrated from legacy CLAUDE.md

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI + Python 3.12 | LangChain (langchain-core, -google-genai, -openai, -groq, -anthropic) |
| Validation | Pydantic BaseModel | `with_structured_output()` |
| Frontend | Astro.js | frontend/ — separates Deployment |
| Deploy | Render | realizetogether-ai.onrender.com |
| Dev-Env | Google Firebase Studio | .idx/dev.nix |
| Monitoring | Sentry | SENTRY_DSN via .env |

---

## Commands

```bash
# Backend starten (aus backend/)
source .venv/bin/activate
bash start.sh               # oder: uvicorn main:app --reload --port 8000

# Dependencies
pip install -r requirements.txt

# Modelle testen
python check_models.py
```

---

## Architecture: Multi-Provider Fallback

`invoke_resiliently()` tries models in order:

1. `google:gemini-flash-latest`
2. `google:gemini-2.0-flash`
3. `openai:gpt-4o-mini`
4. `groq:llama-3.3-70b-versatile`

Falls through on quota error / timeout.

---

## API Endpoints

| Endpoint | Task | Key File |
|---|---|---|
| `POST /api/chat` | CV-Assistent (context: `data/cv.md`) | `main.py` |
| `POST /api/vision` | UX-Screenshot-Analyse → `VisionAnalysis` | `main.py` |
| `POST /api/analyze` | Sentiment-Analyse → `SentimentAnalysis` | `main.py` |
| `POST /api/agent` | Agent with tools (calculator, web_search, etc.) | `main.py` |

---

## Coding Rules

- **Structured Output:** always `llm.with_structured_output(PydanticModel)` — no manual JSON parsing
- **Errors:** LLM calls in try/except, use fallback actively — no silent catch without logging
- **Agent:** manual tool loop (no LangGraph) — keep as-is while it suffices
- **CORS:** maintain allowlist in `main.py` — no wildcard `*`
- **Secrets:** only via `.env` + `python-dotenv` — never hardcode
- **Uploads:** max 4 MB, only JPEG/PNG/WebP/GIF — type-check before processing

---

## Context Authority

**Trust the repository files, not the chat history.**

If the chat history contradicts what is written in `docs/ai/PROJECT.md`, `docs/ai/CURRENT.md`, or `docs/ai/HANDOFF.md`, the repository files take precedence.

---

## Before Starting Any Significant Work

1. Read `AGENTS.md` (full rule set).
2. Read `docs/ai/PROJECT.md` — tech stack and conventions.
3. Read `docs/ai/CURRENT.md` — active goal and branch.
4. Read `docs/ai/TASKS.md` — in progress, next, blocked.
5. Read `docs/ai/HANDOFF.md` — previous agent's handoff.
6. Summarize understanding in 5–10 bullet points before touching any file.

---

## End of Session

Before finishing:

1. Update `docs/ai/CURRENT.md` with current status, last action, next step.
2. Update `docs/ai/TASKS.md` — move completed tasks, add discovered tasks.
3. Update `docs/ai/HANDOFF.md` with full handoff summary.

Handoff must be complete enough that a fresh Codex or Gemini session can continue without asking for context.
