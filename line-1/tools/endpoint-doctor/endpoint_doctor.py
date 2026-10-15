#!/usr/bin/env python3
"""One readable diagnosis from bounded Endpoint Sentry evidence. No retries."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


def sibling(folder, filename):
    """Load only the fixed, delivered sibling tools, never user-specified code."""
    path = Path(__file__).resolve().parent.parent / folder / filename
    if not path.resolve().is_relative_to(Path.cwd().resolve()):
        raise ValueError('run from the workspace containing the delivered tools')
    spec = importlib.util.spec_from_file_location('doctor_' + folder.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dependencies():
    return {
        'triage': sibling('probe-triage', 'probe_triage.py'),
        'redirect': sibling('redirect-lens', 'redirect_lens.py'),
        'retry': sibling('retry-lens', 'retry_lens.py'),
        'cache': sibling('cache-lens', 'cache_lens.py'),
    }


def diagnose(source, modules, at=None, shared=False):
    """Keep each lens's evidence and failures separate from observed HTTP health."""
    triage = modules['triage'].triage(source)
    if at is not None:
        # Invalid explicit evaluation time is a caller error, not missing evidence.
        modules['retry'].timestamp(at)
    probe = source['probe'] if source.get('schema') == 'deadline-sentry/v1' and 'probe' in source else source
    completed_worker = probe.get('schema') == 'endpoint-sentry/v1'
    # The older triage helper predates Retry-After capture. Its 429 guidance
    # assumes absence of evidence; this combined view has a dedicated Retry lens.
    for finding in triage['findings']:
        if finding['code'] == 'http_status' and finding['observation'].startswith('HTTP 429 '):
            finding['next_step'] = ('Stop repeated probing and review published rate limits. '
                                    'Consult the Retry section for captured hints and unknowns; '
                                    'no hint grants permission to retry.')
    sections = {'triage': {'state': 'available', 'result': triage}}
    for name, analyze in (
        ('redirect', lambda: modules['redirect'].analyze(source)),
        ('retry', lambda: modules['retry'].analyze(source, at)),
        ('cache', lambda: modules['cache'].inspect(source, shared, at)),
    ):
        if not completed_worker:
            sections[name] = {'state': 'not_applicable',
                              'reason': 'Watchdog returned no completed worker report.'}
            continue
        if name == 'cache' and (probe.get('error') or not probe.get('final_url')):
            sections[name] = {'state': 'not_applicable',
                              'reason': 'No complete terminal HTTP response was captured.'}
            continue
        try:
            sections[name] = {'state': 'available', 'result': analyze()}
        except (ValueError, TypeError, KeyError, IndexError, AttributeError,
                OverflowError, RecursionError):
            # Do not turn missing/invalid supplemental evidence into a health pass.
            sections[name] = {'state': 'unavailable',
                              'reason': 'This lens rejected missing, invalid or unsupported evidence; '
                                        'inspect the original report with the individual lens.'}
    return {
        'schema': 'endpoint-doctor/v1',
        'observed_ok': triage['observed_ok'],
        'analysis_complete': all(s['state'] != 'unavailable' for s in sections.values()),
        'checked_at': probe.get('checked_at'),
        'evaluation_basis': 'explicit_time' if at is not None else 'recorded_header_receipt',
        'evaluation_time': at,
        'sections': sections,
        'source': source,
        'limits': [
            'Observed health covers only the captured probe and its requested checks.',
            'Supplemental lens availability is separate from observed HTTP health.',
            'Default cache/retry arithmetic uses historical header receipt, not the current time.',
            'Available means the lens ran, not that all evidence is known or authenticated.',
            'No retry, wait, TLS-only follow-up, repair or conditional request is performed.',
            'Saved evidence is unauthenticated; lens evidence pointers address source, not this wrapper.',
        ],
    }


def render(result):
    """Plain text; escape all saved strings to prevent terminal control injection."""
    quote = lambda value: json.dumps(value, ensure_ascii=True, allow_nan=False)
    sections = result['sections']
    lines = ['Endpoint Doctor: ' + ('CHECKS PASSED' if result['observed_ok'] else 'NEEDS ATTENTION'),
             'Captured at: ' + quote(result['checked_at']),
             'Supplemental lenses: ' + ('all applicable lenses ran' if result['analysis_complete'] else 'INCOMPLETE'),
             'Time basis: ' + result['evaluation_basis'] + ' (never assumed current health)']
    for finding in sections['triage']['result']['findings']:
        lines += ['Finding ' + quote(finding['code']) + ' at ' + quote(finding['evidence']),
                  '  ' + quote(finding['observation']), '  Next: ' + quote(finding['next_step'])]
    for name in ('redirect', 'retry', 'cache'):
        section = sections[name]
        if section['state'] != 'available':
            lines.append(name.title() + ': ' + section['state'] + ' - ' + section['reason'])
            continue
        value = section['result']
        if name == 'redirect':
            lines.append('Redirect: {} redirects, {} origin changes; {}'.format(
                value['redirects'], value['origin_changes'], value['outcome']))
            for finding in value['findings']:
                lines.append('  ' + quote(finding['observation']) + ' at ' + quote(finding['evidence']))
        elif name == 'retry':
            if not value['responses']:
                lines.append('Retry: no response headers captured')
            for response in value['responses']:
                text = 'Retry: HTTP {} at {}: {}'.format(
                    response['status'], quote(response['evidence']), response['outcome'])
                if 'remaining_seconds' in response:
                    text += '; {} seconds remaining at {}'.format(
                        response['remaining_seconds'], quote(response['evaluated_at']))
                lines.append(text)
        else:
            lines.append('Cache: {} ({}) at {}'.format(
                value['verdict'], value['cache_type'], quote(value['evaluated_at'])))
            for warning in value['warnings']:
                lines.append('  Warning: ' + quote(warning))
    lines += ['Scope: one captured observation; no availability or root-cause guarantee.',
              'Cache/retry metadata grants no permission to reuse or retry.',
              'Use --format json for the full source, lens results and evidence pointers.']
    return '\n'.join(lines)


def live(args):
    sentry = sibling('endpoint-sentry', 'sentry.py')
    sentry.https_url(args.url)
    watchdog = sibling('deadline-sentry', 'deadline_sentry.py')
    path = Path(sentry.__file__).resolve()
    command = [sys.executable, '-I', '-B', str(path), args.url,
               '--timeout', str(args.deadline), '--max-bytes', str(args.max_bytes),
               '--max-redirects', str(args.max_redirects), '--status', str(args.status)]
    if args.expect_json:
        command.append('--json')
    started = time.monotonic()
    report, code = watchdog.supervise(command, args.deadline)
    if code == 2:
        raise ValueError('probe arguments were refused')
    report.update(schema='deadline-sentry/v1', deadline_seconds=args.deadline,
                  elapsed_ms=round((time.monotonic() - started) * 1000, 3))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--report', help='saved report inside the current workspace; offline')
    source.add_argument('--url', help='explicit public HTTPS probe; default: no redirect following')
    parser.add_argument('--deadline', type=float, default=None, help='live watchdog seconds (default 6)')
    parser.add_argument('--max-bytes', type=int, default=None, help='live body-byte budget (default 1048576)')
    parser.add_argument('--max-redirects', type=int, default=None, help='live redirect budget (default 0)')
    parser.add_argument('--status', type=int, default=None, help='expected live terminal status (default 200)')
    parser.add_argument('--expect-json', action='store_true')
    parser.add_argument('--at', help='timezone-aware ISO evaluation time; default: recorded receipt')
    parser.add_argument('--shared', action='store_true', help='shared-cache interpretation')
    parser.add_argument('--format', choices=('text', 'json'), default='text')
    parser.add_argument('--require-complete', action='store_true',
                        help='also exit 1 if a supplemental lens rejects evidence')
    args = parser.parse_args(argv)
    try:
        if args.report and (any(getattr(args, key) is not None for key in
                              ('deadline', 'max_bytes', 'max_redirects', 'status')) or args.expect_json):
            raise ValueError('probe options require --url')
        args.deadline = 6.0 if args.deadline is None else args.deadline
        args.max_bytes = 1048576 if args.max_bytes is None else args.max_bytes
        args.max_redirects = 0 if args.max_redirects is None else args.max_redirects
        args.status = 200 if args.status is None else args.status
        if not math.isfinite(args.deadline) or not 0 < args.deadline <= 120:
            raise ValueError('deadline must be finite and in (0, 120]')
        if not 1 <= args.max_bytes <= 16777216 or not 0 <= args.max_redirects <= 10:
            raise ValueError('invalid byte or redirect budget')
        if not 100 <= args.status <= 599:
            raise ValueError('invalid expected status')
        modules = dependencies()
        if args.at is not None:
            modules['retry'].timestamp(args.at)  # Refuse before any network operation.
        original = modules['triage'].load_report(args.report) if args.report else live(args)
        result = diagnose(original, modules, args.at, args.shared)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        print(json.dumps({'schema': 'endpoint-doctor/v1',
                          'error': 'Invalid input or unavailable delivered dependency; '
                                   'use workspace paths and public HTTPS URLs.'}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False)
          if args.format == 'json' else render(result))
    return int(not result['observed_ok'] or
               (args.require_complete and not result['analysis_complete']))


if __name__ == '__main__':
    sys.exit(main())
