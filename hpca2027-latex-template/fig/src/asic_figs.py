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

# ---- (2) Sub-core area: Ten-Four Fig. 9(b) shares, TCU parts listed under it
# The slice shares are Ten-Four's sub-core breakdown; the TCU is split in the
# ratios of the E3-D-NT4 TCU sub-components (asic_e3d_breakdown.csv)
parts = {r["component"]: float(r["area_um2"]) for r in read("asic_e3d_breakdown.csv")}
TCU_PCT = 36.0
slices = [
    ("FPU", 25.0, "#3b8beb"),
    ("Register File", 16.0, "#17a589"),
    ("Issue", 10.0, "#e0518d"),
    ("Shared Memory", 3.7, "#c98a06"),
    ("LSU", 3.0, "#ec7063"),
    ("ALU", 2.8, "#1e8a1e"),
    ("Warp Scheduler", 2.6, "#9b8fe8"),
    ("Rest of Core", 1.0, "#a6a6a6"),
    ("TCU", TCU_PCT, "#e4572e"),
]
total = 100.0  # Ten-Four's rounded shares sum to 100.1
pct = lambda v: 100 * v / total
tcu_parts = [
    ("FEDP Datapath", parts["TCU - FEDP datapath"]),
    ("Block Glue", parts["TCU - block glue"]),
    ("AGU + Dispatch", parts["TCU - AGU + lane dispatch/gather"]),
    ("WGMMA Buffers + Ctrl.",
     parts["TCU - WGMMA tile buffers"] + parts["TCU - WGMMA control"]),
]
tcu_um2 = sum(v for _, v in tcu_parts)
tcu_parts = [(sub, TCU_PCT * v / tcu_um2) for sub, v in tcu_parts]
tcu = TCU_PCT
INSIDE = 7.0  # % threshold for an inside label

fig = plt.figure(figsize=(3.4, 2.0))
ax = fig.add_axes([0.0, 0.0, 0.545, 1.0])
wedges, _ = ax.pie([v for _, v, _ in slices], colors=[c for *_, c in slices],
                   startangle=90, counterclock=False, radius=1.0,
                   wedgeprops=dict(edgecolor="white", linewidth=0.5))
ax.set_aspect("equal")
for w, (name, v, _) in zip(wedges, slices):
    if pct(v) < INSIDE:
        continue
    ang = math.radians((w.theta1 + w.theta2) / 2)
    r = 0.55 if pct(v) > 20 else 0.7
    ax.text(r * math.cos(ang), r * math.sin(ang),
            f"{name.replace(' ', chr(10))}\n{pct(v):.0f}%",
            ha="center", va="center", fontsize=7, fontweight="bold",
            color="white", linespacing=0.95)

small = [(w, n, v) for w, (n, v, _) in zip(wedges, slices) if pct(v) < INSIDE]
leg = fig.legend([Patch(facecolor=w.get_facecolor()) for w, *_ in small],
                 [f"{n}  {pct(v):.1f}%" for _, n, v in small],
                 loc="upper left", bbox_to_anchor=(0.555, 0.99), fontsize=7.5,
                 handlelength=0.9, handleheight=0.9, handletextpad=0.5,
                 labelspacing=0.3, borderpad=0.2, frameon=False)
lines = [f"{sub}  {pct(sv):.1f}%" for sub, sv in tcu_parts]
fig.text(0.57, 0.37, f"TCU ({pct(tcu):.1f}%)", ha="left", va="bottom",
         fontsize=7.5, fontweight="bold", color="#e4572e")
fig.text(0.57, 0.35, "\n".join(lines), ha="left", va="top", fontsize=7,
         linespacing=1.3)
fig.savefig(FIG / "asic_area_breakdown.pdf")
plt.close(fig)
