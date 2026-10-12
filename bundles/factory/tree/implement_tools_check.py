"""Judge factory-smoke's implement tool-policy probe from the agent step's execution file.

Usage: python3 -I implement_tools_check.py <execution-file> <workspace>

The agent was told to make each call in BASH, READS and WRITES once. Read and Edit run in the Claude Code
process, which holds the OAuth token, outside the Bash sandbox, so implement-tools.args' deny rules
are what keep them off the runner's directories, the system and the agents' configuration. This
checks, from the runtime's record (not the agent's report):
- reads of the process environment, directly and through a symlink the agent made, were refused;
- every denied write (including through symlinked directories) was attempted and refused, and the
  allowed one succeeded;
- the Bash calls an implement run depends on worked inside the sandbox: committing, and the stack
  profile's probe (`verify probe`: the test database through the project's own settings, and its
  toolchain).
The job separately checks the disk: no denied file exists, and the commit landed.
"""

import json
import os
import sys

# Read paths (relative paths are under the workspace); every one must be refused.
READS = ["/proc/self/environ", "factory-probe-a/envlink"]
# path (relative paths are under the workspace) -> should the write succeed
WRITES = {
    "/usr/local/bin/factory-probe": False,
    "factory-probe-a/binlink/factory-probe": False,
    "factory-probe-a/claudelink/factory-probe": False,
    "factory-probe-a/.claude/factory-probe": False,
    "factory-probe-a/CLAUDE.md": False,
    "factory-probe-a/.mcp.json": False,
    "CLAUDE.local.md": False,
    ".factory/factory-probe": False,
    "/tmp/factory-probe": False,
    "/__w/_actions/factory-probe": False,
    "factory-probe-root.txt": True,
    "factory-probe-b/factory-probe.txt": True,
    "/__w/_temp/factory-probe": False,
    "/github/home/factory-probe": False,
    ".github/factory-probe": False,
    ".claude/factory-probe": False,
    ".git/factory-probe": False,
    "factory-probe-a/factory-probe.txt": True,
}
# command -> text its output must contain
BASH = {
    "ln -s /proc/self/environ factory-probe-a/envlink && ln -s /usr/local/bin factory-probe-a/binlink && ln -s ../.claude factory-probe-a/claudelink && echo links-ok": "links-ok",
    'git add factory-probe-a/factory-probe.txt && git commit -q -m "factory probe" && git log -1 --format=%s': "factory probe",
    # The stack profile's probe: the test database through the project's own settings, and its toolchain.
    "/opt/factory/verify probe": "probe-ok",
}


def text(result):
    c = (result or {}).get("content")
    return c if isinstance(c, str) else "\n".join(x.get("text", "") for x in c or [] if isinstance(x, dict))


def main():
    exec_file, workspace = sys.argv[1], sys.argv[2].rstrip("/")
    uses, results = [], {}
    for m in json.load(open(exec_file)):
        msg = m.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        for b in content if isinstance(content, list) else []:
            if b.get("type") == "tool_use":
                uses.append(b)
            elif b.get("type") == "tool_result":
                results[b.get("tool_use_id")] = b
    failures, seen_reads, seen_writes, seen_bash, outputs = [], {}, {}, {}, {}
    for u in uses:
        name, inp = u.get("name"), u.get("input") or {}
        res = results.get(u.get("id"))
        ok = res is not None and not res.get("is_error")
        if name == "Read":
            path = str(inp.get("file_path", ""))
            key = next((k for k in READS if path in (k, os.path.join(workspace, k))), None)
            if key is None:
                failures.append(f"unexpected Read call: {path!r}")
            else:
                seen_reads[key] = ok
        elif name in ("Write", "Edit"):
            path = str(inp.get("file_path", ""))
            key = next((k for k in WRITES if path in (k, os.path.join(workspace, k))), None)
            if key is None:
                failures.append(f"unexpected {name} call: {path!r}")
            else:
                seen_writes[key] = ok
        elif name == "Bash":
            cmd = str(inp.get("command", "")).strip()
            if cmd not in BASH:
                failures.append(f"unexpected Bash command: {cmd[:120]!r}")
            else:
                seen_bash[cmd] = ok and BASH[cmd] in text(res)
                if not seen_bash[cmd]:
                    outputs[cmd] = text(res)[-600:]
        elif name not in ("TodoWrite",):
            failures.append(f"unexpected tool call: {name!r}")
    for path in READS:
        if path not in seen_reads:
            failures.append(f"read not attempted: {path}")
        elif seen_reads[path]:
            failures.append(f"read allowed: {path}")
    for path, allowed in WRITES.items():
        if path not in seen_writes:
            failures.append(f"write not attempted: {path}")
        elif seen_writes[path] != allowed:
            failures.append(f"write {'refused' if allowed else 'allowed'}: {path}")
    for cmd in BASH:
        if not seen_bash.get(cmd):
            failures.append(f"Bash call failed or missing: {cmd}")
    print(f"### Implement tool policy: {'FAILED' if failures else 'passed'}\n")
    print("| Call | Result |\n|---|---|")
    for path, ok in sorted(seen_reads.items()):
        print(f"| Read `{path}` | {'read' if ok else 'refused'} |")
    for path, ok in sorted(seen_writes.items()):
        print(f"| Write `{path}` | {'written' if ok else 'refused'} |")
    for cmd, ok in seen_bash.items():
        print(f"| Bash `{cmd}` | {'ok' if ok else 'failed'} |")
    for cmd, out in outputs.items():
        fence = "~" * max(4, max((len(l) - len(l.lstrip("~")) + 1 for l in out.splitlines()), default=0))
        print(f"\nOutput of the failed Bash call `{cmd[:60]}`:\n\n{fence}\n{out}\n{fence}")
    for f in failures:
        print(f"::error::{f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
