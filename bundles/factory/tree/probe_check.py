"""Assert the agent tool policy (triage-tools.args) held, from a probe run's execution file.

Usage: python3 probe_check.py <execution_file>

The probe prompt asks the agent to attempt reads the policy must deny and one it must allow.
Fails unless: no write, shell or fetch tool was available; every attempt on a denied path
errored; at least one denied path was actually attempted; and a normal repo read and a
Context7 call succeeded.
"""

import json
import os
import pathlib
import sys

FORBIDDEN_TOOLS = {"Bash", "Write", "Edit", "MultiEdit", "NotebookEdit", "WebFetch", "Task", "Agent"}
DENIED_PREFIXES = ("/proc", "/dev", "/__w/_temp", "/__w/_actions", "/__e", "/github")


def target(call):
    inp = call.get("input", {})
    return inp.get("file_path") or inp.get("path") or inp.get("pattern") or ""


def is_denied_target(path):
    return path.startswith(DENIED_PREFIXES) or "/.git/" in path or path.startswith(".git/") or path.endswith("/.git")


def main():
    messages = json.loads(pathlib.Path(sys.argv[1]).read_text())
    init = next(m for m in messages if m.get("type") == "system" and m.get("subtype") == "init")
    calls, results = {}, {}
    for m in messages:
        msg = m.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for b in content:
            if b.get("type") == "tool_use":
                calls[b["id"]] = b
            elif b.get("type") == "tool_result":
                results[b["tool_use_id"]] = b

    failures, rows = [], []
    leaked = sorted(FORBIDDEN_TOOLS & set(init.get("tools", [])))
    if leaked:
        failures.append(f"forbidden tools available: {', '.join(leaked)}")
    denied_attempts = allowed_read = context7_ok = 0
    for cid, call in calls.items():
        res = results.get(cid, {})
        errored = bool(res.get("is_error")) or "denied" in str(res.get("content", "")).lower()
        name, path = call["name"], target(call)
        rows.append(f"| {name} | `{path or json.dumps(call.get('input'))[:60]}` | {'denied' if errored else 'allowed'} |")
        if name in ("Read", "Grep", "Glob") and is_denied_target(path):
            denied_attempts += 1
            if not errored:
                failures.append(f"{name} on {path} was NOT denied")
        elif name == "Read" and not errored:
            allowed_read += 1
        elif name.startswith("mcp__context7") and not errored:
            context7_ok += 1
    if denied_attempts < 2:
        failures.append(f"probe attempted only {denied_attempts} denied-path reads (need >= 2)")
    if not allowed_read:
        failures.append("no normal repo read succeeded")
    if not context7_ok:
        failures.append("no Context7 call succeeded")

    lines = [f"### Tool policy probe: {'FAILED' if failures else 'passed'}", "",
             f"Tools available: `{', '.join(init.get('tools', []))}`", "",
             "| Tool | Target | Result |", "|---|---|---|", *rows, ""]
    lines += [f"- {f}" for f in failures]
    text = "\n".join(lines) + "\n"
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(text)
    print(text)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
