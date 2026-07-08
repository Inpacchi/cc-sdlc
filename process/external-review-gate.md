# External Review Gate

An **optional, opt-in** final review pass that sends the converged change to a
**non-Claude model** — OpenAI Codex, or a local LLM (llama.cpp / Ollama / vLLM) —
for an independent second opinion. It runs *after* the internal review-fix loop
exits clean and *before* commit. Its findings re-enter the normal triage; they
never auto-apply.

This gate is disabled by default. It activates only when the project provides the
wrapper described under "Enabling the gate."

---

## Why a cross-vendor gate

`[sdlc-root]/process/debate-protocol.md` establishes that the primary value of
multi-agent review is **ensembling** — independent reviewers with different blind
spots — not debate itself. Every internal reviewer is still a Claude model, so
they share systematic blind spots: the same training distribution fails on the
same edge cases. A reviewer from a different vendor (Codex) or a different
architecture (a local Qwen) is the most independent reviewer available — it
catches the class of issue Claude reviewers miss *together*. This gate is one
more ensemble member, deliberately chosen to maximize independence.

It is **not** a replacement for the internal loop. The internal loop still runs
to completion first — the external model reviews an already-clean change, so its
signal is "what did an entire vendor's-worth of independent judgment still catch?"

## Where it sits in the loop

```
internal review-fix loop → CLEAN
   ↓
External Review Gate (if enabled)
   ├─ no findings → proceed to commit
   └─ findings → triage (Step C of review-fix-loop.md)
                   ├─ FIX → dispatch domain agent → re-run INTERNAL loop → re-run gate
                   ├─ INVESTIGATE / DECIDE → surface to CD
                   └─ PRE-EXISTING → record, no action
```

The gate is a source of findings, not a fixer. External findings flow through the
exact same classification (`[sdlc-root]/process/finding-classification.md`) and
the exact same fix path as any agent finding: **the external model never edits
files; domain agents fix, and the internal loop re-verifies.** This keeps the
Manager Rule intact — an external model's output is input to triage, subordinate
to cc-sdlc's own review.

A FIX from the external gate re-opens the internal loop: after the fix, dispatch
the internal reviewers again (fixes can introduce new problems), and only once
the internal loop is clean again does the gate re-run. Cap the gate at 2 rounds —
if the external model still surfaces new FIX findings after two fix cycles,
surface the remainder to CD via `AskUserQuestion` rather than looping
indefinitely (external models can generate an unbounded stream of low-value
style opinions).

## Data egress — read before enabling

Sending a diff to an external model **publishes that code to that service.** For
a hosted model (Codex / OpenAI), the code leaves the machine and may be retained
or logged by the provider. This is an outward-facing action:

- **Never** send secrets, `.env` files, credentials, or key material. The wrapper
  payload is the diff plus spec/plan context — scrub or exclude secret-bearing
  files before they reach the wrapper.
- For proprietary or sensitive codebases, prefer a **local** model (llama.cpp /
  Ollama) so nothing leaves the machine. The OpenCode local-serving reference
  (`[sdlc-root]/../skills/sdlc-port-opencode/references/local-model-serving.md`
  in source; consult the installed local-model notes) documents a suitable local
  setup.
- The gate must state, each time it runs, **where the code is going** (which
  model / endpoint) so CD sees the egress. If the project has not durably
  authorized egress to a hosted provider, confirm with CD before the first
  hosted-model run of a session.

If the codebase's sensitivity is unknown, default to local-only or skip the gate.

## Enabling the gate

The gate is convention-driven — no manifest schema change. It activates when an
executable wrapper exists at:

```
[sdlc-root]/external-review.sh
```

If the file is absent or not executable, the gate is **skipped silently** (it is
optional). If present, the skill runs it as the gate.

### Wrapper contract

- **stdin** — the review payload: a rubric header, the spec/plan context (when
  available), and the unified diff being reviewed. Plain text.
- **stdout** — findings, one per line or as a markdown list, each in the form
  `SEVERITY | file:line | finding` where SEVERITY ∈ {critical, major, minor}.
  Empty stdout means "no findings."
- **exit code** — `0` on success (including zero findings). Non-zero means the
  gate could not run; the skill records "external gate errored — skipped" and
  proceeds to commit. **Never block a commit on external availability.**
- The wrapper owns model choice, endpoint, secret scrubbing, and prompt shaping.
  cc-sdlc ships no default wrapper — the project author writes it, because the
  right model and the egress policy are project decisions.

### Example wrappers

Local model via Ollama (nothing leaves the machine):

```bash
#!/usr/bin/env bash
# [sdlc-root]/external-review.sh — local Qwen reviewer
set -euo pipefail
payload="$(cat)"
printf '%s\n\nReturn findings as: SEVERITY | file:line | finding. Empty if none.\n' \
  "$payload" | ollama run qwen3.6-27b
```

Hosted second opinion via the Codex CLI (egress — hosted):

```bash
#!/usr/bin/env bash
# [sdlc-root]/external-review.sh — Codex reviewer (SENDS CODE TO OPENAI)
set -euo pipefail
payload="$(cat)"
codex exec "You are an independent code reviewer. Review the diff below. \
Return findings as: SEVERITY | file:line | finding. Empty if none.

$payload"
```

The invoking skill builds the payload like:

```bash
{
  echo "Independent review. Report only real defects: correctness, security,"
  echo "data integrity, contract breaks. Skip style. Severity + file:line + why."
  echo
  echo "=== SPEC/PLAN CONTEXT ==="; cat "$plan_or_spec" 2>/dev/null || echo "(none)"
  echo; echo "=== DIFF ==="; git diff --staged 2>/dev/null || git diff
} | "[sdlc-root]/external-review.sh"
```

## Anti-conformity for external findings

The external model is an outsider — it lacks the internal reviewers' context,
which is exactly its value, but also means it will produce more false positives
(it does not know the codebase conventions or the plan's deliberate trade-offs).
Apply the debate-protocol safeguards:

- **Do not defer to it.** An external finding is not more authoritative because it
  came from another vendor. Classify on evidence, like any finding.
- **Scrutinize before FIX.** External findings uncorroborated by tests or the
  internal reviewers lean toward INVESTIGATE, not FIX — verify before spending a
  fix cycle. (Same discipline as the security-finding calibration in
  `[sdlc-root]/process/review-fix-loop.md` Step C.)
- **Watch for conformity.** If an internal reviewer flips to agree with the
  external model on re-review without new evidence, treat the flip as suspect
  (debate-protocol § Anti-Conformity Safeguard).

## When to run it

- **High value:** high-risk domains (auth, payments, migrations, concurrency,
  public APIs), or any change where a second independent opinion is cheap
  insurance. Pairs naturally with MTS4 risk escalation.
- **Low value / skip:** trivial changes, docs-only diffs, or sensitive code with
  no local model available.

The gate is invoked from `[sdlc-root]/process/review-fix-loop.md` (Step E) and
surfaced as an optional step in `sdlc-review-code`, `sdlc-execute`, and
`sdlc-lite-execute`. It is always optional and always after the internal loop.
