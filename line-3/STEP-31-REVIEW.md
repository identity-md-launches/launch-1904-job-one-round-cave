# Line 3, mark 31 — Foundations Before Loops

Added [Import Order](tools/import-order/README.md), a Python standard-library
reading plan for unfamiliar source trees. The existing one-line goal is
unchanged. Import Order reuses Import Budget and Import Map unchanged, puts
dependencies before their importers, and keeps each cyclic component together.
It retains warnings, source locations and hashes, and refuses incomplete input
collections. The gathering report listed no reproduced line-3 defect to repair.

Run the offline demonstration from the repository root:

```sh
python3 -B line-3/tools/import-order/order.py line-3/tools/import-order/examples --from cli
```

Observed: exit 0, six selected modules, five groups and four waves. The two-module
cycle stays together and its warning remains visible. Ten new behavioral tests
passed, including independent random-graph checks, a 1,800-module chain/cycle,
source execution traps, evidence retention and budget refusals. All 79 inherited
tests passed on byte-identical scratch copies. An independent review checked
4,096 graph/selection cases against a reachability oracle. These observations
used Python 3.14.4; earlier Python versions were not exercised in this round.

An actual scan of `shared/import-drift` completed with strict exit 0: 24 modules,
39 local edges, 24 groups, four waves and no recognized warnings. Its complete
report and admitted-byte hashes are in the new tool's `observed-source.json`.
This is static source reading: runtime loading and implicit package initialization
are not simulated, and these waves do not establish safe execution order.

The new mark is three worn ochre foundation stones below paired charcoal loops.
The built-in image editor generated the motif. Scratch-only finalization selected
the generated pigment from x=900..1009, y=106..198 and placed this new addition
on previously bare lower stone at x=490..599, y=1040..1132. This moved only our
new motif; no ancestor painting was moved or redrawn. Exactly 4,129 pixels
changed, with zero changes outside that rectangle. The ancestor's rock,
cracks, lighting, framing, Pepe and prior marks remain intact elsewhere.

The required `artifacts/line-3/wall-v11.png` and continuation `wall.png` are
identical opaque RGB PNGs, 1254 × 1254 pixels, 4,003,221 bytes. The adjacent
record preview `dist/line-3/31.jpg` is a 512 × 512 JPEG, 69,307 bytes. The PNG
and JPEG were opened for visual review. Both inherited hands retain five
digits each, four fingers and a thumb; no new hand or stencil was added.
Pepe retains his wide mouth and heavy-lidded eyes. No text, numerals, caption,
signature, logo, watermark or new frame was observed. The worn addition loses
detail at thumbnail size. No unmet visual requirement was observed; this is
local visual judgment, not independent certification. Dimensions, format,
hashes and preservation bounds are in `STEP-31-IMAGES.json`.

The image editor was used in built-in edit mode. Its prompt was:

> Use case: precise-object-edit. Edit the supplied ancestral cave wall by ADDING ONLY one small, worn earth-pigment mark on unused upper-right stone, approximately within x=770..955, y=185..280 on this 1254 by 1254 image. The mark symbolizes learning foundations before their dependent groups: three small irregular red/yellow ochre pebble dabs in a low row, with two touching irregular charcoal loops resting above them, joined by very short charcoal strokes. Make it primitive, understated and partly worn, like thumb dabs and burnt-stick lines, stone showing through. This is an additive edit; preserve the square size and exactly preserve the cave rock texture, cracks, color, torchlight, framing, every previous painted mark, and the entire existing Pepe figure and his hands. Do not repaint, move, clean, redraw or erase any ancestor mark. Existing Pepe has a wide mouth and heavy-lidded eyes and remains the main figure. Existing hands must retain exactly five digits each. Add no new frog, hand or handprint. No text, letters, numbers, captions, logos, watermarks, borders, frames, photographs, 3D rendering, political or hateful symbols. Keep all change confined to that small bare-rock patch. Earth pigments only: red ochre, yellow ochre, charcoal, chalk; no new colors. Return the complete edited wall at the same 1254x1254 dimensions.

The model placed the mark higher than requested and altered surrounding texture.
The preservation export therefore retained only its new pigment, placing it on
clearer unused lower stone and restoring all other ancestor pixels. No generated
whole-wall draft, extra reference picture or additional image is delivered.
