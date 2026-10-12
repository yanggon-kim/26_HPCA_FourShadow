"""Emit fig3_v2_prototype.html: inline SVG drawn from fig3_spec.ELEMENTS (1048 x 278 units)."""
import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig3_spec as S  # noqa: E402

FAMILY = "Helvetica, Arial, 'Liberation Sans', sans-serif"
LINE = 1.2          # draw.io html label line height
BASE = 0.346        # baseline offset from the line centre, in em (Liberation Sans metrics)


def text_svg(e):
    lines = e["label"].split("\n")
    fs = e["fs"]
    weight = "bold" if e.get("bold", True) else "normal"
    cx, cy = e["x"] + e["w"] / 2, e["y"] + e["h"] / 2
    out = []
    if e.get("vertical"):
        return (f'<text x="{cx}" y="{cy + BASE * fs:.2f}" font-size="{fs}" font-weight="{weight}" '
                f'fill="{e["fc"]}" text-anchor="middle" transform="rotate(-90 {cx} {cy})">'
                f'{escape(e["label"])}</text>')
    n = len(lines)
    block = n * LINE * fs
    if e.get("valign", "middle") == "top":
        top = e["y"]
    else:
        top = cy - block / 2
    if e.get("align") == "left":
        x, anchor = e["x"], "start"
    elif e.get("align") == "right":
        x, anchor = e["x"] + e["w"], "end"
    else:
        x, anchor = cx, "middle"
    for i, ln in enumerate(lines):
        yc = top + (i + 0.5) * LINE * fs
        out.append(f'<text x="{x}" y="{yc + BASE * fs:.2f}" font-size="{fs}" font-weight="{weight}" '
                   f'fill="{e["fc"]}" text-anchor="{anchor}">{escape(ln)}</text>')
    return "\n".join(out)


def svg():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S.CANVAS_W}" height="{S.CANVAS_H}" '
             f'viewBox="0 0 {S.CANVAS_W} {S.CANVAS_H}" font-family="{FAMILY}">',
             '<defs><marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" '
             'markerHeight="6" markerUnits="userSpaceOnUse" orient="auto">'
             '<path d="M0,0 L10,5 L0,10 L2.5,5 z" fill="#000"/></marker></defs>',
             f'<rect x="0" y="0" width="{S.CANVAS_W}" height="{S.CANVAS_H}" fill="#fff"/>']
    for e in S.ELEMENTS:
        k = e["kind"]
        if k == "R":
            dash = ' stroke-dasharray="4 3"' if e["dashed"] else ""
            parts.append(f'<rect id="{e["id"]}" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" '
                         f'fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["sw"]}"{dash}/>')
            if e["label"]:
                parts.append(text_svg(e))
        elif k == "T":
            parts.append(text_svg(e))
        elif k == "M":
            x, y, w, h = e["x"], e["y"], e["w"], e["h"]
            dx = 0.2 * h
            parts.append(f'<polygon id="{e["id"]}" points="{x},{y} {x + w},{y + dx} {x + w},{y + h - dx} {x},{y + h}" '
                         f'fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["sw"]}"/>')
        elif k == "E":
            pts = " ".join(f"{a},{b}" for a, b in e["pts"])
            dash = ' stroke-dasharray="4 3"' if e["dashed"] else ""
            mk = ' marker-end="url(#arr)"' if e["arrow"] else ""
            parts.append(f'<polyline id="{e["id"]}" points="{pts}" fill="none" stroke="{e["stroke"]}" '
                         f'stroke-width="{e["sw"]}"{dash}{mk}/>')
        elif k == "X":
            cx, cy, s = e["cx"], e["cy"], e["s"]
            x0, y0 = cx - s / 2, cy - s / 2
            parts.append(f'<g id="{e["id"]}"><rect x="{x0}" y="{y0}" width="{s}" height="{s}" fill="#fff" '
                         f'stroke="#000" stroke-width="1"/><path d="M{x0},{y0} L{x0 + s},{y0 + s} M{x0 + s},{y0} '
                         f'L{x0},{y0 + s}" stroke="#000" stroke-width="1"/></g>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    html = ("<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>Figure 3 v2 prototype</title>\n"
            "<style>html,body{margin:0;padding:0;background:#fff}svg{display:block}</style></head>\n"
            "<body>\n" + svg() + "\n</body></html>\n")
    with open(os.path.join(here, "fig3_v2_prototype.html"), "w") as f:
        f.write(html)
    print("wrote fig3_v2_prototype.html")


if __name__ == "__main__":
    main()
