"""Fig. motiv_simt, three-panel version (Section III, Motivation): SIMT-only Vortex, tensor core off, 8 threads per warp.

(a) GEMM 128x128x512 share of the 16 FLOP/cycle lane peak as SIMT limits are removed one at a time,
    with the limit that binds after each step and the ideal-SIMT cap (IPC 1) as a dashed line (as in motiv_simt.py).
(b) Work per instruction: share of warp instructions by role (100 % stacked) against the thread tile, direct-load kernels
    (same x-axis and kernels as (c)), FMA share printed in each bar.
(c) Register-file reads: operand words loaded into registers per MAC and GPR lane-reads per MAC against the thread tile,
    with the FMA floor of three reads per MAC.

All values are hard-coded from Part 4's evidence files (read-only, part4-owner), all [M] unless marked:
  FQ16 = 00_doc/vortex-wgdxa2k/results/MOTIV_MASTER_FQ16.md
  TCT  = 00_doc/vortex-wgdxa2k/results/MOTIV_MASTER_TC_TABLES.md
  F1D  = 00_doc/vortex-wgdxa2k/results/MOTIV_FIG1_DATA.md and motiv_fig1_data.json (keys panel_b_tiles, panel_c)
Measured on upstream Vortex master 7300bc849 (SimX). (b) and (c) are properties of the kernel binaries (byte-identical on
every core configuration, F1D 1.2); they are measured on the reference core NT 8, NW 4, IW 1.
If the evidence JSON is reachable, the script cross-checks every hard-coded (b)/(c) value against it.

Run from the paper repo root:
    python3 hpca2027-latex-template/fig/src/motiv_simt3.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = Path(__file__).parents[1] / "motiv_simt3.pdf"
EVIDENCE = Path("/home/yanggon/00_sparse/01_ISPASS/00_doc/vortex-wgdxa2k/results/motiv_fig1_data.json")

PEAK = 16.0  # FP32 FLOP/cycle = 2 * NT * IW at NT 8, IW 1 (FQ16 header)

# ---- (a) the tuning chain, GEMM 128x128x512 (unchanged from motiv_simt.py) -------------------------------
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
# Ideal SIMT cap [D]: 4.54 MACs per warp-instruction (TCT F; F1D 1: 4.536 for rt-t4x4-b8x1/b8x2-k8-gl) at IPC 1
# -> 2 * 4.54 / 16 = 56.75 % of peak, printed 57.
MACS_PER_WARP_INSTR = 4.54
IDEAL = 2 * MACS_PER_WARP_INSTR / PEAK * 100
assert round(IDEAL) == 57
for _, flop, pct, _ in CHAIN:
    assert abs(flop / PEAK * 100 - pct) < 0.1, (flop, pct)

# ---- (b) share of warp instructions by role against the thread tile, GEMM 128x128x512 -----------------------
# F1D 1.3 table; json panel_b_tiles.<tile>.share_pct (% of warp instructions) and .macs_per_warp_instr.
# Trace run motivm-fig1tr-nt8-w4-iw1-m7300bc8-20261123 (DEBUG=2 traces, MACs = 8,388,608), direct-load (-gl) kernels,
# best CTA per tile; shared loads/stores are 0 in all five kernels (F1D 1.3).
ROLES = ["FMA", "global load", "integer/address", "spill/fill", "control/other"]  # bottom to top
TILES = ["1×1", "2×2", "4×4", "8×4", "8×8"]
TILE_KEYS = ["1x1", "2x2", "4x4", "8x4", "8x8"]
SHARES = {  # tile: (% of warp instructions in ROLES order, MACs per warp instruction)
    "1x1": ([21.22, 42.64, 30.21, 0.0, 5.93], 1.6975),   # rt-t1x1-b8x1-k8-gl
    "2x2": ([41.58, 41.69, 14.96, 0.0, 1.77], 3.3267),   # rt-t2x2-b8x1-k8-gl
    "4x4": ([56.70, 28.38, 6.10, 5.32, 3.51], 4.5356),   # rt-t4x4-b8x1-k8-gl (also the tuned-core stream, F1D 1.2)
    "8x4": ([37.39, 14.03, 2.75, 43.27, 2.56], 2.9912),  # rt-t8x4-b8x4-k8-gl
    "8x8": ([32.21, 8.06, 1.18, 57.98, 0.57], 2.5766),   # rt-t8x8-b8x4-k8-gl
}
for key, (sh, mpi) in SHARES.items():
    assert abs(sum(sh) - 100) < 0.05, (key, sum(sh))
    # every FMA runs on all 8 lanes (no divergence), so FMA share x 8 = MACs per warp instruction
    assert abs(sh[0] / 100 * 8 - mpi) < 0.002, (key, sh[0], mpi)
FMA_PCT = [SHARES[k][0][0] for k in TILE_KEYS]
assert [round(v) for v in FMA_PCT] == [21, 42, 57, 37, 32]
# Text claims (mot-work-per-instr): the 4x4 tile has the highest FMA share, 57 %, and 4.5 MACs per warp instruction.
assert FMA_PCT.index(max(FMA_PCT)) == 2 and round(max(FMA_PCT)) == 57
assert round(SHARES["4x4"][1], 1) == 4.5

# ---- (c) register-file reads against the thread tile (direct-load kernels, best CTA per tile) --------------
# F1D 2 table; json panel_c.<tile>.ideal_words_per_mac (= (r+c)/(r*c) [S], measured load lanes within 0.5 %)
# and .gpr_lane_reads_per_mac (traces; acct2 instrumented SimX agrees exactly). FMA floor 3.00 [S, measured].
WORDS = [2.0, 1.0, 0.5, 0.375, 0.25]
GPR_READS = [7.9629, 4.6924, 3.9348, 5.3802, 6.0485]
FMA_FLOOR = 3.0
for key, w in zip(TILE_KEYS, WORDS):
    r, c = (int(v) for v in key.split("x"))
    assert abs((r + c) / (r * c) - w) < 1e-9
assert min(GPR_READS) > FMA_FLOOR and GPR_READS.index(min(GPR_READS)) == 2
assert round(min(GPR_READS), 1) == 3.9

# ---- optional cross-check against the evidence JSON --------------------------------------------------------
if EVIDENCE.exists():
    ev = json.loads(EVIDENCE.read_text())
    for key in TILE_KEYS:
        e = ev["panel_b_tiles"][key]
        sh, mpi = SHARES[key]
        assert [round(e["share_pct"][r], 2) for r in ROLES] == sh, key
        assert round(e["macs_per_warp_instr"], 4) == mpi, key
    for key, w, g in zip(TILE_KEYS, WORDS, GPR_READS):
        e = ev["panel_c"][key]
        assert e["ideal_words_per_mac"] == w and round(e["gpr_lane_reads_per_mac"], 4) == g, key
        assert e["fma_lane_reads_per_mac"] == FMA_FLOOR, key
    print("cross-checked against", EVIDENCE)

# ---- style (LazyDP system: luminance ramp, four spines, hatches when the ramp runs out) --------------------
GRAY1, GRAY2, GRAY3 = "#E8E8E8", "#BFBFBF", "#808080"
plt.rcParams.update({
    "font.size": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.8,
    "hatch.linewidth": 0.5,
})
FS_SMALL = 6.5

W, H = 7.14, 1.36  # \textwidth = 516 pt
fig = plt.figure(figsize=(W, H))
BOT, TOP = 0.255, 0.95
ax_a = fig.add_axes([0.135, BOT, 0.172, TOP - BOT])
ax_b = fig.add_axes([0.468, BOT, 0.150, TOP - BOT])
ax_c = fig.add_axes([0.808, BOT, 0.184, TOP - BOT])


def panel_letter(letter, x):
    fig.text(x, 0.99, f"({letter})", fontsize=7.5, fontweight="bold", va="top", ha="left")


def frame(ax, grid_axis):
    ax.tick_params(length=2, pad=1.5)
    ax.grid(axis=grid_axis, ls=":", lw=0.5, color=GRAY3, zorder=0)
    ax.set_axisbelow(True)


# (a) horizontal bars, top to bottom in chain order
n = len(CHAIN)
ys = list(range(n))[::-1]
for y, (label, _, pct, _) in zip(ys, CHAIN):
    face = GRAY3 if label.startswith("+ 8") else GRAY2
    ax_a.barh(y, pct, height=0.62, color=face, edgecolor="black", linewidth=0.5, zorder=2)
    ax_a.text(pct + 0.8, y, f"{pct:.1f}", va="center", ha="left", fontsize=FS_SMALL, zorder=3)
ax_a.axvline(IDEAL, color="black", ls="--", lw=0.8, zorder=1)
ax_a.text(IDEAL - 0.8, ys[0] - 0.1, f"ideal\nSIMT {IDEAL:.0f}", va="center", ha="right", fontsize=FS_SMALL,
          linespacing=0.9)
ax_a.set_yticks(ys)
ax_a.set_yticklabels([c[0] for c in CHAIN], fontsize=FS_SMALL)
ax_a.set_ylim(-0.55, n - 0.45)
ax_a.set_xlim(0, 60)
ax_a.set_xticks([0, 20, 40, 60])
ax_a.set_xlabel("% of lane peak", labelpad=1)
frame(ax_a, "x")
ax_r = ax_a.twinx()
ax_r.set_ylim(ax_a.get_ylim())
ax_r.set_yticks(ys)
ax_r.set_yticklabels([c[3] for c in CHAIN], fontsize=FS_SMALL)
ax_r.tick_params(length=2, pad=1.5)
ax_r.set_ylabel("binding limit", labelpad=2, fontsize=FS_SMALL)
panel_letter("a", 0.002)

# (b) 100 % stacked bars: share of warp instructions by role per thread tile; FMA share printed in the FMA segment
STYLE = {  # role: (face, hatch); FMA darkest, then the ramp, a hatch where the ramp runs out
    "FMA": ("black", None),
    "global load": (GRAY3, None),
    "integer/address": (GRAY2, None),
    "spill/fill": ("white", "xxxx"),
    "control/other": (GRAY1, None),
}
xb = list(range(len(TILES)))
for x, key in zip(xb, TILE_KEYS):
    bottom = 0.0
    for role, v in zip(ROLES, SHARES[key][0]):
        if v == 0:
            continue
        face, hatch = STYLE[role]
        ax_b.bar(x, v, 0.68, bottom=bottom, color=face, hatch=hatch, edgecolor="black", linewidth=0.5, zorder=2)
        bottom += v
    fma = SHARES[key][0][0]
    ax_b.text(x, fma / 2, f"{fma:.0f}", ha="center", va="center", fontsize=FS_SMALL, color="white", zorder=3)
ax_b.set_xticks(xb)
ax_b.set_xticklabels(TILES, fontsize=FS_SMALL)
ax_b.set_xlim(-0.5, len(TILES) - 0.5)
ax_b.set_ylim(0, 100)
ax_b.set_yticks([0, 25, 50, 75, 100])
ax_b.set_xlabel("thread tile", labelpad=1)
ax_b.set_ylabel("% of warp\ninstructions", labelpad=1, linespacing=0.9)
frame(ax_b, "y")
handles = [Patch(facecolor=STYLE[r][0], hatch=STYLE[r][1], edgecolor="black", lw=0.5, label=r) for r in ROLES][::-1]
ax_b.legend(handles=handles, loc="center left", bbox_to_anchor=(1.03, 0.5), frameon=False, fontsize=FS_SMALL,
            handlelength=1.3, handleheight=0.9, handletextpad=0.4, labelspacing=0.3, borderaxespad=0.0)
panel_letter("b", 0.392)

# (c) words loaded and GPR reads per MAC against the thread tile, log2 y
xt = list(range(len(TILES)))
ax_c.plot(xt, GPR_READS, color="black", marker="o", ms=3.2, lw=1.0, zorder=3)
ax_c.plot(xt, WORDS, color=GRAY3, marker="s", ms=3.0, lw=1.0, mfc="white", mec=GRAY3, zorder=3)
ax_c.axhline(FMA_FLOOR, color="black", ls="--", lw=0.8, zorder=2)
ax_c.text(4.2, FMA_FLOOR * 0.9, "FMA: 3 reads/MAC", ha="right", va="top", fontsize=FS_SMALL - 0.5)
for x, g in zip(xt, GPR_READS):
    ax_c.text(x, g * 1.17, f"{g:.1f}", ha="center", va="bottom", fontsize=FS_SMALL - 0.5)
for x, w in ((0, WORDS[0]), (4, WORDS[4])):
    ax_c.text(x + (0.18 if x == 0 else -0.18), w * 0.82, f"{w:g}", ha="left" if x == 0 else "right", va="top",
              fontsize=FS_SMALL - 0.5, color="black")
ax_c.text(2.15, 0.62, "words loaded", ha="left", va="bottom", fontsize=FS_SMALL - 0.5, color="black")
ax_c.text(2.0, 10.8, "register reads", ha="center", va="center", fontsize=FS_SMALL - 0.5)
ax_c.set_yscale("log", base=2)
ax_c.set_ylim(0.125, 16)
ax_c.set_yticks([0.25, 1, 4, 16])
ax_c.set_yticklabels(["0.25", "1", "4", "16"])
ax_c.minorticks_off()
ax_c.set_xticks(xt)
ax_c.set_xticklabels(TILES, fontsize=FS_SMALL)
ax_c.set_xlim(-0.35, len(TILES) - 0.65)
ax_c.set_xlabel("thread tile", labelpad=1)
ax_c.set_ylabel("per MAC", labelpad=1)
frame(ax_c, "y")
panel_letter("c", 0.752)

fig.savefig(OUT)
print(f"wrote {OUT}")
