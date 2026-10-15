# Import Snapshot Undo

Prepare a reverse patch for a reviewed change to saved Python import snapshots.
This joins Line 2's checked CSV undo with Line 3's module-keyed import evidence.
It changes neither source code nor CSV files; all output goes to stdout.
Python 3.10+, standard library only. Keep this shared folder together.

One command works offline on the retained real Endpoint Sentry dependency change:

```sh
python3 -B shared/import-drift/import_undo.py shared/import-drift/observed-sentry.csv shared/import-drift/observed-patch26.json
```

Tried: exit 0, one reverse change removing the later test import from the saved
snapshot. The emitted plan matches [observed-undo31.json](observed-undo31.json).
The [HTML review](observed-undo31.html) validates that reverse plan against
[the exact forward-result CSV](observed-current31.csv). These are historical
observations, not a claim that today's source tree has been reverted.

Review and apply explicitly, using new output paths:

```sh
python3 -B shared/import-drift/patch_review.py shared/import-drift/observed-current31.csv shared/import-drift/observed-undo31.json
python3 -B shared/import-drift/patch.py inspect shared/import-drift/observed-current31.csv shared/import-drift/observed-undo31.json
python3 -B shared/import-drift/patch.py apply shared/import-drift/observed-current31.csv shared/import-drift/observed-undo31.json
```

Exit 0 emits a complete plan; exit 2 refuses invalid, inconsistent or stale
input without a partial plan. Only `import-drift/v1` columns keyed exactly by
`module` are accepted. Empty/duplicate module keys, malformed operations,
incorrect fingerprints and duplicate JSON members are refused. Generic CSV
users can use `undo.py` directly; the import-specific entry point adds schema
checks and never infers a key.

Restoration concerns exact keyed values, not original byte formatting. The
reverse baseline hashes the forward engine's emitted bytes, which can differ
from the target CSV's ordering, quoting or newlines. Later edits, even newline
changes, prevent application. Reverse output uses canonical sorted rows, LF and
normalized quoting. Original BOM/CRLF formatting is not restored. Keep both the
original CSV and forward plan, and review the reverse plan before application.
Never redirect stdout over an input file.

Snapshots omit source hashes and full scan evidence. Reverting a CSV does not
revert Python files or prove import safety. Preserve the bounded collection
manifests and warnings separately. Fingerprints are mismatch checks, not proof
of authorship, authorization or an atomic filesystem snapshot. Use stable files.
The inherited limits are 16 MiB and 100,000 rows per CSV and 64 MiB per plan;
processing and serialization are in memory, without a precise CPU/time bound.

Six integration regressions pass, including actual worker round trip, escaped
HTML, stale current bytes, altered plans, wrong schema/key and duplicate JSON:

```sh
python3 -B -m unittest discover -s shared/import-drift -p test_import_undo.py -v
```

No network, environment/configuration access, wallet, signing or sending occurs.
This capability requires no coin.
