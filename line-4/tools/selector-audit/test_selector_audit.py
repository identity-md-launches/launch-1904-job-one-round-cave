import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import selector_audit as tool


def fn(name, *types, outputs=None):
    return dict(type='function', name=name,
                inputs=[{'type': t} for t in types], outputs=outputs or [])


class SelectorAuditTests(unittest.TestCase):
    def test_published_erc20_selectors(self):
        result = tool.audit([fn('transfer', 'address', 'uint'), fn('balanceOf', 'address'),
                             fn('approve', 'address', 'uint256')])
        self.assertEqual([r['selector'] for r in result['functions']],
                         ['0xa9059cbb', '0x70a08231', '0x095ea7b3'])
        self.assertFalse(result['has_findings'])

    def test_known_distinct_signature_collision(self):
        result = tool.audit([fn('burn', 'uint256'),
                             fn('collate_propagate_storage', 'bytes16')])
        self.assertEqual(result['ambiguities'], [{
            'selector': '0x42966c68', 'kind': 'collision',
            'signatures': ['burn(uint256)', 'collate_propagate_storage(bytes16)'],
            'indices': [0, 1]}])
        self.assertTrue(result['has_findings'])

    def test_alias_duplicate_not_overload(self):
        result = tool.audit([fn('f', 'uint'), fn('f', 'uint256'), fn('f', 'address')])
        self.assertEqual(len(result['ambiguities']), 1)
        self.assertEqual(result['ambiguities'][0]['kind'], 'duplicate')
        self.assertEqual(result['ambiguities'][0]['indices'], [0, 1])

    def test_unsupported_input_retains_supported_rows(self):
        result = tool.audit([fn('f', 'bytes[]'), fn('balanceOf', 'address')])
        self.assertIsNone(result['functions'][0]['selector'])
        self.assertEqual(result['functions'][1]['selector'], '0x70a08231')
        self.assertTrue(result['has_findings'])

    def test_unsupported_output_keeps_selector(self):
        result = tool.audit([fn('f', outputs=[{'type': 'bytes[]'}])])
        self.assertTrue(result['functions'][0]['inputs_supported'])
        self.assertFalse(result['functions'][0]['outputs_supported'])
        self.assertIsNotNone(result['functions'][0]['selector'])

    def test_nested_tuple_and_nonfunction(self):
        result = tool.audit([{'type': 'event', 'name': 'Changed'},
            {'type': 'function', 'name': 'f', 'inputs': [
                {'type': 'tuple', 'components': [{'type': 'uint'}, {'type': 'address'}]}]}])
        self.assertEqual(result['function_count'], 1)
        self.assertEqual(result['functions'][0]['signature'], 'f((uint256,address))')
        self.assertEqual(result['functions'][0]['index'], 1)

    def test_cli_status_and_clean_invalid_json(self):
        with tempfile.TemporaryDirectory(dir='test/scratch') as tmp:
            path = Path(tmp) / 'abi.json'
            for value, status in [([fn('f')], 0), ([fn('f'), fn('f')], 1), ({}, 2)]:
                path.write_text(json.dumps(value))
                out, err = io.StringIO(), io.StringIO()
                with patch('sys.argv', ['audit', '--abi', str(path)]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    self.assertEqual(tool.main(), status)
                if status == 2:
                    self.assertEqual(out.getvalue(), '')
                    self.assertTrue(err.getvalue().startswith('error:'))
                else:
                    self.assertEqual(json.loads(out.getvalue())['has_findings'], status == 1)
            path.write_text('[{"type":"function","name":"f","name":"g"}]')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON field'):
                tool.read_abi(path)

    def test_schema_and_file_budgets(self):
        p = {'type': 'uint'}
        for _ in range(33):
            p = {'type': 'tuple', 'components': [p]}
        result = tool.audit([{'type': 'function', 'name': 'f', 'inputs': [p]}])
        self.assertIn('32 levels', result['functions'][0]['error'])
        with tempfile.TemporaryDirectory(dir='test/scratch') as tmp:
            path = Path(tmp) / 'abi.json'
            path.write_bytes(b' ' * (tool.abi.MAX_ABI_BYTES + 1))
            with self.assertRaisesRegex(ValueError, '1 MiB'):
                tool.read_abi(path)


if __name__ == '__main__':
    unittest.main()
