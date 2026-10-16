"""Judge sandbox_probe.py output.

Usage:
  python3 -I sandbox_check.py control <control-output> <services>
  python3 -I sandbox_check.py agent <agent-output> <control-output> <services>

control: the probe ran unsandboxed with the real secrets in its environment and a canary planted
         under the runner's temp directory. It must find the OAuth and GitHub tokens in its
         environment and its process's environment, and the canary in a file (plain and base64),
         which proves each detection path works. The kernel files systempaths=unconfined unmasks
         must stay unreadable and unwritable.
agent:   the probe ran as sandboxed agent Bash. It must find no secret anywhere, no credential
         variable by name, a PID namespace other than the control's, unlistable runner mounts,
         unwritable protected paths, the allowed registries reachable through the proxy, every
         other host blocked, and no route that bypasses the proxy.
both:    the stack profile's test services (its `services` file, "<label> <port>" a line) answer on
         the job container's loopback (through the sandbox proxy, for the agent), and the Docker
         socket doesn't. A missing or malformed services file fails.

The job copies this file out of the workspace before the agent runs.
"""

import os
import re
import secrets
import sys

CREDENTIAL_NAMES = {
    "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "GH_TOKEN", "GITHUB_TOKEN",
    "OVERRIDE_GITHUB_TOKEN", "DEFAULT_WORKFLOW_TOKEN", "CONTEXT7_API_KEY",
    "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
}
REACHABLE = {"https://pypi.org/simple/", "https://registry.npmjs.org/"}
BLOCKED = {"https://example.com/", "https://api.github.com/"}
REQUIRED_KINDS = ["processes", "pid1", "pidns", "path", "write", "kcore", "procwrite", "localsvc", "unixsock",
                  "files-scanned", "net", "noproxy", "direct", "dns"]
SERVICE_LINE = re.compile(r"([a-z][a-z0-9-]*) ([1-9][0-9]{0,4})")


def read_services(path):
    """The test services the probe must reach on the job container's loopback, from the stack profile's
    `services` file: [] when it lists none, None when it's missing or a line is malformed (the probe parses it
    the same way)."""
    try:
        text = open(path).read()
    except OSError:
        return None
    services = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = SERVICE_LINE.fullmatch(line)
        if not m or int(m[2]) > 65535:
            return None
        services.append((m[1], int(m[2])))
    return services


def sockets(lines, services):
    """Each of the profile's test services answers; the Docker socket doesn't."""
    if services is None:
        return ["the stack profile's services file is missing or malformed"]
    failures = [f"test service unreachable: {label}" for label, _ in services
                if f"localsvc {label} connected" not in lines]
    if "unixsock docker connected" in lines:
        failures.append("the Docker socket accepts connections")
    return failures


def kernel_files(lines):
    failures = []
    if "kcore unreadable" not in lines:
        failures.append("/proc/kcore is readable")
    failures += [f"{l.split()[1]} is writable" for l in lines
                 if l.startswith("procwrite ") and l.endswith(" writable")]
    return failures


def judge_control(lines, services):
    failures = kernel_files(lines) + sockets(lines, services)
    # Each check the agent run must fail has to succeed here, or the agent's pass proves nothing.
    failures += [f"control could not list {l.split()[1]}" for l in lines
                 if l.startswith("path ") and l.endswith(" unreadable")]
    failures += [f"control could not write {l.split()[1]}" for l in lines
                 if l.startswith("write ") and not l.endswith(" allowed")]
    if "direct 1.1.1.1:443 open" not in lines:
        failures.append("control could not open a direct TCP connection")
    if not any(l.startswith("noproxy ") and 200 <= int(l.split()[2]) < 400 for l in lines):
        failures.append("control could not reach a host without a proxy")
    if "dns example.com resolved" not in lines:
        failures.append("control could not resolve DNS")
    env = {l.split()[2] for l in lines if l.startswith("secret env ")}
    proc = {l.split()[3] for l in lines if l.startswith("secret proc ")}
    files = {l.split()[2] for l in lines if l.startswith("secret file ")}
    for label in ("oauth", "github"):
        if label not in env:
            failures.append(f"control did not see the {label} token in its environment")
        if label not in proc:
            failures.append(f"control did not see the {label} token in /proc/*/environ")
    canary_files = {l.split()[3].rsplit("/", 1)[-1] for l in lines if l.startswith("secret file canary ")}
    for name in ("plain.txt", "extraheader.txt"):
        if name not in canary_files:
            failures.append(f"control did not find the planted canary in {name}")
    return failures


def judge_agent(lines, control, services):
    failures = kernel_files(lines) + sockets(lines, services)
    failures += [f"credential visible: {l}" for l in lines if l.startswith("secret ")]
    names = {l.split(" ", 1)[1] for l in lines if l.startswith("env-name ")}
    failures += [f"credential variable present: {n}" for n in sorted(names & CREDENTIAL_NAMES)]
    ns = next((l for l in lines if l.startswith("pidns ")), None)
    if ns is None or ns == "pidns unreadable" or ns in control:
        failures.append("not in its own PID namespace")
    failures += [f"runner mount listable: {l.split()[1]}" for l in lines
                 if l.startswith("path ") and l.endswith(" readable")]
    failures += [f"protected path writable: {l.split()[1]}" for l in lines
                 if l.startswith("write ") and l.endswith(" allowed")]
    for l in (l for l in lines if l.startswith("net ")):
        _, url, code = l.split()
        ok = 200 <= int(code) < 400
        if url in REACHABLE and not ok:
            failures.append(f"allowed registry unreachable: {url} ({code})")
        if url in BLOCKED and ok:
            failures.append(f"host outside the allowlist reachable: {url} ({code})")
    if any(l.startswith("noproxy ") and not l.endswith(" 000") for l in lines):
        failures.append("reached a host without the sandbox proxy")
    if "direct 1.1.1.1:443 closed" not in lines:
        failures.append("opened a direct TCP connection")
    if "dns example.com failed" not in lines:
        failures.append("resolved DNS from inside the sandbox")
    return failures


def main():
    mode, path = sys.argv[1], sys.argv[2]
    shown = open(path).read().splitlines()
    failures = []
    # Claude Code appends its own notes (such as <sandbox_violations>) after a command's output:
    # judge the probe's lines up to its end marker, show everything.
    if "end" in shown:
        lines = shown[:shown.index("end") + 1]
    else:
        lines = shown
        failures.append("probe output is incomplete (no end marker)")
    kinds = {l.split(" ", 1)[0] for l in lines}
    failures += [f"probe output has no '{k}' line" for k in REQUIRED_KINDS if k not in kinds]
    if mode == "control":
        failures += judge_control(lines, read_services(sys.argv[3]))
    else:
        failures += judge_agent(lines, open(sys.argv[3]).read().splitlines(), read_services(sys.argv[4]))

    # The output is agent-influenced: stop workflow-command parsing and fence it safely.
    token = secrets.token_hex(16)
    fence = "~" * max([3] + [len(l.lstrip(" ")) - len(l.lstrip(" ").lstrip("~")) + 1 for l in shown])
    body = [f"### Bash sandbox probe ({mode}): {'FAILED' if failures else 'passed'}", "",
            fence, *shown, fence, "", *[f"- {f}" for f in failures]]
    print(f"::stop-commands::{token}")
    print("\n".join(body))
    print(f"::{token}::")
    for f in failures:
        print(f"::error::{f}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as s:
            s.write("\n".join(body) + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
