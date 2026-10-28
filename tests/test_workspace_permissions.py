"""A private worker umask must not hide public scaffold files from the agent."""
import os
from pathlib import Path
import stat
import tempfile
import unittest

from dungeness.compiler import prepare_workspace_permissions


class WorkspacePermissionsTests(unittest.TestCase):
    def test_private_umask_public_workspace_and_private_siblings(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            original = os.umask(0o077)
            try:
                root = base / 'workspace'
                (root / 'solution').mkdir(parents=True)
                (root / 'Cargo.toml').write_text('public scaffold')
                (root / 'solution/answer.txt').write_text('fresh candidate')
                executable = root / 'check'
                executable.write_text('#!/bin/sh\nexit 0\n')
                executable.chmod(0o700)
                (root / 'guide').symlink_to('Cargo.toml')
                private = base / 'credentials'
                private.mkdir()
                (private / 'synthetic.json').write_text('synthetic only')
                self.assertEqual(stat.S_IMODE((root / 'Cargo.toml').stat().st_mode), 0o600)
                prepare_workspace_permissions(root)
                probe = base / 'still-private'
                probe.write_text('synthetic only')
            finally:
                os.umask(original)
            for path in [root, root / 'solution', executable]:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o755)
            for path in [root / 'Cargo.toml', root / 'solution/answer.txt']:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o644)
            self.assertTrue((root / 'guide').is_symlink())
            self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o700)
            for path in [private / 'synthetic.json', probe]:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_rejects_links_outside_workspace_without_changing_target(self):
        for hardlink in [False, True]:
            with self.subTest(hardlink=hardlink), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                root = base / 'workspace'
                root.mkdir(mode=0o700)
                secret = base / 'private'
                secret.write_text('synthetic only')
                secret.chmod(0o600)
                if hardlink:
                    os.link(secret, root / 'link')
                else:
                    (root / 'link').symlink_to(secret)
                with self.assertRaises(ValueError):
                    prepare_workspace_permissions(root)
                self.assertEqual(stat.S_IMODE(secret.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)

    def test_rejects_special_files_and_symlink_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / 'workspace'
            root.mkdir()
            os.mkfifo(root / 'pipe')
            with self.assertRaisesRegex(ValueError, 'unsupported workspace file'):
                prepare_workspace_permissions(root)
            link = base / 'linked-root'
            link.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'root must not be a symlink'):
                prepare_workspace_permissions(link)
