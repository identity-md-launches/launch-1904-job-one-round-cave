"""Offline integration checks against the actual delivered diagnostic lenses."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import endpoint_doctor as doctor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class DoctorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = doctor.dependencies()
        cls.real = cls.modules['triage'].load_report(HERE / 'observed-live.json')

    def diagnose(self, report=None, **kwargs):
        return doctor.diagnose(copy.deepcopy(self.real if report is None else report),
                               self.modules, **kwargs)

    def call(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = doctor.main(args)
        return status, output.getvalue()

    def test_real_offline_lenses_agree_and_keep_source(self):
        original = copy.deepcopy(self.real)
        result = self.diagnose()
        self.assertTrue(result['observed_ok'])
        self.assertTrue(result['analysis_complete'])
        self.assertEqual(result['source'], original)
        self.assertEqual(self.real, original)
        self.assertEqual(result['sections']['retry']['result']['responses'][0]['outcome'], 'absent')
        self.assertEqual(result['sections']['redirect']['result']['redirects'], 0)
        self.assertEqual(result['sections']['cache']['result']['verdict'], 'within_freshness_lifetime')

    def test_later_time_ages_real_cache_without_changing_http_health(self):
        result = self.diagnose(at='2026-10-16T00:00:00Z')
        self.assertTrue(result['observed_ok'])
        self.assertEqual(result['sections']['cache']['result']['verdict'], 'stale')
        self.assertEqual(result['evaluation_basis'], 'explicit_time')

    def test_synthetic_429_combines_triage_and_retry_without_wait(self):
        source = copy.deepcopy(self.real)
        source['ok'] = source['probe']['ok'] = False
        hop = source['probe']['hops'][0]
        hop.update(status=429, retry_after=['60'])
        source['probe']['checks'] = [dict(name='status', ok=False, actual=429, expected=200)]
        result = self.diagnose(source)
        retry = result['sections']['retry']['result']['responses'][0]
        self.assertEqual(retry['outcome'], 'hint_pending')
        self.assertEqual(retry['remaining_seconds'], 60)
        self.assertEqual(result['sections']['triage']['result']['findings'][0]['code'], 'http_status')
        text = doctor.render(result)
        self.assertIn('NEEDS ATTENTION', text)
        self.assertIn('60 seconds remaining', text)
        self.assertIn('no permission', text)
        self.assertNotIn('contains no Retry-After evidence', text)

    def test_watchdog_failure_keeps_unknown_stage_and_no_fake_lenses(self):
        report = dict(schema='deadline-sentry/v1', ok=False,
                      error=dict(kind='deadline', message='worker killed'))
        result = self.diagnose(report)
        self.assertFalse(result['observed_ok'])
        self.assertTrue(result['analysis_complete'])
        for name in ('redirect', 'cache', 'retry'):
            self.assertEqual(result['sections'][name]['state'], 'not_applicable')
        self.assertIn('watchdog_deadline', doctor.render(result))

    def test_body_refusal_still_explains_captured_headers(self):
        source = copy.deepcopy(self.real)
        source['ok'] = source['probe']['ok'] = False
        source['probe'].pop('final_url')
        source['probe']['checks'] = []
        source['probe']['error'] = dict(kind='body', message='response exceeds byte limit')
        result = self.diagnose(source)
        self.assertEqual(result['sections']['cache']['state'], 'not_applicable')
        self.assertEqual(result['sections']['retry']['state'], 'available')
        self.assertEqual(result['sections']['redirect']['state'], 'available')

    def test_missing_legacy_headers_are_visible_not_invented(self):
        source = copy.deepcopy(self.real)
        source['probe']['hops'][0].pop('retry_after')
        source['probe']['hops'][0].pop('cache_headers')
        result = self.diagnose(source)
        self.assertTrue(result['observed_ok'])
        self.assertFalse(result['analysis_complete'])
        self.assertEqual(result['sections']['retry']['result']['responses'][0]['outcome'], 'not_captured')
        self.assertEqual(result['sections']['cache']['state'], 'unavailable')
        self.assertIn('INCOMPLETE', doctor.render(result))

    def test_unknown_retry_value_is_available_but_not_a_health_pass(self):
        source = copy.deepcopy(self.real)
        source['probe']['hops'][0]['retry_after'] = ['not a date']
        result = self.diagnose(source)
        self.assertTrue(result['analysis_complete'])
        self.assertIn('invalid_or_unsupported_value', doctor.render(result))

    def test_invalid_supplement_does_not_discard_good_triage(self):
        source = copy.deepcopy(self.real)
        source['probe']['hops'][0]['url'] = 'https://different.example/'
        result = self.diagnose(source)
        self.assertFalse(result['analysis_complete'])
        self.assertEqual(result['sections']['redirect']['state'], 'unavailable')
        self.assertEqual(result['sections']['triage']['state'], 'available')

    def test_wrapper_contradiction_is_invalid(self):
        source = copy.deepcopy(self.real)
        source['ok'] = False
        with self.assertRaises(ValueError):
            self.diagnose(source)

    def test_endpoint_extra_probe_field_cannot_override_evidence(self):
        source = copy.deepcopy(self.real['probe'])
        source['probe'] = 'unrelated extension'
        result = self.diagnose(source)
        self.assertTrue(result['analysis_complete'])
        self.assertEqual(result['checked_at'], source['checked_at'])

    def test_terminal_strings_are_escaped(self):
        result = self.diagnose()
        result['checked_at'] = '\x1b[2J\nforged success'
        output = doctor.render(result)
        self.assertNotIn('\x1b', output)
        self.assertIn('\\u001b[2J\\nforged success', output)

    def test_offline_cli_does_not_call_live_and_json_reproduces_source(self):
        with patch.object(doctor, 'live', side_effect=AssertionError('network called')):
            code, output = self.call(['--report', str(HERE / 'observed-live.json'), '--format', 'json'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)['source'], self.real)

    def test_invalid_live_time_and_budget_refused_before_network(self):
        with patch.object(doctor, 'live', side_effect=AssertionError('network called')):
            for options in (['--at', 'yesterday'], ['--deadline', 'nan'],
                            ['--max-bytes', '0'], ['--status', '0'], ['--max-redirects', '11']):
                with self.subTest(options=options):
                    code, output = self.call(['--url', 'https://api.imd.fun/launches'] + options)
                    self.assertEqual(code, 2)
                    self.assertIn('error', json.loads(output))

    def test_offline_live_flags_are_refused(self):
        code, _ = self.call(['--report', str(HERE / 'observed-live.json'), '--expect-json'])
        self.assertEqual(code, 2)

    def test_gate_exit_status_health_and_incomplete_are_independent(self):
        with patch.object(self.modules['triage'], 'load_report', return_value=self.real), \
                patch.object(doctor, 'dependencies', return_value=self.modules):
            self.assertEqual(self.call(['--report', 'unused'])[0], 0)
            incomplete = copy.deepcopy(self.real)
            incomplete['probe']['hops'][0].pop('cache_headers')
            with patch.object(self.modules['triage'], 'load_report', return_value=incomplete):
                self.assertEqual(self.call(['--report', 'unused'])[0], 0)
                self.assertEqual(self.call(['--report', 'unused', '--require-complete'])[0], 1)
            failed = dict(schema='deadline-sentry/v1', ok=False,
                          error=dict(kind='deadline', message='stalled'))
            with patch.object(self.modules['triage'], 'load_report', return_value=failed):
                self.assertEqual(self.call(['--report', 'unused'])[0], 1)

    def test_live_constructs_bounded_get_with_no_redirects_or_retries(self):
        argv = ['--url', 'https://api.imd.fun/launches', '--expect-json']
        watchdog = doctor.sibling('deadline-sentry', 'deadline_sentry.py')
        original_loader = doctor.sibling
        with patch.object(watchdog, 'supervise', return_value=(copy.deepcopy(self.real), 0)) as supervise:
            def loader(folder, filename):
                return watchdog if folder == 'deadline-sentry' else original_loader(folder, filename)
            with patch.object(doctor, 'sibling', side_effect=loader):
                code, _ = self.call(argv)
        self.assertEqual(code, 0)
        supervise.assert_called_once()
        command, deadline = supervise.call_args.args
        self.assertEqual(deadline, 6)
        self.assertEqual(command[command.index('--max-redirects') + 1], '0')
        self.assertIn('--json', command)
        self.assertEqual(command[1:3], ['-I', '-B'])

    def test_duplicate_json_and_oversize_input_refused(self):
        # Scratch stays outside the delivered source and is never a runtime dependency.
        scratch = ROOT / 'test' / 'scratch' / 'line1-31'
        scratch.mkdir(parents=True, exist_ok=True)
        path = scratch / 'invalid.json'
        for content in ('{"ok":true,"ok":false}', ' ' * (1048576 + 1),
                        '{"x":1e999}', '{"x":NaN}'):
            path.write_text(content)
            code, _ = self.call(['--report', str(path)])
            self.assertEqual(code, 2)

    def test_input_outside_workspace_rejected_before_open(self):
        with patch('pathlib.Path.open', side_effect=AssertionError('file opened')):
            with self.assertRaises(ValueError):
                self.modules['triage'].load_report(Path.cwd().resolve().parent / 'not-input.json')

    def test_isolated_subprocess_demo(self):
        child = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'endpoint_doctor.py'),
                                '--report', str(HERE / 'observed-live.json')],
                               capture_output=True, text=True, timeout=5, cwd=ROOT)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertIn('CHECKS PASSED', child.stdout)


if __name__ == '__main__':
    unittest.main()
