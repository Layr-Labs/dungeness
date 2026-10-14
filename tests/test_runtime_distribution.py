"""Distribution boundary: committed runtime only, with independently checked bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime_export", ROOT / "script/export_runtime.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class RuntimeDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Runtime test")
        self.git("config", "user.email", "runtime@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        for path in (
            "dungeness", "src/dungeness/compiler.py", "adapters/harbor/command_agent.py",
            "services/gateway/gateway.py", "tasks/projects/dungeness/ecdsa-starter/task.yaml",
            "run-specs/projects/dungeness/ecdsa-starter.yaml", ".env.example",
            "watcher/render_gateway_transcript.py", "watcher/serve_gateway_transcripts.py",
        ):
            self.write(path, f"runtime {path}\n")
        (self.root / "dungeness").chmod(0o755)
        # Even accidentally committed private/research files cannot enter this bundle.
        for path in (
            ".env", "services/gateway/.env", "runs/users/test/result.json",
            "knowledge-bases/users/test/paper.pdf", "run-specs/users/test/run.yaml",
            "tasks/users/test/task.yaml", "experiments/users/test/result.md",
        ):
            self.write(path, "synthetic-private-data\n")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Test source")

    def export(self, name="runtime.tar.gz"):
        output = Path(self.temp.name) / name
        return output, exporter.export_runtime(self.root, "HEAD", output)

    def test_committed_bytes_only_with_modes_digests_and_reproducible_output(self):
        self.write("src/dungeness/compiler.py", "uncommitted change\n")
        self.write("services/gateway/local-secret.py", "untracked secret\n")
        output, report = self.export()
        other, again = self.export("again.tar.gz")
        self.assertEqual(output.read_bytes(), other.read_bytes())
        self.assertEqual(report["sha256"], again["sha256"])
        self.assertEqual(report["source_commit"], self.git("rev-parse", "HEAD").decode().strip())
        with tarfile.open(output) as archive:
            names = archive.getnames()
            self.assertIn("dungeness-runtime/.env.example", names)
            self.assertIn("dungeness-runtime/watcher/serve_gateway_transcripts.py", names)
            self.assertEqual(archive.getmember("dungeness-runtime/dungeness").mode, 0o755)
            source = json.load(archive.extractfile("dungeness-runtime/RUNTIME_SOURCE.json"))
            for name, digest in source["files"].items():
                content = archive.extractfile("dungeness-runtime/" + name).read()
                self.assertNotIn(b"private", content)
                self.assertNotIn(b"uncommitted", content)
                self.assertNotIn(b"untracked", content)
                self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertEqual(len(names), report["files"] + 1)
            self.assertEqual(source["source_commit"], report["source_commit"])
        with self.assertRaises(FileExistsError):
            exporter.export_runtime(self.root, "HEAD", output)

    def test_symlink_and_lfs_runtime_members_are_rejected(self):
        path = self.root / "services/gateway/escape.py"
        path.symlink_to("../../.env")
        self.commit()
        with self.assertRaisesRegex(ValueError, "Unexpected runtime archive entry"):
            self.export()
        path.unlink()
        path.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:" + "a" * 64 + "\nsize 4\n")
        self.commit()
        with self.assertRaisesRegex(ValueError, "LFS pointer"):
            self.export()
        self.assertFalse((Path(self.temp.name) / "runtime.tar.gz").exists())

    def test_old_revision_missing_command_support_cannot_be_distributed(self):
        self.git("rm", "adapters/harbor/command_agent.py")
        self.git("commit", "-qm", "Missing adapter")
        with self.assertRaisesRegex(ValueError, "lacks runtime files"):
            self.export()


if __name__ == "__main__":
    unittest.main()
