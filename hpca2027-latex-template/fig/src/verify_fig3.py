"""Checks for Figure 3 v2 (plan step 4).

usage: python3 verify_fig3.py <viewer-render prefix> <prototype-render prefix> <old figure PDF>
The prefixes are the outputs of cdp_render.mjs (<prefix>.png/.json/.svg).

 (a) labels: every printed line of the spec is rendered exactly as often as the spec prints it, and the
     word multiset equals the old Figure 3's (minus its occluded "(step_m/k, wid)" text)
 (b) prototype vs draw.io render: rect positions in the viewer SVG against the spec, and a pixel diff
 (c) no rendered text line leaves its box; no edge segment crosses a rendered text line
 (d) the .drawio parses as mxGraph XML; the viewer logged no error (read from the render JSON)
"""
import collections
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig3_spec as S  # noqa: E402

viewer, proto, oldpdf = sys.argv[1], sys.argv[2], sys.argv[3]
V = json.load(open(viewer + ".json"))
P = json.load(open(proto + ".json"))
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


# ---- (d) XML + viewer log ---------------------------------------------------------------------
here = os.path.dirname(os.path.abspath(__file__))
tree = ET.parse(os.path.join(here, "fourshadow_uarch_v2.drawio"))
diagrams = list(tree.getroot().iter("diagram"))
cells = list(tree.getroot().iter("mxCell"))
ids = [c.get("id") for c in cells]
check(len(diagrams) == 1 and diagrams[0].get("name") == "Figure 3 v2", "one diagram page named 'Figure 3 v2'")
check(len(ids) == len(set(ids)), f"{len(ids)} mxCell ids, all unique")
check(all(c.get("parent") in set(ids) for c in cells if c.get("id") not in ("0",)), "every cell's parent exists")
check(V["log"] == [], f"viewer console/log/exception entries: {len(V['log'])}")

# crossed port boxes: sp meta, matrix B, A, C only; matrix D is an arrow ending at the TCU box's right edge
ports = sorted(e["id"] for e in S.ELEMENTS if e["kind"] == "X")
check(ports == ["x_a", "x_b", "x_c", "x_meta"], f"crossed port boxes {ports} (no matrix D port)")
check(not any(i.startswith("x_d") for i in ids), "no matrix D port cell in the .drawio")
tcu = next(e for e in S.ELEMENTS if e["id"] == "tcu")
e_d = next(e for e in S.ELEMENTS if e["id"] == "e_d")
check(e_d["arrow"] and e_d["pts"][-1] == (tcu["x"] + tcu["w"], 201), "matrix D arrow ends at the TCU box's right edge")

# ---- (a) labels -------------------------------------------------------------------------------
expected = collections.Counter()
for _id, lab, fs in S.labels():
    for ln in lab.split("\n"):
        expected[ln] += 1
rendered = collections.Counter(t["text"] for t in V["texts"])
check(rendered == expected, f"rendered text lines == spec lines ({sum(expected.values())} lines)")
if rendered != expected:
    print("   missing:", dict(expected - rendered), " extra:", dict(rendered - expected))
proto_lines = collections.Counter(t["text"] for t in P["texts"])
check(proto_lines == expected, "prototype text lines == spec lines")

import subprocess  # noqa: E402
old = subprocess.run(["pdftotext", "-raw", oldpdf, "-"], capture_output=True, text=True).stdout
old = old.replace("(step_m/k, wid)", " ")
old_words = collections.Counter(w for w in re.split(r"\s+", old.replace("\xa0", " ")) if w)
# a label broken after "/" (WMMA/ + WGMMA?) is one word in the old figure
new_words = collections.Counter(w for _id, lab, _fs in S.labels() for w in lab.replace("/\n", "/").split())
# the four labels renamed to the paper's terms (2026-10-11); every other word stays the old figure's
RENAMES = [("A Buffer %d (Warp %d)" % (i, i), "A Buffer %d (Block %d)" % (i, i)) for i in range(4)] + [
    ("Shared B Row Buffer (Broadcast to all TCUs)", "Shared B Buffer (broadcast to all tensor blocks)"),
    ("WMMA/WGMMA? RS/SS?", "RS/SS?"),
    ("WMMA_SP?", "Sparse?"),
]
for o, n in RENAMES:
    o_w, n_w = collections.Counter(o.split()), collections.Counter(n.split())
    check(not (o_w - old_words) and not (n_w - new_words), f"renamed label '{o}' -> '{n}'")
    old_words = old_words - o_w + n_w
check(old_words == new_words, f"word multiset equals the old Figure 3 with the {len(RENAMES)} renames "
      f"({sum(old_words.values())} words)")
if old_words != new_words:
    print("   only old:", dict(old_words - new_words), " only new:", dict(new_words - old_words))

# ---- (b) rect positions + pixel diff ----------------------------------------------------------
svg = open(viewer + ".svg").read()
rects = [tuple(float(v) for v in m) for m in re.findall(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)]
worst = 0.0
missing = []
for e in S.ELEMENTS:
    if e["kind"] != "R":
        continue
    want = (e["x"], e["y"], e["w"], e["h"])
    best = min((max(abs(a - b) for a, b in zip(r, want)) for r in rects), default=99)
    worst = max(worst, best)
    if best > 0.6:
        missing.append((e["id"], want, best))
check(not missing, f"every spec box is drawn by the viewer at its position (worst deviation {worst:.2f} units)")
for m in missing:
    print("   ", m)

a = Image.open(viewer + ".png").convert("L")
b = Image.open(proto + ".png").convert("L")
check(a.size == b.size, f"render sizes equal {a.size}")
diff = ImageChops.difference(a, b)
hist = diff.histogram()
n = a.size[0] * a.size[1]
big = sum(hist[64:]) / n
mean = sum(i * c for i, c in enumerate(hist)) / n
print(f"     raw pixel diff: mean {mean:.2f}/255, pixels off by >= 64: {100 * big:.2f}% (glyph edges shifted <= 1 unit)")
import numpy as np  # noqa: E402
A, Bm = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
k = 2  # tolerate a shift of up to 2 px = 1 unit (draw.io label rounding)
pad = np.pad(Bm, k, mode="edge")
best = np.full(A.shape, 255, dtype=np.int16)
for dy in range(-k, k + 1):
    for dx in range(-k, k + 1):
        best = np.minimum(best, np.abs(A - pad[k + dy:k + dy + A.shape[0], k + dx:k + dx + A.shape[1]]))
tol = float((best >= 64).mean())
print(f"     shift-tolerant (<= 1 unit) diff: pixels off by >= 64: {100 * tol:.3f}%")
check(tol < 0.005, "prototype and draw.io render agree within a 1-unit shift (< 0.5% of pixels differ)")
# side-by-side / overlay image
side = Image.new("RGB", (a.size[0], a.size[1] * 3), "white")
side.paste(Image.open(proto + ".png").convert("RGB"), (0, 0))
side.paste(Image.open(viewer + ".png").convert("RGB"), (0, a.size[1]))
side.paste(Image.merge("RGB", (a, b, b)), (0, 2 * a.size[1]))
side.save(viewer + "_vs_prototype.png")

# ---- (c) text inside boxes, edges vs text ------------------------------------------------------
boxes = [e for e in S.ELEMENTS if e["kind"] in ("R", "T") and e.get("label")]
overflow = []
for t in V["texts"]:
    cx, cy = t["x"] + t["w"] / 2, t["y"] + t["h"] / 2
    own = [e for e in boxes if t["text"] in e["label"].split("\n")
           and e["x"] <= cx <= e["x"] + e["w"] and e["y"] <= cy <= e["y"] + e["h"]]
    if not own:
        overflow.append((t["text"], "no owner", round(cx, 1), round(cy, 1)))
        continue
    e = own[0]
    if e.get("vertical"):
        ok = t["x"] >= e["x"] - 0.5 and t["x"] + t["w"] <= e["x"] + e["w"] + 0.5 and t["y"] >= e["y"] - 0.5 \
            and t["y"] + t["h"] <= e["y"] + e["h"] + 0.5
    else:
        # draw.io places html labels up to +1 unit right of the box maths (centre +0.5, right +1)
        ok = t["x"] >= e["x"] - 0.5 and t["x"] + t["w"] <= e["x"] + e["w"] + 1.1
    if not ok:
        overflow.append((t["text"], e["id"], round(t["x"], 1), round(t["x"] + t["w"], 1), e["x"], e["x"] + e["w"]))
check(not overflow, "every rendered text line lies inside its box horizontally")
for o in overflow:
    print("   ", o)


def seg_hits_rect(p, q, r):
    (x0, y0), (x1, y1) = p, q
    rx0, ry0, rx1, ry1 = r
    # Liang-Barsky clip
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0 - rx0), (dx, rx1 - x0), (-dy, y0 - ry0), (dy, ry1 - y0)):
        if pp == 0:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t0 <= t1


segs = []
for e in S.ELEMENTS:
    if e["kind"] == "E":
        segs += [(e["id"], p, q) for p, q in zip(e["pts"], e["pts"][1:])]
hits = []
for t in V["texts"]:
    # glyph box: the line box minus its leading (1.2 em line, ~0.92 em of ink)
    fs = float(t["fontSize"].rstrip("px"))
    pad = 0.12 * fs
    r = (t["x"] + 0.5, t["y"] + pad, t["x"] + t["w"] - 0.5, t["y"] + t["h"] - pad)
    for sid, p, q in segs:
        if seg_hits_rect(p, q, r):
            hits.append((sid, t["text"]))
check(not hits, "no edge segment crosses a text line")
for h in hits:
    print("   ", h)

# font sizes
sizes = sorted({float(t["fontSize"].rstrip("px")) for t in V["texts"]})
print(f"     font sizes (units): {sizes}; smallest prints at {sizes[0] * 505.89 / 1048.08:.2f} pt at \\textwidth")
check(sizes[0] >= 13.5, "smallest text >= 13.5 units (6.5 pt printed)")

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAIL")
sys.exit(1 if fails else 0)
