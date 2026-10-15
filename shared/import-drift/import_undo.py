#!/usr/bin/env python3
"""Prepare a schema-checked reverse patch for a saved import snapshot."""
import argparse
import json
import sys

import drift
import undo


def reverse(baseline, forward):
    # Validate the complete plan before relying on any of its schema fields.
    result = undo.reverse(baseline, forward)
    if forward['keys'] != ['module'] or set(forward['header']) != set(drift.FIELDS):
        raise ValueError('requires import-drift/v1 columns keyed only by module')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('baseline', help='original workspace import snapshot CSV')
    parser.add_argument('forward_plan', help='reviewed csv-patch/v1 JSON')
    args = parser.parse_args(argv)
    try:
        patch = undo.patch
        forward = json.loads(patch.read_local(args.forward_plan, patch.MAX_PLAN_BYTES),
                             object_pairs_hook=patch.unique_object)
        text = json.dumps(reverse(args.baseline, forward), ensure_ascii=True, indent=2) + '\n'
        if len(text.encode()) > patch.MAX_PLAN_BYTES:
            raise ValueError('serialized undo plan exceeds byte limit')
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=True), file=sys.stderr)
        return 2
    sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
