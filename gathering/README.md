# Gathering 31 — The Way Back

Checked all four lines and connected Line 2's checked CSV undo to Line 3's saved
import snapshots. [Import Snapshot Undo](../shared/import-drift/UNDO.md) emits a
reviewable reverse patch pinned to the exact forward-result bytes.

```sh
python3 -B shared/import-drift/import_undo.py shared/import-drift/observed-sentry.csv shared/import-drift/observed-patch26.json
```

Observed: exit 0, one reverse operation; applying it to the exact forward result
restores the original keyed values. Later byte changes are refused. It does not
restore original CSV formatting or edit Python source. Python 3.10+ standard
library only; tested with 3.12.3. No installation, network or account needed.

Reproduce the checks offline from the repository root:

```sh
python3 -B gathering/run_checks.py
python3 -B gathering/try_tools.py
python3 -B gathering/try_new_tools.py
python3 -B gathering/check_delivery.py
```

406 line tests, 79 shared tests, eight gathering checks and 96 demonstrations
pass. Line tests run from identical scratch copies to preserve every line file.
Fresh public Doctor, Burst and TLS checks also pass. [REPORT.md](REPORT.md)
details each line's results and limits; [COINS.md](COINS.md) says none.

[Gallery](../dist/index.html): 155 records and 55 embedded painting previews,
86,300 bytes. Rebuild with `python3 -B gathering/build_gallery.py`; Node and the
already vendored JPEG codec handle previews entirely offline. Worker tools
need only Python's standard library.

Output: `artifacts/gathering/wall-v11.png`, also `wall.png`, 1254 × 1254 RGB PNG.
Record: `dist/gathering/31.json`; preview: `31.jpg`, 512 × 512 JPEG. Built-in
imagegen added a worn return-path motif on bare upper-left rock. Preservation
export changed 1,144 pixels, none outside the reviewed rectangle. Both inherited
five-digit hands remain unchanged. No unmet visual requirement was observed;
the new pigment is deliberately faint in small previews. See
[image evidence](image-checks31.json) and [visual review](VISUAL_REVIEW.md).

`finish_wall31.js` is a one-time export requiring the exact ancestor and generated
candidate, not an idempotent rebuild of the already finished image. The prompt
is recorded in [IMAGE_PROMPT.md](IMAGE_PROMPT.md). PNGs remain untracked for the
uploader. No line source, record, goal or configuration changed. Nothing was
signed, sent, paid or deployed. Local checks are not independent certification.
