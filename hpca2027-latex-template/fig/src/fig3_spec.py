"""Figure 3 v2 (fig:figure_integration): one geometry and style table.

Both the HTML/SVG prototype (make_prototype.py) and the draw.io file (make_drawio.py) are generated
from ELEMENTS below, so the two cannot drift. Canvas: 1048 x 278 units (the old PDF is
1048.08 x 277.92 pt). At \\textwidth (505.89 pt) one unit prints at 0.4827 pt, so 13.5 units = 6.5 pt.

Element kinds
  R  box with an optional (multi-line, "\\n") label
  T  text only (no fill, no stroke)
  M  multiplexer (trapezoid, narrow side on the right), bounding box x, y, w, h
  E  polyline edge through absolute points, optional arrow head, optional dash
  X  crossing mark: a square with an X, centred at (cx, cy)
"""

CANVAS_W, CANVAS_H = 1048, 278

# Palette (architecture-paper-writing 02_structure_and_figures.md, F6)
INK = "#000000"
WHITE = "#FFFFFF"
GRAY1 = "#E8E8E8"          # existing containers / blocks
GRAY3 = "#808080"          # zoom lines
TINT = "#CFE2F3"           # large areas FourShadow adds
TINT_STROKE = "#2B5FA8"
RED = "#E03127"            # small marks only (AGU tags)

FONT = "Helvetica"

# font sizes in units (pt printed = units * 0.4827)
F_TOP = 18      # Socket, Tensor Core Unit       (8.7 pt)
F_SUB = 16      # subsystem titles               (7.7 pt)
F_BLK = 15      # block labels                   (7.2 pt)
F_BLK_L = 15.5  # long single-line block labels  (7.5 pt)
F_SM = 14       # small labels                   (6.8 pt)
F_MIN = 13.5    # smallest text                  (6.5 pt)

ELEMENTS = []


def R(id, x, y, w, h, label=None, fs=F_BLK, fill=WHITE, stroke=INK, sw=1.0, dashed=False,
      fc=INK, bold=True, align="center", valign="middle", vertical=False):
    ELEMENTS.append(dict(kind="R", id=id, x=x, y=y, w=w, h=h, label=label, fs=fs, fill=fill,
                         stroke=stroke, sw=sw, dashed=dashed, fc=fc, bold=bold, align=align,
                         valign=valign, vertical=vertical))


def T(id, x, y, w, h, text, fs=F_SM, align="center", valign="middle", fc=INK, bold=True):
    ELEMENTS.append(dict(kind="T", id=id, x=x, y=y, w=w, h=h, label=text, fs=fs, align=align,
                         valign=valign, fc=fc, bold=bold))


def M(id, x, y, w, h):
    ELEMENTS.append(dict(kind="M", id=id, x=x, y=y, w=w, h=h, fill=WHITE, stroke=INK, sw=1.0))


def E(id, pts, arrow=True, dashed=False, stroke=INK, sw=1.2):
    ELEMENTS.append(dict(kind="E", id=id, pts=pts, arrow=arrow, dashed=dashed, stroke=stroke, sw=sw))


def X(id, cx, cy, s=14):
    ELEMENTS.append(dict(kind="X", id=id, cx=cx, cy=cy, s=s))


# ----------------------------------------------------------------------------------------------
# Socket side (layout of the old figure, restyled)
# ----------------------------------------------------------------------------------------------
R("socket", 4, 4, 242, 270, sw=1.5)
T("socket_t", 120, 5, 122, 21, "Socket", fs=F_TOP, align="right")
R("core0", 12, 26, 226, 220, fill=GRAY1, sw=1.2)
T("core0_t", 130, 27, 103, 18, "core [0]", fs=F_BLK, align="right")
RX, RW = 20, 210
for i, (cid, lab) in enumerate([("ws", "Warp Scheduler"), ("fetch", "Fetch"), ("decode", "Decode"),
                                ("issue", "Issue (Uop Sequencer)"), ("dispatch", "Dispatch")]):
    R(cid, RX, 46 + 20 * i, RW, 17, lab, fs=F_BLK)
# functional units
for cid, lab, x, w in [("lsu", "LSU", 20, 34), ("sfu", "SFU", 57, 34), ("alu", "ALU", 94, 34),
                       ("fpu", "FPU", 131, 34)]:
    R(cid, x, 146, w, 18, lab, fs=F_SM)
R("tcu_fu", 168, 146, 62, 18, "TCU", fs=F_BLK, fill=TINT, stroke=TINT_STROKE, sw=2.0)
R("gather", RX, 167, RW, 17, "Gather", fs=F_BLK)
R("rf", RX, 187, RW, 17, "Register File", fs=F_BLK)
R("smem", RX, 207, RW, 36)
T("smem_t", 104, 207, 122, 17, "Shared Memory", fs=F_BLK, align="right")
for cid, lab, x, w in [("bank_dots", "...", 24, 36), ("bank2", "Bank 2", 64, 50), ("bank1", "Bank 1", 118, 50),
                       ("bank0", "Bank 0", 172, 54)]:
    R(cid, x, 224, w, 16, lab, fs=F_MIN, fill=GRAY1)
R("core1", 12, 250, 226, 18, "core [1...]", fs=F_BLK, fill=GRAY1, sw=1.2)

# ----------------------------------------------------------------------------------------------
# Tensor Core Unit
# ----------------------------------------------------------------------------------------------
R("tcu", 258, 4, 786, 270, sw=1.5)
T("tcu_t", 888, 5, 150, 23, "Tensor Core Unit", fs=F_TOP, align="right")
# zoom lines core[0] TCU -> TCU box
E("zoom_tcu_top", [(230, 146), (258, 4)], arrow=False, dashed=True, stroke=GRAY3)
E("zoom_tcu_bot", [(230, 164), (258, 274)], arrow=False, dashed=True, stroke=GRAY3)

# --- top tier: Warp-Group Tile Buffer Subsystem ------------------------------------------------
R("wg", 264, 8, 449, 108, fill=TINT, stroke=TINT_STROKE, sw=1.5)
T("wg_t", 272, 9, 300, 21, "Warp-Group Tile Buffer Subsystem", fs=F_SUB, align="left")
for i in range(4):
    ax = 272 + 81 * i
    R(f"abuf{i}", ax, 32, 77, 56)
    T(f"abuf{i}_l", ax, 33, 77, 37, f"A Buffer {i}\n(Block {i})", fs=F_BLK)
    R(f"abuf{i}_agu", ax + 40, 70, 34, 15, "AGU", fs=F_MIN, fill=RED, stroke=RED, fc=WHITE)
R("bbuf", 596, 12, 111, 100)
T("bbuf_l", 596, 13, 111, 76, "Shared B Buffer\n(broadcast to all\ntensor blocks)", fs=F_SM)
R("bbuf_agu", 669, 92, 34, 15, "AGU", fs=F_MIN, fill=RED, stroke=RED, fc=WHITE)
R("arbiter", 272, 92, 180, 20, "SMEM Read Arbiter", fs=F_BLK_L)
R("lockstep", 456, 92, 133, 20, "Lockstep", fs=F_BLK_L)

# --- top tier: Selection MUX inset ----------------------------------------------------------------
R("selmux", 719, 8, 161, 108, stroke=TINT_STROKE, sw=1.5)
T("selmux_t", 719, 9, 161, 18, "Selection MUX", fs=14.5)
T("meta_l", 733, 28, 40, 16, "meta:", fs=F_SM, align="right")
for i, b in enumerate("1001"):
    one = b == "1"
    R(f"meta_b{i}", 776 + 15 * i, 29, 15, 15, b, fs=F_MIN, fill=INK if one else WHITE, fc=WHITE if one else INK)
M("sel_mux", 795, 47, 20, 66)
E("sel_meta_arrow", [(805, 44), (805, 49.6)])
R("grp_in0", 731, 48, 26, 30, dashed=True)
R("grp_in1", 731, 81, 26, 30, dashed=True)
for cid, lab, y, sel in [("b0_in", "b0", 49, True), ("b1_in", "b1", 63, False),
                         ("b2_in", "b2", 82, False), ("b3_in", "b3", 96, True)]:
    R(cid, 733, y, 22, 14, lab, fs=F_MIN, fill=INK if sel else WHITE, fc=WHITE if sel else INK)
E("sel_in0", [(757, 63), (795, 63)])
E("sel_in1", [(757, 96), (795, 96)])
R("grp_out", 838, 64, 26, 32, dashed=True)
R("b0_out", 840, 66, 22, 14, "b0", fs=F_MIN, fill=INK, fc=WHITE)
R("b3_out", 840, 80, 22, 14, "b3", fs=F_MIN, fill=INK, fc=WHITE)
E("sel_out", [(815, 80), (838, 80)])

# --- top tier: FEDP inset ------------------------------------------------------------------------
R("fedp_detail", 892, 30, 146, 86, stroke=TINT_STROKE, sw=1.5)
for i, lab in enumerate(["MULTIPLY", "ALIGN", "ACCUMULATE", "NORM & ROUND"]):
    R(f"stage{i}", 902, 35 + 20 * i, 126, 17, lab, fs=14.5, fill=GRAY1)

# --- bottom tier: operand-A select (RF / SMEM) ---------------------------------------------------
R("rs_sel", 266, 148, 68, 54, "RS/SS?", fs=F_MIN, dashed=True)
M("rs_mux", 312, 210, 18, 48)
E("rs_sel_arrow", [(321, 202), (321, 214.8)])
T("rf_l", 266, 203, 30, 16, "RF", fs=F_SM, align="left")
E("rf_in", [(266, 220), (312, 220)])
T("smem_l", 266, 231, 46, 16, "SMEM", fs=F_SM, align="left")
E("smem_in", [(266, 248), (312, 248)])
E("rs_out", [(330, 234), (337, 234)])

# --- bottom tier: 2:4 Structured Sparsity Subsystem ---------------------------------------------
R("sp", 344, 122, 448, 146, fill=TINT, stroke=TINT_STROKE, sw=1.5)
T("sp_t", 352, 123, 280, 21, "2:4 Structured Sparsity Subsystem", fs=F_SUB, align="left")
X("x_meta", 344, 165)
X("x_b", 344, 196)
X("x_a", 344, 234)
X("x_c", 344, 256)
T("spmeta_l", 355, 147, 58, 16, "sp meta", fs=F_SM, align="left")
T("mb_l", 355, 179, 60, 16, "matrix B", fs=F_SM, align="left")
T("ma_l", 355, 217, 60, 16, "matrix A", fs=F_SM, align="left")
T("mc_l", 355, 239, 60, 16, "matrix C", fs=F_SM, align="left")
R("meta_agu", 416, 146, 82, 38, "Metadata\nAGU Load", fs=F_BLK)
R("meta_sram", 514, 146, 86, 38, "Metadata\nTCU SRAM", fs=F_BLK)
R("spmux", 624, 146, 92, 38, "Sparse MUX\nArray", fs=F_BLK)
E("e_meta", [(351, 165), (416, 165)], dashed=True)
E("e_agu_sram", [(498, 165), (514, 165)], dashed=True)
E("e_sram_spmux", [(600, 165), (624, 165)])
M("sp_mux", 736, 155, 18, 52)
R("sp_sel", 668, 212, 88, 18, "Sparse?", fs=F_SM, dashed=True)
E("sp_sel_arrow", [(745, 212), (745, 201.8)])
E("e_spmux_mux", [(716, 165), (736, 165)])
E("e_b", [(351, 196), (736, 196)])
E("e_b_branch", [(670, 196), (670, 184)])
R("pb", 768, 146, 20, 118, "Pipeline Buffer", fs=F_BLK_L, vertical=True)
E("e_mux_pb", [(754, 181), (768, 181)])
E("e_a", [(351, 234), (768, 234)])
E("e_c", [(351, 256), (768, 256)])

# --- bottom tier: FEDP arrays and matrix D ------------------------------------------------------
AW, AH = 88, 62
for r in range(2):
    for c in range(2):
        ax, ay = 796 + c * (AW + 4), 136 + r * (AH + 6)
        R(f"arr{r}{c}", ax, ay, AW, AH, fill=TINT, stroke=TINT_STROKE, sw=1.2)
        for i in range(2):
            for j in range(2):
                R(f"fedp{r}{c}{i}{j}", ax + 3 + j * 43, ay + 3 + i * 20, 40, 18, "FEDP", fs=F_MIN)
        T(f"arr{r}{c}_l", ax, ay + 43, AW, 18, "FEDP Array", fs=14.5)
E("e_pb_arr0", [(788, 167), (796, 167)])
E("e_pb_arr1", [(788, 235), (796, 235)])
E("e_arr0_d", [(976, 167), (981, 167), (981, 201)], arrow=False)
E("e_arr1_d", [(976, 235), (981, 235), (981, 201)], arrow=False)
# output arrow ends at the TCU box's right edge (x = 258 + 786); "matrix D" sits just above its head
E("e_d", [(981, 201), (1044, 201)])
T("md_l", 984, 180, 56, 16, "matrix D", fs=F_MIN, align="right")

# zoom lines of the two insets
E("zoom_sel_l", [(624, 146), (719, 116)], arrow=False, dashed=True, stroke=GRAY3)
E("zoom_sel_r", [(716, 146), (880, 116)], arrow=False, dashed=True, stroke=GRAY3)
E("zoom_fedp_l", [(934, 139), (892, 116)], arrow=False, dashed=True, stroke=GRAY3)
E("zoom_fedp_r", [(974, 139), (1038, 116)], arrow=False, dashed=True, stroke=GRAY3)


def labels():
    """Every printed string, one entry per text occurrence (for the presence check)."""
    out = []
    for e in ELEMENTS:
        if e["kind"] in ("R", "T") and e.get("label"):
            out.append((e["id"], e["label"], e["fs"]))
    return out
