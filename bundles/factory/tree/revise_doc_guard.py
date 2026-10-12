"""Check a spec or plan revision before the factory pushes it (factory-revise-doc.yml, publish job).

Usage: python3 -I revise_doc_guard.py <bundle> <base> <result.json> <issue> <run-url> <out-dir> <stage> <merge-base> [<stats.json>]
       (REVISION and REVISION_LIMIT in the environment)

<stage> is the document PR's: spec or plan. <base> is the PR's head the agent started from, <merge-base>
where the PR left main. The result follows revise-doc.schema.json: a planning result (the document,
deliverable, brief, findings) plus a revision's answers (summary, one response per request,
verification, follow-ups).

It applies the planning stage's own checks (implement_guard.py), so a revision can publish nothing a
plan run couldn't: commits in a straight line on <base>, only docs/ and the SDLC hygiene files, nothing
CODEOWNERS owns, the caps, no tokens or embeds; a result whose brief, document path and findings pass
the planning rules; and the document is the PR's own. On success it writes <out-dir>/head, comment.md
(the revision comment, with the App's factory-revise marker) and pr-body.md: the PR description
rendered again from the revised Approval Brief, since CD approves the document by merging the PR.
"""

import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import implement_guard as g  # noqa: E402

STAGES = ("spec", "plan")
REVISION_KEYS = ("summary", "responses", "verification", "follow_ups")
SCHEMA = pathlib.Path(__file__).resolve().parent / "revise-doc.schema.json"


def check(result, stage):
    if not isinstance(result, dict) or result.get("status") not in ("awaiting-approval", "escalated"):
        raise g.Refused(f"nothing to publish for status {result.get('status') if isinstance(result, dict) else None!r}")
    props = json.loads(SCHEMA.read_text())["properties"]
    for key in REVISION_KEYS:
        g.conforms(result.get(key), props[key], key)
    if not result["summary"].strip() or not result["responses"]:
        raise g.Refused("a revision needs a summary and a response to each request")
    for t in g.strings({k: result[k] for k in REVISION_KEYS}):
        if g.TOKEN.search(t):
            raise g.Refused("the result contains a credential-like string")
        if g.EMBED.search(t):
            raise g.Refused("the result contains an image or embed")
    # The planning stage's own rules for the rest: the brief, the document path, the findings.
    g.check_result({k: v for k, v in result.items() if k not in REVISION_KEYS}, stage)


def main():
    bundle, base, result_path, issue, run_url, out_dir, stage, merge_base = sys.argv[1:9]
    stats_path = sys.argv[9] if len(sys.argv) > 9 else ""
    out = pathlib.Path(out_dir)
    try:
        if not re.fullmatch(r"[0-9a-f]{40}", base) or not re.fullmatch(r"[0-9a-f]{40}", merge_base) or not issue.isdigit():
            raise g.Refused("bad base, merge base or issue number")
        if stage not in STAGES:
            raise g.Refused(f"unknown document stage {stage!r}")
        revision, limit = int(os.environ["REVISION"]), int(os.environ["REVISION_LIMIT"])
        if not 1 <= revision <= limit:
            raise g.Refused(f"revision {revision} is outside 1..{limit}")
        result = json.loads(pathlib.Path(result_path).read_text())
        check(result, stage)
        patterns = g.codeowners_patterns(pathlib.Path(".github/CODEOWNERS").read_text())
        head, paths = g.check_commits(bundle, base, patterns, g.DOC_STAGE_PATHS)
        # The document must be the PR's own, still there at the head.
        pr_paths = g.git("diff", "--name-only", "-M", merge_base, head).split()
        present = g.git("diff", "--name-only", "-M", "--diff-filter=d", merge_base, head).split()
        if result["document"] not in present:
            raise g.Refused(f"{result['document']} isn't a document this PR adds or changes")
        try:
            stats = json.loads(pathlib.Path(stats_path).read_text()) if stats_path else None
        except (OSError, ValueError):
            stats = None
        comment = g.revise_comment({**result, "status": "escalated" if result["status"] == "escalated" else "done"},
                                   revision, limit, run_url, paths, stats)
        plan_gates = None
        if stage == "plan" and result["document"].endswith("_plan.md"):
            plan_gates = g.plan_gate_lines(g.git("show", f"{head}:{result['document']}"), g.read_catalog()) or None
        body = g.pr_body({k: v for k, v in result.items() if k not in REVISION_KEYS}, issue, run_url, pr_paths, stage,
                         stats, present=present, plan_gates=plan_gates)
    except (g.Refused, ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError) as e:
        print(f"::error::{stage} revision refused: {e}")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    (out / "head").write_text(head + "\n")
    (out / "comment.md").write_text(comment)
    (out / "pr-body.md").write_text(body)
    print(f"{stage} revision accepted: {head[:12]}, {len(paths)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
