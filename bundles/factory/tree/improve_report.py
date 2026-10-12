"""Render the weekly improvement report from the analysis and the digest (factory-improve.yml, report job).

Usage: python3 -I improve_report.py <digest.json> <result.json> <run-url> <out-dir>
       Writes <out-dir>/title, <out-dir>/body.md (the issue) and <out-dir>/notes.md (the run summary's
       record). Every refusal is printed as ::error:: and exits 1; nothing is posted then.

CD's decisions (2026-10-10, handoff § Next build): report only; every item actionable or "nothing to
action"; every area covered; the top items first; the same proposal never shown twice. So:
- Structure is this script's, never the agent's: headings, numbering, links and the marker. Agent text
  goes through the guard's literal() (one line, every punctuation mark escaped, markers, mentions and refs
  neutralized). A result with token-shaped strings, images or embeds is refused whole.
- Evidence is checked against the digest: an id the harvest didn't produce is dropped, a proposal left
  with none is dropped, and the report says so. Links come from the digest, never from agent text.
- Fingerprints are this script's: a hash of section, target and title for a new proposal. The agent may
  only point at a fingerprint the ledger already has (`matches`); an unknown one is ignored.
- A proposal matching an earlier one isn't re-proposed: it's one line under Earlier proposals with the
  new evidence. Open items from earlier reports are listed there too, numbered, so CD can decide them here.
- The marker at the top (`<!-- factory-improve: {...} -->`) carries the week, the window, the cost and
  every numbered item; the next harvest rebuilds the ledger from it and from CD's replies.
"""

import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import implement_guard as guard  # noqa: E402

HEADLINE = 5
MAX_OPEN_LISTED = 15
BODY_CAP = 60000
SECTIONS = {"factory-process": "Factory process", "sdlc-content": "SDLC content", "z-sdlc": "For z-sdlc",
            "factory-infrastructure": "Factory infrastructure", "project": "The project"}
ROUTES = {"hygiene": "SDLC hygiene an agent may write", "cd": "you apply", "z-sdlc": "carry to z-sdlc",
          "issue": "file as an issue"}
# The framework was renamed from cc-sdlc to z-sdlc (2026-10-12): an analysis by a pre-rename sdlc-audit names
# the framework section and route cc-sdlc. Read as z-sdlc.
RENAMED = {"cc-sdlc": "z-sdlc"}
SEVERITY = {"high": 0, "medium": 1, "low": 2}
STATUS_ORDER = {"open": 0, "deferred": 1, "accepted": 2, "rejected": 3}
FAILED = {"failure", "timed_out", "startup_failure"}


class Refused(Exception):
    pass


def plural(n, word, many=None):
    return f"{n} {word if n == 1 else many or word + 's'}"


def fingerprint(section, target, title):
    norm = lambda s: " ".join(s.lower().split())  # noqa: E731
    # Hashed under the framework section's name before the rename, so its proposals keep their fingerprints.
    section = {"z-sdlc": "cc-sdlc"}.get(section, section)
    return hashlib.sha256(f"{section}|{norm(target)}|{norm(title)}".encode()).hexdigest()[:10]


def marker(data):
    """The ledger marker: one line of JSON with nothing that can close the comment, mention anyone or
    reference an issue (JSON escapes, which the harvest's parse turns back into the same text)."""
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
    for ch in "<>&@#":
        text = text.replace(ch, f"\\u{ord(ch):04x}")
    return f"<!-- factory-improve: {text} -->"


def check(result, schema):
    try:
        guard.conforms(result, schema, "result")
    except guard.Refused as e:
        raise Refused(f"the analysis breaks its schema: {e}")
    for text in guard.strings(result):
        if guard.TOKEN.search(text):
            raise Refused("the analysis contains a credential-like string")
        if guard.EMBED.search(text):
            raise Refused("the analysis contains an image or embed")
    if result["status"] != "awaiting-approval":
        raise Refused(f"the analysis returned {result['status']}: {result['reason'][:300]}")


def link(signal, repo):
    """A link to a signal, labelled from its kind and numbers (never from quoted text)."""
    url = signal.get("url") or ""
    if not re.match(rf"^https://github\.com/{re.escape(repo)}/[A-Za-z0-9/#_.?=-]+$", url):
        return None
    kind, pr, issue = signal["kind"], signal.get("pr"), signal.get("issue")
    label = {
        "review": f"review on PR {pr}",
        "revision": f"revision {signal.get('revision')} on PR {pr}",
        "pr-outcome": f"PR {pr} {signal.get('outcome')}",
        "question": f"question on {issue}",
        "triage": f"triage of {issue}",
        "override": f"override on {issue}",
        "release": f"release of {issue}",
        "revision-request": f"revision asked on {issue}",
        "gate-retry": f"gate retry on {issue}",
        "escalation": f"escalation on {issue}",
        "follow-ups": f"follow-ups from PR {pr}",
        "failure": f"{signal.get('workflow')} failed" + (f" on {issue}" if issue else ""),
        "reaction": f"reaction on {issue}",
        "decision": f"your decision on report {signal.get('report')}",
        "commit": f"commit {signal['id'].split(':', 1)[1][:7]}",
    }.get(kind, kind)
    return f"[{label}]({url})"


def links(ids, signals, repo, limit=6):
    out = [link(signals[i], repo) for i in ids]
    out = [x for x in out if x]
    more = len(ids) - min(len(out), limit)
    return ", ".join(out[:limit]) + (f" and {more} more" if more > 0 else "")


def plan(digest, result):
    """Sort the proposals into new items, earlier ones seen again, and dropped ones."""
    signals = {s["id"]: s for s in digest["signals"]}
    ledger = {e["fingerprint"]: e for e in digest["ledger"]}
    new, again, dropped, bad_ids = {}, {}, [], 0
    for index, p in enumerate(result["proposals"]):
        p = {**p, "section": RENAMED.get(p["section"], p["section"]), "route": RENAMED.get(p["route"], p["route"])}
        evidence = list(dict.fromkeys(i for i in p["evidence"] if i in signals))
        bad_ids += len(set(p["evidence"])) - len(evidence)
        if not evidence:
            dropped.append(p["title"])
            continue
        fp = p["matches"] if p["matches"] in ledger else fingerprint(p["section"], p["target"], p["title"])
        if fp in ledger:
            seen = again.setdefault(fp, {"entry": ledger[fp], "evidence": []})
            seen["evidence"] += [i for i in evidence if i not in ledger[fp]["evidence"] and i not in seen["evidence"]]
        elif fp in new:
            new[fp]["evidence"] += [i for i in evidence if i not in new[fp]["evidence"]]
        else:
            new[fp] = {"fp": fp, "p": p, "evidence": evidence, "index": index}
    ranked = sorted(new.values(), key=lambda x: (SEVERITY[x["p"]["severity"]], -len(x["evidence"]), x["index"]))
    earlier = [{**v, "fp": fp} for fp, v in again.items()]
    earlier += [{"fp": e["fingerprint"], "entry": e, "evidence": []} for e in digest["ledger"]
                if e["status"] in ("open", "deferred") and e["fingerprint"] not in again]
    earlier.sort(key=lambda x: (not x["evidence"], STATUS_ORDER[x["entry"]["status"]], x["entry"]["first_week"], x["fp"]))
    quiet = [x for x in earlier if not x["evidence"]]
    unlisted = quiet[MAX_OPEN_LISTED:]
    earlier = [x for x in earlier if x["evidence"]] + quiet[:MAX_OPEN_LISTED]
    return ranked, earlier, unlisted, dropped, bad_ids


def facts(digest):
    """The week in numbers, all from the digest."""
    counts = digest["counts"]
    sig = lambda kind: [s for s in digest["signals"] if s["kind"] == kind]  # noqa: E731
    runs = sum(n for per in digest["runs"].values() for c, n in per.items())
    failed = sum(n for per in digest["runs"].values() for c, n in per.items() if c in FAILED)
    outcomes = {}
    for s in sig("pr-outcome"):
        outcomes[s.get("outcome")] = outcomes.get(s.get("outcome"), 0) + 1
    asked = sig("question")
    answered = [q for q in asked if q.get("answered_at")]
    lines = [
        f"- **Factory runs:** {runs}, {failed} failed"
        + (f" (most in {max(digest['runs'], key=lambda w: sum(n for c, n in digest['runs'][w].items() if c in FAILED))})" if failed else ""),
        "- **Factory PRs closed:** " + (", ".join(f"{n} {k}" for k, n in sorted(outcomes.items())) or "none"),
        f"- **Your reviews:** {sum(1 for r in sig('review') if r.get('state') == 'changes_requested')} asked for changes; "
        f"{plural(counts.get('revision', 0), 'revision')} answered",
        f"- **Questions to you:** {len(asked)}, {len(answered)} answered in the window",
        f"- **Your overrides:** {plural(counts.get('override', 0), 'triage override')}, "
        f"{plural(counts.get('release', 0), 'release')}, "
        f"{plural(sum(len(s.get('unchecked') or []) for s in sig('follow-ups')), 'follow-up')} unchecked at merge",
    ]
    known = [m["cost"] for m in digest["metrics"] if isinstance(m.get("cost"), (int, float))]
    if digest["metrics"]:
        cost = f"${sum(known):.2f} at API rates over {len(known)} agent runs"
        if len(known) < len(digest["metrics"]):
            cost += f" ({len(digest['metrics']) - len(known)} more with no cost recorded)"
    else:
        # Before metrics records existed, PR bodies and revision comments carried the run's cost.
        recorded = [s["cost"] for s in digest["signals"] if s["kind"] in ("pr-outcome", "revision")
                    and isinstance(s.get("cost"), (int, float))]
        cost = (f"no metrics records; the window's PRs and revisions record ${sum(recorded):.2f} at API rates"
                if recorded else "not recorded (no metrics records in the window)")
    previous = digest.get("previous_report") or {}
    if isinstance(previous.get("cost"), (int, float)):
        cost += f"; last report ${previous['cost']:.2f}"
    lines.append(f"- **Cost:** {cost}")
    return lines, (round(sum(known), 2) if known else None)


def item_lines(n, x, signals, repo, full):
    p = x["p"]
    head = (f"**{n}. {guard.literal(p['title'])}** · {p['severity'].capitalize()} · {SECTIONS[p['section']]} · "
            f"{ROUTES[p['route']]}")
    target = f"`{p['target']}`" if guard.SAFE_PATH.match(p["target"]) else guard.literal(p["target"])
    if not full:
        return [f"- {head}. {target}: {guard.literal(p['change'])} Evidence: {links(x['evidence'], signals, repo)}"]
    return [head, "", f"- **Where:** {target}", f"- **Change:** {guard.literal(p['change'])}",
            f"- **Why:** {guard.literal(p['why'])} Evidence: {links(x['evidence'], signals, repo)}",
            f"- **Expected:** {guard.literal(p['effect'])}", ""]


def render(digest, result, run_url):
    signals = {s["id"]: s for s in digest["signals"]}
    repo, window = digest["repo"], digest["window"]
    ranked, earlier, unlisted, dropped, bad_ids = plan(digest, result)
    lines, cost = facts(digest)
    items, n = [], 0
    body = [f"**Factory improvement report, {window['week']}** ({window['since'][:10]} to {window['until'][:10]})", ""]
    previous = digest.get("previous_report")
    if not ranked and not any(x["evidence"] for x in earlier):
        body += ["**Nothing needs action this week.** " + guard.literal(result["summary"]), ""]
    else:
        body += [guard.literal(result["summary"]), ""]
    body += ["### The week", ""] + lines + [""]

    numbered = []
    for x in ranked:
        n += 1
        numbered.append((n, x))
        items.append({"n": n, "fp": x["fp"], "s": x["p"]["section"], "r": x["p"]["route"], "sev": x["p"]["severity"],
                      "t": x["p"]["title"][:120], "p": x["p"]["target"][:200], "e": x["evidence"]})
    if numbered:
        body += ["### Top items", ""]
        for n_, x in numbered[:HEADLINE]:
            body += item_lines(n_, x, signals, repo, full=True)
        body += ["### By section", ""]
        for key, name in SECTIONS.items():
            mine = [(n_, x) for n_, x in numbered if x["p"]["section"] == key]
            body += [f"#### {name}", ""]
            top = [str(n_) for n_, _ in mine if n_ <= HEADLINE]
            rest = [(n_, x) for n_, x in mine if n_ > HEADLINE]
            if top:
                body.append(f"- Item{'s' if len(top) > 1 else ''} {', '.join(top)} above.")
            for n_, x in rest:
                body += item_lines(n_, x, signals, repo, full=False)
            if not mine:
                body.append("Nothing to action.")
            body.append("")
    else:
        body += ["### By section", "", "Nothing to action in any section: " + ", ".join(SECTIONS.values()) + ".", ""]

    if earlier or unlisted:
        body += ["### Earlier proposals", ""]
        for x in earlier:
            n += 1
            e = x["entry"]
            status = {"open": f"open since {e['first_week']}", "deferred": f"deferred ({guard.literal(e['reason'])})" if e["reason"] else "deferred",
                      "accepted": "accepted", "rejected": f"rejected ({guard.literal(e['reason'])})" if e["reason"] else "rejected"}[e["status"]]
            seen = (f": seen again, {len(x['evidence'])} new signal{'s' if len(x['evidence']) > 1 else ''}: "
                    f"{links(x['evidence'], signals, repo)}") if x["evidence"] else "."
            body.append(f"- **{n}. {guard.literal(e['title'])}** ({status}; report #{e['last_report']}){seen}")
            items.append({"n": n, "fp": x["fp"], "s": e["section"], "r": e["route"], "sev": e["severity"],
                          "t": e["title"][:120], "p": e["target"][:200], "e": sorted(set(e["evidence"]) | set(x["evidence"]))})
        if unlisted:
            reports = sorted({x["entry"]["last_report"] for x in unlisted})
            body.append(f"- {len(unlisted)} more open item{'s' if len(unlisted) > 1 else ''} from earlier reports, "
                        f"not listed: {', '.join(f'#{r}' for r in reports)}. Decide them there.")
        body.append("")

    if dropped or bad_ids:
        body += ["### Dropped", ""]
        if dropped:
            body.append(f"- {len(dropped)} proposal{'s' if len(dropped) > 1 else ''} cited no signal the harvest "
                        f"produced, so {'they were' if len(dropped) > 1 else 'it was'} dropped: "
                        + "; ".join(guard.literal(t) for t in dropped) + ".")
        if bad_ids:
            body.append(f"- {bad_ids} evidence id{'s' if bad_ids > 1 else ''} the harvest didn't produce "
                        f"{'were' if bad_ids > 1 else 'was'} removed from the proposals above.")
        body.append("")

    if items:
        body += ["**Your call:** reply on this issue with `accept 1 3`, `reject 2: why`, or `defer 4`. You apply what "
                 "you accept (or ask a session to). Unanswered items stay open and come back as one line.", ""]
    footer = [f"factory improve · [run]({run_url})"]
    if previous:
        footer.append(f"last report #{previous['number']}")
    if window.get("capped"):
        footer.append("window capped at 35 days")
    body.append(f"<sub>{' · '.join(footer)}</sub>")
    state = {"v": 1, "week": window["week"], "since": window["since"], "until": window["until"], "cost": cost,
             "items": items}
    text = marker(state) + "\n" + "\n".join(body) + "\n"
    if len(text) > BODY_CAP:
        raise Refused(f"the report is {len(text)} characters (cap {BODY_CAP})")
    return f"Factory improvement report {window['week']}", text


def main():
    digest_path, result_path, run_url, out = sys.argv[1:5]
    digest = json.loads(pathlib.Path(digest_path).read_text())
    result = json.loads(pathlib.Path(result_path).read_text())
    schema = json.loads((pathlib.Path(__file__).resolve().parent / "improve.schema.json").read_text())
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        if digest.get("kind") != "factory-digest" or digest.get("version") != 1:
            raise Refused("the digest isn't a version 1 factory digest")
        check(result, schema)
        title, body = render(digest, result, run_url)
    except Refused as e:
        print(f"::error::{e}")
        return 1
    (out / "title").write_text(title + "\n")
    (out / "body.md").write_text(body)
    (out / "notes.md").write_text("<details><summary>Analysis notes</summary>\n\n" + guard.literal(result["notes"])
                                  + "\n\n</details>\n")
    print(f"{title}: {body.count(chr(10))} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
