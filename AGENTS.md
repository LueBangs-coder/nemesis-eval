# AGENTS.md — Nemesis

Operating contract for Codex (and any Codex-family coding agent) working in the Nemesis repo.

**Project:** Nemesis — Python evaluation harness for agentic failure modes.
**Reference spec:** `BUILD_SPEC.md`.
**Parent project:** Pantheon (private operating context).

---

## Canonical doctrine

The full doctrine, operating rules, stop conditions, and current-phase definition live in `CLAUDE.md`. **That file is the single source of truth for how any agent operates in this repo.** Codex must apply the same doctrine as Claude Code — no agent gets a softer contract.

Read `CLAUDE.md` end to end before doing anything in this repo. Then read `BUILD_SPEC.md`.

This file (`AGENTS.md`) exists because Codex looks for it by convention. Its job is to point Codex at `CLAUDE.md` and add the Codex-specific notes that don't apply to Claude Code.

---

## Why this file exists at all

Pantheon doctrine, failure mode 14 — *missing root doctrine updates* — and failure mode 20 — *workflow drift across tools* — both reduce to the same root cause: agents on shared substrate operating from different rule sets.

The fix is centralized doctrine in shared root files. `CLAUDE.md` and `AGENTS.md` are pair-files. They cannot drift.

If either file changes, the other must be updated in the same commit, or the change is incomplete.

---

## Codex-specific notes

These supplement `CLAUDE.md`. They do not override it.

- **Codex's tool surface differs from Claude Code's.** Claude Code's `Bash`/`PreToolUse` hook layer is where Terminus enforces boundaries. Codex's sandbox and tool-call surface are where Ananke does the equivalent work. The guardian model is the same; the implementation path is not.
- **Codex sandbox sessions are ephemeral by default.** State that should persist across sessions must be written to the repo, not to the Codex session. This is the operational shape of failure mode 5 (*old session folders leaking files*) — fix is the same as for Claude Code: explicit archive or cleanup before phase closeout.
- **Codex's commit behavior:** all commits authored by Codex must be reviewed against the canonical checkout before declaring success. Codex's session report alone is not proof. See `CLAUDE.md` operating rule 7.
- **Identity stamping (Pantheon's `argus-identity-migration`):** when work moves from Codex to Claude Code or vice versa, the handoff prompt must include: branch, HEAD, upstream parity, worktree status, and a brief stake-in-the-ground description of what is and is not done. Anything weaker is an incomplete handoff and violates failure mode 11.

---

## When Codex finishes a phase

Same closeout as Claude Code (`CLAUDE.md` "When the phase passes"). The phase closes in `CLAUDE.md` *and* in this file. Identity stamping is mandatory on phase boundaries.

---

*Built in the Pantheon's shadow.*
