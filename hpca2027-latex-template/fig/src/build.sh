#!/bin/bash
# NOTE: once fourshadow_uarch_v2.drawio is edited by hand in draw.io, the .drawio is the master copy: export the PDF from draw.io and do NOT rerun make_drawio.py (or this script) over it.
# Regenerate Figure 3 v2 end to end: spec -> prototype HTML + .drawio -> renders (headless Chrome; the
# .drawio through draw.io's own viewer script, fetched from viewer.diagrams.net) -> checks -> PDF.
# usage: build.sh [scratch dir for render byproducts, default ./build (gitignored)] [output PDF, default ../fourshadow_uarch_v2.pdf]
# Writes here (fig/src): fig3_v2_prototype.html, fourshadow_uarch_v2.drawio, fig3_v2_viewer.html
# Writes the PDF to:     ../fourshadow_uarch_v2.pdf (the file the paper includes), or the second argument
# Writes to the scratch dir only: proto.png (prototype), viewer.png (draw.io render), viewer_vs_prototype.png,
#              viewer.pdf (Chrome print before cropping), verify.txt, the render JSON/SVG files
set -e
D=$(cd "$(dirname "$0")" && pwd)
W=$(mkdir -p "${1:-$D/build}" && cd "${1:-$D/build}" && pwd)
OUT=${2:-$D/../fourshadow_uarch_v2.pdf}
OLD=$D/../fourshadow_uarch.pdf
cd /
python3 "$D/make_prototype.py"
python3 "$D/make_drawio.py"
CDP_UDD_ROOT=$W timeout 150 node "$D/cdp_render.mjs" "$D/fig3_v2_prototype.html" "$W/proto" --scale 2 >/dev/null
CDP_UDD_ROOT=$W timeout 150 node "$D/cdp_render.mjs" "$D/fig3_v2_viewer.html" "$W/viewer" --pdf --scale 2 >/dev/null
python3 "$D/verify_fig3.py" "$W/viewer" "$W/proto" "$OLD" | tee "$W/verify.txt"
python3 "$D/crop_pdf.py" "$W/viewer.pdf" "$OUT"
pdfinfo "$OUT" | grep -E 'Pages|Page size'
