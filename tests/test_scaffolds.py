"""Scaffold contracts use synthetic text files, independent of any challenge."""
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from dungeness.scaffolds import (
    resolve_scaffold, apply_scaffold_trusted_files, materialize_scaffold_candidate,
)


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'scaffolds/example'
        self.folder.mkdir(parents=True)
        (self.folder / 'blank.txt').write_text('implement here\n')
        (self.folder / 'guide.txt').write_text('trusted instructions\n')
        self.document = {
            'schema_version': 2, 'type': 'scaffold', 'id': 'example',
            'candidate_path': 'solution', 'candidate_files': {'blank.txt': 'answer.txt'},
            'workspace_paths': ['settings.txt'], 'trusted_files': {'guide.txt': 'guide.txt'},
            'text_edits': [{'path': 'settings.txt', 'pattern': 'PLACEHOLDER',
                            'replacement': 'fixed', 'matches': 1}],
        }
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        (self.workspace / 'settings.txt').write_text('value=PLACEHOLDER\n')

    def resolve(self):
        (self.folder / 'scaffold.yaml').write_text(yaml.safe_dump(self.document))
        return resolve_scaffold(self.root, 'scaffolds/example/scaffold.yaml')

    def test_fresh_candidate_and_same_trusted_edits_in_workspace_and_verifier(self):
        scaffold = self.resolve()
        candidate = self.workspace / 'solution'
        candidate.mkdir()
        (candidate / 'prior-answer.txt').write_text('must not survive')
        apply_scaffold_trusted_files(scaffold, self.workspace)
        materialize_scaffold_candidate(scaffold, self.workspace)
        self.assertEqual([p.name for p in candidate.iterdir()], ['answer.txt'])
        self.assertEqual((candidate / 'answer.txt').read_text(), 'implement here\n')
        self.assertEqual((self.workspace / 'settings.txt').read_text(), 'value=fixed\n')
        self.assertEqual((self.workspace / 'guide.txt').read_text(), 'trusted instructions\n')
        verifier = self.root / 'verifier'
        verifier.mkdir()
        (verifier / 'settings.txt').write_text('value=PLACEHOLDER\n')
        apply_scaffold_trusted_files(scaffold, verifier)
        self.assertEqual((verifier / 'settings.txt').read_bytes(),
                         (self.workspace / 'settings.txt').read_bytes())
        self.assertFalse((verifier / 'solution').exists())

    def test_edit_fails_closed_on_missing_or_ambiguous_source(self):
        scaffold = self.resolve()
        for text in ('wrong source', 'PLACEHOLDER PLACEHOLDER'):
            with self.subTest(text=text):
                target = self.workspace / 'settings.txt'
                target.write_text(text)
                with self.assertRaisesRegex(ValueError, 'expected 1 matches'):
                    apply_scaffold_trusted_files(scaffold, self.workspace)
                self.assertEqual(target.read_text(), text)

    def test_rejects_candidate_edits_and_old_problem_specific_fields(self):
        for path in ('solution', 'solution/answer.txt'):
            with self.subTest(path=path):
                self.document['text_edits'][0]['path'] = path
                with self.assertRaisesRegex(ValueError, 'outside the editable candidate'):
                    self.resolve()
        self.document['text_edits'] = []
        self.document['rust_modules'] = ['example']
        with self.assertRaisesRegex(ValueError, 'unsupported scaffold fields'):
            self.resolve()

    def test_rejects_path_traversal_and_symlink_escape(self):
        for field, value in (('candidate_path', '../outside'), ('workspace_paths', ['/etc'])):
            original = self.document[field]
            self.document[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.resolve()
            self.document[field] = original
        (self.folder / 'blank.txt').unlink()
        (self.folder / 'blank.txt').symlink_to(self.workspace / 'settings.txt')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.resolve()

    def test_refuses_destination_symlink_without_touching_its_target(self):
        scaffold = self.resolve()
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'retained.txt').write_text('retain')
        (self.workspace / 'solution').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            materialize_scaffold_candidate(scaffold, self.workspace)
        self.assertEqual((outside / 'retained.txt').read_text(), 'retain')
