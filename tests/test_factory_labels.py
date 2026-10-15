"""The factory's labels: process/factory.md § Labels, which github-provenance's audit (§ 10h) checks a repository
against, names exactly the labels bootstrap.py creates."""
import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def bootstrap_labels():
    tree = ast.parse((ROOT / "bundles/factory/tree/bootstrap.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "LABELS" for t in node.targets):
            return [ast.literal_eval(item)[0] for item in node.value.elts]
    raise AssertionError("bootstrap.py has no LABELS")


def table_labels():
    text = (ROOT / "process/factory.md").read_text()
    section = text[text.index("\n## Labels\n"):]
    section = section[:section.index("\n## ", 1)]
    return re.findall(r"(?m)^\| `(factory:[a-z-]+)` \|", section)


class FactoryLabels(unittest.TestCase):
    def test_the_table_and_bootstrap_name_the_same_labels(self):
        self.assertTrue(bootstrap_labels())
        self.assertEqual(sorted(table_labels()), sorted(bootstrap_labels()))

    def test_every_label_is_in_the_factorys_namespace(self):
        prefix = re.search(r'LABEL_PREFIX = "([^"]+)"', (ROOT / "bundles/factory/tree/bootstrap.py").read_text())[1]
        self.assertTrue(all(name.startswith(prefix) for name in bootstrap_labels()))


if __name__ == "__main__":
    unittest.main()
