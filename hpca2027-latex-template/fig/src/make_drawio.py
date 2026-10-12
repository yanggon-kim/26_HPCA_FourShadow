"""Emit fourshadow_uarch_v2.drawio (one page, "Figure 3 v2") from fig3_spec.ELEMENTS.

Styles are draw.io-native: rounded=0, html=1, explicit fontSize/fontStyle, fillColor/strokeColor, edges as
explicit orthogonal polylines (edgeStyle=none with waypoints, so the viewer draws exactly the prototype's
paths), dashed zoom lines, and the multiplexers as the existing tabs' trapezoid cells
(shape=trapezoid;rotation=90). Also emits fig3_v2_viewer.html, which renders the file with draw.io's
own viewer script (viewer.diagrams.net); only that script is downloaded, the diagram stays local.
"""
import json
import os
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig3_spec as S  # noqa: E402

SPACING = "spacing=0;spacingTop=0;spacingBottom=0;spacingLeft=0;spacingRight=0;"


def font(e):
    return (f"fontFamily={S.FONT};fontSize={e['fs']};fontStyle={1 if e.get('bold', True) else 0};"
            f"fontColor={e['fc']};align={e.get('align', 'center')};verticalAlign={e.get('valign', 'middle')};")


def label_value(text):
    return "<br>".join(escape(t) for t in text.split("\n")) if text else ""


class Doc:
    def __init__(self):
        self.cells = []
        self.n = 0

    def vertex(self, cid, value, style, x, y, w, h):
        self.cells.append(f'<mxCell id={quoteattr(cid)} value={quoteattr(value)} style={quoteattr(style)} '
                          f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
                          f'as="geometry"/></mxCell>')

    def edge(self, cid, pts, style):
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        mid = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts[1:-1])
        arr = f'<Array as="points">{mid}</Array>' if mid else ""
        self.cells.append(f'<mxCell id={quoteattr(cid)} value="" style={quoteattr(style)} edge="1" parent="1">'
                          f'<mxGeometry relative="1" as="geometry"><mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
                          f'<mxPoint x="{tx}" y="{ty}" as="targetPoint"/>{arr}</mxGeometry></mxCell>')


def edge_style(stroke, sw, dashed, arrow):
    s = f"edgeStyle=none;rounded=0;html=1;strokeColor={stroke};strokeWidth={sw};"
    s += "endArrow=classic;endFill=1;endSize=5;" if arrow else "endArrow=none;"
    s += "startArrow=none;"
    if dashed:
        s += "dashed=1;dashPattern=4 3;fixDash=1;"
    return s


def build():
    d = Doc()
    # white canvas so the diagram bounds are exactly the figure footprint
    d.vertex("canvas", "", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=none;", 0, 0, S.CANVAS_W, S.CANVAS_H)
    for e in S.ELEMENTS:
        k = e["kind"]
        if k == "R":
            st = (f"rounded=0;html=1;whiteSpace=nowrap;fillColor={e['fill']};strokeColor={e['stroke']};"
                  f"strokeWidth={e['sw']};" + SPACING)
            if e["dashed"]:
                st += "dashed=1;dashPattern=4 3;fixDash=1;"
            if e["label"]:
                st += font(e)
                if e.get("vertical"):
                    st += "horizontal=0;"
            d.vertex(e["id"], label_value(e["label"]), st, e["x"], e["y"], e["w"], e["h"])
        elif k == "T":
            st = "text;html=1;whiteSpace=nowrap;strokeColor=none;fillColor=none;" + SPACING + font(e)
            d.vertex(e["id"], label_value(e["label"]), st, e["x"], e["y"], e["w"], e["h"])
        elif k == "M":
            # existing tabs' mux cell: shape=trapezoid rotated by 90 degrees (narrow side on the right).
            cx, cy = e["x"] + e["w"] / 2, e["y"] + e["h"] / 2
            gw, gh = e["h"], e["w"]          # unrotated geometry
            st = (f"shape=trapezoid;perimeter=trapezoidPerimeter;size=0.2;rotation=90;html=1;"
                  f"fillColor={e['fill']};strokeColor={e['stroke']};strokeWidth={e['sw']};")
            d.vertex(e["id"], "", st, round(cx - gw / 2, 3), round(cy - gh / 2, 3), gw, gh)
        elif k == "E":
            d.edge(e["id"], e["pts"], edge_style(e["stroke"], e["sw"], e["dashed"], e["arrow"]))
        elif k == "X":
            cx, cy, s = e["cx"], e["cy"], e["s"]
            x0, y0 = cx - s / 2, cy - s / 2
            d.vertex(e["id"], "", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;",
                     x0, y0, s, s)
            d.edge(e["id"] + "_d1", [(x0, y0), (x0 + s, y0 + s)], edge_style("#000000", 1, False, False))
            d.edge(e["id"] + "_d2", [(x0 + s, y0), (x0, y0 + s)], edge_style("#000000", 1, False, False))
    model = (f'<mxGraphModel dx="0" dy="0" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
             f'fold="1" page="0" pageScale="1" pageWidth="{S.CANVAS_W}" pageHeight="{S.CANVAS_H}" '
             f'background="#FFFFFF" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
             + "".join(d.cells) + "</root></mxGraphModel>")
    mxfile = (f'<mxfile host="revision-owner make_drawio.py" pages="1">'
              f'<diagram name="Figure 3 v2" id="fig3-v2">{model}</diagram></mxfile>')
    return mxfile


def viewer_html(xml):
    cfg = {"highlight": "#0000ff", "nav": False, "resize": False, "toolbar": "", "edit": None,
           "lightbox": False, "border": 0, "xml": xml}
    return ("<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>Figure 3 v2 (draw.io viewer)</title>\n"
            "<style>html,body{margin:0;padding:0;background:#fff}"
            "@page{size:1048px 278px;margin:0}</style></head>\n<body>\n"
            f"<div class=\"mxgraph\" data-mxgraph={quoteattr(json.dumps(cfg))}></div>\n"
            "<script type=\"text/javascript\" src=\"https://viewer.diagrams.net/js/viewer-static.min.js\"></script>\n"
            "</body></html>\n")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    xml = build()
    with open(os.path.join(here, "fourshadow_uarch_v2.drawio"), "w") as f:
        f.write(xml + "\n")
    with open(os.path.join(here, "fig3_v2_viewer.html"), "w") as f:
        f.write(viewer_html(xml))
    print("wrote fourshadow_uarch_v2.drawio and fig3_v2_viewer.html")


if __name__ == "__main__":
    main()
