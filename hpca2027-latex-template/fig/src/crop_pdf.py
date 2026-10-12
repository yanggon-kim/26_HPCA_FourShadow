"""Crop the viewer's print (1 unit = 1 CSS px = 0.75 pt; Chrome rounds the paper height up) to the
diagram bounds and place it, as vectors, on a page of the old figure's size 1048.08 x 277.92 pt, so
1 diagram unit = 1.00008 pt and the aspect ratio equals the old PDF's.
usage: python3 crop_pdf.py <chrome print.pdf> <out.pdf>
"""
import sys

import fitz  # PyMuPDF

W_OLD, H_OLD = 1048.08, 277.92
src = fitz.open(sys.argv[1])
p = src[0]
k = 0.75                                  # pt per diagram unit in the print
clip = fitz.Rect(0, 0, 1048 * k, 1048 * k * H_OLD / W_OLD)
assert clip.y1 <= p.rect.y1 + 1e-6, (clip, p.rect)
out = fitz.open()
page = out.new_page(width=W_OLD, height=H_OLD)
page.show_pdf_page(page.rect, src, 0, clip=clip)
out.set_metadata({"title": "FourShadow datapath (Figure 3 v2)", "creator": "draw.io viewer in headless Chrome",
                  "producer": "PyMuPDF crop (fig/src/crop_pdf.py)"})
out.save(sys.argv[2], garbage=4, deflate=True)
print(f"source page {p.rect.width:.2f} x {p.rect.height:.2f} pt, clip {clip}, out {W_OLD} x {H_OLD} pt")
