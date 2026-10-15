# CSV Checked Undo

Prepare a reverse `csv-patch/v1` plan for a fully validated forward patch.
It reverses additions, removals and edits, including composite keys. A worker
can keep the original CSV and both reviewed plans, then restore the original
keyed values if the forward result is still byte-identical. Python 3.9+ and
only its standard library are needed; keep the sibling `csv-patch/patch.py`.

From the repository root, this one command prints a working reverse plan for
the inherited inventory example:

```sh
python3 -B line-2/tools/csv-undo/undo.py line-2/tools/csv-reconcile/demo-before.csv line-2/tools/csv-patch/demo-plan.json
```

Exit 0 means a complete plan was emitted on stdout; exit 2 means invalid
input or an I/O error, with a JSON error on stderr and no partial plan.
No source CSV is written. The output uses ASCII JSON escaping, preserving
Unicode values and making control characters inert in terminal output.

To try a complete round trip (the redirects below create scratch files):

```sh
mkdir -p test/scratch
python3 -B line-2/tools/csv-undo/undo.py line-2/tools/csv-reconcile/demo-before.csv line-2/tools/csv-patch/demo-plan.json > test/scratch/undo31.json
python3 -B line-2/tools/csv-patch/patch.py apply line-2/tools/csv-reconcile/demo-before.csv line-2/tools/csv-patch/demo-plan.json > test/scratch/applied31.csv
python3 -B line-2/tools/csv-patch/patch.py inspect test/scratch/applied31.csv test/scratch/undo31.json
python3 -B line-2/tools/csv-patch/patch.py apply test/scratch/applied31.csv test/scratch/undo31.json > test/scratch/restored31.csv
```

Review the reverse plan before applying it. Never redirect output onto an
input file: shells truncate it before the command can validate it. Use a new
output path. Undo expects the exact bytes emitted by the forward patch engine,
not the target CSV used to create the forward plan (which may have different
ordering or quoting). Even newline-only edits after application cause refusal.

## What happened when tried

Nine new behavioral tests and all eleven existing patch tests passed on
Python 3.12.3. The inventory round trip restored all three original keyed
records: removed chalk, restored flint, and changed lamp quantity back to 1.
Tests cover mixed operations, empty/no-change tables, composite keys,
multiline Unicode, original BOM/CRLF/quoting, reordered columns, altered plans,
stale originals, changed current bytes, duplicate JSON members, malformed
JSON and workspace containment. Run:

```sh
python3 -B -m unittest discover -s line-2/tools/csv-undo -v
```

## Limits

Restoration is **semantic, not byte-for-byte**: the existing engine sorts rows
by key, uses the original header order, emits LF newlines and normalizes CSV
quoting, dropping a BOM. The reverse result digest therefore hashes the
canonical original table, not necessarily the original file. Empty or duplicate
keys and schema changes are refused by the inherited parser. Limits are
16 MiB / 100,000 data rows per CSV and 64 MiB per serialized plan. Inputs and
outputs reside in memory. Paths must resolve inside the current workspace.
Keep files stable across reads; digest checks are not filesystem locking.
The CLI bounds serialized output; library callers must bound their own
serialization. Digests detect mismatches, not authorship or approval.

No network, coin, wallet, secret, environment, signing, transaction or posting
operation is involved. This general offline file workflow needs no asset.
