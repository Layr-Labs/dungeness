"""Accounting and collector credentials remain private even with a permissive umask."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gateway_usage import UsageLedger, append_jsonl_locked


class UsagePermissionsTests(unittest.TestCase):
    def test_private_creation_and_existing_mode_repair(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'MAX_SEARCHES': '0', 'MAX_FETCHES': '0', 'MAX_MODEL_REQUESTS': '10'}):
            root = Path(directory)
            root.chmod(0o777)
            for name in ('events.jsonl', '.event-token', '.summary.json.tmp'):
                (root / name).touch()
                (root / name).chmod(0o666)
            previous = os.umask(0)
            try:
                ledger = UsageLedger('private-usage', root)
                ledger.emit(source='gateway', kind='gateway.test', data={})
                append_jsonl_locked(root / 'fallback.jsonl', {'test': True})
            finally:
                os.umask(previous)
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            for name in ('events.jsonl', '.event-token', 'summary.json', 'fallback.jsonl'):
                self.assertEqual((root / name).stat().st_mode & 0o777, 0o600, name)

    def test_no_following_links_or_changing_their_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'outside'
            target.write_text('unchanged')
            target.chmod(0o644)
            usage = root / 'usage'
            usage.mkdir()
            (usage / 'events.jsonl').symlink_to(target)
            with self.assertRaises(OSError):
                append_jsonl_locked(usage / 'events.jsonl', {'test': True})
            self.assertEqual(target.read_text(), 'unchanged')
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)


if __name__ == '__main__':
    unittest.main()
