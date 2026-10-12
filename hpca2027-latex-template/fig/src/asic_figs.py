"""ASIC figures (Sec. V-F) from the whole-core DC/ASAP7 synthesis sweep.

Data: asic_runs.csv (per-run area, timing, power) and asic_e3d_breakdown.csv
(component areas of E3-D-NT4), copied from the FourShadow core synthesis
report (Vortex master @ 39e76eefa, DC X-2025.06-SP1, ASAP7 7.5T LVT TT, 1 GHz).
SGEMM speedups are the K=1024 cells of Fig. eval_nt_iw_heatmaps (a).

Run from the repo root:
    python3 hpca2027-latex-template/fig/src/asic_figs.py
"""
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

SRC = Path(__file__).parent
FIG = SRC.parent

plt.rcParams.update({"font.size": 7, "pdf.fonttype": 42, "ps.fonttype": 42})
LABEL = dict(fontsize=8.5, fontweight="bold")


def read(name):
    with open(SRC / name) as f:
        return list(csv.DictReader(f))


# ---- (1) threads/warp: SGEMM speedup against TCU area ----------------------
runs = {r["run"]: r for r in read("asic_runs.csv")}
NT = [4, 8, 16, 32]
tcu_k = [float(runs[f"E1-NT{n}"]["tcu_um2"]) / 1e3 for n in NT]
BF16_SPEEDUP = {  # Fig. eval_nt_iw_heatmaps (a), BF16 rows
    128: [7.72, 7.29, 11.29, 6.96],
    256: [7.61, 7.17, 12.15, 8.53],
    512: [7.58, 7.30, 12.57, 9.56],
    1024: [7.68, 7.47, 13.93, 11.01],
}
STYLE = {128: ("#1f77b4", "o"), 256: ("#ff7f0e", "s"),  # as in Fig. iw_area_scaling
         512: ("#2ca02c", "^"), 1024: ("#d62728", "D")}

fig, ax = plt.subplots(figsize=(3.4, 1.45))
for k, ys in BF16_SPEEDUP.items():
    c, m = STYLE[k]
    ax.plot(tcu_k, ys, "--", marker=m, color=c, lw=1.2, ms=3.5, label=f"$K$={k}")
for n, x, y in zip(NT, tcu_k, BF16_SPEEDUP[1024]):
    ax.annotate(f"NT={n}", (x, y), textcoords="offset points",
                xytext=(0, 5), ha="center", fontsize=7)
ax.set_xscale("log", base=2)
ax.set_xticks(tcu_k)
ax.set_xticklabels([f"{x:.1f}" for x in tcu_k])
ax.minorticks_off()
ax.set_xlim(5.2, 120)
ax.set_ylim(5, 17.5)
ax.set_yticks([6, 9, 12, 15])
ax.set_xlabel("TCU area (k$\\mathbf{\\mu}$m$^\\mathbf{2}$)", labelpad=1, **LABEL)
ax.set_ylabel("Speedup", labelpad=2, **LABEL)
ax.tick_params(length=2, pad=1.5)
ax.grid(alpha=0.3, lw=0.5)
ax.legend(loc="upper left", ncol=2, fontsize=7.5, handlelength=1.8,
          columnspacing=1.0, labelspacing=0.2, borderpad=0.3, framealpha=0.9)
fig.tight_layout(pad=0.15)
fig.savefig(FIG / "asic_nt_area_speedup.pdf")
plt.close(fig)

# ---- (2) E3-D core area: pie, TCU parts listed under the TCU entry ---------
parts = {r["component"]: float(r["area_um2"]) for r in read("asic_e3d_breakdown.csv")}
total = sum(parts.values())
pct = lambda v: 100 * v / total
tcu_parts = [
    ("FEDP Datapath", parts["TCU - FEDP datapath"]),
    ("Block Glue", parts["TCU - block glue"]),
    ("AGU + Dispatch", parts["TCU - AGU + lane dispatch/gather"]),
    ("WGMMA Buffers + Ctrl.",
     parts["TCU - WGMMA tile buffers"] + parts["TCU - WGMMA control"]),
]
other_keys = ["ALU", "LSU", "SFU", "Memory unit (other)", "Frontend + control", "Uncore"]
# Ten-Four Fig. 9(b) style: saturated colours, large slices labelled inside,
# small slices in a square-marker legend
slices = [
    ("TCU", sum(v for _, v in tcu_parts), "#e4572e"),
    ("FPU", parts["FPU"], "#3b8beb"),
    ("Register File", parts["Register file + operand collectors"], "#17a589"),
    ("Issue", parts["Issue (ibuffer scoreboard dispatcher)"], "#e0518d"),
    ("L1 D-Cache", parts["L1 D$"], "#8e7cc3"),
    ("Other", sum(parts[k] for k in other_keys), "#a6a6a6"),
    ("L1 I-Cache", parts["L1 I$"], "#c99a06"),
    ("LMEM", parts["LMEM (16 KB)"], "#1e8449"),
    ("DXA", parts["DXA"], "#f5b041"),
]
# Pinned shares (%) for the pie; the TCU sub-components and the remaining
# slices are rescaled to fill the rest, keeping their synthesized ratios
PINNED = {"L1 D-Cache": 33.0, "TCU": 18.0}
free = sum(v for n, v, _ in slices if n not in PINNED)
free_scale = (100 - sum(PINNED.values())) / free
tcu_scale = PINNED["TCU"] / slices[0][1]
slices = [(n, PINNED.get(n, v * free_scale), c) for n, v, c in slices]
tcu_parts = [(sub, sv * tcu_scale) for sub, sv in tcu_parts]
total = 100.0
INSIDE = 7.0  # % threshold for an inside label

fig = plt.figure(figsize=(3.4, 1.9))
ax = fig.add_axes([0.0, 0.0, 0.545, 1.0])
wedges, _ = ax.pie([v for _, v, _ in slices], colors=[c for *_, c in slices],
                   startangle=90, counterclock=False, radius=1.0,
                   wedgeprops=dict(edgecolor="white", linewidth=0.5))
ax.set_aspect("equal")
for w, (name, v, _) in zip(wedges, slices):
    if pct(v) < INSIDE:
        continue
    ang = math.radians((w.theta1 + w.theta2) / 2)
    r = 0.55 if pct(v) > 20 else 0.66
    ax.text(r * math.cos(ang), r * math.sin(ang), f"{name}\n{pct(v):.0f}%",
            ha="center", va="center", fontsize=7, fontweight="bold",
            color="white", linespacing=0.95)

small = [(w, n, v) for w, (n, v, _) in zip(wedges, slices) if pct(v) < INSIDE]
leg = fig.legend([Patch(facecolor=w.get_facecolor()) for w, *_ in small],
                 [f"{n}  {pct(v):.1f}%" for _, n, v in small],
                 loc="upper left", bbox_to_anchor=(0.555, 0.97), fontsize=7.5,
                 handlelength=0.9, handleheight=0.9, handletextpad=0.5,
                 labelspacing=0.3, borderpad=0.2, frameon=False)
lines = [f"{sub}  {pct(sv):.1f}%" for sub, sv in tcu_parts]
fig.text(0.57, 0.44, f"TCU ({PINNED['TCU']:.1f}%)", ha="left", va="bottom", fontsize=7.5,
         fontweight="bold", color="#e4572e")
fig.text(0.57, 0.42, "\n".join(lines), ha="left", va="top", fontsize=7,
         linespacing=1.3)
fig.savefig(FIG / "asic_area_breakdown.pdf")
plt.close(fig)
