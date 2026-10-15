#!/usr/bin/env python3
"""Create the factory's GitHub App from its manifest (z-sdlc process/factory.md, Enablement step 5).

    python3 .github/factory/create_app.py <organization> [--name NAME] [--key-out PATH]
    python3 .github/factory/create_app.py <organization> --runners [--name NAME] [--key-out PATH]

Opens GitHub's create-an-App page for the organization with the factory's manifest filled in (a local
page posts it); you confirm it there. GitHub sends the browser back to this script, which converts the
result into the App's private key (written to --key-out, mode 600; by default in your home directory,
outside any checkout) and client ID, writes the App's bot
user into factory.json, and prints the install link and the commands that store the key and the client
ID in the factory-writer environment. The App gets exactly the permissions bootstrap.py checks for
(contents, issues and pull requests write, metadata read) and no webhook. Standard library only.

--runners creates the CI tier's runner-registration App instead (process/factory.md, Enablement step 10, The CI
tier). Its one permission is the organization's self-hosted runners, and GitHub has no narrower one that registers
runners: it reaches every runner group in the organization (registering runners into any of them, moving runners,
changing a group's restrictions). So its key goes to the runner host root-only, never into a checkout, and every
other copy is deleted. factory.json is left alone.
"""
import argparse
import html
import http.server
import json
import os
import pathlib
import re
import secrets
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

FACTORY = pathlib.Path(__file__).resolve().parent
API = "https://api.github.com"
PERMISSIONS = {"contents": "write", "issues": "write", "pull_requests": "write", "metadata": "read"}
RUNNER_PERMISSIONS = {"organization_self_hosted_runners": "write"}


def manifest(name, org, port, permissions=PERMISSIONS):
    """The App as the factory needs it: private, no webhook, nothing beyond its permissions."""
    return {"name": name, "url": f"https://github.com/{org}", "public": False,
            "redirect_url": f"http://127.0.0.1:{port}/created",
            "default_permissions": dict(permissions), "default_events": []}


def page(org, state, app_manifest):
    """The local page that posts the manifest to GitHub's create-an-App form for the organization."""
    action = f"https://github.com/organizations/{urllib.parse.quote(org)}/settings/apps/new?state={state}"
    return (f'<!doctype html><meta charset="utf-8"><title>Create the factory App</title>'
            f'<form id="f" method="post" action="{html.escape(action)}">'
            f'<input type="hidden" name="manifest" value="{html.escape(json.dumps(app_manifest))}">'
            f'<p>Sending the factory App\'s manifest to GitHub. <button>Continue</button></p></form>'
            f'<script>document.getElementById("f").submit()</script>')


def request(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method, headers={"Accept": "application/vnd.github+json",
                                                                          "User-Agent": "z-sdlc-factory"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def convert(code, call=request):
    """GitHub's half of the manifest flow: the App's id, slug, client ID and private key."""
    return call("POST", f"{API}/app-manifests/{urllib.parse.quote(code)}/conversions", b"")


def bot_user_id(slug, call=request):
    return call("GET", f"{API}/users/{urllib.parse.quote(slug + '[bot]')}")["id"]


def write_app(factory_json, slug, user_id):
    """Set factory.json's app.user_id and app.login, leaving the rest of the file as it is."""
    path = pathlib.Path(factory_json)
    text = path.read_text()
    text, n1 = re.subn(r'("user_id"\s*:\s*)-?\d+', rf"\g<1>{user_id}", text, count=1)
    text, n2 = re.subn(r'("login"\s*:\s*)"[^"]*"', rf'\g<1>"{slug}[bot]"', text, count=1)
    data = json.loads(text)
    if (n1, n2) != (1, 1) or data["app"] != {"user_id": user_id, "login": f"{slug}[bot]"}:
        raise SystemExit("create_app: couldn't set app.user_id and app.login in factory.json; set them by hand")
    path.write_text(text)


def wait_for_code(org, name, open_browser=webbrowser.open, permissions=PERMISSIONS):
    """Serve the page, open it, and wait for GitHub's redirect; returns the conversion code."""
    state, result = secrets.token_urlsafe(16), {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            query = dict(urllib.parse.parse_qsl(url.query))
            if url.path == "/":
                body = page(org, state, manifest(name, org, self.server.server_port, permissions))
            elif url.path == "/created" and query.get("state") == state and query.get("code"):
                result["code"] = query["code"]
                body = "<!doctype html><p>The App is created. Return to the terminal.</p>"
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self.send_error(400)
                return
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Opening {url} to create the App in {org} (open it yourself if no browser appears).")
    open_browser(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()
    return result["code"]


def repository():
    r = subprocess.run(["git", "-C", str(FACTORY), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", r.stdout)
    return m.group(1) if m else "<owner>/<repository>"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("organization")
    ap.add_argument("--name", help="the App's name (default: <organization>-factory)")
    ap.add_argument("--key-out", help="where to write the private key (default: ~/<name>.private-key.pem)")
    ap.add_argument("--runners", action="store_true", help="the CI tier's runner-registration App instead")
    args = ap.parse_args(argv)
    name = args.name or f"{args.organization}-factory{'-runners' if args.runners else ''}"
    # Outside the repository by default, so no `git add` can pick the key up.
    args.key_out = args.key_out or str(pathlib.Path.home() / f"{name}.private-key.pem")
    if pathlib.Path(args.key_out).exists():
        raise SystemExit(f"create_app: {args.key_out} exists; move it or pass --key-out")
    app = convert(wait_for_code(args.organization, name,
                                permissions=RUNNER_PERMISSIONS if args.runners else PERMISSIONS))
    key = pathlib.Path(args.key_out)
    # Created here, readable only by you; an existing file is never overwritten.
    with os.fdopen(os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as f:
        f.write(app["pem"])
    if args.runners:
        return runners_done(app, key)
    user_id = bot_user_id(app["slug"])
    write_app(FACTORY / "factory.json", app["slug"], user_id)
    repo = repository()
    print(f"""
Created {app['slug']} (bot user {user_id}); factory.json's app is set, and its private key is {key}.
1. Install it on the repository: https://github.com/apps/{app['slug']}/installations/new
2. After bootstrap.py --apply has created the factory-writer environment, store the key and client ID,
   then delete the key file:
     gh secret set FACTORY_APP_PRIVATE_KEY --env factory-writer --repo {repo} < {key}
     gh variable set FACTORY_APP_CLIENT_ID --env factory-writer --repo {repo} --body {app['client_id']}
3. Run python3 .github/factory/render.py and commit factory.json and the workflows.""")
    return 0


def runners_done(app, key):
    """The runner-registration App: say where its key and client ID go on the runner host."""
    granted = app.get("permissions") or {}
    if granted and {k: v for k, v in granted.items() if k != "metadata"} != RUNNER_PERMISSIONS:
        print(f"create_app: the App has {granted}, not just {RUNNER_PERMISSIONS}: fix it in its settings before use")
    print(f"""
Created {app['slug']}, the CI tier's runner-registration App; its private key is {key}. The key can register
runners into every runner group in the organization: keep it only where step 2 puts it.
1. Install it on the organization (it needs no repository): https://github.com/apps/{app['slug']}/installations/new
2. Copy the key to the runner host and install it root-only, never in a checkout (factory-ci-<instance> for another
   organization's runners on that host), then delete every other copy, {key} included:
     sudo install -D -m 600 -o root -g root <the copied key> /etc/factory-runner/factory-ci/app.pem
3. Set CI_APP_CLIENT_ID={app['client_id']} in the CI tier's checkout's .github/factory/host/host.conf, and run
   sudo TIER=ci bash .github/factory/host/setup.sh there (process/factory.md, Enablement step 10).""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
