# CURRENT.md — Current Working State

> **This file must be updated at the end of every meaningful AI session.**
> It represents the live state of the work — not a backlog, not a history.
> If it is out of date, the next agent will start from wrong assumptions.

---

## Last Updated

- **Date:** TODO: YYYY-MM-DD HH:MM
- **Updated by:** TODO: Claude Code / Codex / Gemini / human
- **Session duration:** TODO: approximate

---

## Current Goal

TODO: one clear sentence — what is being worked on right now?

Example: "Implement user authentication using Supabase Auth with email/password."

---

## Current Branch

```
TODO: git branch name
e.g., feat/user-auth
```

---

## Status

### Done (this session)
- [ ] TODO: list what was completed in this session

### In Progress
- [ ] TODO: list what is actively being worked on

### Blocked
- [ ] TODO: describe any blockers — what is blocking, why, and what is needed to unblock

---

## Relevant Files

TODO: list files that are central to the current work.

```
src/path/to/file.ts      — reason why it matters
src/another/file.ts      — reason why it matters
```

---

## Current Git State

```
TODO: paste output of `git status` and `git diff --stat` here, or describe
e.g.:
Branch: feat/user-auth
Modified: src/lib/auth/session.ts, src/app/api/auth/route.ts
Untracked: src/lib/auth/types.ts
```

---

## Known Problems

TODO: list any bugs, errors, or incorrect behaviors discovered during this session.

Examples:
- Login redirect does not preserve the original URL
- TypeScript error in `session.ts` line 42 — type mismatch not yet resolved

---

## Assumptions Made

TODO: list any assumptions made during this session that should be verified.

Examples:
- Assumed Supabase project is already set up with email auth enabled
- Assumed `DATABASE_URL` is set in `.env.local`

---

## Next Step

TODO: one concrete, actionable next step for the next agent or human.

Example: "Fix the TypeScript error in `src/lib/auth/session.ts:42`, then run `pnpm typecheck` to verify."

---

## Notes for Next Agent

TODO: anything the next agent should know that doesn't fit the above structure.
