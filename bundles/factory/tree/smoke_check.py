"""Assert that a factory run loaded the framework, from the runtime's own init event.

Usage: python3 smoke_check.py <execution_file> [expected_claude_code_version]

Reads the claude-code-action execution file (a JSON array of SDK messages), finds the
system/init event, and fails unless every `.claude/skills/*` skill, every
`.claude/agents/*` agent and a connected Context7 MCP server are present. Writes the
findings and the run's cost to the job summary either way.
"""

import json
import os
import pathlib
import sys

REPO = pathlib.Path(os.environ.get("GITHUB_WORKSPACE", "."))


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    text = "\n".join(lines) + "\n"
    if path:
        with open(path, "a") as f:
            f.write(text)
    print(text)


def main():
    messages = json.loads(pathlib.Path(sys.argv[1]).read_text())
    expected_version = sys.argv[2] if len(sys.argv) > 2 else None
    init = next((m for m in messages if m.get("type") == "system" and m.get("subtype") == "init"), None)
    result = next((m for m in reversed(messages) if m.get("type") == "result"), None)
    if init is None:
        summary(["### Factory smoke: FAILED", "No system/init event in the execution file."])
        return 1

    want_skills = sorted(p.parent.name for p in REPO.glob(".claude/skills/*/SKILL.md"))
    want_agents = sorted(p.stem for p in REPO.glob(".claude/agents/*.md"))
    got_skills = set(init.get("skills") or [])
    got_agents = init.get("agents")
    servers = {s.get("name"): s.get("status") for s in init.get("mcp_servers") or []}

    failures = []
    missing_skills = [s for s in want_skills if s not in got_skills]
    if not want_skills:
        failures.append("checkout has no .claude/skills/*/SKILL.md")
    if missing_skills:
        failures.append(f"skills not loaded: {', '.join(missing_skills)}")
    if got_agents is None:
        failures.append("init event has no `agents` field: add a self-report fallback")
        missing_agents = want_agents
    else:
        missing_agents = [a for a in want_agents if a not in set(got_agents)]
        if missing_agents:
            failures.append(f"agents not loaded: {', '.join(missing_agents)}")
    if servers.get("context7") != "connected":
        failures.append(f"context7 MCP not connected (status: {servers.get('context7', 'absent')})")
    if init.get("permissionMode") != "auto":
        failures.append(f"permission mode is {init.get('permissionMode')}, expected auto")
    if init.get("apiKeySource") == "ANTHROPIC_API_KEY":
        failures.append("billed to an API key, not the Max OAuth token")
    version = init.get("claude_code_version")
    if expected_version and version != expected_version:
        failures.append(f"Claude Code {version}, expected the pinned {expected_version}")
    if result is None or result.get("is_error"):
        failures.append(f"run did not finish cleanly (result subtype: {result and result.get('subtype')})")

    cost = result.get("total_cost_usd") if result else None
    lines = [
        f"### Factory smoke: {'FAILED' if failures else 'passed'}",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Claude Code | `{version}` |",
        f"| Model | `{init.get('model')}` |",
        f"| Permission mode | `{init.get('permissionMode')}` |",
        f"| API key source | `{init.get('apiKeySource')}` |",
        f"| Skills | {len(want_skills) - len(missing_skills)}/{len(want_skills)} repo skills loaded ({len(got_skills)} total) |",
        f"| Agents | {len(want_agents) - len(missing_agents)}/{len(want_agents)} repo agents loaded |",
        f"| MCP servers | {', '.join(f'{k}={v}' for k, v in servers.items()) or 'none'} |",
        f"| Turns | {result and result.get('num_turns')} |",
        f"| Cost (API-rate equivalent) | {'$%.4f' % cost if cost is not None else 'n/a'} |",
        "",
    ]
    lines += [f"- {f}" for f in failures]
    if result and result.get("result"):
        lines += ["", "**Reply:**", "", "> " + str(result["result"]).replace("\n", "\n> ")]
    lines += ["", "<details><summary>init event</summary>", "", "```json",
              json.dumps(init, indent=2), "```", "</details>"]
    summary(lines)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
