#!/usr/bin/env python3
"""Inventory offline ABI function selectors and flag ambiguous dispatch."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

# Reuse this line's reviewed standard-library codec, never import the target ABI.
CODEC = Path(__file__).resolve().parents[1] / 'abi-workbench' / 'abi_workbench.py'
spec = importlib.util.spec_from_file_location('line4_abi_codec', CODEC)
abi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(abi)


def audit(entries):
    abi.validate_abi(entries)
    rows = []
    by_selector = {}
    for index, entry in enumerate(entries):
        if entry['type'] != 'function':
            continue
        row = {'index': index, 'name': entry['name']}
        try:
            signature = abi.input_signature(entry)
        except ValueError as exc:
            row.update(signature=None, selector=None, inputs_supported=False,
                       outputs_supported=False, error=str(exc))
            rows.append(row)
            continue
        selector = '0x' + abi.keccak256(signature.encode('ascii'))[:4].hex()
        row.update(signature=signature, selector=selector, inputs_supported=True)
        by_selector.setdefault(selector, []).append(row)
        try:
            outputs = entry.get('outputs', [])
            abi.check_type_tree(outputs)
            row['output_types'] = [abi.canonical(p) for p in outputs]
            row['outputs_supported'] = True
        except ValueError as exc:
            row.update(outputs_supported=False, output_error=str(exc))
        rows.append(row)
    ambiguities = []
    for selector, group in sorted(by_selector.items()):
        if len(group) > 1:
            signatures = sorted({row['signature'] for row in group})
            ambiguities.append({'selector': selector,
                                'kind': 'collision' if len(signatures) > 1 else 'duplicate',
                                'signatures': signatures,
                                'indices': [row['index'] for row in group]})
    findings = bool(ambiguities or any(not row['inputs_supported'] or
                                     not row['outputs_supported'] for row in rows))
    return {'function_count': len(rows), 'functions': rows,
            'ambiguities': ambiguities, 'has_findings': findings}


def read_abi(path):
    source = Path(path).resolve()
    if not source.is_relative_to(Path.cwd().resolve()):
        raise ValueError('ABI path must stay inside the current workspace')
    with source.open('rb') as stream:
        raw = stream.read(abi.MAX_ABI_BYTES + 1)
    if len(raw) > abi.MAX_ABI_BYTES:
        raise ValueError('ABI file exceeds the 1 MiB input limit')
    try:
        return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=abi.unique_object)
    except RecursionError as exc:
        raise ValueError('ABI JSON nesting is too deep') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--abi', required=True, help='workspace-contained JSON ABI')
    args = parser.parse_args()
    try:
        result = audit(read_abi(args.abi))
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['has_findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
