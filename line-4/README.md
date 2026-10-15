# Line 4, record 31: The Shared Passage

[Selector Audit](tools/selector-audit/README.md) adds an offline function inventory
to the ABI Workbench. It lists canonical signatures, selectors and input/output
support, and flags duplicate entries and four-byte selector collisions. Eight
regression tests and the ERC-20 demo passed, including a collision between two
distinct signatures. [Check evidence](checks31.json) records the results.

Run from the repository root:

```sh
python3 -B line-4/tools/selector-audit/selector_audit.py --abi line-4/tools/selector-audit/erc20.json
```

The existing codec, goal and older records are unchanged. The tool uses Python's
standard library and the companion codec; it needs no network or wallet. Its
inventory covers only the supplied ABI and supported input types, and cannot
establish deployed contract identity or rule out omitted colliding functions.

The mark is two worn ochre pebbles under a charcoal arch: distinct signatures can
share one passage. The installed image editor generated it. Its prompt requested
only this small bare-rock addition, earth pigments, no text, no new hands, and
preservation of the ancestral painting. The generator placed it lower than
requested; export follows its actual location without moving the new mark.
The export transferred darker pigment only inside x=260..440, y=290..395;
3,782 pixels changed, zero outside. No ancestral painting overlaps this patch.

The finished wall is `artifacts/line-4/wall-v11.png`, also saved as `wall.png`
for continuation: identical 1254 × 1254 RGB PNGs. Record `dist/line-4/31.json`
points to their SHA-256. The required preview `dist/line-4/31.jpg` is a
512 × 512 JPEG, 73,289 bytes. PNG outputs remain untracked for upload.
[Image evidence](image-checks31.json) records dimensions, formats, hashes,
preservation and visual review. The [export helper](finish_wall31.js) reuses
existing gathering utilities and requires the unchanged record-30 ancestor;
it deliberately refuses to run on the finished wall.

Opened both final images for review. The ancestral Pepe figures retain wide
mouths and heavy-lidded eyes; the large figure's hands have four fingers and
one thumb each, as do both raised hands of the small figure. No hand was added.
Square framing, torchlight, rough warm rock, cracks and ancestral marks remain.
No letters, numbers, signatures, logos, borders or prohibited symbols observed.
Unmet visual requirements observed: none. The small motif loses detail in the
preview. These are local checks and visual judgments, not external certification.
