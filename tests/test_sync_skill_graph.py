import tempfile
import unittest
from pathlib import Path

from scripts.sync_skill_graph import END, START, run


class SyncSkillGraphTest(unittest.TestCase):
    def make_repo(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "demo"
        (root / "skill" / "nested").mkdir(parents=True)
        (root / "SKILL.md").write_text(f"---\nname: demo\ndescription: Demo.\n---\n# Demo\n\n{START}\n{END}\n")
        (root / "skill" / "alpha.md").write_text("# Alpha\n\nHandles alpha. See [Beta](nested/beta.md).\n")
        (root / "skill" / "nested" / "beta.md").write_text("# Beta\n\n<!-- graph-summary: Handles beta precisely. -->\nSee [Alpha](../alpha.md).\n")
        return temporary, root

    def test_sync_builds_catalog_and_accepts_cycles(self):
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        self.assertEqual(run(root, check=False), 0)
        generated = (root / "SKILL.md").read_text()
        self.assertIn("[Alpha](skill/alpha.md) — Handles alpha.", generated)
        self.assertIn("[Beta](skill/nested/beta.md) — Handles beta precisely.", generated)
        self.assertEqual(run(root, check=True), 0)

    def test_new_node_requires_resync(self):
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        self.assertEqual(run(root, check=False), 0)
        (root / "skill" / "new.md").write_text("# New node\n\nNew capability.\n")
        self.assertEqual(run(root, check=True), 1)
        self.assertEqual(run(root, check=False), 0)
        self.assertIn("skill/new.md", (root / "SKILL.md").read_text())

    def test_broken_graph_edge_fails(self):
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        (root / "skill" / "alpha.md").write_text("# Alpha\n\nSee [Missing](missing.md).\n")
        self.assertEqual(run(root, check=False), 1)


if __name__ == "__main__":
    unittest.main()
