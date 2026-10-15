#!/usr/bin/env python3
"""Emit a reviewed reverse CSV patch, pinned to the forward result bytes."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

_spec = importlib.util.spec_from_file_location(
    'csv_undo_patch', Path(__file__).resolve().with_name('patch.py'))
patch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(patch)


def reverse(baseline, forward):
    """Validate forward completely; reverse operations toward canonical baseline."""
    result = patch.apply(baseline, forward)
    # A second baseline read must still match the reviewed original bytes.
    raw = patch.read_local(baseline, patch.MAX_BYTES)
    if patch.digest(raw) != forward['baseline_sha256']:
        raise patch.InputError('baseline changed while preparing undo')
    header, original = patch.parse_table(raw, forward['keys'])
    canonical = patch.encode_table(header, original)
    undo = {'format': 'csv-patch/v1', 'keys': list(forward['keys']),
            'header': list(header), 'baseline_sha256': patch.digest(result),
            'result_sha256': patch.digest(canonical),
            'operations': [{'before': copy.deepcopy(op['after']),
                            'after': copy.deepcopy(op['before'])}
                           for op in forward['operations']]}
    return undo


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', help='unchanged original CSV used for the forward plan')
    parser.add_argument('forward_plan', help='csv-patch/v1 JSON plan to validate and reverse')
    args = parser.parse_args(argv)
    try:
        forward = json.loads(patch.read_local(args.forward_plan, patch.MAX_PLAN_BYTES),
                             object_pairs_hook=patch.unique_object)
        output = json.dumps(reverse(args.baseline, forward), ensure_ascii=True, indent=2) + '\n'
        if len(output.encode('utf-8')) > patch.MAX_PLAN_BYTES:
            raise patch.InputError('serialized undo plan exceeds byte limit')
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
