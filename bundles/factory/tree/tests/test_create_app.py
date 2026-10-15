"""create_app.py: the manifest the factory's App is created from, the local page that posts it, the redirect
it waits for, and the factory.json update. GitHub's side (the form, the conversion) is faked."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))
import bootstrap  # noqa: E402
import create_app  # noqa: E402


class Manifest(unittest.TestCase):
    def test_exactly_the_permissions_bootstrap_checks(self):
        m = create_app.manifest("acme-factory", "acme", 4321)
        self.assertEqual(m["default_permissions"], bootstrap.APP_PERMISSIONS)
        self.assertEqual(m["default_events"], [])
        self.assertNotIn("hook_attributes", m)
        self.assertIs(m["public"], False)
        self.assertEqual(m["redirect_url"], "http://127.0.0.1:4321/created")

    def test_the_runner_registration_app_has_one_permission(self):
        m = create_app.manifest("acme-factory-runners", "acme", 4242, create_app.RUNNER_PERMISSIONS)
        self.assertEqual(m["default_permissions"], {"organization_self_hosted_runners": "write"})
        self.assertEqual((m["public"], m["default_events"]), (False, []))
        self.assertNotIn("hook_attributes", m)

    def test_the_runner_audits_app_only_reads_runners(self):
        m = create_app.manifest("acme-factory-runner-audit", "acme", 4343, create_app.AUDITOR_PERMISSIONS)
        self.assertEqual(m["default_permissions"], {"organization_self_hosted_runners": "read"})
        self.assertEqual((m["public"], m["default_events"]), (False, []))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            create_app.auditor_done({"slug": "acme-factory-runner-audit", "client_id": "Iv23audit",
                                     "permissions": {"organization_self_hosted_runners": "write", "metadata": "read"}},
                                    pathlib.Path("/home/me/k.pem"), "acme")
        text = out.getvalue()
        self.assertIn("not just {'organization_self_hosted_runners': 'read'}", text)  # a write grant is called out
        self.assertIn("gh secret set RUNNER_AUDIT_APP_KEY --repo acme/<repo> < /home/me/k.pem", text)
        self.assertIn("runner_audit.py workflow expected.json", text)

    def test_the_page_posts_to_the_organizations_form(self):
        html = create_app.page("acme", "st4te", create_app.manifest("acme-factory", "acme", 4321))
        self.assertIn('action="https://github.com/organizations/acme/settings/apps/new?state=st4te"', html)
        self.assertIn('name="manifest"', html)
        self.assertIn("&quot;pull_requests&quot;: &quot;write&quot;", html)


class Conversion(unittest.TestCase):
    def test_convert_and_bot_user(self):
        calls = []

        def fake(method, url, data=None):
            calls.append((method, url))
            return {"id": 7, "slug": "acme-factory", "client_id": "Iv1.x", "pem": "KEY"} if method == "POST" else {"id": 99}

        self.assertEqual(create_app.convert("c0de", call=fake)["slug"], "acme-factory")
        self.assertEqual(create_app.bot_user_id("acme-factory", call=fake), 99)
        self.assertEqual(calls, [("POST", "https://api.github.com/app-manifests/c0de/conversions"),
                                 ("GET", "https://api.github.com/users/acme-factory%5Bbot%5D")])

    def test_write_app_changes_only_the_app(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "factory.json"
            seed = (FACTORY / "factory.json").read_text()
            path.write_text(seed)
            create_app.write_app(path, "acme-factory", 99)
            after = path.read_text()
            self.assertEqual(json.loads(after)["app"], {"user_id": 99, "login": "acme-factory[bot]"})
            changed = [(a, b) for a, b in zip(seed.splitlines(), after.splitlines()) if a != b]
            self.assertEqual(len(changed), 2)


class Redirect(unittest.TestCase):
    def test_waits_for_githubs_redirect_with_the_right_state(self):
        opened = {}

        def browser(url):
            opened["url"] = url

            def visit():
                page = urllib.request.urlopen(url).read().decode()
                state = page.split("state=")[1].split('"')[0]
                with self.assertRaises(urllib.error.HTTPError) as refused:  # a wrong state is refused
                    urllib.request.urlopen(url + "created?state=wrong&code=x")
                refused.exception.close()
                urllib.request.urlopen(url + f"created?state={state}&code=the-code").read()

            threading.Thread(target=visit, daemon=True).start()

        with contextlib.redirect_stdout(io.StringIO()):
            code = create_app.wait_for_code("acme", "acme-factory", open_browser=browser)
        self.assertEqual(code, "the-code")
        self.assertTrue(opened["url"].startswith("http://127.0.0.1:"))


if __name__ == "__main__":
    unittest.main()
