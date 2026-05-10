# DECISIONS.md — Architecture & Workflow Decisions

> This file documents significant decisions about architecture, tooling, and workflow.
> Record a decision here when:
> - It affects how the project is structured or deployed
> - It is non-obvious why a particular approach was chosen
> - A future agent or developer might otherwise change it without understanding the reason
> - A meaningful tradeoff was made
>
> Do NOT document every minor implementation detail here — only decisions with lasting consequences.

---

## Format (ADR — Architecture Decision Record)

```markdown
## ADR-XXX: Title

**Date:** YYYY-MM-DD
**Status:** Accepted | Deprecated | Superseded by ADR-YYY
**Decided by:** human / Claude Code / Codex / Gemini + human confirmation

### Context
What situation or problem triggered this decision?

### Decision
What was decided?

### Rationale
Why this approach over alternatives?

### Consequences
What becomes easier or harder as a result?

### Alternatives considered
What else was considered and why rejected?
```

---

## ADR-000: Shared AI Repository State

**Date:** 2026-05-10
**Status:** Accepted
**Decided by:** human

### Context
Multiple AI agents (Claude Code, Codex, Gemini) work on the same codebase across different sessions. Each agent has independent context windows and no memory of previous sessions. Without a shared, version-controlled state, knowledge is lost between sessions and agents make conflicting decisions.

### Decision
This project uses the following files as the shared, authoritative AI state:

- `AGENTS.md` — universal rules for all agents
- `CLAUDE.md` — Claude Code adapter
- `GEMINI.md` — Gemini adapter
- `docs/ai/PROJECT.md` — permanent project context
- `docs/ai/CURRENT.md` — live working state
- `docs/ai/TASKS.md` — task board
- `docs/ai/DECISIONS.md` — this file (ADR log)
- `docs/ai/HANDOFF.md` — agent-to-agent handoff
- `docs/ai/CODE_REVIEW.md` — review rules
- `docs/ai/WORKFLOW.md` — daily workflow

### Rationale
Chat histories are not portable. They cannot be shared between tools, are lost when context windows fill, and cannot be reviewed or amended by humans. Repository files are version-controlled, durable, human-readable, and accessible by any agent.

### Consequences
- Every agent must read the AI state files before starting significant work.
- Every agent must update `CURRENT.md`, `TASKS.md`, and `HANDOFF.md` before ending a session.
- Humans must commit these files to Git regularly.
- The overhead is small compared to the benefit of reliable cross-agent continuity.

### Alternatives considered
- Relying on chat history: not portable, not version-controlled, lost on context window exhaustion.
- Using a separate database or API: adds infrastructure complexity, requires internet access, not universally available.

---

## ADR-001: Multi-Provider LLM Fallback via `invoke_resiliently()`

**Date:** 2026-05-10
**Status:** Accepted
**Decided by:** Sinan Uçar (human)

### Context

A portfolio AI chat backend must stay available even when individual LLM providers hit quota limits or timeouts. Relying on a single provider makes the demo unreliable during peak traffic or free-tier exhaustion.

### Decision

Implement `invoke_resiliently()` in `main.py` that tries 4 LLM providers in sequence:

1. `google:gemini-flash-latest`
2. `google:gemini-2.0-flash`
3. `openai:gpt-4o-mini`
4. `groq:llama-3.3-70b-versatile`

Falls through immediately on quota error or timeout.

### Rationale

- Maximizes uptime without complex infrastructure
- LangChain supports all 4 providers with a unified interface
- Free-tier quotas across multiple providers cover typical portfolio traffic
- No user-facing changes needed — fallback is transparent

### Consequences

- All 4 provider API keys must be configured in `.env`
- `check_models.py` verifies connectivity to all providers
- The function signature and behavior must remain stable — it is called by all 4 endpoints
- Do not add LangGraph or complex orchestration unless `invoke_resiliently()` proves insufficient

### Alternatives considered

- Single provider (OpenAI): simpler, but fails on quota exhaustion
- LangChain retry with one provider: does not help with quota limits
- LangSmith routing: adds infrastructure and cost not justified for a portfolio demo
