# Gathering 31 image prompt and export

Mode: built-in imagegen, precise-object-edit. Input: the exact gathering wall
from painted record 30. Requested preservation of square size, warm rough rock,
cracks, torchlight, framing, all inherited marks, Pepe and every five-digit hand.

Prompt: Add only one very small worn charcoal-and-red-ochre motif on bare upper
left rock, centered near (345,175) in the 1254-pixel square: two curved parallel
trails of tiny ochre pebbles bending back toward each other, a return path for a
carefully reversible change. Hand-painted uneven earth pigments, stone visible.
No arrowheads, letters, numbers, writing, logos, watermark, border or new hands.

The generated candidate placed the motif slightly farther left. After viewing,
finish_wall31.js exported only darker new pigment within [245,130,390,225] onto
the exact ancestor pixels, leaving all outside pixels unchanged. The original
candidate was not retained as an extra image. Only the finished wall outputs and
the required numbered JPEG are delivered. Visual results/limits are recorded
in VISUAL_REVIEW.md and image-checks31.json.
