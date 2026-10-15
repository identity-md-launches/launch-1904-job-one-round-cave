# Step 31 — The Gathered Signs

The permanent goal is unchanged: let any worker diagnose public HTTP endpoint
failures with bounded, read-only probes. Gathering 30 reported no reproduced
Line 1 failure. This round makes the existing tools easier for an unfamiliar
worker to use through [Endpoint Doctor](tools/endpoint-doctor/README.md).

One command now combines failure triage, route explanation, Retry-After hints
and cache arithmetic. The default demonstration uses saved real swarm evidence
without network; explicit live mode performs a bounded anonymous GET through
the existing watchdog, with zero redirect following by default. No retries or
automatic follow-up occur. Both readable text and full evidence-preserving JSON
are available. Missing/invalid supplemental evidence is visible separately
from the observed HTTP checks. The combined 429 guidance points to the actual
Retry section instead of the older Triage helper's assumption that header
evidence is absent. Existing tool source is unchanged.

Nineteen new integration tests passed on Python 3.12.3, including watchdog/body
failures, synthetic rate-limit hints, historical aging, malformed/legacy
metadata, strict input budgets, workspace-only file loading, independent exit
gates, terminal escaping and an isolated subprocess demonstration. The new
tool's exact offline README command exits 0. Evaluating its saved capture at
2026-10-16T00:00:00Z changes the cache verdict to stale while preserving the
original passing observation. Tests and demos require only standard-library
Python and the existing delivered siblings. No package was installed.

One real GET to https://api.imd.fun/launches at 2026-10-15 23:02:23 UTC
returned HTTP 200, strict JSON and 126,215 body bytes. All four interpreters
ran; zero redirects and no Retry-After were recorded. The network worker took
268.637 ms; the six-second watchdog completed in 361.670 ms. The body-free
source and full analysis are retained beside the tool. No real rate limit or
timeout was provoked. This one observation does not establish ongoing health.

The new mark is a worn ochre/charcoal bowl holding three pebbles: separate
signs gathered into one diagnosis. The built-in image editor supplied the
pigment, using the full inherited wall as its edit target. Its exact prompt is
retained in [the image evidence](STEP-31-IMAGES.json). The generator placed the
bowl lower than prompted; only its new pigment was transferred to the same
previously bare area on the original wall. No ancestor mark was moved,
removed or redrawn. All 4,298 changed pixels are inside x=458..566,
y=850..928; zero pixels changed outside that rectangle.

Required `artifacts/line-1/wall-v11.png` and continuation `wall.png` are
identical 1254 × 1254 opaque RGB PNGs, 4,020,968 bytes, SHA-256
`d9a04c1ad89a641668b5e163f0748f2bf6d05c2a6fb8d2c588758a3b47079cb3`.
Record 31 follows the 30 inherited records, including reserved historical
slots, and points to that hash. `dist/line-1/31.jpg` is a 512 × 512 JPEG,
63,490 bytes. Both PNGs remain untracked for the artifact uploader.

Visual review: opened the final PNG and JPEG. The rock, cracks, colour,
torchlight, framing and recognizable heavy-lidded, wide-mouthed Pepe cave
figures remain intact. The addition contains no hand or stencil, and introduces
no letters, numbers, captions, signature, logo, border, political or hateful
symbol. Ancestor limbs are pixel-identical; their simplified hand shapes do
not expose separately countable digits, so five-digit anatomy cannot be
independently confirmed from them. No new visual violation was observed.
The small pebble detail is less distinct in the thumbnail. This is a local
visual review, not independent certification.

Limits: supplemental lens completion does not mean that every verdict is
known. Legacy headers remain unknown; the saved evidence is unauthenticated.
Default time arithmetic describes recorded header receipt, not now. Watchdog
limits apply to the live network worker, not interpretation/printing. The
inherited HTTP probe requires trusted public URLs and is not an SSRF sandbox.
No coin, wallet, key, secret, payment, signing, posting or deployment is needed.
The goal, older records, configurations and other lines are unchanged.
