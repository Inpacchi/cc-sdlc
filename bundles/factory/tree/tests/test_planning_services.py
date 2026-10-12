"""planning-services.sh's early exits: no database named (planning runs without production data) and a
database named without its password. Starting pgbouncer itself needs the job container; factory-smoke covers it."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "planning-services.sh"


class PlanningServices(unittest.TestCase):
    def run_it(self, database, password=None):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = pathlib.Path(tmp) / "planning.json"
            cfg.write_text(json.dumps({"database": database}))
            env = {k: v for k, v in os.environ.items() if k != "FACTORY_DB_READER_PASSWORD"}
            if password is not None:
                env["FACTORY_DB_READER_PASSWORD"] = password
            return subprocess.run(["bash", str(SCRIPT), str(cfg), str(pathlib.Path(tmp) / "db")],
                                  capture_output=True, text=True, env=env)

    def test_no_database_is_not_an_error(self):
        for database in ({"host": "", "port": 5432, "name": "", "user": "factory_reader", "local_port": 6432}, {}):
            r = self.run_it(database)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("names no database", r.stdout)

    def test_a_named_database_needs_its_password(self):
        r = self.run_it({"host": "db.example", "port": 5432, "name": "app", "user": "reader", "local_port": 6432})
        self.assertEqual(r.returncode, 1)
        self.assertIn("no database password", r.stderr)


if __name__ == "__main__":
    unittest.main()
