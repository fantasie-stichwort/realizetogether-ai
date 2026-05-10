# HANDOFF.md — Agent-to-Agent Handoff

> **This file enables any agent to continue work without chat history.**
> It must be updated at the end of every meaningful AI session.
> The rule: if the next agent cannot understand the situation from this file alone, the handoff is incomplete.

---

## Last Updated

- **Date:** TODO: YYYY-MM-DD HH:MM
- **Updated by:** TODO: Claude Code / Codex / Gemini / human
- **Handoff to:** TODO: Claude Code / Codex / Gemini / human / unspecified

---

## Short Summary

TODO: 2–3 sentences. What is the state of the project right now? What happened this session?

Example: "Implemented the login form UI and wired it to the Supabase Auth signIn method. The form works but the redirect after login is broken — it goes to `/` instead of the intended `/dashboard`. This needs to be fixed next."

---

## Last Action

TODO: what was the very last thing done before writing this handoff?

Example: "Committed `src/components/LoginForm.tsx` and `src/app/login/page.tsx`. Tests not yet written."

---

## Changed Files

TODO: list all files modified, created, or deleted during this session.

| File | Change type | Notes |
|---|---|---|
| TODO: path/to/file.ts | modified / created / deleted | brief reason |

---

## Open Items

TODO: what is incomplete, unverified, or intentionally left for the next session?

- [ ] TODO: open item
- [ ] TODO: open item

---

## Risks / Attention

TODO: what could break? What areas are fragile? What should the next agent be careful about?

Examples:
- The auth middleware has not been updated — it may block the new login route
- No error handling for network failures in the form
- TypeScript strict mode may flag the optional chaining in `session.ts`

---

## Checks

TODO: what was verified before ending the session?

| Check | Status | Notes |
|---|---|---|
| `pnpm typecheck` | TODO: passed / failed / not run | TODO |
| `pnpm test` | TODO: passed / failed / not run | TODO |
| `pnpm lint` | TODO: passed / failed / not run | TODO |
| Manual smoke test | TODO: done / not done | TODO |

---

## Next Concrete Action

TODO: one specific, actionable instruction for the next agent.

Example: "Fix the redirect in `src/app/login/page.tsx` — after successful sign-in, redirect to `/dashboard` instead of `/`. Then run `pnpm typecheck` and `pnpm test`."

---

## Ideal Next Prompt

TODO: copy-paste ready prompt for the next agent. Include context so they can start immediately.

```
Read docs/ai/HANDOFF.md, docs/ai/CURRENT.md, and docs/ai/PROJECT.md first.

Current situation: [paste Short Summary here]

Your task: [paste Next Concrete Action here]

After completing the task, update docs/ai/CURRENT.md, docs/ai/TASKS.md, and docs/ai/HANDOFF.md.
```
