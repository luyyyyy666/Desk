import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase0StructureTest(unittest.TestCase):
    def test_rust_workspace_declares_backend_crates(self) -> None:
        cargo_toml = ROOT / "Cargo.toml"
        self.assertTrue(cargo_toml.exists(), "root Cargo.toml should define the Rust workspace")

        data = tomllib.loads(cargo_toml.read_text(encoding="utf-8"))
        members = set(data["workspace"]["members"])

        required_members = {
            "apps/api",
            "crates/agent-core",
            "crates/domain",
            "crates/persistence",
            "crates/tool-runtime",
        }

        self.assertTrue(required_members.issubset(members))

    def test_python_tooling_and_environment_files_exist(self) -> None:
        self.assertTrue((ROOT / "pyproject.toml").exists())
        self.assertTrue((ROOT / ".env.example").exists())
        self.assertTrue((ROOT / "justfile").exists())

    def test_local_development_docs_exist(self) -> None:
        docs = ROOT / "docs" / "development" / "local-setup.md"
        self.assertTrue(docs.exists())
        content = docs.read_text(encoding="utf-8")

        self.assertIn("Phase 0", content)
        self.assertIn("just check", content)
        self.assertIn("frontend/", content)


if __name__ == "__main__":
    unittest.main()
