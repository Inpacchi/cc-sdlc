"""File a merged execute PR's checked follow-ups as issues, then start triage on each (factory-follow-ups.yml).

Usage: python3 -I follow_ups.py   (inputs in the environment: REPO, PR, BODY_B64, DEFAULT_BRANCH, RUN_URL;
       GH_TOKEN reads and dispatches, APP_TOKEN writes issues and comments as the factory App)

Policy (CD, 2026-10-09; design: README § Follow-ups):
- Only a merged, factory-opened execute PR files follow-ups (an executed plan; never a direct fix). Its
  writer marker `<!-- factory-pr: v1 execute -->` and the App as author prove which stage opened it.
- The checklist between the guard's markers is the source: checked items are filed, unchecked ones are
  dropped. The body is the snapshot taken at merge (BODY_B64), so later edits change nothing.
- A follow-up's own follow-ups are never filed (depth 1): the source issue's App-written provenance
  marker says it was a follow-up, and the items are listed on it for CD instead.
- Each filed issue is triaged, then held: triage starts no stage for it until CD adds `factory:go`.
- At most MAX_PER_MERGE items per merge (the checklist's cap); any beyond it are listed on the source
  issue for CD to file by hand. No daily cap (CD): the hold after triage is what bounds the work. Nothing
  is dropped silently.
- Re-runs are safe: an item already filed (same PR and item id, open or closed) is not filed again, and
  triage is started for any filed item that hasn't been triaged yet.
"""

import base64
import json
import os
import pathlib
import re
import subprocess
import sys

# The factory App's bot user, from this repository's factory.json (beside this file).
APP = json.loads((pathlib.Path(__file__).resolve().parent / "factory.json").read_text())["app"]
APP_USER_ID = APP["user_id"]
MAX_PER_MERGE = 10
OPEN, CLOSE = "<!-- factory-follow-ups v1 -->", "<!-- /factory-follow-ups -->"
EXECUTE_MARKER = "<!-- factory-pr: v1 execute -->"
ITEM = re.compile(r"^- \[([ xX])\] \*\*(F(?:[1-9]|10)): (.+?)\*\*: (.*)$")
PROVENANCE = re.compile(r"<!-- factory-follow-up: (\{[^<>]*\}) -->")
HEAD = re.compile(r"^factory/(\d+)-impl$")
UNESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
# What the guard refuses in agent text, re-checked because the body is editable until merge.
UNSAFE = re.compile(r"<!--|sk-ant-|gh[pousr]_[A-Za-z0-9_]{20}|github_pat_|ctx7sk|-----BEGIN [A-Z ]*PRIVATE KEY-----"
                    r"|!\[|<\s*(img|picture|source|video|audio|svg|iframe|object|embed)\b", re.I)
STATE_LABELS = {"factory:ready-for-dispatch", "factory:ready-to-plan", "factory:needs-input", "factory:wait"}


class Stop(Exception):
    """Nothing to file, for a reason worth reporting (not a failure)."""


def parse(body):
    """The checklist items between the markers: [{id, checked, title, text}], in order. `title` is plain
    text for the issue title; `text` stays the guard's neutralized markdown for the issue body."""
    if OPEN not in body or CLOSE not in body:
        return []
    block = body[body.index(OPEN) + len(OPEN):body.index(CLOSE)]
    items, seen = [], set()
    for line in block.split("\n"):
        m = ITEM.match(line.strip())
        if not m or m.group(2) in seen:
            continue
        seen.add(m.group(2))
        title = " ".join(UNESCAPE.sub(r"\1", m.group(3)).split())[:120]
        items.append({"id": m.group(2), "checked": m.group(1) != " ", "title": title, "text": m.group(4)})
    return items


def provenance(issue):
    """The App-written follow-up marker on an issue (its body, App-authored), or None."""
    if (issue.get("user") or {}).get("id") != APP_USER_ID:
        return None
    m = PROVENANCE.search(issue.get("body") or "")
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def plan_filing(items, pr, existing):
    """Decide each item's fate. `existing` maps (pr, item id) to an issue number already filed.
    Returns (keep, create, overflow, skipped): keep = [(item, number)], create = [item], overflow =
    [item] over the per-merge cap, skipped = [(item, reason)]."""
    keep, create, overflow, skipped = [], [], [], []
    for item in items:
        if not item["checked"]:
            skipped.append((item, "unchecked"))
        elif UNSAFE.search(item["title"] + " " + item["text"]):
            skipped.append((item, "refused: a marker, credential-like string or embed"))
        elif (pr, item["id"]) in existing:
            keep.append((item, existing[(pr, item["id"])]))
        elif len(create) >= MAX_PER_MERGE:
            overflow.append(item)
        else:
            create.append(item)
    return keep, create, overflow, skipped


def issue_body(item, pr, source):
    marker = json.dumps({"pr": pr, "issue": source, "item": item["id"], "depth": 1}, separators=(",", ":"))
    return (f"{item['text']}\n\n"
            f"Follow-up {item['id']} from PR #{pr} (issue #{source}), proposed by the factory when the plan was "
            f"executed and kept by CD at merge. It is triaged, then held: add `factory:go` to start the next stage.\n\n"
            f"<!-- factory-follow-up: {marker} -->\n")


def gh(token, *args, data=None):
    env = dict(os.environ, GH_TOKEN=token)
    out = subprocess.run(["gh", *args], input=data, capture_output=True, text=True, env=env)
    if out.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {out.stderr.strip()[:300]}")
    return out.stdout


def api(token, path):
    return json.loads(gh(token, "api", path) or "null")


def api_list(token, path):
    """Every item across a paginated list endpoint."""
    return [json.loads(line) for line in gh(token, "api", "--paginate", path, "--jq", ".[] | tojson").splitlines() if line]


def main():
    repo, pr, default = os.environ["REPO"], int(os.environ["PR"]), os.environ["DEFAULT_BRANCH"]
    read, write, run_url = os.environ["GH_TOKEN"], os.environ["APP_TOKEN"], os.environ["RUN_URL"]
    body = base64.b64decode(os.environ["BODY_B64"]).decode("utf-8", errors="replace")

    pull = api(read, f"repos/{repo}/pulls/{pr}")
    head = HEAD.match(pull["head"]["ref"])
    checks = [(pull.get("merged_at") is not None, "it isn't merged"),
              (pull["base"]["ref"] == default, f"it didn't merge into {default}"),
              (pull["head"]["repo"] and pull["head"]["repo"]["full_name"] == repo, "its branch is from a fork"),
              (head is not None, "its branch isn't factory/<issue>-impl"),
              ((pull.get("user") or {}).get("id") == APP_USER_ID, "the factory App didn't open it"),
              (body.lstrip().startswith(EXECUTE_MARKER), "it wasn't opened by the execute stage (a direct fix files none)")]
    for ok, why in checks:
        if not ok:
            print(f"No follow-ups filed for PR #{pr}: {why}.")
            return 0
    source = int(head.group(1))
    items = parse(body)
    if not items:
        print(f"PR #{pr} has no follow-up checklist.")
        return 0

    def comment(text):
        gh(write, "issue", "comment", str(source), "-R", repo, "--body-file", "-",
           data=text + f"\n\n<sub>factory follow-ups · [run]({run_url})</sub>\n")

    def listed(entries):
        return "\n".join(f"- **{i['id']}: {i['title']}**: {i['text']}" for i in entries)

    if provenance(api(read, f"repos/{repo}/issues/{source}")):
        comment(f"**Follow-ups from PR #{pr} were not filed:** this issue is itself a follow-up, and the factory "
                f"never files a follow-up's follow-ups. File any you want by hand:\n\n"
                f"{listed([i for i in items if i['checked']])}")
        return 0

    children = api_list(read, f"repos/{repo}/issues?labels=factory:follow-up&state=all&per_page=100")
    existing = {}
    for child in children:
        mark = provenance(child)
        if not mark:
            continue
        existing[(mark.get("pr"), mark.get("item"))] = child["number"]
    keep, create, overflow, skipped = plan_filing(items, pr, existing)

    filed, failed = [], []
    for item in create:
        try:
            url = gh(write, "issue", "create", "-R", repo, "--title", item["title"], "--label", "factory:follow-up",
                     "--body-file", "-", data=issue_body(item, pr, source)).strip()
            filed.append((item, int(url.rstrip("/").rsplit("/", 1)[1])))
        except (RuntimeError, ValueError, IndexError) as e:
            failed.append((item, f"filing failed: {e}"))
    triaged, started = [], []
    for item, number in keep + filed:
        labels = {l["name"] for l in api(read, f"repos/{repo}/issues/{number}").get("labels") or []}
        if labels & STATE_LABELS:
            triaged.append((item, number))
            continue
        try:
            gh(read, "workflow", "run", "factory-triage.yml", "-R", repo, "--ref", default, "-f", f"issue_number={number}")
            started.append((item, number))
        except RuntimeError as e:
            failed.append((item, f"#{number} filed, but starting triage failed (re-run this workflow): {e}"))

    lines = [f"**Follow-ups from PR #{pr}:**", ""]
    lines += [f"- #{n} ({i['id']}): filed, triage started; it will hold for `factory:go`" for i, n in started]
    lines += [f"- #{n} ({i['id']}): already triaged" for i, n in triaged]
    lines += [f"- {i['id']} ({i['title']}): not filed: {why}" for i, why in skipped if why != "unchecked"]
    lines += [f"- {i['id']} ({i['title']}): {why}" for i, why in failed]
    if overflow:
        lines += ["", f"Over the cap of {MAX_PER_MERGE} per merge; file these by hand:", "", listed(overflow)]
    unchecked = [i["id"] for i, why in skipped if why == "unchecked"]
    if unchecked:
        lines += ["", f"Unchecked at merge, so not filed: {', '.join(unchecked)}."]
    comment("\n".join(lines))
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
