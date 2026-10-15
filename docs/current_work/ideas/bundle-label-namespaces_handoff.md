---
type: handoff
slug: bundle-label-namespaces
created: 2026-10-15
status: resolved
trigger: issue
recommended_next_skill: direct-dispatch
source_session_summary: "The incubator's post-migration compliance audit (v2.1.0, 2026-10-15) flagged all 13 factory:* labels as label sprawl: github-provenance's exact-set label check and the factory bundle's own labels were never reconciled"
active_deliverable: null
related_files:
  - process/github-checkpoints.md
  - process/factory.md
  - bundles/github-provenance/fragments/sdlc-compliance-auditor.md
  - bundles/factory/tree/bootstrap.py
  - skeleton/manifest.json
---

# Two bundles disagree about who owns a repository's labels

## Why this is a handoff

After the incubator migrated to v2.1.0 (2026-10-15), its compliance audit flagged every one of the factory's 13 `factory:*` labels as `minor` drift. CD asked how two z-sdlc bundles could disagree, and what the fix is. The answer went to CD through the incubator's migration session. This file is the work it leaves. That session was about the v2.1.0 release and the incubator's migration, so nothing was changed there.

## What needs to happen

**1. Ownership by label namespace.** A label belongs to exactly one checker:
- **`process/github-checkpoints.md` § Labels:** labels in a namespace an installed bundle owns (the factory's `factory:`) are that bundle's. They're outside the config block's allowed set, and the config never lists them. Today's text says the config block "owns the complete allowed label set … a label not listed there is definitionally sprawl", which was written when the checkpoint skills were z-sdlc's only automated label writers.
- **The auditor's § 10h** (`bundles/github-provenance/fragments/sdlc-compliance-auditor.md:98`): skip labels in any installed bundle's declared namespace. It should read the namespace from a declaration, not from another bundle's code.
- **The declaration:** one field on the factory bundle's entry in `skeleton/manifest.json`, e.g. `"label_namespace": "factory:"`. It travels into `.sdlc-manifest.json`'s installed bundles, where § 10h can read it. `sdlc-initialize` and `sdlc-migrate` carry it, since it's a manifest field addition with a back-fill default (`contract_changes.yaml`).
- **The factory's own check:**
  - `bootstrap.py` already creates the labels in its `LABELS` list (`bundles/factory/tree/bootstrap.py:30`);
  - it should also report any `factory:` label in the repository that list doesn't define, so the typo sprawl § 10h exists for is still caught in the factory's namespace.
- **`process/factory.md` § Labels** says the same from the factory's side.

**2. A check that installed bundles agree.** This went unseen because nothing looks at bundles together:
- the import's proof installs only the factory bundle;
- the release reviews were scoped to the factory's code;
- `CLAUDE.md`'s consistency checks cover the manifest, references, paths and public content.

A rule for this repository's `CLAUDE.md` would close it: when a bundle adds something a project's GitHub or config holds (labels, workflows, environments, issue types), check every other bundle's checks and audits against it. And the import's empty-project proof could install the factory alongside github-provenance.

## Evidence

- **`process/github-checkpoints.md:437-466`** (§ Labels): the config block owns the complete allowed set, and § 10h is the "designated detector" for extra labels.
- **`bundles/github-provenance/fragments/sdlc-compliance-auditor.md:98`** (§ 10h, "Taxonomy parity check"): "The repo's label set must equal exactly the config block's label set (universal + conditional + human). Both directions are drift". An extra label is `minor`.
- **`bundles/factory/tree/bootstrap.py:30`** (`LABELS`) and **`process/factory.md:306`** (§ Labels) list the 13 `factory:*` labels: `triage`, `ready-for-dispatch`, `ready-to-plan`, `needs-input`, `wait`, `review-capped`, `advisor`, `follow-up`, `go`, `revise`, `escalated`, `gate`, `gate-retry`.
- **Neither process doc names the other bundle.** github-provenance came first (2026-09-02); the factory bundle debuted on 2026-10-12, promoted from the incubator.
- **Who's affected:** the incubator's post-migration audit flagged all 13. The pilot project and one other project have both bundles installed, so their audits should flag the same.
- **The interim advice given:** leave the finding open, as a known upstream gap, until this lands. Don't list the factory's labels under `human:`. That means "applied by humans only", which the factory's App contradicts, and it would add a drifting copy that hides typos.

## Recommended next step

Open a new session in z-sdlc and run this as **direct dispatch**, with this file as the seed.

Reasoning: the design is settled, and the change is a manifest field plus four edits that follow from it. It's a minor release, since the auditor reads a new manifest field. A plan earns its keep only if a second bundle needs a namespace too.

## Open questions

- **Prefix only?** Does any other bundle create GitHub labels, now or planned? If none does, one prefix field is enough. If several do, the field might hold a list.
- **When § 10h can't read the declaration:** in an install from before the field existed, should it fall back to today's exact-set check, or skip `factory:` by name? The back-fill default decides this.

## Out of scope (do NOT pursue)

- **Changing the factory's label names or the checkpoint labels themselves.**
- **The incubator's own config:** it waits for this fix, and the finding stays open there until then.

## Resolution (2026-10-15, z-sdlc v2.1.1)

Fixed without the manifest field. A field in the installed bundles wouldn't have reached the incubator, which runs the factory without installing the bundle, and the factory is the only bundle that creates labels. So § 10h recognizes the factory by `.github/factory/factory.json`, and checks `factory:` labels against `process/factory.md` § Labels, which a repository test keeps equal to `bootstrap.py`'s `LABELS`. `bootstrap.py` reports a `factory:` label it doesn't define, for projects without github-provenance's audit, and `CLAUDE.md` gained the rule that bundles are checked against each other. A generic namespace declaration waits for a second bundle that creates labels. The changelog entry is "The factory owns its labels".
