"""Cross-line reverse-patch checks on real snapshots and rejected changes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import import_undo
import drift


class ImportUndoTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = import_undo.undo.patch
        self.old = Path('shared/import-drift/observed-sentry.csv')
        self.new = Path('shared/import-drift/observed-sentry23.csv')

    def plan(self):
        return self.patch.plan(self.old, self.new, ['module'])

    def test_real_worker_roundtrip_and_html(self):
        forward = self.plan()
        reverse = import_undo.reverse(self.old, forward)
        current = self.root / 'current.csv'
        current.write_bytes(self.patch.apply(self.old, forward))
        self.assertTrue(self.patch.inspect(current, reverse)['valid'])
        restored = self.root / 'restored.csv'
        restored.write_bytes(self.patch.apply(current, reverse))
        self.assertTrue(drift.compare(self.old, restored)['equal'])
        import patch_review
        self.assertIn('<!doctype html>', patch_review.render(current, reverse).lower())

    def test_stale_current_refused(self):
        reverse = import_undo.reverse(self.old, self.plan())
        current = self.root / 'current.csv'
        current.write_bytes(self.patch.apply(self.old, self.plan()).replace(b'\n', b'\r\n'))
        with self.assertRaisesRegex(ValueError, 'baseline changed'):
            self.patch.apply(current, reverse)

    def test_modified_forward_refused(self):
        forward = copy.deepcopy(self.plan())
        forward['operations'] = []
        with self.assertRaises(ValueError):
            import_undo.reverse(self.old, forward)

    def test_generic_csv_refused(self):
        a, b = self.root / 'a.csv', self.root / 'b.csv'
        a.write_text('module,value\na,1\n')
        b.write_text('module,value\na,2\n')
        with self.assertRaisesRegex(ValueError, 'import-drift'):
            import_undo.reverse(a, self.patch.plan(a, b, ['module']))

    def test_other_key_refused(self):
        forward = self.patch.plan(self.old, self.new, ['path'])
        with self.assertRaisesRegex(ValueError, 'keyed only by module'):
            import_undo.reverse(self.old, forward)

    def test_cli_duplicate_json_no_partial_plan(self):
        p = self.root / 'duplicate.json'
        p.write_text('{"format":1,"format":2}')
        command = [sys.executable, '-B', str(Path(import_undo.__file__)), str(self.old), str(p)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('error', json.loads(result.stderr))


if __name__ == '__main__':
    unittest.main()
