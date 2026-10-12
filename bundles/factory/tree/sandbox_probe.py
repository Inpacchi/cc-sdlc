"""Credential and isolation probe for sandboxed agent Bash (factory-smoke, bash-sandbox job).

Usage: python3 -I sandbox_probe.py <secret-hash-file>

The hash file holds "<label> <hash>" lines: the first 12 hex digits of the SHA-256 of each
secret the job holds, plus a planted canary. The probe hashes every candidate value it can see
and reports matches by label: its environment, every process's environment, and token-like
strings in readable files (raw, and inside base64 such as a git extraheader). It prints names,
counts and labels only, never a value. It also reports its PID namespace, which runner mounts
it can list, which protected paths it can write, the kernel files `systempaths=unconfined`
unmasks, which Unix sockets it can connect to (the test services a stage starts before the agent,
listed in a `sockets` file beside the hash file, plus the Docker socket), and what it can reach
through the sandbox proxy and directly. sandbox_check.py judges the output.
"""

import base64
import binascii
import hashlib
import os
import re
import socket
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN = re.compile(rb"[A-Za-z0-9_-]{20,}")
BASE64 = re.compile(rb"[A-Za-z0-9+/]{24,}={0,2}")
RUNNER_MOUNTS = ["/__w/_temp", "/__w/_actions", "/__e", "/github"]
SCAN_ROOTS = ["/__w/_temp", "/github", os.path.expanduser("~"), os.getcwd(), "/tmp"]
MAX_FILE_BYTES = 5 * 1024 * 1024
PROXIED = [
    "https://pypi.org/simple/",
    "https://registry.npmjs.org/",
    "https://example.com/",
    "https://api.github.com/",
]
WRITE_TESTS = [".git/hooks/factory-probe", ".git/config", ".claude/settings.local.json"]
DOCKER_SOCKET = "/var/run/docker.sock"


def short_hash(value):
    return hashlib.sha256(value).hexdigest()[:12]


def candidates(data):
    """Token-like strings in data, raw and inside base64."""
    found = set(TOKEN.findall(data))
    for blob in BASE64.findall(data):
        try:
            decoded = base64.b64decode(blob + b"=" * (-len(blob) % 4))
        except (binascii.Error, ValueError):
            continue
        found.update(TOKEN.findall(decoded))
    return found


def labels(known, value):
    """Labels of the known secrets in value: the whole value, or embedded (a URL, JSON, base64)."""
    found = {known[h] for h in [short_hash(value)] if h in known}
    found.update(known[h] for h in map(short_hash, candidates(value)) if h in known)
    return sorted(found)


def main():
    known = {}
    with open(sys.argv[1]) as f:
        for line in f:
            if line.strip():
                label, digest = line.split()
                known[digest] = label
    out = []

    for name, value in sorted(os.environ.items()):
        if len(value) >= 20:
            out.append(f"env-name {name}")
        for label in labels(known, value.encode()):
            out.append(f"secret env {label} {name}")

    pids = [p for p in os.listdir("/proc") if p.isdigit()]
    out.append(f"processes {len(pids)}")
    try:
        with open("/proc/1/comm") as f:
            out.append(f"pid1 {f.read().strip()}")
    except OSError:
        out.append("pid1 unreadable")
    try:
        out.append(f"pidns {os.readlink('/proc/self/ns/pid')}")
    except OSError:
        out.append("pidns unreadable")
    for pid in pids:
        try:
            with open(f"/proc/{pid}/environ", "rb") as f:
                pairs = f.read().split(b"\0")
        except OSError:
            continue
        for pair in pairs:
            name, _, value = pair.partition(b"=")
            for label in labels(known, value):
                out.append(f"secret proc {pid} {label} {name.decode(errors='replace')}")

    # A denied directory may still list as empty (an empty mount over it), so only a
    # non-empty listing counts as readable.
    for mount in RUNNER_MOUNTS:
        try:
            readable = bool(os.listdir(mount))
        except OSError:
            readable = False
        out.append(f"path {mount} {'readable' if readable else 'unreadable'}")

    for path in WRITE_TESTS:
        existed = os.path.exists(path)
        try:
            # An existing file is opened for appending and closed unwritten; a new one is created
            # and removed.
            flags = os.O_WRONLY | os.O_APPEND if existed else os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = os.open(path, flags, 0o600)
        except OSError:
            out.append(f"write {path} denied")
            continue
        os.close(fd)
        if not existed:
            os.unlink(path)
        out.append(f"write {path} allowed")

    # Docker masks it with /dev/null (reads return nothing); only real bytes count.
    try:
        with open("/proc/kcore", "rb") as f:
            got = f.read(1)
        out.append(f"kcore {'readable' if got else 'unreadable'}")
    except OSError:
        out.append("kcore unreadable")
    for path in ("/proc/sysrq-trigger", "/proc/sys/kernel/hostname"):
        try:
            os.close(os.open(path, os.O_WRONLY))  # opened, never written
            out.append(f"procwrite {path} writable")
        except OSError:
            out.append(f"procwrite {path} unwritable")

    # The stage's test services on the job container's loopback must answer (through the sandbox
    # proxy, which allows `localhost`); the Docker socket must not.
    for label, port in (("db", 5432), ("redis", 6379)):
        out.append(f"localsvc {label} {connect_local(port)}")
    out.append(f"unixsock docker {connect_unix(DOCKER_SOCKET)}")
    # Every Unix socket it can find (report only).
    for root in ("/tmp", "/run", "/var/run", os.getcwd(), "/opt"):
        for dirpath, _, names in os.walk(root, onerror=lambda e: None):
            for name in names:
                path = os.path.join(dirpath, name)
                try:
                    is_socket = stat.S_ISSOCK(os.lstat(path).st_mode)
                except OSError:
                    continue
                if is_socket and path != DOCKER_SOCKET:
                    out.append(f"unixsock-found {path} {connect_unix(path)}")

    files = 0
    seen = set()
    for root in SCAN_ROOTS:
        for dirpath, _, names in os.walk(root, onerror=lambda e: None):
            for name in names:
                path = os.path.join(dirpath, name)
                if path in seen or os.path.islink(path) or not os.path.isfile(path):
                    continue
                seen.add(path)
                try:
                    if os.path.getsize(path) > MAX_FILE_BYTES:
                        continue
                    with open(path, "rb") as f:
                        data = f.read()
                except OSError:
                    continue
                if b"\0" in data[:8192]:
                    continue
                files += 1
                for token in candidates(data):
                    label = known.get(short_hash(token))
                    if label:
                        out.append(f"secret file {label} {path}")
    out.append(f"files-scanned {files}")

    for url in PROXIED:
        out.append(f"net {url} {fetch(urllib.request.build_opener(), url):03d}")
    # Bypass the sandbox proxy: inside the sandbox's network namespace these must all fail.
    out.append(f"noproxy https://example.com/ {fetch(urllib.request.build_opener(urllib.request.ProxyHandler({}))):03d}")
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=5).close()
        out.append("direct 1.1.1.1:443 open")
    except OSError:
        out.append("direct 1.1.1.1:443 closed")
    try:
        socket.getaddrinfo("example.com", 443)
        out.append("dns example.com resolved")
    except OSError:
        out.append("dns example.com failed")

    out.append("end")
    print("\n".join(out))


def connect_local(port):
    """connected or refused: localhost:<port> through the sandbox's HTTP proxy, or directly."""
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    try:
        if proxy:
            # http://[user:token@]host:port — the sandbox's proxy takes a per-session credential.
            url = urllib.parse.urlsplit(proxy)
            auth = ""
            if url.username:
                pair = f"{urllib.parse.unquote(url.username)}:{urllib.parse.unquote(url.password or '')}"
                auth = f"Proxy-Authorization: Basic {base64.b64encode(pair.encode()).decode()}\r\n"
            with socket.create_connection((url.hostname, url.port), timeout=5) as s:
                s.sendall(f"CONNECT localhost:{port} HTTP/1.1\r\nHost: localhost:{port}\r\n{auth}\r\n".encode())
                status = s.recv(200).split(b"\r\n", 1)[0]
                return "connected" if b" 200" in status else "refused"
        with socket.create_connection(("127.0.0.1", port), timeout=5):
            return "connected"
    except OSError:
        return "refused"


def connect_unix(path):
    """connected, absent (no socket there) or refused (any other failure)."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    except OSError:
        return "blocked"  # the sandbox's seccomp filter refuses to create Unix sockets at all
    s.settimeout(5)
    try:
        s.connect(path)
        return "connected"
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "refused"
    finally:
        s.close()


def fetch(opener, url="https://example.com/"):
    """HTTP status, or 0 when the connection itself fails."""
    try:
        with opener.open(url, timeout=8) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


if __name__ == "__main__":
    main()
