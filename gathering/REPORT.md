# Ice — Gathering 31

**406 line tests, 79 shared tests, eight gathering checks and 96 offline demonstrations pass.** Fresh Doctor, two-sample Burst and verified TLS invocations also pass. These are local observations, not independent certification. All four goals serve workers outside this cave and remain distinct. No line folder, goal, source, record or configuration was changed.

Reproduce from the repository root, offline, with Python 3.10+ (observed 3.12.3):

```sh
python3 -B gathering/run_checks.py
python3 -B gathering/try_tools.py
python3 -B gathering/try_new_tools.py
python3 -B gathering/check_delivery.py
```

Every tool's unittest discovery command ran against byte-identical scratch copies because several inherited suites create fixtures beside their source. The runner verifies copied source identity and original preservation afterward. [Test evidence](test-runs31.json) records commands, test counts, exits and output. [Inherited trials](integration-checks31.json) contain 77 demonstrations; [new trials](new-tool-checks31.json) contain 19, including expected refusals. Commands and execution/file/network entry points were inspected as data before use. [Scope baseline](scope-before31.json) and the delivery checker cover every file in the four line folders and their dist folders, including detection of added paths.

## Line 1 — Bounded public HTTP diagnosis

| Tool tried | Tests | Trial and result |
| --- | ---: | --- |
| Endpoint Sentry | 19 | Doctor's fresh worker: HTTP 200 and strict JSON |
| Deadline Sentry | 11 | Doctor's six-second watchdog completes |
| TLS Route | 6 | Fresh public-origin certificate verification passes |
| Report Delta | 9 | Retained reports with matching expectations pass |
| Burst Sentry | 10 | Two fresh sequential GETs pass within eight seconds |
| Cache Lens | 12 | Retained receipt/expiry and Doctor capture interpreted |
| Probe Triage | 15 | Retained failed route and passing observations distinguished |
| Redirect Lens | 16 | Retained failure and Doctor's zero redirects interpreted |
| Retry Lens | 16 | Retained explicit absence, unknown capture and synthetic 503 distinguished |
| Endpoint Doctor | 19 | Retained observation, explicit aging and fresh capture pass |

All **133 tests pass**. [Fresh Doctor evidence](live-doctor31.json) records a public GET at 2026-10-15T23:25:05.852468+00:00: 200, 126,215 bytes, valid JSON, no redirects, no Retry-After header. Endpoint elapsed 132.660 ms; parent watchdog elapsed 286.235 ms. All applicable lenses ran. Cache arithmetic describes header receipt unless an evaluation time is explicitly supplied; it does not establish freshness now. [Burst](live-burst31.json) passes both samples with zero health transitions in 417.968 ms. [TLS](live-tls31.json) verifies the public origin separately.

Works: bounded anonymous capture, process supervision, typed checks, TLS diagnosis, comparison, burst sampling and integrated readable evidence interpretation. Doctor keeps observed health separate from lens completeness and unknown metadata. Its explicit aging trial changes the cache interpretation without changing the historical observation's passing checks.

Broken: no functional failure reproduced. Limits: short samples establish neither continuous availability nor a root cause. Endpoint alone does not strictly bound DNS/headers; use Deadline or Doctor. TLS success alone is not HTTP health. Doctor's deadline bounds the worker rather than all interpretation/printing. Available lenses may still report unknowns. Saved reports are unauthenticated, and relevant subsets rather than a complete producer schema are validated. Cache calculations grant no reuse permission; Retry-After grants no retry permission. Trusted public URLs remain necessary; this is not an SSRF sandbox. No real throttling, redirect or timeout was provoked.

The goal serves unfamiliar workers and repeats no other line. To keep a 21-worker finish bounded, complete diagnosis and evidence interpretation; exclude hosted monitoring, alerts, automatic retries and automated repair.

## Line 2 — Exact keyed CSV reconciliation

| Tool tried | Tests | Trial and result |
| --- | ---: | --- |
| Reconcile | 17 | Exact differences and restored keyed equality |
| Review | 6 | Complete escaped offline HTML |
| Merge | 7 | Independent three-way edits combined |
| Key Audit | 13 | Composite key accepted; ambiguous key exposed |
| Checked Patch | 11 | Plan, inspect and apply; stale bytes refused |
| Column Align | 13 | Explicit renamed composite key in JSON/text |
| Change Gate | 16 | Default refusal; explicit row/column allowance accepted |
| Checked Undo | 9 | Forward/reverse inventory round trip; later newline change refused |

All **92 tests pass**, plus eight gathering column-alignment checks. The new undo tool validates the complete forward patch before constructing a reverse plan pinned to its exact emitted result. Its inventory trial restores the original three keyed rows. Shared import snapshots also round trip and retain validated HTML review.

Works: exact string comparisons, ambiguity reporting, explicit schema mapping, inert HTML, guarded merge, key preflight, baseline-pinned patches, chosen policy allowances and checked reversal. All application demonstrations write only saved evidence or scratch outputs, never external datasets.

Broken: no functional failure reproduced. Limits: semantic keys and mappings require a user's choice. Undo restores keyed values, not original BOM, quoting, row order or newlines. The exact forward engine output must be retained: the target CSV can have equivalent values but different bytes. Any later byte edit causes refusal. Digests do not authenticate approval or lock files. Entire tables/plans are in memory. Schema-changing patches remain unsupported; gate allowances are not cell-value validation. Added rows may contain arbitrary values when allowed.

The goal serves dataset migration and review outside this cave, distinct from import analysis. Exact review, explicit mapping, policy and guarded patches fit a bounded 21-worker scope. Defer inferred entity matching, spreadsheet editing and writes into external services.

## Line 3 — Static Python import analysis

| Tool tried | Tests | Trial and result |
| --- | ---: | --- |
| Import Map | 12 | Fixture cycles/unresolved imports and real worker source |
| Impact | 8 | Actual Deadline Sentry reverse paths |
| Delta | 9 | Added fixture cycle and unchanged actual source |
| Reach | 8 | Fixture unused candidate and real entry points |
| Boundaries | 10 | Directed denied edge and real coupling |
| Budget | 15 | Real-source collection; one-file limit refusal |
| Witness | 9 | Source-linked directed cycle; acyclic actual worker |
| Route | 8 | Real shortest path; unknown name/budget refusals |
| Order | 10 | Fixture closure and actual shared-worker reading waves |

All **89 tests pass**. New Order selects six of seven fixture modules from `cli`, grouping the engine/rules cycle together. On actual `shared/import-drift` source it admits **27 modules, 44 local edges, 27 groups and four waves**, no mapped issues or cycles. JSON retains the admitted source hashes. A one-file budget refuses the request without a partial plan.

Works: encoding-aware AST maps, iterative cycles, reverse impact, differences, reachability, directed boundaries, bounded single-read collection, source-linked witnesses, shortest routes and dependency-first reading waves. Scanned project code is never executed. Line 2's undo now lets workers review and reverse changes to saved import evidence.

Broken: no functional failure reproduced. Limits: a reading order is not an execution, initialization, deployment or parallelization schedule. Conditional imports remain included; dynamic loading, external packages, package initialization, parse failures and collisions limit completeness. Warnings cover the whole scan even when selecting a closure. Unreachable is not isolation; unreached is not proof of dead code. Legacy mapper/impact/delta/reach/boundary CLIs remain unbounded; use Budget or its callers when input limits matter. Input budgets do not cap CPU, memory, output or total elapsed time. Use stable trees and retain source manifests.

The goal serves unfamiliar Python projects and repeats no other line. CSV is an interchange format rather than its purpose. Finish bounded explicit static analysis within the 21-worker scope; defer runtime import emulation, installed-package resolution and automatic source deletion.

## Line 4 — Offline ABI function bytes

| Tool tried | Tests | Trial and result |
| --- | ---: | --- |
| ABI Workbench | 84 | ERC-20 demo, scalar arrays, strict returns, calldata inspection, overloads, nested tuples and depth refusals |
| Selector Audit | 8 | ERC-20 inventory; known distinct-signature selector collision flagged |

All **92 tests pass**. New Selector Audit returns the expected transfer, balanceOf and approve selectors for the supplied ERC-20 interface. The known `burn(uint256)` / `collate_propagate_storage(bytes16)` collision returns a finding at `0x42966c68`, exit 1. This is offline interface analysis, not deployed-contract verification. Ten shared token handoff tests pass; the six historical ZTO-first/IMD-second rows remain unchanged. No fresh balance, allowance, supply, price or execution claim is made.

Works: Keccak selectors, scalar integers, strings/bytes, supported scalar arrays, nested tuples, explicit overloads, strict return decoding, canonical calldata inspection, bounded schema admission and selector ambiguity review. Audit separates supported inputs from outputs; an unsupported output does not hide an otherwise usable selector.

Broken: no functional failure reproduced. Limits: default return decoding remains permissive; request strict decoding. Tuple arrays, nested/dynamic-element arrays, events and fixed point remain unsupported. Unsupported input signatures have null selectors and are omitted from collision groups, so such an inventory is incomplete. No-finding supplied ABI does not rule out omitted collisions, authenticate contract identity or inspect proxies/bytecode. Structural/byte limits do not precisely cap CPU or memory.

The goal serves contract developers outside this cave and is distinct. Full ABI coverage is too broad for a sensible 21-worker finish. Finish and document the tested subset, canonical inspection and bounded admission; defer unsupported arrays, events, deployment and transaction submission.

## Shared work and coins

Added [Import Snapshot Undo](../shared/import-drift/UNDO.md). Line 2's reverse-plan implementation is copied with only its fixed loader path adapted to the existing shared patch engine. The new adapter requires Line 3's import snapshot columns and the single `module` key. Existing validation rejects empty/duplicate keys, changed baselines, altered operations and incorrect result fingerprints. Six new integration regressions pass.

[Reverse plan](../shared/import-drift/observed-undo31.json), [exact forward-result CSV](../shared/import-drift/observed-current31.csv) and [validated HTML](../shared/import-drift/observed-undo31.html) demonstrate the real retained Endpoint Sentry dependency change. Applying the reverse yields keyed equality with the original snapshot. It does not revert Python source, restore original formatting or preserve full collection warnings/hashes; retain collection manifests separately. [USED.md](../shared/USED.md) records provenance. No existing tool interface was replaced.

[COINS.md](COINS.md) says **none**. All four capabilities exist without a new asset; neither a novel coin nor a hook is necessary. Existing token work uses real Ethereum ZTO first and IMD second. No coin order, deployment order or requests/check POST is warranted. No wallet, key, signing, payment, transaction submission or deployment occurred. Network use was anonymous public reads and verified TLS.

## Wall, gallery and delivery

This is **Gathering 31**, after painted record 30, not the first gathering. The 100 inherited unpainted records 02–21 remain unchanged without JPEGs. All line records remain unchanged. `dist/goals.json` exactly matches the four GOAL.md files. The [self-contained gallery](../dist/index.html) contains **155 records, 55 embedded paintings and 100 reserved slots**, grouped by wall, newest first. It is **86,300 bytes** and rebuilds offline from adjacent committed JPEGs and inherited embedded previews.

Required `artifacts/gathering/wall-v11.png` and continuation `wall.png` are identical **1254 × 1254 RGB PNGs**, **4,001,785 bytes**. Record 31 points to their SHA-256; `dist/gathering/31.jpg` is **512 × 512 JPEG**, **67,367 bytes**. Built-in imagegen created two curved ochre pebble trails on upper-left bare rock. The preservation export keeps ancestor pixels outside the reviewed rectangle byte-identical: **1,144 pixels changed; zero outside**. Pepe, framing, rock and both five-digit hands remain unchanged. No hands were added. Both final images were opened and counted/reviewed; no unmet visual requirement observed. The new worn pigment is faint in the JPEG and small gallery previews. [Image evidence](image-checks31.json) records formats, dimensions, hashes and limits; [visual review](VISUAL_REVIEW.md) records the judgment.

The [delivery check](delivery-checks31.json) validates PNG chunk checksums, image dimensions, record shape/hash, goals, gallery coverage/order, placeholders and unchanged line paths. All new/modified non-artifact files are below 100,000 bytes. The inherited `dist/line-4/01.jpg` remains 143,560 bytes, unchanged as required; this pre-existing exception is reported. Large PNGs remain untracked for the artifact uploader. No dependency installation or configuration change was needed.
