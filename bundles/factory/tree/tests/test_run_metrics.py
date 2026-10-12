"""Tests for run_metrics.py: the record keeps only allowlisted values, and what it can't read is null."""

import json
import pathlib
import sys
import tempfile
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import run_metrics as rm  # noqa: E402


class Record(unittest.TestCase):
    def exec_file(self, events):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(events, f)
        f.close()
        self.addCleanup(pathlib.Path(f.name).unlink)
        return f.name

    def test_from_the_runtime_record(self):
        path = self.exec_file([
            {"type": "system"},
            {"type": "result", "total_cost_usd": 1.0, "num_turns": 3},
            {"type": "result", "subtype": "success", "total_cost_usd": 4.25, "num_turns": 40, "duration_ms": 9000,
             "modelUsage": {"claude-opus-5-5": {}, "claude-haiku-5-5": {}, "<script>": {}},
             "permission_denials": [{"tool": "Read"}], "result": "agent words"}])
        env = {"EXEC": path, "RESULT": json.dumps({"status": "awaiting-approval", "reason": "words"}),
               "INPUTS": json.dumps({"tier": "full", "advisor": "auto", "model": "claude-opus-5-5", "prompt": "x", "compare": True}),
               "RUN_ID": "123", "RUN_ATTEMPT": "2", "WORKFLOW": "factory-plan"}
        r = rm.record("spec", "47", env)
        self.assertEqual(r, {
            "v": 1, "stage": "spec", "issue": 47, "workflow": "factory-plan", "run_id": 123, "run_attempt": 2,
            "status": "awaiting-approval", "end": "success", "lost": None, "cost": 4.25, "turns": 40, "duration_ms": 9000,
            "models": ["claude-haiku-5-5", "claude-opus-5-5"], "denials": 1,
            "inputs": {"tier": "full", "advisor": "auto", "model": "claude-opus-5-5", "compare": "true"}})
        self.assertNotIn("agent words", json.dumps(r))
        self.assertNotIn("words", json.dumps(r))

    def test_nothing_readable_is_null(self):
        r = rm.record("plan", "", {"EXEC": "/nonexistent", "RESULT": "{not json", "LOST": "stopped at the 4-hour limit after 240 minutes"})
        self.assertEqual((r["issue"], r["status"], r["cost"], r["turns"], r["models"], r["denials"], r["lost"]),
                         (None, None, None, None, [], None, "time-limit"))

    def test_status_state_and_lost(self):
        self.assertEqual(rm.outcome(json.dumps({"state": "ready-to-plan"})), "ready-to-plan")
        self.assertIsNone(rm.outcome(json.dumps({"status": "approved-by-me"})))
        self.assertIsNone(rm.outcome(json.dumps(["done"])))
        self.assertEqual(rm.lost("ended after 3 minutes without a usable result (error_max_turns)"), "turn-limit")
        self.assertEqual(rm.lost("stopped after 3 minutes with no result and no record of why"), "no-result")
        self.assertIsNone(rm.lost(""))

    def test_bad_values(self):
        path = self.exec_file([{"type": "result", "total_cost_usd": -1, "num_turns": 2.5, "duration_ms": True}])
        r = rm.record("triage", "0", {"EXEC": path, "RUN_ID": "12; rm", "WORKFLOW": "ci"})
        self.assertEqual((r["cost"], r["turns"], r["duration_ms"], r["run_id"], r["workflow"], r["issue"]),
                         (None, None, None, None, None, None))
        with self.assertRaises(ValueError):
            rm.record("deploy", "1", {})


if __name__ == "__main__":
    unittest.main()
