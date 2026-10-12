#!/usr/bin/env python3
"""Column-width WGMMA operation figure.

Emits wgmma_operation.drawio (editable), wgmma_operation.pdf and wgmma_operation.svg
from one scene description, so the draw.io file and the paper figure share
geometry. Coordinates are in points; the page is one IEEE column (250 pt).
"""
import xml.sax.saxutils as sx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

W, H = 250, 364

C = {  # fill, stroke
    "logic":   ("#dbe8f5", "#2f5b86"),
    "buffer":  ("#fbefd0", "#9c7a1b"),
    "reg":     ("#e3efe1", "#3d7a45"),
    "control": ("#ece3f1", "#74508a"),
    "plain":   ("#ffffff", "#444444"),
    "panel":   ("#f7f7f7", "#9a9a9a"),
}

boxes, texts, edges = [], [], []


def attr(s):
    return sx.escape(s, {'"': "&quot;"})


def box(x, y, w, h, text="", kind="plain", fs=6.5, bold=False, align="center", stroke_w=0.8):
    boxes.append(dict(x=x, y=y, w=w, h=h, text=text, kind=kind, fs=fs, bold=bold,
                      align=align, sw=stroke_w))


def label(x, y, text, fs=6.5, bold=False, align="left", color="#111111"):
    texts.append(dict(x=x, y=y, text=text, fs=fs, bold=bold, align=align, color=color))


def edge(pts, arrow=True, dashed=False, color="#222222", width=0.8):
    edges.append(dict(pts=pts, arrow=arrow, dashed=dashed, color=color, width=width))


# ---------------------------------------------------------------- panel 1
box(2, 2, W - 4, 86, kind="panel", stroke_w=0.6)
label(5, 5, "(a) Shared memory of one CTA, block-major, NRC = 8", fs=7, bold=True)

label(5, 16, "A: per-warp slice, x10[w]", fs=6.5, bold=True)
cw, ch = 22, 10
for i in range(4):
    y = 26 + 12 * i
    label(5, y + 2, f"w{i}", fs=6.5)
    for j, t in enumerate(["k0m0", "k0m1", "k1m0", "k1m1"]):
        box(17 + 23 * j, y, cw, ch, t, kind="logic", fs=6.5)
label(5, 76, "block = tcM × fedpK words", fs=6.5)

label(126, 16, "B: one tile for all warps, x11", fs=6.5, bold=True)
for i in range(2):
    y = 26 + 12 * i
    label(126, y + 2, f"k{i}", fs=6.5)
    for j in range(4):
        box(138 + 23 * j, y, cw, ch, f"n{j}", kind="logic", fs=6.5)
edge([(139, 50), (139, 53), (182, 53), (182, 50)], arrow=False, color="#9c7a1b")
label(126, 55, "bank row = 2 blocks (NT 8, 32),", fs=6.5)
label(126, 63, "1 block at NT 16 or with 2K FEDP", fs=6.5)
label(126, 71, "stride ≠ 0: row-major A, K-major B", fs=6.5)

# ---------------------------------------------------------------- panel 2
P2 = 92
box(2, P2, W - 4, 144, kind="panel", stroke_w=0.6)
label(5, P2 + 3, "(b) Engine: 4 + 1 tile buffers, one port, four tensor blocks", fs=7, bold=True)

r1 = P2 + 14
box(5, r1, 100, 12, "Local memory (one port)", kind="buffer", fs=6.5)
box(112, r1, 80, 12, "5 → 1 priority arbiter", kind="control", fs=6.5)
edge([(112, r1 + 6), (105, r1 + 6)])

AX = [4 + 47 * b for b in range(4)]
AC = [x + 22.5 for x in AX]
BX, BW = 190, 56
BC = BX + BW / 2
r2 = r1 + 23
edge([(152, r2 - 6), (152, r1 + 12)])
edge([(AC[0], r2 - 6), (BC, r2 - 6)], arrow=False)
for c in AC + [BC]:
    edge([(c, r2), (c, r2 - 6)], arrow=False)
for b in range(4):
    box(AX[b], r2, 45, 24, f"A buf {b}\nboth m, one k\ntag: desc_a, k", kind="buffer", fs=6.5)
box(BX, r2, BW, 24, "B buf (shared)\n1 bank row\ntag: desc_b, k, n", kind="buffer", fs=6.5)

r3 = r2 + 46
for b in range(4):
    edge([(AC[b], r2 + 24), (AC[b], r3)])
    box(AX[b], r3, 45, 20, f"Tensor block {b}\nD = f(2n+m)", kind="logic", fs=6.5)
yb = r3 - 5
edge([(BC, r2 + 24), (BC, yb), (AC[0] + 8, yb)], arrow=False, dashed=True, color="#9c7a1b")
for b in range(4):
    edge([(AC[b] + 8, yb), (AC[b] + 8, r3)], dashed=True, color="#9c7a1b")
label(BC - 4, yb - 9, "B broadcast", fs=6.5, align="right", color="#7a5c00")
box(BX, r3, BW, 20, "CTA gate\nowner per block", kind="control", fs=6.5)

r4 = r3 + 24
label(5, r4, "ready[b] = A buf[b] ∧ B buf ∧ key[b] ∧ ¬conflict[b]", fs=6.5)
label(5, r4 + 8, "key[b]: (desc_b, k, n, NRC) same as the leader block", fs=6.5)
label(5, r4 + 16, "conflict[b]: another block runs a different CTA", fs=6.5)
label(5, r4 + 24, "RS mode: A comes from f24–f27 and bypasses the A buffer", fs=6.5)

# ---------------------------------------------------------------- panel 3
P3 = P2 + 148
box(2, P3, W - 4, H - P3 - 2, kind="panel", stroke_w=0.6)
label(5, P3 + 3, "(c) One warp's micro-ops, SS mode, NRC = 8: k outer, n, m inner", fs=7, bold=True)
label(5, P3 + 13, "one µop: a tcM × tcN output block over fedpK words of K", fs=6.5)

rows = [
    ("µop", [str(i) for i in range(16)]),
    ("k",   [str(i // 8) for i in range(16)]),
    ("n",   [str((i // 2) % 4) for i in range(16)]),
    ("m",   [str(i % 2) for i in range(16)]),
    ("acc", [f"f{i % 8}" for i in range(16)]),
    ("A buf", ["F" if i % 8 == 0 else "H" for i in range(16)]),
    ("B buf", ["F" if i % 4 == 0 else "H" for i in range(16)]),
]
x0, cwid, chgt = 41, 12.9, 8.5
t0 = P3 + 23
for r, (name, vals) in enumerate(rows):
    y = t0 + chgt * r
    label(5, y + 1.5, name, fs=6.5)
    for j, v in enumerate(vals):
        kind = "plain"
        if name in ("A buf", "B buf"):
            kind = "buffer" if v == "F" else "reg"
        elif name == "acc":
            kind = "reg"
        box(x0 + cwid * j, y, cwid, chgt, v, kind=kind, fs=6.5)

yb = t0 + chgt * 7 + 2
label(5, yb + 1, "slot lock", fs=6.5)
box(x0, yb, cwid * 16, 8, "fu_lock at µop 0  ·  held by this warp  ·  fu_unlock at µop 15", kind="control", fs=6.5, stroke_w=0.5)
yb2 = yb + 10
label(5, yb2 + 1, "CTA owner", fs=6.5)
box(x0, yb2, cwid * 16, 8, "claimed at µop 0  ·  released at µop 15", kind="control", fs=6.5, stroke_w=0.5)
label(5, yb2 + 11, "F: fetch from local memory, the µop stalls.  H: resident hit.", fs=6.5)
label(5, yb2 + 19, "A refills at each new k and at µop 0 of every instruction.", fs=6.5)

# ------------------------------------------------------------- draw.io out


def drawio():
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    n = 2
    for b in boxes:
        fill, stroke = C[b["kind"]]
        html = sx.escape(b["text"]).replace("\n", "<br>")
        if b["bold"]:
            html = f"<b>{html}</b>"
        html = f'<font style="font-size: {b["fs"]}px">{html}</font>'
        style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                 f"strokeWidth={b['sw']};fontFamily=Helvetica;fontSize={b['fs']};fontColor=#111111;"
                 f"align={b['align']};verticalAlign={'top' if b['kind']=='panel' else 'middle'};spacing=0;")
        cells.append(f'<mxCell id="{n}" value="{attr(html)}" style="{style}" vertex="1" parent="1">'
                     f'<mxGeometry x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" as="geometry"/></mxCell>')
        n += 1
    for t in texts:
        html = sx.escape(t["text"])
        if t["bold"]:
            html = f"<b>{html}</b>"
        w = max(20, int(len(t["text"]) * t["fs"] * 0.55))
        x = t["x"] - (w if t["align"] == "right" else 0)
        style = (f"text;html=1;strokeColor=none;fillColor=none;align={t['align']};verticalAlign=top;"
                 f"whiteSpace=nowrap;fontFamily=Helvetica;fontSize={t['fs']};fontColor={t['color']};spacing=0;")
        cells.append(f'<mxCell id="{n}" value="{attr(html)}" style="{style}" vertex="1" parent="1">'
                     f'<mxGeometry x="{x}" y="{t["y"] - 1}" width="{w}" height="{t["fs"] + 3}" as="geometry"/></mxCell>')
        n += 1
    for e in edges:
        pts = e["pts"]
        style = (f"edgeStyle=none;html=1;strokeColor={e['color']};strokeWidth={e['width']};"
                 f"endArrow={'block' if e['arrow'] else 'none'};endFill=1;endSize=3;"
                 f"{'dashed=1;' if e['dashed'] else ''}")
        mid = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts[1:-1])
        cells.append(f'<mxCell id="{n}" style="{style}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                     f'<mxPoint x="{pts[0][0]}" y="{pts[0][1]}" as="sourcePoint"/>'
                     f'<mxPoint x="{pts[-1][0]}" y="{pts[-1][1]}" as="targetPoint"/>'
                     f'<Array as="points">{mid}</Array></mxGeometry></mxCell>')
        n += 1
    body = "\n".join(cells)
    return (f'<mxfile host="Electron" type="device"><diagram id="wgmma-col" name="WGMMA column">'
            f'<mxGraphModel dx="{W}" dy="{H}" grid="1" gridSize="1" guides="1" tooltips="1" connect="1" arrows="1" '
            f'fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{H}" math="0" shadow="0"><root>\n{body}\n'
            f'</root></mxGraphModel></diagram></mxfile>\n')


# ------------------------------------------------------------- matplotlib


def render(path_pdf, path_svg):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Nimbus Sans", "Nimbus Sans L", "Arial", "Liberation Sans", "DejaVu Sans"],
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })
    fig = plt.figure(figsize=(W / 72, H / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    for b in boxes:
        fill, stroke = C[b["kind"]]
        ax.add_patch(Rectangle((b["x"], b["y"]), b["w"], b["h"], facecolor=fill, edgecolor=stroke,
                               linewidth=b["sw"], zorder=1 if b["kind"] == "panel" else 2))
        if b["text"]:
            ax.text(b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, b["text"], fontsize=b["fs"],
                    ha="center", va="center", fontweight="bold" if b["bold"] else "normal",
                    linespacing=1.15, zorder=4)
    for t in texts:
        ha = {"left": "left", "right": "right", "center": "center"}[t["align"]]
        ax.text(t["x"], t["y"], t["text"], fontsize=t["fs"], ha=ha, va="top", color=t["color"],
                fontweight="bold" if t["bold"] else "normal", zorder=4)
    for e in edges:
        pts = e["pts"]
        ls = (0, (2, 1.5)) if e["dashed"] else "-"
        for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
            ax.plot([x1, x2], [y1, y2], color=e["color"], linewidth=e["width"], linestyle=ls, zorder=3,
                    solid_capstyle="butt")
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        if e["arrow"]:
            ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=5,
                                         color=e["color"], linewidth=e["width"], linestyle=ls,
                                         shrinkA=0, shrinkB=0, zorder=3))
        else:
            ax.plot([x1, x2], [y1, y2], color=e["color"], linewidth=e["width"], linestyle=ls, zorder=3)
    fig.savefig(path_pdf)
    fig.savefig(path_svg)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "wgmma_operation.drawio"), "w") as f:
        f.write(drawio())
    render(os.path.join(here, "wgmma_operation.pdf"), os.path.join(here, "wgmma_operation.svg"))
    print(f"min font {min([b['fs'] for b in boxes if b['text']] + [t['fs'] for t in texts])} pt, page {W}x{H} pt")
