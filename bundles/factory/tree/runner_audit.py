#!/usr/bin/env python3
"""The organization's runner audit: every runner group, compared exactly with what's expected (z-sdlc
process/factory.md, Enablement step 12, The runner audit).

    python3 .github/factory/runner_audit.py snapshot <organization> > expected.json
    python3 .github/factory/runner_audit.py workflow expected.json > factory-runner-audit.yml
    python3 runner_audit.py check expected.json        (in that workflow, on GitHub's own runners)

Why: the CI tier's runner-registration App (organization self-hosted runners: write) can register a runner into
any group and change any group's repositories and workflows, and its key is on the runner host. The audit runs off
that host, on GitHub-hosted runners, with a read-only App of its own (create_app.py --auditor), and every hour
compares:
- the set of runner groups;
- each group's visibility, whether public repositories may use it, its repositories, whether it's restricted to
  selected workflows, and those workflows;
- each group's runners: their names, IDs and custom labels. A group of just-in-time runners (the CI tier, whose
  runners come and go with their jobs) is checked by a name pattern, a most-at-once and their labels instead;
- the factory's runner labels on any runner outside the groups expected to carry them.
Anything different is drift: the run fails, and the workflow opens or updates an issue in its repository. So does
a run that can't read all of it, which fails closed: a revoked or narrowed key raises the alarm too.

What it doesn't see:
- anything done and undone between two runs: a runner registered into a group that takes one job and goes (a
  just-in-time one removes itself), or a group opened to another repository or workflow for one job and restored.
  The organization's audit log would see both (its REST API needs GitHub Enterprise Cloud): the upgrade;
- a runner in the CI tier's group that fits its name pattern and most-at-once (its jobs hold read-only tokens);
- repository-level runners, which belong to each repository's settings;
- a run that never happens: silence isn't an all-clear, so look at the workflow's runs now and then. GitHub turns
  off a public repository's schedules after 60 days without activity: keep the audit in a private one;
- the audit's own job taken by a runner of the key holder's: one registered with a GitHub-hosted label
  (ubuntu-latest) shortly before a run, in a group the audit's repository may use, then removed, answers for the
  audit. A runner left with such a label is drift, and so is a group opened to the audit's repository, so keep the
  audit's repository out of every group (the default one included). Each run's job names the runner that took it.

`workflow` writes this script and the expected state into the workflow file itself. Neither App the factory uses
has the workflows permission, so neither can change what the audit expects, or the audit. Regenerate the file to
change either; never edit it by hand.

Exit 0: as expected. 1: drift. 2: couldn't read the organization, or a usage or settings error. Standard library and
openssl only.
"""

import base64
import http.client
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"
FIELDS = ("visibility", "allows_public_repositories", "restricted_to_workflows")
LISTS = ("repositories", "selected_workflows")
DEFAULT_LABELS = ("factory", "factory-plan", "factory-prod", "factory-ci")
# A self-hosted runner carrying one of these could take a job meant for GitHub's own runners, the audit's included.
HOSTED_STYLE = re.compile(r"(ubuntu|windows|macos)(-.*)?", re.I)
# Hourly: an hour's gap between a change and its alarm, for about 12 hosted minutes a day. Tighten it here (and
# regenerate) if that gap is too long; the audit log closes it entirely.
CRON = "17 * * * *"
# The heredocs' ends in the workflow, built so this file, written into one of them, never contains either.
SCRIPT_END, EXPECTED_END = "RUNNER_AUDIT_" + "SCRIPT_END", "RUNNER_AUDIT_" + "EXPECTED_END"
# A GitHub expression's opening, built so this file never contains it: the file is written into a workflow, where
# GitHub would read one as an expression.
EXPRESSION = "$" + "{{"
ISSUE_TITLE = "Runner audit: the organization's runner groups aren't as expected"


class Unreadable(Exception):
    """The organization couldn't be read in full: the audit fails closed."""


def printable(text, limit=300):
    return " ".join("".join(c if 32 <= ord(c) < 127 else " " for c in str(text)).split())[:limit]


def api(method, path, bearer, body=None, base=API):
    """(HTTP status, a JSON object or None). Anything short of an answer is Unreadable."""
    request = urllib.request.Request(base + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                     headers={"Accept": ACCEPT, "X-GitHub-Api-Version": API_VERSION,
                                              "Authorization": f"Bearer {bearer}", "User-Agent": "z-sdlc-runner-audit"})
    try:
        with urllib.request.urlopen(request, timeout=30) as r:
            status, text = r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        status, text = e.code, ""
    except (OSError, ValueError, http.client.HTTPException) as e:
        raise Unreadable(f"{method} {path}: {type(e).__name__}: {printable(e, 200)}") from None
    try:
        data = json.loads(text) if text else None
    except ValueError:
        data = None
    return status, data if isinstance(data, dict) else None


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def app_jwt(client_id, key_file, now=None):
    """The audit App's JWT (RS256), signed by openssl."""
    now = int(now if now is not None else time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": client_id}).encode())
    r = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key_file)], input=f"{header}.{claims}".encode(),
                       capture_output=True, timeout=30)
    if r.returncode or not r.stdout:
        raise Unreadable("openssl couldn't sign with the audit App's key")
    return f"{header}.{claims}.{b64url(r.stdout)}"


def installation_token(org, client_id, key_text, call=api):
    """A token of the audit App's installation on the organization, narrowed to reading its runners."""
    with tempfile.TemporaryDirectory() as tmp:
        key_file = pathlib.Path(tmp) / "key.pem"
        fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(key_text)
        jwt = app_jwt(client_id, key_file)
    status, data = call("GET", f"/orgs/{org}/installation", jwt)
    if status != 200 or not data or not isinstance(data.get("id"), int):
        raise Unreadable(f"the audit App isn't installed on {org}: HTTP {status}")
    status, data = call("POST", f"/app/installations/{data['id']}/access_tokens", jwt,
                        {"permissions": {"organization_self_hosted_runners": "read"}})
    if status != 201 or not data or not data.get("token"):
        raise Unreadable(f"the audit App's installation token: HTTP {status}")
    return data["token"]


def paged(get, path, key):
    items, page = [], 1
    while True:
        status, data = get(f"{path}?per_page=100&page={page}")
        if status != 200 or not data or not isinstance(data.get(key), list):
            raise Unreadable(f"{path}: HTTP {status}")
        items += data[key]
        if len(data[key]) < 100:
            return items
        page += 1


def current(org, get):
    """The organization's runner groups as they are, in the expected state's shape."""
    groups = {}
    for g in paged(get, f"/orgs/{org}/actions/runner-groups", "runner_groups"):
        if not isinstance(g, dict) or not isinstance(g.get("id"), int) or not isinstance(g.get("name"), str):
            raise Unreadable("a runner group without an ID or a name")
        base = f"/orgs/{org}/actions/runner-groups/{g['id']}"
        entry = {f: g.get(f) for f in FIELDS}
        entry["selected_workflows"] = sorted(g.get("selected_workflows") or [])
        # A group open to every repository has no list of them.
        entry["repositories"] = (sorted(str(r.get("full_name")) for r in paged(get, f"{base}/repositories", "repositories")
                                        if isinstance(r, dict))
                                 if g.get("visibility") == "selected" else [])
        runners = {}
        for r in paged(get, f"{base}/runners", "runners"):
            if not isinstance(r, dict) or not isinstance(r.get("id"), int) or not isinstance(r.get("name"), str):
                raise Unreadable(f"group {g['name']}: a runner without an ID or a name")
            runners[r["name"]] = {"id": r["id"], "labels": sorted(
                str(label.get("name")) for label in r.get("labels") or []
                if isinstance(label, dict) and label.get("type") == "custom")}
        entry["runners"] = runners
        groups[g["name"]] = entry
    return groups


def strings(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def load_expected(text):
    """The expected state, checked for shape: a malformed one is a settings error, never an empty audit."""
    expected = json.loads(text)

    def bad(what):
        raise ValueError(f"the expected state: {what}")

    if not isinstance(expected, dict) or not isinstance(expected.get("organization"), str):
        bad("an object with the organization's name")
    if not isinstance(expected.get("groups"), dict) or not expected["groups"]:
        bad("groups, by name")
    labels = expected.get("factory_labels", [])
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        bad("factory_labels, a list of labels")
    for name, group in expected["groups"].items():
        if not isinstance(group, dict):
            bad(f"group {name}: an object")
        for f in FIELDS:
            if f in group and not isinstance(group[f], (str if f == "visibility" else bool)):
                bad(f"group {name}: {f}")
        for f in LISTS:
            if f in group and not (isinstance(group[f], list) and all(isinstance(x, str) for x in group[f])):
                bad(f"group {name}: {f}, a list")
        runners = group.get("runners")
        if isinstance(runners, dict) and "pattern" in runners:
            try:
                matches_nothing_in_particular = re.fullmatch(runners["pattern"], "") is not None
            except (re.error, TypeError):
                bad(f"group {name}: runners.pattern, a regular expression")
            if matches_nothing_in_particular:
                bad(f"group {name}: runners.pattern matches an empty name: name the runners, such as "
                    "^<prefix>-ci-[0-9]+-[0-9a-f]{6}$")
            if not isinstance(runners.get("max"), int) or runners["max"] < 1 or not strings(runners.get("labels")):
                bad(f"group {name}: runners, a pattern with max (1 or more) and labels")
        elif not isinstance(runners, dict) or not all(
                isinstance(r, dict) and isinstance(r.get("id"), int) and strings(r.get("labels"))
                for r in runners.values()):
            bad(f"group {name}: runners, by name, each with its id and labels")
    return expected


def label_homes(expected):
    """For each factory label, the groups whose runners are expected to carry it."""
    homes = {label: set() for label in expected.get("factory_labels", [])}
    for name, group in expected["groups"].items():
        runners = group["runners"]
        carried = set(runners["labels"]) if "pattern" in runners else {x for r in runners.values() for x in r["labels"]}
        for label in carried & set(homes):
            homes[label].add(name)
    return homes


def drift(expected, groups):
    """Every difference between the expected state and the groups as they are, as sentences."""
    out, want = [], expected["groups"]
    out += [f"group {n}: not expected (a new group)" for n in sorted(set(groups) - set(want))]
    out += [f"group {n}: expected, but it's gone" for n in sorted(set(want) - set(groups))]
    for name in sorted(set(want) & set(groups)):
        w, h = want[name], groups[name]
        for f in FIELDS:
            if f in w and h.get(f) != w[f]:
                out.append(f"group {name}: {f} is {json.dumps(h.get(f))}, expected {json.dumps(w[f])}")
        for f in LISTS:
            if f in w:
                extra, missing = sorted(set(h[f]) - set(w[f])), sorted(set(w[f]) - set(h[f]))
                out += [f"group {name}: {f} has {x}, not expected" for x in extra]
                out += [f"group {name}: {f} is missing {x}" for x in missing]
        out += runner_drift(name, w["runners"], h["runners"])
    homes = label_homes(expected)
    for name, group in sorted(groups.items()):
        for runner, r in sorted(group["runners"].items()):
            for label in r["labels"]:
                if HOSTED_STYLE.fullmatch(label):
                    out.append(f"group {name}: runner {runner} carries {label}, a GitHub-hosted runner's label: it "
                               "could take jobs meant for GitHub's own runners, this audit's included")
                if label in homes and name not in homes[label]:
                    out.append(f"group {name}: runner {runner} carries the factory label {label}, expected only in "
                               f"{', '.join(sorted(homes[label])) or 'no group'}")
    return out


def runner_drift(group, want, have):
    out = []
    if "pattern" in want:
        for name, r in sorted(have.items()):
            if not re.fullmatch(want["pattern"], name):
                out.append(f"group {group}: runner {name} doesn't match {want['pattern']}")
            if r["labels"] != sorted(want["labels"]):
                out.append(f"group {group}: runner {name} has labels {', '.join(r['labels']) or 'none'}, expected "
                           f"{', '.join(sorted(want['labels']))}")
        if len(have) > want["max"]:
            out.append(f"group {group}: {len(have)} runners, at most {want['max']} expected")
        return out
    out += [f"group {group}: runner {n} (ID {have[n]['id']}) not expected" for n in sorted(set(have) - set(want))]
    out += [f"group {group}: runner {n} expected, but it's gone" for n in sorted(set(want) - set(have))]
    for name in sorted(set(want) & set(have)):
        w, h = want[name], have[name]
        if h["id"] != w["id"]:
            out.append(f"group {group}: runner {name} is registered again (ID {h['id']}, expected {w['id']}): "
                       "a runner registered with --replace takes an existing runner's name")
        if h["labels"] != sorted(w["labels"]):
            out.append(f"group {group}: runner {name} has labels {', '.join(h['labels']) or 'none'}, expected "
                       f"{', '.join(sorted(w['labels'])) or 'none'}")
    return out


def audit(expected, get):
    """(exit status, report lines)."""
    try:
        groups = current(expected["organization"], get)
    except Unreadable as e:
        return 2, [f"couldn't read the organization's runner groups: {e}"]
    found = drift(expected, groups)
    if found:
        return 1, [f"DRIFT {line}" for line in found]
    runners = sum(len(g["runners"]) for g in groups.values())
    return 0, [f"ok: {len(groups)} runner groups and {runners} runners, as expected"]


def factory_labels():
    """The factory's runner labels: factory.json's, when this runs from a factory checkout."""
    try:
        runners = json.loads((pathlib.Path(__file__).resolve().parent / "factory.json").read_text())["runners"]
        return sorted({v for v in runners.values() if isinstance(v, str)} | set(DEFAULT_LABELS))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return list(DEFAULT_LABELS)


def snapshot(org, token, call=api):
    """The groups as they are, as an expected state to review (and, for the CI tier's group, to edit: its runners
    become a pattern, a most-at-once and labels)."""
    groups = current(org, lambda path: call("GET", path, token))
    return {"organization": org, "factory_labels": factory_labels(), "groups": groups}


def indent(text, spaces):
    pad = " " * spaces
    return "".join(pad + line if line.strip() else "\n" for line in text.splitlines(keepends=True))


def workflow(expected_text, script_text, cron=CRON):
    """The audit's workflow, with this script and the expected state written into it."""
    load_expected(expected_text)
    for what, text, end in (("the expected state", expected_text, EXPECTED_END), ("the script", script_text, SCRIPT_END)):
        if EXPRESSION in text:
            raise ValueError(f"{what} can't contain a dollar sign followed by two braces: GitHub would read an expression")
        if end in text:
            raise ValueError(f"{what} can't contain {end}")
    if not re.fullmatch(r"[0-9*/,-]+( [0-9*/,-]+){4}", cron):
        raise ValueError(f"--cron {cron!r} isn't a five-field schedule")
    # Written as JSON again, ASCII only: nothing of the operator's file but its data reaches the workflow.
    expected_text = json.dumps(json.loads(expected_text), indent=2, ensure_ascii=True) + "\n"
    return f"""# The organization's runner audit, generated by z-sdlc's runner_audit.py (process/factory.md, Enablement step
# 12). Regenerate it; never edit it by hand. The expected state and the audit itself are in this file because only
# someone who may change workflows can change it: neither App the factory uses can.
name: factory-runner-audit

on:
  schedule:
    # Hourly: an hour's gap between a change and its alarm, for about 12 hosted minutes a day. Tighten it with
    # runner_audit.py workflow --cron; the organization's audit log would close the gap entirely.
    - cron: "{cron}"
  workflow_dispatch:

permissions:
  issues: write

concurrency:
  group: factory-runner-audit

jobs:
  audit:
    # GitHub's own runners only: the audit must not run on a host it audits.
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Audit the organization's runner groups
        # The step's own limit, under the job's: a step that runs out of time fails, and the alarm still runs.
        timeout-minutes: 8
        shell: bash
        env:
          AUDIT_APP_CLIENT_ID: {EXPRESSION} vars.RUNNER_AUDIT_APP_CLIENT_ID }}}}
          AUDIT_APP_KEY: {EXPRESSION} secrets.RUNNER_AUDIT_APP_KEY }}}}
        run: |
          cat > "$RUNNER_TEMP/runner_audit.py" <<'{SCRIPT_END}'
{indent(script_text, 10)}          {SCRIPT_END}
          cat > "$RUNNER_TEMP/expected.json" <<'{EXPECTED_END}'
{indent(expected_text, 10)}          {EXPECTED_END}
          python3 -I "$RUNNER_TEMP/runner_audit.py" check "$RUNNER_TEMP/expected.json" | tee "$RUNNER_TEMP/report.txt"

      # Also when the audit ran out of time (cancelled). A failed scheduled run also emails whoever last changed the
      # schedule: the one channel no App can touch.
      - name: Raise the alarm in an issue
        if: failure() || cancelled()
        shell: bash
        env:
          GH_TOKEN: {EXPRESSION} github.token }}}}
          GH_REPO: {EXPRESSION} github.repository }}}}
          NOTIFY: {EXPRESSION} vars.RUNNER_AUDIT_NOTIFY }}}}
        run: |
          title="{ISSUE_TITLE}"
          report=$(head -c 60000 "$RUNNER_TEMP/report.txt" 2> /dev/null || true)
          [[ -n $report ]] || report="the audit failed before it wrote a report: see the run"
          # The repository's RUNNER_AUDIT_NOTIFY variable names the people to mention: GitHub logins, space-separated.
          cc=$(printf '%s' "$NOTIFY" | tr -cs 'A-Za-z0-9-' ' ' | sed -E 's/(^| )([A-Za-z0-9-]+)/\\1@\\2/g; s/^ +//; s/ +$//')
          [[ -z $cc ]] || cc="$cc"$'\\n\\n'
          body=$(printf '%sRun: %s\\n\\n```\\n%s\\n```\\n' "$cc" \\
            "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID" "$report")
          # An open issue the workflow itself opened gets the comment; anything else (none, one someone else opened
          # with this title, one locked or closed meanwhile) gets a new issue, so a decoy can't swallow the alarm.
          number=$(gh issue list --state open --author "app/github-actions" --search "\\"$title\\" in:title" \\
            --json number --jq '.[0].number // empty') || number=
          if [[ -z $number ]] || ! gh issue comment "$number" --body "$body"; then
            gh issue create --title "$title" --body "$body"
          fi
"""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = __doc__.split("\n\n")[1]
    if not argv or argv[0] not in ("snapshot", "workflow", "check"):
        print(usage, file=sys.stderr)
        return 2
    try:
        if argv[0] == "snapshot":
            if len(argv) != 2 or not re.fullmatch(r"[A-Za-z0-9-]+", argv[1]):
                print(usage, file=sys.stderr)
                return 2
            token = os.environ.get("GH_TOKEN") or subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                                                                 timeout=30).stdout.strip()
            print(json.dumps(snapshot(argv[1], token), indent=2, sort_keys=True))
            return 0
        if argv[0] == "workflow":
            cron = CRON
            if "--cron" in argv:
                cron = argv[argv.index("--cron") + 1]
            print(workflow(pathlib.Path(argv[1]).read_text(), pathlib.Path(__file__).read_text(), cron), end="")
            return 0
        expected = load_expected(pathlib.Path(argv[1]).read_text())
        client_id, key = os.environ.get("AUDIT_APP_CLIENT_ID", ""), os.environ.get("AUDIT_APP_KEY", "")
        if not client_id or not key:
            print("couldn't read the organization's runner groups: no audit App client ID or key (the repository's "
                  "RUNNER_AUDIT_APP_CLIENT_ID variable and RUNNER_AUDIT_APP_KEY secret)")
            return 2
        try:
            token = installation_token(expected["organization"], client_id, key)
        except Unreadable as e:
            print(f"couldn't read the organization's runner groups: {e}")
            return 2
        status, lines = audit(expected, lambda path: api("GET", path, token))
        print("\n".join(lines))
        return status
    except (OSError, ValueError, IndexError, subprocess.SubprocessError) as e:
        print(f"runner_audit: {printable(e)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
