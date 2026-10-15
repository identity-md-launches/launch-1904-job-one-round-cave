# Endpoint Doctor

Get one readable HTTP diagnosis instead of choosing and invoking four separate
evidence interpreters. Uses the delivered Probe Triage, Redirect Lens, Retry
Lens and Cache Lens, and optionally Endpoint/Deadline Sentry for a bounded
live capture. Python 3.10+ standard library only; no installation or account.
Keep the sibling tool folders with this one. Run from the repository root.

One command shows it working **offline on a retained real swarm observation**:

```sh
python3 -B line-1/tools/endpoint-doctor/endpoint_doctor.py --report line-1/tools/endpoint-doctor/observed-live.json
```

It prints `CHECKS PASSED`, the original capture time, zero redirects, explicit
Retry-After absence, and the private-cache freshness verdict **at receipt**.
This is historical evidence, not a new health check. `--report` performs no
network or subprocess work and writes no file. Its strict loader refuses
duplicate JSON keys, non-finite numbers, inputs over 1 MiB and paths resolving
outside the current workspace. There is no stdin or home-directory expansion.

For an explicit new anonymous public GET:

```sh
python3 -B line-1/tools/endpoint-doctor/endpoint_doctor.py --url https://api.imd.fun/launches --expect-json --deadline 6
```

The default is **one GET, no redirect following, no retries**, at most 1 MiB
of response body, expected status 200. The inherited User-Agent is
`Pepeolithic-Endpoint-Sentry/1.0 (public read-only diagnostics)`.
`--deadline` covers DNS, TLS, headers and body capture using a killed/reaped
worker. It bounds the network worker, not startup, report interpretation or
printing. `--max-redirects 1..10` explicitly permits additional GETs along the
redirect route; these are not retries. `--max-bytes 1..16777216`, `--status
100..599` and `--deadline 0<seconds<=120` configure capture limits.
Probe options with `--report` are rejected rather than silently ignored.
Only public, non-secret HTTPS URLs should be supplied; the inherited HTTP probe
does not filter DNS answers and is not an SSRF sandbox. No credentials are
accepted in URL userinfo. Responses and redirects can expose query strings
in evidence, so do not provide secret-bearing URLs.

Use `--format json` for the complete source and separate lens results. Every
lens evidence pointer refers to the original document inside `source`, e.g.
`/probe/hops/0` resolves relative to `source`, **not** the Doctor wrapper.
`observed_ok` preserves the probe's original expectations; the Doctor does not
change them. Text output escapes saved strings, including terminal controls.
For 429 findings its integrated guidance points to the Retry section, replacing
the older Triage helper's assumption that no Retry-After evidence was captured.

Supplemental sections distinguish `available`, `not_applicable` and
`unavailable`. A killed worker has no response to interpret; failed body
capture still permits redirect/header explanation but has no completed cache
capture. Legacy or malformed optional evidence remains visibly unavailable.
`analysis_complete` means no applicable lens rejected its input. It does **not**
mean that every lens knows an answer: `not_captured`, `freshness_unknown`,
unsupported retry values and warnings remain in the individual results and text.
Thus HTTP checks can pass while supplemental analysis is incomplete or unknown.

Exit status is 0 for a valid passing observation, 1 for a valid failing
observation, and 2 for invalid core evidence, arguments, file or dependency
errors. `--require-complete` also returns 1 when a supplemental lens rejects
evidence; it does not reject every supported-but-unknown verdict.
There is no partial result on core validation failure.

Cache and retry calculations default to the captured header-receipt time.
To age the saved real observation explicitly, without waiting or requesting:

```sh
python3 -B line-1/tools/endpoint-doctor/endpoint_doctor.py --report line-1/tools/endpoint-doctor/observed-live.json --at 2026-10-16T00:00:00Z
```

The cache becomes `stale`; `observed_ok` stays true because it describes the
original observation. `--shared` selects shared-cache semantics. An invalid
explicit timestamp is refused before live capture. An evaluation before
receipt remains unsupported/unknown in the relevant lens. These calculations
grant neither cache reuse nor permission to retry. There is no scheduling,
automatic follow-up, TLS-only probe, repair, posting or transaction submission.

## What happened when tried

On 2026-10-15 at 23:02:23 UTC the live command against
`https://api.imd.fun/launches` returned 200, strict JSON, 126,215 body bytes,
zero redirects and no Retry-After field. The six-second watchdog completed in
361.670 ms; Endpoint Sentry measured 268.637 ms. All four interpreters ran.
Cache-Control was `public, max-age=10`; the cache verdict was within lifetime
at receipt, not now. [observed-live.json](observed-live.json) is the body-free
raw capture; [observed-analysis.json](observed-analysis.json) reproduces the
combined JSON. No real rate-limit, redirect or timeout was provoked.

Nineteen offline integration tests passed on Python 3.12.3. They exercise real
saved evidence, synthetic 429 hints, watchdog failures, rejected body capture,
missing legacy metadata, malformed optional evidence, independent exit gates,
typed core contradictions, terminal escaping, loader limits, fixed live command
construction, and isolated subprocess invocation. Run:

```sh
python3 -B -m unittest discover -s line-1/tools/endpoint-doctor -v
```

Saved reports remain unauthenticated. The inherited lenses validate relevant
subsets, not a complete producer schema. A successful observation establishes
neither continuous availability nor a root cause. Lens limits still apply:
Retry Lens uses local recorded clocks and IMF-fixdate only; Cache Lens does
not evaluate request directives, authorization or complete reuse policy;
Redirect Lens recognizes exact URL loops only. Use TLS Route separately when
you need independent DNS/TCP/TLS evidence. This tool needs no coin or payment.
