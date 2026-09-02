## GitHub Provenance Reconciliation (Dimension 10)

**Activation gate:** skip this entire section unless `[sdlc-root]/process/github-checkpoints.md` exists and its config block says `enabled: true`. When skipped because the bundle is installed but not enabled, report the dimension as "not applicable — convention not configured" in coverage rather than omitting it silently.

A **tenth dimension** on top of the framework's nine, present only where the `github-provenance` bundle is installed and enabled. Compliance mode only. **Any "all 9 dimensions" language elsewhere in this skill describes the upstream base set — when this section is active, this project runs ten**, and the dispatch prompt must say so (the added line below), or the auditor will legitimately scan nine.

**Execution lives in the agent, not here.** The join runs inside `sdlc-compliance-auditor` § GitHub Provenance Reconciliation. Add one line to the compliance dispatch prompt: *"Also run Dimension 10 — GitHub provenance reconciliation — per your § GitHub Provenance Reconciliation section."* Findings come back in the ordinary findings table and route through report, triage, and fix unchanged.

**The full contract is specified once, in the agent** — scope gate, sub-deliverable join, status parsing, board enumeration, drift-class tests and severities, exemptions, and the label presence check all live in `sdlc-compliance-auditor` § GitHub Provenance Reconciliation (10a–10j). Do not restate them here; a second copy is a second thing to drift.

Two properties to preserve during triage:

1. **Read-only.** Dimension 10 findings are *detected and reported*; fixes to the board or issues go forward-only under the floor rule, and a human decides. GitHub never writes back into the catalog.
2. **Log-independence.** The dimension **may** read `[sdlc-root]/.local/github-checkpoint-misses.jsonl` to prioritize where it looks, but it must produce **identical findings** whether that log is present, empty, absent, or **wrong** — carrying entries for drift that live GitHub does not show, or missing drift that it does. If the log's contents change the conclusions, the log has become authoritative and the design has failed. Live GitHub state is the only source of truth.
