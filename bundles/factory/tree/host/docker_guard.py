"""The CI tier's docker guard (z-sdlc process/factory.md, Enablement step 10, The CI tier).

Usage: python3 -I docker_guard.py <instance.json> [docker arguments...]

A pull request's run executes the pull request's own workflow, and the CI tier's runner group is open to
the repositories that use it, not to workflows (a pull request's merge ref never matches a pinned one). So
on the CI tier a job definition can be hostile: workflow_policy.py is a merge gate, not an execution gate.
The runner turns a job definition into docker commands (the container's options and volumes, its ports,
services, docker:// steps), so the CI tier's runners reach docker only through this guard: first on their
PATH, root-owned, with each instance's directories in a root-owned file (setup.sh writes both). It lets
through the commands the runner itself makes (actions/runner v2.338.0, Runner.Worker/Container/
DockerCommandManager.cs and Handlers/StepHost.cs) and refuses by default:
- any option it doesn't know: `--env-file <runner dir>/.credentials` would read the runner's credentials
  into the container, and `--cidfile <runner dir>/.env` would write the runner's settings;
- a value option in any form but the runner's own separate token (`-v X`; never `-vX`, `-v=X`, `--volume=X`);
- a mount other than the runner's own directories, by their exact paths with no symlink below the work or
  runner directory, or an anonymous volume: never a named volume, --mount or --volumes-from;
- privilege and namespace options (--privileged, --cap-add, --pid, --ipc, --userns, --network other than
  the runner's job network, -p), and security options other than the factory seccomp profile,
  systempaths=unconfined and no-new-privileges (workflow_policy.py's ALLOWED_OPTIONS: keep the two a pair);
- docker run and docker build: the runner makes them mid-job (docker:// steps, container actions), after
  the job's own code could have replaced a directory it mounts with a symlink. The CI tier runs neither.
docker create stops reading options at the image (docker/cli sets SetInterspersed(false) for create and
run), and so does this. Every container gets --security-opt no-new-privileges. docker always runs against
this instance's daemon (--host), with no DOCKER_* variable. A step's environment reaches docker exec by
design (`-e KEY` hands KEY's value to the step); every other command runs with PATH, HOME, LANG and
XDG_RUNTIME_DIR only, so a container's `-e KEY` can't read the runner's environment.
Tested by tests/test_docker_guard.py.
"""

import json
import os
import re
import sys

NETWORK = re.compile(r"^github_network_[0-9a-f]{32}$")
SECURITY_OPTS = {"seccomp=/etc/factory-runner/seccomp-bwrap.json", "systempaths=unconfined",
                 "no-new-privileges", "no-new-privileges:true", "no-new-privileges=true"}
DOCKER_SOCKET = "/var/run/docker.sock"
# Commands that make no container and mount nothing; the runner passes them its own container IDs.
PLAIN = {"version", "info", "ps", "inspect", "port", "logs", "start", "rm"}
MINIMAL_ENV = ("PATH", "HOME", "LANG", "XDG_RUNTIME_DIR")


class Refused(Exception):
    pass


def load(path):
    with open(path) as f:
        conf = json.load(f)
    for key in ("docker", "host", "work", "externals"):
        if not isinstance(conf.get(key), str) or not conf[key].startswith(("/", "unix:///")):
            raise Refused(f"{path} has no {key}")
    return conf


def below(path, base):
    """The path, resolved, is the base resolved plus the same relative part: no symlink below the base."""
    rel = os.path.relpath(path, base)
    expected = os.path.realpath(base) if rel == "." else os.path.join(os.path.realpath(base), rel)
    return os.path.realpath(path) == expected


def check_volume(value, conf):
    parts = value.split(":")
    if len(parts) == 1:
        if not value.startswith("/"):
            raise Refused(f"volume {value}: a named volume")
        return  # an anonymous volume: new and empty
    if len(parts) not in (2, 3) or (len(parts) == 3 and parts[2] != "ro"):
        raise Refused(f"volume {value}: not source:target[:ro]")
    source, target = parts[0], parts[1]
    readonly = len(parts) == 3
    if source == DOCKER_SOCKET:
        # The runner mounts the host socket path into job containers; the rootless daemon can't reach the
        # host daemon (setup.sh's isolation test checks it from a container).
        if target != DOCKER_SOCKET:
            raise Refused(f"volume {value}: the socket only at {DOCKER_SOCKET}")
        return
    if not source.startswith("/"):
        raise Refused(f"volume {value}: a named volume")
    work, externals = conf["work"], conf["externals"]
    # The runner's own mounts: the work directory and its temp, actions and tool directories, the job's home
    # and workflow directories, and its externals read-only (ContainerOperationProvider.MountWellKnownDirectories).
    allowed = {work, f"{work}/_temp", f"{work}/_actions", f"{work}/_tool", f"{work}/_temp/_github_home",
               f"{work}/_temp/_github_workflow"}
    if source == externals:
        if not readonly:
            raise Refused(f"volume {value}: the runner's externals only read-only")
        base = os.path.dirname(externals)
    elif source in allowed:
        base = work
    else:
        raise Refused(f"volume {value}: not one of the runner's own directories")
    if not below(source, base):
        raise Refused(f"volume {value}: a symlink below {base}")


def check_create(args, conf):
    """The runner's docker create: its options up to the image. Returns where the options end."""
    i, security = 0, set()
    while i < len(args):
        token = args[i]
        if token == "--" or not token.startswith("-"):
            # As the policy holds it: systempaths=unconfined only with the factory seccomp profile.
            if "systempaths=unconfined" in security and "seccomp=/etc/factory-runner/seccomp-bwrap.json" not in security:
                raise Refused("systempaths=unconfined only with the factory seccomp profile")
            return i
        if token not in ("--name", "--label", "--workdir", "--network", "--network-alias", "-e", "--env",
                         "--entrypoint", "--security-opt", "-v", "--volume"):
            raise Refused(f"create option {token}")
        if i + 1 >= len(args):
            raise Refused(f"create option {token} has no value")
        value = args[i + 1]
        if token == "--network" and not NETWORK.match(value):
            raise Refused(f"network {value}: only the runner's job network")
        if token == "--security-opt":
            if value not in SECURITY_OPTS:
                raise Refused(f"security option {value}")
            security.add(value)
        if token in ("-v", "--volume"):
            check_volume(value, conf)
        i += 2
    raise Refused("create names no image")


def check_exec(args):
    """The runner's docker exec of a step: -i, --workdir, -e, then the container and the command."""
    i = 0
    while i < len(args):
        token = args[i]
        if not token.startswith("-"):
            return
        if token == "-i":
            i += 1
        elif token in ("--workdir", "-e") and i + 1 < len(args):
            i += 2
        else:
            raise Refused(f"exec option {token}")
    raise Refused("exec names no container")


def check_only(args, flags, values, positionals):
    """Exactly these boolean flags and value options, and this many positionals."""
    count, i = 0, 0
    while i < len(args):
        token = args[i]
        if token in flags:
            i += 1
        elif token in values and i + 1 < len(args):
            i += 2
        elif token.startswith("-"):
            raise Refused(f"option {token}")
        else:
            count, i = count + 1, i + 1
    if count not in positionals:
        raise Refused(f"{count} arguments")


def check(argv, conf):
    """The docker command to run instead (argv without the program), and whether it keeps the environment."""
    i, prefix = 0, []
    if argv[:1] == ["--config"]:
        # The runner's registry login and pull keep their config in this job's temp directory.
        if len(argv) < 2:
            raise Refused("--config has no directory")
        config, temp = argv[1], f"{conf['work']}/_temp"
        if not (config.startswith(temp + "/") and below(config, conf["work"])):
            raise Refused(f"--config {config}: not in the job's temp directory")
        prefix, i = argv[:2], 2
    if i >= len(argv):
        raise Refused("no command")
    command, args = argv[i], argv[i + 1:]
    if command.startswith("-"):
        raise Refused(f"global option {command}")
    keep_env = False
    if command == "create":
        end = check_create(args, conf)
        args = args[:end] + ["--security-opt", "no-new-privileges"] + args[end:]
    elif command == "exec":
        check_exec(args)
        keep_env = True
    elif command == "pull":
        check_only(args, (), (), (1,))
    elif command == "login":
        # The registry the runner read from the image name: none for Docker Hub.
        check_only(args, ("--password-stdin",), ("-u", "--username"), (0, 1))
    elif command == "logout":
        check_only(args, (), (), (0, 1))
    elif command == "network":
        sub, rest = (args[0], args[1:]) if args else ("", [])
        if sub == "create":
            check_only(rest, (), ("--label",), (1,))
            name = [t for j, t in enumerate(rest) if not t.startswith("-") and (j == 0 or rest[j - 1] != "--label")]
            if not NETWORK.match(name[0]):
                raise Refused(f"network {name[0]}: only the runner's job network")
        elif sub == "rm":
            check_only(rest, (), (), range(1, 100))
        elif sub == "prune":
            check_only(rest, ("--force",), ("--filter",), (0,))
        else:
            raise Refused(f"network {sub}")
    elif command in ("run", "build"):
        raise Refused(f"docker {command}: the CI tier runs no docker:// step and no container action")
    elif command not in PLAIN:
        raise Refused(f"docker {command}")
    return ["--host", conf["host"], *prefix, command, *args], keep_env


def main(argv):
    if len(argv) < 2:
        print("usage: docker_guard.py <instance.json> [docker arguments...]", file=sys.stderr)
        return 2
    try:
        conf = load(argv[1])
        args, keep_env = check(argv[2:], conf)
    except (Refused, OSError, ValueError) as e:
        print(f"docker guard (CI tier): refused: {e}", file=sys.stderr)
        return 125
    if keep_env:
        env = {k: v for k, v in os.environ.items() if not k.startswith("DOCKER_")}
    else:
        env = {k: os.environ[k] for k in MINIMAL_ENV if k in os.environ}
    os.execve(conf["docker"], [conf["docker"], *args], env)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
