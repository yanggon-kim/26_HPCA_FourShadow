"""Fig. motiv_simt (Section III, Motivation): SIMT-only Vortex, tensor core off, 8 threads per warp, IW 1.

(a) GEMM 128x128x512 share of the 16 FLOP/cycle lane peak as SIMT limits are removed one at a time,
    with the limit that binds after each step and the ideal-SIMT cap (IPC 1) as a dashed line.
(b) Decode GEMV 8192x2048 on the tuned core: weight bytes and speed of each weight format, relative to FP32.

All values are hard-coded from Part 4's evidence files (read-only, part4-owner):
  FQ16 = 00_doc/vortex-wgdxa2k/results/MOTIV_MASTER_FQ16.md
  TCT  = 00_doc/vortex-wgdxa2k/results/MOTIV_MASTER_TC_TABLES.md
Measured on upstream Vortex master 7300bc849 (SimX cycles; RTL agrees within 0.4 % on the tuned GEMM, FQ16 5b.4).

Run from the paper repo root:
    python3 hpca2027-latex-template/fig/src/motiv_simt.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = Path(__file__).parents[1] / "motiv_simt.pdf"

PEAK = 16.0  # FP32 FLOP/cycle = 2 * NT * IW at NT 8, IW 1 (FQ16 header)

# ---- (a) the tuning chain, GEMM 128x128x512 --------------------------------------------------------------
# (label, FLOP/cycle, % of peak as printed in the source, binding limit after the step)
CHAIN = [
    # FQ16 2, row "NW 4, FQ 2 (ref)": 2.71 (17.0); best kernel rt-t4x4-b8x1-k8-gl; binds: FPU tags (FQ16 0 / 2 reading)
    ("Reference", 2.71, 17.0, "FPU queue"),
    # FQ16 2, row "NW 4, FQ 16": 2.91 (18.2), rt-t4x4-b8x2-k8-gl; binds: per-warp fflags ordering (FQ16 0, 3)
    ("FPU queue 16", 2.91, 18.2, "flags"),
    # FQ16 2, row "NW 16, FQ 2": 3.12 (19.5), rt-t4x4-b8x1-k8-gl; binds: FPU tags (0.199 FMA/cycle = 2 tags / 10.1 cycles)
    ("16 warps", 3.12, 19.5, "FPU queue"),
    # FQ16 2, row "NW 16, FQ 16": 5.33 (33.3), rt-t4x4-b8x2-k8-gl; binds: FPU dispatch credits (FQ16 0, 4)
    ("16 warps, queue 16", 5.33, 33.3, "credits"),
    # FQ16 2, row "what-if NW 16, FQ 16, DQ 8": 6.47 (40.4), rt-t4x4-b8x2-k8-gl; binds: GPR bank conflicts (FQ16 5b.2)
    ("+ dispatch queue 8", 6.47, 40.4, "reg. banks"),
    # FQ16 5b.4, row "+ 8 banks" (NW 16 FQ 16 DQ 8 + 8 GPR banks): 7.19 (44.9 %), rt-t4x4-b8x2-k8-gl;
    # collector-full cycles still 14.9 % (FQ16 5b.1). Best kernel of that config is b8x4-gl 7.23 (45.2 %), TCT B row gpr8.
    ("+ 8 register banks", 7.19, 44.9, "collector"),
]
# Ideal SIMT cap [D]: 4.54 MACs per warp-instruction (TCT F, row 128x128x512 rt-t4x4-b8x2-k8-gl) at IPC 1
# -> 2 * 4.54 / 16 = 56.75 % of peak, printed 57.
MACS_PER_WARP_INSTR = 4.54
IDEAL = 2 * MACS_PER_WARP_INSTR / PEAK * 100
assert round(IDEAL) == 57
for _, flop, pct, _ in CHAIN:
    assert abs(flop / PEAK * 100 - pct) < 0.1, (flop, pct)

# ---- (b) decode GEMV 8192x2048 on the tuned core (NW 16, FQ 16, DQ 8, 8 GPR banks) ------------------------
# TCT B, rows "gpr8 nt8-w16-iw1-fq16-dq8-gpr8[-zfh] | GEMV 8192x2048 <fmt>" (run ids motivm-tcref-...-gpr8[-zfh]-m7300bc8-20261123)
FP32_CYCLES = 7_258_989  # gemv-cm-r4-f32
FORMATS = [
    # (label, weight bytes relative to FP32 [S/D: storage size; 2:4 = half the values + 2-bit indices], cycles)
    ("FP32", 1.00, FP32_CYCLES),
    ("FP16", 0.50, 10_428_186),  # gemv-cm-r4-f16 (Zfhmin build)
    ("BF16", 0.50, 9_887_838),   # gemv-pk-r4-bf16
    ("INT8", 0.25, 9_204_399),   # gemv-cm-r4-i8
    ("SW 2:4", 0.53, 10_151_040),  # gemvsp-r2-f32, 2 FP32 values + 2x2-bit indices per group of 4 -> 0.53 [D]
]
SPEED = [FP32_CYCLES / c for _, _, c in FORMATS]
assert [round(s, 2) for s in SPEED] == [1.00, 0.70, 0.73, 0.79, 0.72], SPEED
# Not plotted: measured DRAM bytes on this core are 0.95 / 0.69 / 0.29 / 0.56 x FP32 (TCT I, "SIMT gpr8" rows).

# ---- style (LazyDP system: luminance ramp, four spines, no hue for the baseline) ---------------------------
GRAY1, GRAY2, GRAY3 = "#E8E8E8", "#BFBFBF", "#808080"
plt.rcParams.update({
    "font.size": 6.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.8,
    "hatch.linewidth": 0.5,
})

fig = plt.figure(figsize=(3.45, 2.32))
ax_a = fig.add_axes([0.305, 0.53, 0.50, 0.44])
ax_b = fig.add_axes([0.10, 0.10, 0.88, 0.28])

# (a) horizontal bars, top to bottom in chain order
n = len(CHAIN)
ys = list(range(n))[::-1]
for y, (label, _, pct, _) in zip(ys, CHAIN):
    face = GRAY3 if label.startswith("+ 8") else GRAY2
    ax_a.barh(y, pct, height=0.62, color=face, edgecolor="black", linewidth=0.5, zorder=2)
    ax_a.text(pct + 0.8, y, f"{pct:.1f}", va="center", ha="left", fontsize=6, zorder=3)
ax_a.axvline(IDEAL, color="black", ls="--", lw=0.8, zorder=1)
ax_a.text(IDEAL - 0.8, ys[0], f"ideal\nSIMT {IDEAL:.0f}", va="center", ha="right", fontsize=6, linespacing=0.95)
ax_a.set_yticks(ys)
ax_a.set_yticklabels([c[0] for c in CHAIN])
ax_a.set_ylim(-0.55, n - 0.45)
ax_a.set_xlim(0, 60)
ax_a.set_xticks([0, 10, 20, 30, 40, 50])
ax_a.set_xlabel("GEMM FLOP/cycle (% of lane peak)", labelpad=1)
ax_a.tick_params(length=2, pad=1.5)
ax_a.grid(axis="x", ls=":", lw=0.5, color=GRAY3, zorder=0)
ax_a.set_axisbelow(True)
# binding limit after each step, as right-hand tick labels
ax_r = ax_a.twinx()
ax_r.set_ylim(ax_a.get_ylim())
ax_r.set_yticks(ys)
ax_r.set_yticklabels([c[3] for c in CHAIN])
ax_r.tick_params(length=2, pad=1.5)
ax_r.set_ylabel("binding limit", labelpad=2)
ax_a.text(-0.58, 1.0, "(a)", transform=ax_a.transAxes, fontsize=7, fontweight="bold", va="top")

# (b) paired bars per format
w = 0.36
xs = range(len(FORMATS))
for x, (label, nbytes, _), spd in zip(xs, FORMATS, SPEED):
    ax_b.bar(x - w / 2, nbytes, w, color="white", edgecolor="black", linewidth=0.5, zorder=2)
    ax_b.bar(x + w / 2, spd, w, color=GRAY3, edgecolor="black", linewidth=0.5, zorder=2)
    ax_b.text(x - w / 2, nbytes + 0.03, f"{nbytes:.2f}", ha="center", va="bottom", fontsize=5.5, rotation=90)
    ax_b.text(x + w / 2, spd + 0.03, f"{spd:.2f}", ha="center", va="bottom", fontsize=5.5, rotation=90)
ax_b.set_xticks(list(xs))
ax_b.set_xticklabels([f[0] for f in FORMATS])
ax_b.set_xlim(-0.6, len(FORMATS) - 0.4)
ax_b.set_ylim(0, 1.45)
ax_b.set_yticks([0, 0.5, 1.0])
ax_b.set_ylabel("vs. FP32", labelpad=1)
ax_b.tick_params(length=2, pad=1.5)
ax_b.grid(axis="y", ls=":", lw=0.5, color=GRAY3, zorder=0)
ax_b.set_axisbelow(True)
ax_b.legend(handles=[Patch(facecolor="white", edgecolor="black", lw=0.5, label="weight bytes"),
                     Patch(facecolor=GRAY3, edgecolor="black", lw=0.5, label="GEMV speed")],
            loc="upper right", ncol=2, frameon=False, fontsize=6, handlelength=1.2,
            handletextpad=0.4, columnspacing=1.0, borderaxespad=0.2)
ax_b.text(-0.085, 1.0, "(b)", transform=ax_b.transAxes, fontsize=7, fontweight="bold", va="top")

fig.savefig(OUT)
print(f"wrote {OUT}")
