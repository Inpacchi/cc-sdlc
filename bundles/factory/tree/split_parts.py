"""File the parts of a merged split as issues, held for CD (factory-split.yml).

Usage: python3 -I split_parts.py   (inputs in the environment: REPO, PR, DEFAULT_BRANCH, RUN_URL;
       GH_TOKEN reads, APP_TOKEN writes issues and comments as the factory App)

Policy (CD, 2026-10-09; design: README § Splits, z-sdlc process/deliverable_lifecycle.md § Splitting a Deliverable):
- Only a merged, factory-opened split PR (branch factory/<issue>-split, writer marker
  `<!-- factory-pr: v1 split -->`) files parts. CD approved the split by merging it.
- The source of truth is the split record and the catalog as merged (CD may edit them before merging),
  read at the merge commit, never the run's JSON. They must agree, and the parts must follow the split
  rules (catalog.check_parts); otherwise nothing is filed and the parent issue says why.
- The parent is the issue's own reserved ID (its App-written `factory-id` marker), so a split can't
  name another issue's deliverable.
- Each part becomes an issue linked as a sub-issue of the parent, with one App comment whose marker
  block reserves its ID (`factory-id`, reused by the plan stage's claim), records its tier as a triage
  decision (`factory-triage`, so it isn't re-triaged) and, for a full-tier part reusing an approved
  spec, names it (`factory-spec`). It gets `factory:ready-to-plan`, set by the App, so nothing starts:
  it is held until CD adds `factory:go`.
- Re-runs are safe: a part already filed (an App-created issue whose provenance marker names this parent
  and part) is reused, and any missing marker comment, label or link is added. Nothing is filed twice.
- The parent keeps no factory state label afterwards; CD closes it by hand when its parts are done.
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse

# The shared catalog reader sits beside this script, in the default branch's checkout.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import catalog  # noqa: E402

# The factory App's bot user, from this repository's factory.json (beside this file).
APP = json.loads((pathlib.Path(__file__).resolve().parent / "factory.json").read_text())["app"]
APP_USER_ID, APP_LOGIN = APP["user_id"], APP["login"]
SPLIT_MARKER = "<!-- factory-pr: v1 split -->"
HEAD = re.compile(r"^factory/(\d+)-split$")
SPLIT_DOC = re.compile(r"^docs/current_work/planning/(d\d+)_[a-z0-9_]+_split\.md$")
RESERVED = re.compile(r"\A<!-- factory-id: (D\d+[a-z]?) -->")
PROVENANCE = re.compile(r"<!-- factory-part-of: (\{[^<>]*\}) -->")
UNSAFE = re.compile(r"<!--|sk-ant-|gh[pousr]_[A-Za-z0-9_]{20}|github_pat_|ctx7sk|-----BEGIN [A-Z ]*PRIVATE KEY-----"
                    r"|!\[|<\s*(img|picture|source|video|audio|svg|iframe|object|embed)\b", re.I)
PROPERTY_LABELS = {"factory:advisor", "factory:follow-up", "factory:go"}


class Stop(Exception):
    """Nothing can be filed, for a reason the parent issue should show."""


def provenance(issue):
    """The App-written part marker on an issue body, or None."""
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


def existing_parts(issues, parent_issue):
    """{part ID: issue number} for parts of `parent_issue` already filed (App-created, with provenance)."""
    out = {}
    for issue in issues:
        mark = provenance(issue)
        if mark and mark.get("parent") == parent_issue and isinstance(mark.get("part"), str):
            out.setdefault(mark["part"], issue["number"])
    return out


def reserved_id(comments):
    """The issue's own deliverable ID: the latest factory comment that opens with a factory-id marker.
    Like the plan stage's claim, it accepts the App and, before 2026-10-09, github-actions."""
    found = None
    for c in comments:
        user = c.get("user") or {}
        if user.get("type") == "Bot" and (user.get("id") == APP_USER_ID or user.get("login") == "github-actions[bot]"):
            m = RESERVED.match(c.get("body") or "")
            if m:
                found = m.group(1)
    return found


def check_split(record, index, parent):
    """The merged split record's parts, checked against the split rules and the merged catalog."""
    parts = catalog.split_parts(record)
    catalog.check_parts(parent, parts)
    rows = catalog.catalog_rows(index)
    if parent not in rows:
        raise ValueError(f"the catalog has no row for {parent}")
    deps = catalog.ids(rows[parent]["Depends on"])
    for p in parts:
        if p["part"] not in deps:
            raise ValueError(f"the catalog's {parent} row doesn't depend on {p['part']}")
        row = rows.get(p["part"])
        if row is None:
            raise ValueError(f"the catalog has no row for {p['part']}")
        if catalog.ids(row["Depends on"]) != p["depends_on"]:
            raise ValueError(f"the catalog's {p['part']} row and the split record disagree on its dependencies")
        if UNSAFE.search(p["name"] + " " + p["scope"]):
            raise ValueError(f"{p['part']} has a marker, credential-like string or embed in its name or scope")
    return parts


def issue_title(part):
    return f"{part['part']}: {' '.join(part['name'].split())}"[:120]


def issue_body(part, parent_issue, pr, record_path):
    deps = ", ".join(part["depends_on"]) or "nothing"
    spec = f"\n\nIt reuses the approved spec `{part['spec']}`; its plan covers only this part." if part["spec"] else ""
    marker = json.dumps({"parent": parent_issue, "part": part["part"], "pr": pr}, separators=(",", ":"))
    return (f"{part['scope']}\n\n"
            f"Part {part['part']} of #{parent_issue}'s split (approved in PR #{pr}; `{record_path}`). Tier: "
            f"{part['tier']}. Depends on: {deps}. Planning a part isn't blocked by its dependencies; executing "
            f"it is.{spec}\n\n"
            f"Held: add `factory:go` to start planning.\n\n"
            f"<!-- factory-part-of: {marker} -->\n")


def marker_comment(part, run_url):
    """One App comment whose leading marker block reserves the ID, records the tier, names a reused spec."""
    decision = json.dumps({"state": "ready-to-plan", "tier": part["tier"], "estimate": None}, separators=(",", ":"))
    lines = [f"<!-- factory-id: {part['part']} -->", f"<!-- factory-triage: {decision} -->"]
    if part["spec"]:
        lines.append(f"<!-- factory-spec: {part['spec']} -->")
    lines += [f"Reserved **{part['part']}** for this part ({part['tier']} tier) when CD approved the split. "
              f"<sub>factory split · [run]({run_url})</sub>"]
    return "\n".join(lines) + "\n"


def has_markers(comments, part):
    return any((c.get("user") or {}).get("id") == APP_USER_ID and
               (c.get("body") or "").startswith(f"<!-- factory-id: {part} -->") for c in comments)


def gh(token, *args, data=None):
    env = dict(os.environ, GH_TOKEN=token)
    out = subprocess.run(["gh", *args], input=data, capture_output=True, text=True, env=env)
    if out.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {out.stderr.strip()[:300]}")
    return out.stdout


def api(token, path):
    return json.loads(gh(token, "api", path) or "null")


def api_list(token, path):
    return [json.loads(line) for line in gh(token, "api", "--paginate", path, "--jq", ".[] | tojson").splitlines() if line]


def raw(token, repo, path, ref):
    return gh(token, "api", f"repos/{repo}/contents/{urllib.parse.quote(path)}?ref={ref}",
              "-H", "Accept: application/vnd.github.raw")


def main():
    repo, pr, default = os.environ["REPO"], int(os.environ["PR"]), os.environ["DEFAULT_BRANCH"]
    read, write, run_url = os.environ["GH_TOKEN"], os.environ["APP_TOKEN"], os.environ["RUN_URL"]

    pull = api(read, f"repos/{repo}/pulls/{pr}")
    head = HEAD.match(pull["head"]["ref"])
    checks = [(pull.get("merged_at") is not None, "it isn't merged"),
              (pull["base"]["ref"] == default, f"it didn't merge into {default}"),
              (pull["head"]["repo"] and pull["head"]["repo"]["full_name"] == repo, "its branch is from a fork"),
              (head is not None, "its branch isn't factory/<issue>-split"),
              ((pull.get("user") or {}).get("id") == APP_USER_ID, "the factory App didn't open it"),
              ((pull.get("body") or "").lstrip().startswith(SPLIT_MARKER), "it wasn't opened as a split")]
    for ok, why in checks:
        if not ok:
            print(f"No parts filed for PR #{pr}: {why}.")
            return 0
    source = int(head.group(1))

    def comment(text):
        gh(write, "issue", "comment", str(source), "-R", repo, "--body-file", "-",
           data=text + f"\n\n<sub>factory split · [run]({run_url})</sub>\n")

    try:
        files = [f["filename"] for f in api_list(read, f"repos/{repo}/pulls/{pr}/files")]
        records = [f for f in files if SPLIT_DOC.match(f)]
        if len(records) != 1:
            raise Stop(f"the PR changes {len(records)} split records; it must change exactly one")
        record_path = records[0]
        parent = "D" + SPLIT_DOC.match(record_path).group(1)[1:]
        mine = reserved_id(api_list(read, f"repos/{repo}/issues/{source}/comments"))
        if mine != parent:
            raise Stop(f"the split record is for {parent}, but this issue's deliverable is {mine or 'unreserved'}")
        merge = pull["merge_commit_sha"]
        try:
            parts = check_split(raw(read, repo, record_path, merge), raw(read, repo, "docs/_index.md", merge), parent)
        except ValueError as e:
            raise Stop(f"the merged split doesn't follow the rules: {e}")
    except Stop as e:
        comment(f"**The split in PR #{pr} was merged, but no parts were filed:** {e}. Fix it on `{default}` "
                f"(the split record and the catalog rows), then re-run the factory-split workflow for PR #{pr}.")
        print(f"::error::{e}")
        return 1

    # Parts already filed: the parent's sub-issues, plus the App's issues (a part filed but not yet linked).
    subs = api_list(read, f"repos/{repo}/issues/{source}/sub_issues")
    issues = api_list(read, f"repos/{repo}/issues?state=all&creator={urllib.parse.quote(APP_LOGIN)}&per_page=100")
    existing = existing_parts(subs + issues, source)
    linked = {i["number"] for i in subs}

    filed, failed = [], []
    for p in parts:
        try:
            number = existing.get(p["part"])
            new = number is None
            if new:
                url = gh(write, "issue", "create", "-R", repo, "--title", issue_title(p),
                         "--body-file", "-", data=issue_body(p, source, pr, record_path)).strip()
                number = int(url.rstrip("/").rsplit("/", 1)[1])
            if not has_markers(api_list(read, f"repos/{repo}/issues/{number}/comments"), p["part"]):
                gh(write, "issue", "comment", str(number), "-R", repo, "--body-file", "-", data=marker_comment(p, run_url))
            # Set by the App, so no stage starts (stage label triggers ignore bots): held for factory:go.
            gh(write, "issue", "edit", str(number), "-R", repo, "--add-label", "factory:ready-to-plan")
            if number not in linked:
                child_id = api(read, f"repos/{repo}/issues/{number}")["id"]
                gh(write, "api", "-X", "POST", f"repos/{repo}/issues/{source}/sub_issues", "-F", f"sub_issue_id={child_id}")
            filed.append((p, number, new))
        except (RuntimeError, ValueError, IndexError, KeyError) as e:
            failed.append((p, str(e)))

    if not failed:
        labels = {l["name"] for l in api(read, f"repos/{repo}/issues/{source}").get("labels") or []}
        old = sorted(l for l in labels if l.startswith("factory:") and l not in PROPERTY_LABELS)
        if old:
            gh(write, "issue", "edit", str(source), "-R", repo, "--remove-label", ",".join(old))

    lines = [f"**Split approved (PR #{pr}): {len(parts)} parts.**", ""]
    for p, number, new in filed:
        deps = ", ".join(p["depends_on"]) or "nothing"
        lines.append(f"- #{number} **{p['part']}** ({p['tier']}): {'filed' if new else 'already filed'}; "
                     f"depends on {deps}. Held: add `factory:go` to start planning.")
    lines += [f"- **{p['part']}**: not filed: {why}" for p, why in failed]
    lines += ["", "Close this issue by hand once its parts are done." if not failed else
              f"Re-run the factory-split workflow for PR #{pr} to finish; parts already filed are reused."]
    comment("\n".join(lines))
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
