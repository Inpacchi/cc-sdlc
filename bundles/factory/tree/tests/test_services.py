"""Tests for services.py: validation, every slot masked in every run, wiring only for listed stages,
nothing secret in the agent's context, and MCP servers by slot."""

import json
import pathlib
import sys
import tempfile
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import services as svc  # noqa: E402

ENV = {"name": "sentry", "stages": ["plan", "spec"], "slot": "FACTORY_SVC_1", "attach": "env", "read_only": True,
       "domains": ["sentry.io", "*.sentry.io"], "auth": "Authorization: Bearer $FACTORY_SVC_1"}
MCP = {"name": "linear", "stages": ["plan"], "slot": "FACTORY_SVC_2", "attach": "mcp", "read_only": True,
       "url": "https://mcp.linear.app/mcp", "header": "Authorization", "prefix": "Bearer "}
BASE = {"sandbox": {"network": {"allowedDomains": ["localhost"]}, "credentials": {"envVars": []}}}


def load(services):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"services": services}, f)
    return svc.load(f.name)


class Validation(unittest.TestCase):
    def test_accepts(self):
        self.assertEqual(len(load([ENV])), 1)
        self.assertEqual(load([]), [])

    def test_read_only_required_and_mcp_deferred(self):
        for bad in [[{k: v for k, v in ENV.items() if k != "read_only"}], [dict(ENV, read_only=False)], [MCP]]:
            with self.assertRaises(svc.Invalid, msg=bad):
                load(bad)

    def test_refuses(self):
        for bad in [[dict(ENV, domains=["*"])], [dict(ENV, domains=["*.com"])], [dict(ENV, domains=[])],
                    [dict(ENV, stages=["implement"])], [dict(ENV, stages=[])], [dict(ENV, slot="FACTORY_SVC_9")],
                    [ENV, dict(ENV, name="other")], [ENV, dict(ENV, slot="FACTORY_SVC_3")],
                    [dict(ENV, name="Bad Name")], [dict(ENV, attach="file")],
                    [dict(ENV, extra=1)], [dict(ENV, domains=["e.com/path"])]]:
            with self.assertRaises(svc.Invalid, msg=bad):
                load(bad)


class Settings(unittest.TestCase):
    def masks(self, out):
        return {v["name"]: v for v in out["sandbox"]["credentials"]["envVars"]}

    def test_every_slot_masked_even_with_no_services(self):
        out = svc.settings(BASE, [], "plan")
        masks = self.masks(out)
        self.assertEqual(set(masks), set(svc.SLOTS))
        self.assertTrue(all(m["mode"] == "mask" and m["injectHosts"] == [] for m in masks.values()))
        self.assertEqual(out["sandbox"]["network"]["allowedDomains"], ["localhost"])
        self.assertNotIn("tlsTerminate", out["sandbox"]["network"])

    def test_env_service_wired_for_its_stages_only(self):
        services = load([ENV]) + [MCP]  # MCP built by hand: load() rejects it until it has its own proof
        out = svc.settings(BASE, services, "plan")
        self.assertEqual(self.masks(out)["FACTORY_SVC_1"]["injectHosts"], ["sentry.io", "*.sentry.io"])
        self.assertEqual(self.masks(out)["FACTORY_SVC_2"]["injectHosts"], [])  # mcp: never in the sandbox
        self.assertEqual(out["sandbox"]["network"]["allowedDomains"], ["localhost", "sentry.io", "*.sentry.io"])
        self.assertEqual(out["sandbox"]["network"]["tlsTerminate"], {})
        other = svc.settings(BASE, services, "implement")
        self.assertTrue(all(m["injectHosts"] == [] for m in self.masks(other).values()))
        self.assertEqual(other["sandbox"]["network"]["allowedDomains"], ["localhost"])

    def test_base_is_not_mutated_and_slots_not_duplicated(self):
        base = {"sandbox": {"credentials": {"envVars": [{"name": "FACTORY_SVC_1", "mode": "mask", "injectHosts": ["x.io"]},
                                                        {"name": "OTHER", "mode": "mask", "injectHosts": []}]}}}
        snapshot = json.dumps(base)
        out = svc.settings(base, [], "plan")
        self.assertEqual(json.dumps(base), snapshot)
        names = [v["name"] for v in out["sandbox"]["credentials"]["envVars"]]
        self.assertEqual(sorted(names), sorted(svc.SLOTS + ["OTHER"]))


class ContextAndMcp(unittest.TestCase):
    def test_context_has_no_values(self):
        ctx = svc.context(load([ENV]) + [MCP], "plan")
        self.assertEqual([e["name"] for e in ctx["services"]], ["sentry", "linear"])
        self.assertEqual(ctx["services"][0]["variable"], "FACTORY_SVC_1")
        self.assertEqual(svc.context(load([ENV]), "implement"), {"services": []})

    def test_mcp_server_by_slot(self):
        servers = svc.mcp_servers(load([ENV]) + [MCP], "plan")
        self.assertEqual(servers, {"linear": {"type": "http", "url": "https://mcp.linear.app/mcp",
                                              "headers": {"Authorization": "Bearer ${FACTORY_SVC_2}"}}})
        self.assertEqual(svc.mcp_servers([MCP], "spec"), {})


if __name__ == "__main__":
    unittest.main()
