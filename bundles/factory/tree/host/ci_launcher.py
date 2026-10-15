"""The CI tier's launcher: one disposable runner per job (z-sdlc process/factory.md, Enablement step 10, The CI tier).

Usage: python3 -I ci_launcher.py run <launcher.json> <slot>     one cycle; the slot's systemd unit starts the next
       python3 -I ci_launcher.py stop <launcher.json> <slot>    after a slot stops: its container and registration
       python3 -I ci_launcher.py resolve <launcher.json>        the App's installation and the runner group's IDs
       python3 -I ci_launcher.py check <launcher.json>          the tier's isolation check; on failure, its kill switch
       python3 -I ci_launcher.py fwcheck <launcher.json>        the firewall table alone (every minute)
       python3 -I ci_launcher.py trip <launcher.json>           the kill switch, for a check that failed or hung

A cycle mints a just-in-time (JIT) runner config with the runner-registration App. The App's one permission, the
organization's self-hosted runners, reaches every runner group in the organization, so its key (root-only, read by
openssl alone) is the most sensitive thing on the host. The cycle starts a fresh container from the tier's image
as the runner user and watches it until its one job ends. GitHub, never the daemon, says whether the runner is
online and busy, and the container is killed when:
- its job has run CI_JOB_HOURS (the job's own timeout-minutes is the first limit; this is the backstop);
- its runner has idled CI_IDLE_HOURS (recycled);
- GitHub has removed its runner (the job is over), its runner went offline after being online, or its runner
  never came online;
- it is older than CI_IDLE_HOURS + CI_JOB_HOURS, whatever GitHub says;
- the runner home's free space falls below CI_MIN_FREE_GB (and no cycle starts below it).
Then it removes the container and the runner's registration. The job runs inside the container, runner and all:
whatever a pull request's code does there, to the runner's own processes included, ends with the container.

Root-side rules (the job owns its container, so root trusts nothing that comes out of it):
- root reads one thing from the daemon, `docker wait`'s exit status, and only as an integer; containers are
  addressed by the names this script gives them, never by an ID the daemon returns. The check's probes answer
  with their exit status; their output is only logged, as printable ASCII;
- the installation token lives only in this process. The JIT config reaches the container through a 0600 file the
  runner user owns, created in a directory only root can write and deleted once `docker run` returns. Inside the
  container it stays readable to the job (run.sh's environment, the container's config) until the container is
  removed: it is single-use, and registers only the runner the job is already running on;
- every docker call runs as the runner user with a fixed environment and a timeout, never as root. setpriv execs
  docker (runuser would fork a parent that a timeout kills, orphaning docker).
A container escape is a compromise of the runner user, held by the outer boundary: its own user, the firewall,
the caps. Tested by tests/test_ci_launcher.py.
"""

import base64
import contextlib
import datetime
import fcntl
import http.client
import ipaddress
import json
import os
import pathlib
import secrets
import signal
import socket
import stat
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request

ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"
DROPPED_CAPS = ("NET_RAW", "MKNOD")
LOG_MAX = "20m"
# The check's inter-slot test: a listener at a fixed address on a network of its own (outside Docker's default
# address pools, so no slot network has it), which a container on another network must not reach.
CHECK_SUBNET, LISTENER_IP, LISTENER_PORT = "10.254.254.0/24", "10.254.254.10", 8080
REASONS = {
    "job-hours": "the job outran CI_JOB_HOURS",
    "idle": "the runner idled CI_IDLE_HOURS (recycled)",
    "lifetime": "the container outlived CI_IDLE_HOURS + CI_JOB_HOURS",
    "gone": "GitHub removed the runner (its job is over) but its container still runs",
    "offline": "the runner went offline after being online, but its container still runs",
    "never-online": "the runner never came online",
    "disk": "free space under the runner home fell below CI_MIN_FREE_GB",
}
NEUTRAL = ("idle", "lifetime")  # a recycle, not a failure: the backoff counter stays as it is

# The isolation probe: every target closed; with expected caps (in a job's container), cpu.max, memory.max and
# pids.max set to them. Exit 1 on any of those, else exit 2 if the internet is out of reach (liveness, not
# isolation), else 0.
PROBE = r"""
import socket, sys
bad = 0
for h in sys.argv[1].split():
    for p in [int(x) for x in sys.argv[2].split()]:
        try:
            socket.create_connection((h, p), timeout=3).close()
            print(f"REACHABLE {h}:{p}"); bad += 1
        except OSError:
            pass
if sys.argv[3]:
    cpus, memory, pids = sys.argv[3].split()
    def read(name):
        try:
            return open("/sys/fs/cgroup/" + name).read().split()
        except OSError:
            return ["max"]
    quota = read("cpu.max")
    try:
        capped = quota[0] != "max" and abs(int(quota[0]) / int(quota[1]) - float(cpus)) < 0.01
    except (IndexError, ValueError):
        capped = False
    if not capped:
        print(f"cpu.max is {' '.join(quota)}, not {cpus} CPUs"); bad += 1
    for name, want in (("memory.max", memory), ("pids.max", pids)):
        if read(name)[0] != want:
            print(f"{name} is {read(name)[0]}, not {want}"); bad += 1
if bad:
    sys.exit(1)
try:
    socket.create_connection(("api.github.com", 443), timeout=10).close()
except OSError as e:
    print(f"no internet: {e}"); sys.exit(2)
"""
LISTEN = r"""
import socket, sys
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", int(sys.argv[1])))
s.listen(8)
while True:
    s.accept()[0].close()
"""
REACH = r"""
import socket, sys, time
for _ in range(15):
    try:
        socket.create_connection((sys.argv[1], int(sys.argv[2])), timeout=3).close()
        sys.exit(0)
    except OSError:
        time.sleep(1)
sys.exit(1)
"""


class Failed(Exception):
    pass


class Stopped(BaseException):
    """SIGTERM, the slot's unit stopping: unwinds through every finally, so the cycle cleans up after itself."""


def on_sigterm(signum, frame):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)  # one unwind; the cleanup isn't interrupted again
    raise Stopped()


def load(path):
    with open(path) as f:
        return json.load(f)


def printable(text, limit=300):
    """Output from a container or GitHub, as it may appear in a log or the tripped marker."""
    return " ".join("".join(c if 32 <= ord(c) < 127 else " " for c in str(text)).split())[:limit]


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def app_jwt(conf, now=None):
    """The App's JWT (RS256), signed by openssl with the root-only key."""
    now = int(now if now is not None else time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": conf["client_id"]}).encode())
    signing_input = f"{header}.{claims}".encode()
    r = subprocess.run([conf["openssl"], "dgst", "-sha256", "-sign", conf["key"]], input=signing_input,
                       capture_output=True, timeout=30)
    if r.returncode or not r.stdout:
        raise Failed(f"openssl couldn't sign with {conf['key']}: {r.stderr.decode(errors='replace').strip()}")
    return f"{header}.{claims}.{b64url(r.stdout)}"


def api(conf, method, path, bearer, body=None):
    """GitHub's answer, as (HTTP status, JSON or None). Anything short of an answer is Failed."""
    request = urllib.request.Request(conf["api"] + path, method=method,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={"Accept": ACCEPT, "X-GitHub-Api-Version": API_VERSION,
                                              "Authorization": f"Bearer {bearer}", "User-Agent": "z-sdlc-factory-ci"})
    try:
        with urllib.request.urlopen(request, timeout=30) as r:
            text = r.read().decode()
            return r.status, (json.loads(text) if text else None)
    except urllib.error.HTTPError as e:
        try:
            text = e.read().decode(errors="replace")
        except (OSError, http.client.HTTPException):
            text = ""
        try:
            return e.code, json.loads(text) if text else None
        except ValueError:
            return e.code, {"message": printable(text, 200)}
    except (OSError, ValueError, http.client.HTTPException) as e:
        raise Failed(f"{method} {path}: {type(e).__name__}: {printable(e, 200)}") from None


def installation_token(conf):
    """An installation token narrowed to the one permission, and when it expires."""
    status, data = api(conf, "POST", f"/app/installations/{conf['installation_id']}/access_tokens", app_jwt(conf),
                       {"permissions": {"organization_self_hosted_runners": "write"}})
    if status != 201 or not isinstance(data, dict) or not data.get("token"):
        raise Failed(f"installation token: HTTP {status} {printable((data or {}).get('message', ''))}")
    try:
        expires = datetime.datetime.fromisoformat(str(data["expires_at"]).replace("Z", "+00:00")).timestamp()
    except (KeyError, ValueError):
        expires = time.time() + 3600
    return data["token"], expires


class Tokens:
    """A cycle's installation token, in memory only, minted again five minutes before it expires."""

    def __init__(self, conf):
        self.conf, self.token, self.until = conf, None, 0.0

    def get(self):
        if self.token is None or time.time() > self.until:
            self.token, expires = installation_token(self.conf)
            self.until = expires - 300
        return self.token


def jitconfig(conf, token, name):
    status, data = api(conf, "POST", f"/orgs/{conf['org']}/actions/runners/generate-jitconfig", token,
                       {"name": name, "runner_group_id": conf["group_id"], "labels": conf["labels"],
                        "work_folder": "_work"})
    if status != 201 or not isinstance(data, dict) or not data.get("encoded_jit_config"):
        raise Failed(f"JIT config: HTTP {status} {printable((data or {}).get('message', ''))}")
    return int(data["runner"]["id"]), data["encoded_jit_config"]


def runner_state(conf, runner_id, tokens):
    """GitHub's view of the runner, {"online", "busy"}; None once GitHub has removed it."""
    status, data = api(conf, "GET", f"/orgs/{conf['org']}/actions/runners/{runner_id}", tokens.get())
    if status == 404:
        return None
    if status != 200 or not isinstance(data, dict):
        raise Failed(f"runner {runner_id}: HTTP {status}")
    return {"online": data.get("status") == "online", "busy": data.get("busy") is True}


def ran_its_job(conf, runner_id, tokens):
    """After the container ends: GitHub removes a JIT runner once it has run its job, so one still registered
    never ran one (a bad config, a crash), and the next cycle backs off."""
    for attempt in range(int(conf.get("gone_checks", 4))):
        if attempt:
            time.sleep(float(conf.get("gone_delay", 5)))
        try:
            if runner_state(conf, runner_id, tokens) is None:
                return True
        except Failed as e:
            print(f"runner {runner_id}: {e}", file=sys.stderr)
    return False


def deregister(conf, runner_id, tokens):
    """Remove the runner's registration. 404: already gone. GitHub refuses a busy runner."""
    status, data = api(conf, "DELETE", f"/orgs/{conf['org']}/actions/runners/{runner_id}", tokens.get())
    if status not in (204, 404):
        raise Failed(f"deregister runner {runner_id}: HTTP {status} {printable((data or {}).get('message', ''))}")


def runner_argv(conf, *command):
    """A command as the runner user, with a fixed environment. setpriv execs it: no parent left to orphan it."""
    uid = conf["uid"]
    return [conf["setpriv"], f"--reuid={uid}", f"--regid={conf['gid']}", "--clear-groups", "--inh-caps=-all", "--",
            conf["env"], "-i", "PATH=/usr/bin:/bin", f"HOME={conf['home']}", f"XDG_RUNTIME_DIR=/run/user/{uid}",
            f"DOCKER_HOST=unix:///run/user/{uid}/docker.sock", *command]


def docker(conf, *args, timeout=120):
    return subprocess.run(runner_argv(conf, conf["docker"], *args), capture_output=True, text=True, timeout=timeout)


def names(conf, slot):
    """The slot's container and its own network (concurrent jobs can't reach each other)."""
    name = f"{conf['container']}-{slot}"
    return name, name


def memory_bytes(text):
    return int(text[:-1]) * 1024 ** "kmg".index(text[-1].lower()) * 1024


def job_flags(conf):
    """Every job container's caps and hardening. The check's probe runs with the same flags, so it proves them."""
    job = conf["job"]
    flags = ["--cpus", str(job["cpus"]), "--memory", job["memory"], "--memory-swap", job["memory"],
             "--pids-limit", str(job["pids"]), "--shm-size", job["shm"], "--security-opt", "no-new-privileges",
             "--log-driver", "local", "--log-opt", f"max-size={LOG_MAX}", "--log-opt", "max-file=1"]
    for cap in DROPPED_CAPS:
        flags += ["--cap-drop", cap]
    return flags


def state_dir(conf):
    """The launcher's directory, which the JIT config and the runner IDs pass through: only root may write it."""
    path = pathlib.Path(conf["state_dir"])
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != conf.get("state_owner", 0) or st.st_mode & 0o022:
        raise Failed(f"{path} must be a directory only root can write")
    return path


def low_disk(conf):
    st = os.statvfs(conf["home"])
    return st.f_bavail * st.f_frsize < float(conf.get("min_free_gb", 20)) * 2 ** 30


def write_env_file(conf, path, jit):
    """The JIT config for `docker run --env-file`: created fresh (no link followed), 0600, owned by the runner user."""
    with contextlib.suppress(FileNotFoundError):
        os.unlink(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        os.fchown(fd, conf["uid"], conf["gid"])
        os.write(fd, f"ACTIONS_RUNNER_INPUT_JITCONFIG={jit}\nRUNNER_ALLOW_RUNASROOT=1\n".encode())
    finally:
        os.close(fd)


def record_runner(path, runner_id):
    """The cycle's runner ID, kept before its container starts, so a killed cycle's registration is removed later."""
    new = path.with_name(path.name + ".new")
    new.write_text(str(runner_id))
    os.replace(new, path)


def deregister_leftover(conf, path, tokens):
    """A registration a stopped or killed cycle left behind."""
    try:
        runner_id = int(path.read_text())
    except FileNotFoundError:
        return
    except ValueError:
        path.unlink()
        return
    deregister(conf, runner_id, tokens)
    path.unlink(missing_ok=True)


def run(conf, slot):
    """One job's cycle. Returns 0 when the runner ran its job or was recycled, 1 otherwise (the next cycle backs
    off)."""
    state = state_dir(conf)
    fails_file = state / f"slot-{slot}.fails"
    runner_file = state / f"slot-{slot}.runner"
    try:
        fails = int(fails_file.read_text())
    except (OSError, ValueError):
        fails = 0
    if fails:
        # A failing cycle (the API, the image, the group) must not hammer generate-jitconfig: GitHub answers 422.
        time.sleep(min(600, 10 * 2 ** min(fails, 6)))
    tokens = Tokens(conf)
    name, network = names(conf, slot)
    outcome, runner_id = "failed", None
    try:
        deregister_leftover(conf, runner_file, tokens)
        docker(conf, "rm", "-f", "-v", name)  # a container a crash left behind
        if docker(conf, "network", "inspect", network).returncode:
            docker(conf, "network", "create", "--label", "factory-ci", network)
        if low_disk(conf):
            raise Failed(f"less than CI_MIN_FREE_GB free under {conf['home']}: no job starts")
        runner_id, jit = jitconfig(conf, tokens.get(), f"{conf['name_prefix']}-{slot}-{secrets.token_hex(3)}")
        record_runner(runner_file, runner_id)
        env_file = state / f"slot-{slot}.env"
        write_env_file(conf, env_file, jit)
        try:
            started = docker(conf, "run", "-d", "--name", name, "--network", network, "--label", "factory-ci",
                             *job_flags(conf), "--env-file", str(env_file), conf["image"])
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(env_file)
        if started.returncode:
            raise Failed(f"docker run: {printable(started.stderr)}")
        reason, status = watch(conf, slot, name, runner_id, tokens)
        print(f"slot {slot}: " + (f"the runner exited with {status}" if reason is None else REASONS[reason]))
        if ran_its_job(conf, runner_id, tokens):
            outcome = "ran"
        elif reason in NEUTRAL:
            outcome = "recycled"
    except Stopped:
        outcome = "stopped"
        raise
    except (Failed, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as e:
        print(f"slot {slot}: {printable(e)}", file=sys.stderr)
    finally:
        cleanup(conf, slot, name, runner_file, runner_id, tokens, removed=outcome == "ran")
        with contextlib.suppress(OSError):
            fails_file.write_text(str(0 if outcome == "ran" else fails if outcome in ("recycled", "stopped")
                                      else fails + 1))
    return 1 if outcome == "failed" else 0


def watch(conf, slot, name, runner_id, tokens):
    """Wait for the container's one job, killing it on any limit in this file's docstring. Returns (the limit, None)
    for a killed container, or (None, its exit status)."""
    tick = float(conf.get("tick_seconds", 30))
    poll = float(conf.get("poll_seconds", 120))
    job_limit = float(conf["job"]["hours"]) * 3600
    idle_limit = float(conf.get("idle_hours", 24)) * 3600
    grace = float(conf.get("start_grace_seconds", 600))
    started = last_poll = time.monotonic()
    seen_online, busy_since, offline_polls, reason = False, None, 0, None
    # One `docker wait` for the cycle, never killed by a timeout: it returns when the container ends, killed or not.
    waiter = subprocess.Popen(runner_argv(conf, conf["docker"], "wait", name), stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True)
    try:
        while reason is None:
            try:
                out, _ = waiter.communicate(timeout=tick)
                return None, int(out.strip())  # the only thing root reads from the daemon
            except subprocess.TimeoutExpired:
                pass
            now = time.monotonic()
            if low_disk(conf):
                reason = "disk"
            elif now - started > idle_limit + job_limit:
                reason = "lifetime"
            elif busy_since is not None and now - busy_since > job_limit:
                reason = "job-hours"
            elif now - last_poll >= poll:
                last_poll = now
                try:
                    runner = runner_state(conf, runner_id, tokens)
                except Failed as e:
                    print(f"slot {slot}: {e}", file=sys.stderr)  # unknown: the lifetime cap still holds
                    continue
                if runner is None:
                    reason = "gone"
                    continue
                if runner["online"] or runner["busy"]:
                    seen_online, offline_polls = True, 0
                elif seen_online:
                    offline_polls += 1  # one offline poll can be the runner updating itself
                if runner["busy"] and busy_since is None:
                    busy_since = now
                if offline_polls >= 2:
                    reason = "offline"
                elif not seen_online and now - started > grace:
                    reason = "never-online"
                elif busy_since is None and now - started > idle_limit:
                    try:
                        deregister(conf, runner_id, tokens)  # first, so GitHub assigns it nothing meanwhile
                        reason = "idle"
                    except Failed:
                        busy_since = now  # it took a job after all
        print(f"slot {slot}: {REASONS[reason]}; killing its container", file=sys.stderr)
        docker(conf, "kill", name)
        with contextlib.suppress(subprocess.TimeoutExpired):
            waiter.communicate(timeout=60)
        return reason, None
    finally:
        if waiter.poll() is None:
            waiter.kill()
            waiter.wait()


def cleanup(conf, slot, name, runner_file, runner_id, tokens, removed):
    """The container, then the registration (unless GitHub has removed it): each on its own, so one failing doesn't
    skip the other. A registration left over stays in slot-N.runner for the next cycle or the slot's stop."""
    try:
        docker(conf, "rm", "-f", "-v", name)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"slot {slot}: docker rm: {e}", file=sys.stderr)
    if runner_id is None:
        return
    try:
        if not removed:
            deregister(conf, runner_id, tokens)
        runner_file.unlink(missing_ok=True)
    except (Failed, OSError) as e:
        print(f"slot {slot}: {e}", file=sys.stderr)


def stop(conf, slot):
    """After a slot stops (its unit's ExecStopPost): its container and any registration its cycle left."""
    state = state_dir(conf)
    docker(conf, "rm", "-f", "-v", names(conf, slot)[0])
    deregister_leftover(conf, state / f"slot-{slot}.runner", Tokens(conf))
    return 0


def find_group(conf, token):
    page = 1
    while True:
        status, groups = api(conf, "GET", f"/orgs/{conf['org']}/actions/runner-groups?per_page=100&page={page}", token)
        if status != 200 or not isinstance(groups, dict):
            raise Failed(f"runner groups: HTTP {status}")
        found = [g for g in groups.get("runner_groups", []) if g.get("name") == conf["group"]]
        if found:
            return found[0]
        if len(groups.get("runner_groups", [])) < 100:
            raise Failed(f"no runner group {conf['group']}: bootstrap.py --apply creates it once a workflow uses the "
                         "label")
        page += 1


def group_problem(group, name):
    if group.get("visibility") != "selected" or group.get("allows_public_repositories"):
        return f"runner group {name} is open beyond its selected private repositories"
    return None


def resolve(conf):
    """The App's installation on the organization and the runner group's ID (setup writes them into the conf)."""
    status, data = api(conf, "GET", f"/orgs/{conf['org']}/installation", app_jwt(conf))
    if status != 200 or not isinstance(data, dict) or "id" not in data:
        raise Failed(f"the runner-registration App isn't installed on {conf['org']}: HTTP {status}")
    if (data.get("permissions") or {}).get("organization_self_hosted_runners") != "write":
        raise Failed("the runner-registration App's installation lacks organization_self_hosted_runners: write")
    conf = {**conf, "installation_id": int(data["id"])}
    group = find_group(conf, installation_token(conf)[0])
    problem = group_problem(group, conf["group"])
    if problem:
        raise Failed(problem)
    return {"installation_id": conf["installation_id"], "group_id": int(group["id"])}


def firewall_loaded(conf):
    return subprocess.run([conf["nft"], "list", "table", "inet", conf["firewall_table"]], capture_output=True,
                          timeout=30).returncode == 0


def gateway(conf):
    """The default IPv4 gateway, if it's a private address: a LAN target that isn't this host's (whose addresses
    all meet the firewall's loopback rule), so the blocked set itself is tested."""
    try:
        for line in pathlib.Path(conf.get("route_file", "/proc/net/route")).read_text().splitlines()[1:]:
            fields = line.split()
            if len(fields) > 2 and fields[1] == "00000000":
                ip = socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
                return ip if ipaddress.ip_address(ip).is_private else None
    except (OSError, ValueError):
        pass
    return None


def check(conf):
    """The outer boundary, every few hours and before any slot starts. Anything that stops the check finishing
    counts as a failure. On failure: a tripped marker the slot units won't start past (a reboot included), the
    slots and timers stopped, and the runner user's whole session stopped (its daemon and every container)."""
    problems, notes = [], []
    try:
        with open(state_dir(conf) / "check.lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            inspect(conf, problems, notes)
    except Exception as e:  # noqa: BLE001 - a check that can't finish has failed
        problems.append(f"the check couldn't finish: {type(e).__name__}: {printable(e)}")
    for note in notes:
        print(f"CI tier check: {note}", file=sys.stderr)
    if problems:
        trip(conf, problems)
        return 1
    print("CI tier check: ok")
    return 0


def inspect(conf, problems, notes):
    if not firewall_loaded(conf):
        problems.append(f"firewall table {conf['firewall_table']} isn't loaded")
    cgroup = pathlib.Path(conf["cgroup"])
    for name in ("memory.max", "cpu.max"):
        if (cgroup / name).read_text().split()[0] == "max":
            problems.append(f"no {name} on {cgroup}")
    controllers = (cgroup / f"user@{conf['uid']}.service" / "cgroup.controllers").read_text().split()
    for c in ("cpu", "memory", "pids"):
        if c not in controllers:
            problems.append(f"the {c} controller isn't delegated to the runner user")
    if low_disk(conf):
        problems.append(f"less than CI_MIN_FREE_GB free under {conf['home']}")
    # The group as setup found it. GitHub out of reach is liveness, not isolation: noted, not tripped.
    try:
        status, group = api(conf, "GET", f"/orgs/{conf['org']}/actions/runner-groups/{conf['group_id']}",
                            Tokens(conf).get())
        if status == 200 and isinstance(group, dict):
            problem = group_problem(group, conf["group"])
            problems += [problem] if problem else []
        elif status == 404:
            problems.append(f"runner group {conf['group']} is gone")
        else:
            notes.append(f"runner group {conf['group']}: HTTP {status}")
    except Failed as e:
        notes.append(f"couldn't read runner group {conf['group']}: {e}")

    def judge(what, result):
        if result.returncode == 2:
            notes.append(f"{what}: {printable(result.stdout)}")
        elif result.returncode:
            problems.append(f"{what}: {printable(result.stdout) or f'exit {result.returncode}'}")

    targets = conf["probe"]["targets"].split()
    gw = gateway(conf)
    targets += [gw] if gw and gw not in targets else []
    ports = conf["probe"]["ports"].split()
    ports += [] if str(LISTENER_PORT) in ports else [str(LISTENER_PORT)]
    # On the host, as the runner user, with no Docker in the way: the firewall itself, IPv6 included.
    host_probe = runner_argv(conf, conf["python"], "-I", "-c", PROBE, " ".join(targets), " ".join(ports), "")
    judge("the host-side probe", subprocess.run(host_probe, capture_output=True, text=True, timeout=300))
    # At boot the gate can run before the runner user's daemon is up.
    deadline = time.monotonic() + float(conf.get("docker_wait_seconds", 90))
    while docker(conf, "info", timeout=15).returncode:
        if time.monotonic() > deadline:
            problems.append("the runner user's Docker daemon doesn't answer")
            return
        time.sleep(2)
    own, other = f"{conf['container']}-check-a", f"{conf['container']}-check"
    listener = f"{conf['container']}-check-listen"
    docker(conf, "rm", "-f", "-v", listener)
    docker(conf, "network", "rm", own)
    if docker(conf, "network", "create", "--label", "factory-ci", "--subnet", CHECK_SUBNET, own).returncode:
        problems.append(f"couldn't create the check's network {own} ({CHECK_SUBNET})")
        return
    if docker(conf, "network", "inspect", other).returncode:
        docker(conf, "network", "create", "--label", "factory-ci", other)
    job = conf["job"]
    caps = f"{job['cpus']} {memory_bytes(job['memory'])} {job['pids']}"
    v4 = [t for t in targets if ipaddress.ip_address(t).version == 4]
    try:
        if docker(conf, "run", "-d", "--name", listener, "--network", own, "--ip", LISTENER_IP, *job_flags(conf),
                  "--entrypoint", "python3", conf["image"], "-c", LISTEN, str(LISTENER_PORT)).returncode:
            problems.append("the check's listener container didn't start")
            return
        if docker(conf, "run", "--rm", "--network", own, *job_flags(conf), "--entrypoint", "python3", conf["image"],
                  "-c", REACH, LISTENER_IP, str(LISTENER_PORT), timeout=120).returncode:
            problems.append("the check's listener can't be reached on its own network, so the slots' isolation "
                            "from each other is untested")
            return
        # A job's container: the job's flags, a network like a slot's, and another network's listener closed to it.
        judge("the probe container", docker(conf, "run", "--rm", "--network", other, *job_flags(conf),
                                            "--entrypoint", "python3", conf["image"], "-c", PROBE,
                                            " ".join(v4 + [LISTENER_IP]), " ".join(ports), caps, timeout=300))
    finally:
        docker(conf, "rm", "-f", "-v", listener)


def fwcheck(conf):
    """Every minute: the firewall table, which anything that flushes the ruleset would drop."""
    try:
        if firewall_loaded(conf):
            return 0
        problem = f"firewall table {conf['firewall_table']} isn't loaded"
    except Exception as e:  # noqa: BLE001 - a check that can't finish has failed
        problem = f"the firewall check couldn't finish: {type(e).__name__}: {printable(e)}"
    trip(conf, [problem])
    return 1


def trip(conf, problems, keep=False):
    """keep: a marker a check already wrote says more than this caller can (the trip unit, after a failure)."""
    tripped = pathlib.Path(conf["tripped"])
    try:
        if not (keep and tripped.exists()):
            tripped.write_text("".join(f"{printable(p, 1000)}\n" for p in problems))
    except OSError as e:
        print(f"couldn't write {tripped}: {e}", file=sys.stderr)
    print("CI tier check FAILED:\n  " + "\n  ".join(printable(p, 1000) for p in problems), file=sys.stderr)
    unit = conf["unit"]
    # The slots first (their stop removes their containers and registrations), then the timers, so nothing starts
    # the runner user's manager again, then that manager: its daemon and every container in it, a job included.
    for args in (["stop", f"{unit}-slot@*.service"], ["stop", f"{unit}-check.timer", f"{unit}-fw.timer"],
                 ["stop", f"user@{conf['uid']}.service"]):
        with contextlib.suppress(OSError, subprocess.TimeoutExpired):
            subprocess.run([conf["systemctl"], *args], capture_output=True, timeout=300)
    print(f"{unit}: stopped, and held by {tripped} until someone fixes the cause and runs setup", file=sys.stderr)


def main(argv):
    commands = ("run", "stop", "resolve", "check", "fwcheck", "trip")
    if len(argv) < 3 or argv[1] not in commands or (argv[1] in ("run", "stop") and len(argv) < 4):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    if argv[1] == "run":
        signal.signal(signal.SIGTERM, on_sigterm)
    try:
        conf = load(argv[2])
        if argv[1] == "run":
            return run(conf, int(argv[3]))
        if argv[1] == "stop":
            return stop(conf, int(argv[3]))
        if argv[1] == "resolve":
            print(json.dumps(resolve(conf)))
            return 0
        if argv[1] == "trip":
            unit = conf["unit"]
            trip(conf, [f"an isolation check failed or didn't finish: journalctl -u {unit}-gate -u {unit}-check "
                        f"-u {unit}-fw"], keep=True)
            return 0
        return check(conf) if argv[1] == "check" else fwcheck(conf)
    except Stopped:
        return 0
    except (Failed, OSError, ValueError, KeyError, IndexError, subprocess.TimeoutExpired) as e:
        print(f"ci_launcher {argv[1]}: {printable(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
