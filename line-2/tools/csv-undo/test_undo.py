"""Undo behavior, using only workspace scratch fixtures."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import undo


class UndoTests(unittest.TestCase):
    def setUp(self):
        root = Path('test/scratch')
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, name, raw):
        p = self.root / name
        p.write_bytes(raw)
        return p

    def roundtrip(self, before, after, keys):
        a, b = self.file('a.csv', before), self.file('b.csv', after)
        forward = undo.patch.plan(a, b, keys)
        saved = copy.deepcopy(forward)
        reverse = undo.reverse(a, forward)
        self.assertEqual(forward, saved)
        applied = self.file('applied.csv', undo.patch.apply(a, forward))
        restored = undo.patch.apply(applied, reverse)
        header, rows = undo.patch.parse_table(before, keys)
        self.assertEqual(restored, undo.patch.encode_table(header, rows))
        self.assertEqual(reverse['baseline_sha256'], forward['result_sha256'])
        return a, forward, applied, reverse

    def test_add_remove_edit_roundtrip(self):
        self.roundtrip(b'id,v\na,old\nb,drop\nc,same\n',
                       b'id,v\nd,new\nc,same\na,edited\n', ['id'])

    def test_canonical_not_original_bytes(self):
        a, f, current, r = self.roundtrip(b'\xef\xbb\xbfid,v\r\nb,"02"\r\na,=1+1\r\n',
                                        b'v,id\nnew,a\n02,b\n', ['id'])
        self.assertNotEqual(undo.patch.apply(current, r), a.read_bytes())
        self.assertEqual(undo.patch.apply(current, r), b'id,v\na,=1+1\nb,02\n')

    def test_composite_multiline_unicode(self):
        self.roundtrip('id,part,v\nab,c,"α\nβ"\na,bc,\n'.encode(),
                       'id,part,v\na,bc,雪\nab,c,changed\n'.encode(), ['id', 'part'])

    def test_empty_and_no_change(self):
        for a, b in [(b'id,v\n', b'id,v\na,x\n'),
                     (b'id,v\na,x\n', b'id,v\n'),
                     (b'id,v\n', b'id,v\n')]:
            with self.subTest(a=a, b=b):
                self.roundtrip(a, b, ['id'])

    def test_tampered_forward_refused(self):
        a, f, current, r = self.roundtrip(b'id,v\na,x\n', b'id,v\na,y\n', ['id'])
        f['operations'][0]['after']['v'] = 'tampered'
        with self.assertRaises(undo.patch.InputError):
            undo.reverse(a, f)

    def test_stale_original_refused(self):
        a, f, current, r = self.roundtrip(b'id,v\na,x\n', b'id,v\na,y\n', ['id'])
        a.write_bytes(b'id,v\na,stale\n')
        with self.assertRaises(undo.patch.InputError):
            undo.reverse(a, f)

    def test_changed_current_refused_even_line_endings(self):
        a, f, current, r = self.roundtrip(b'id,v\na,x\n', b'id,v\na,y\n', ['id'])
        current.write_bytes(current.read_bytes().replace(b'\n', b'\r\n'))
        with self.assertRaises(undo.patch.InputError):
            undo.patch.apply(current, r)

    def test_cli_and_duplicate_json_no_partial_output(self):
        a, f, current, r = self.roundtrip(b'id,v\na,x\n', b'id,v\na,y\n', ['id'])
        p = self.file('plan.json', json.dumps(f).encode())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(undo.main([str(a), str(p)]), 0)
        self.assertEqual(json.loads(out.getvalue()), r)
        for raw in [b'{"format":1,"format":2}', b'{', b'[]']:
            p.write_bytes(raw)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(undo.main([str(a), str(p)]), 2)
            self.assertEqual(out.getvalue(), '')
            self.assertIn('error', err.getvalue())

    def test_outside_workspace_refused_without_read(self):
        with self.assertRaises(undo.patch.InputError):
            undo.reverse(Path.cwd().parent / 'not-read.csv',
                         {'format':'csv-patch/v1', 'keys':['id'], 'header':['id'],
                          'baseline_sha256':'a'*64, 'result_sha256':'b'*64,
                          'operations':[]})


if __name__ == '__main__':
    unittest.main()
