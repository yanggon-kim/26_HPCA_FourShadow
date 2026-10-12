"""Fig. nrc_h100: FP16 WMMA/WGMMA normalized cycles vs. K, FourShadow and H100.

Data: nrc_h100_scaling.csv (final_fourshadow_h100_fp16_normalized_plot_data.csv);
each platform is normalized to its WGMMA cycles at K=64 (NRC=8 on FourShadow).

Run from the repo root:
    python3 hpca2027-latex-template/fig/src/nrc_h100_scaling.py
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SRC = Path(__file__).with_suffix(".csv")
OUT = Path(__file__).parents[1] / "nrc_h100_scaling.pdf"

series = {}
with open(SRC) as f:
    for r in csv.DictReader(f):
        key = (r["platform"], r["kernel"], int(r["NRC"]) if r["NRC"] else None)
        series.setdefault(key, []).append((int(r["K"]), float(r["normalized_cycles"])))
series = {k: [y for _, y in sorted(v)] for k, v in series.items()}

K = sorted({int(r["K"]) for r in csv.DictReader(open(SRC))})
FOURSHADOW_WGMMA = {n: series[("FourShadow", "WGMMA", n)] for n in (8, 16, 32)}
FOURSHADOW_WMMA = series[("FourShadow", "WMMA", 8)]
H100_WGMMA = series[("H100", "WGMMA", None)]
H100_WMMA = series[("H100", "WMMA", None)]

NRC_COLOR = {8: "#1f77b4", 16: "#2ca02c", 32: "#ff7f0e"}

plt.rcParams.update({
    "font.size": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

fig, ax = plt.subplots(figsize=(3.4, 1.85))
x = range(len(K))
lw, ms = 1.2, 3.2

for nrc, ys in FOURSHADOW_WGMMA.items():
    ax.plot(x, ys, "-o", color=NRC_COLOR[nrc], lw=lw, ms=ms)
ax.plot(x, FOURSHADOW_WMMA, "--o", color=NRC_COLOR[8], lw=lw, ms=ms)
ax.plot(x, H100_WGMMA, "-D", color="black", lw=lw, ms=ms)
ax.plot(x, H100_WMMA, "--D", color="black", lw=lw, ms=ms)

ax.set_xticks(list(x))
ax.set_xticklabels([str(k) for k in K])
ax.set_xlim(-0.2, len(K) - 0.8)
ax.set_ylim(0.3, 6.3)
ax.set_yticks(range(1, 7))
ax.set_xlabel("K", fontsize=8.5, fontweight="bold", labelpad=1)
ax.set_ylabel("Normalized cycles", fontsize=8.5, fontweight="bold", labelpad=2)
ax.tick_params(length=2, pad=1.5)
ax.grid(alpha=0.3, lw=0.5)

handles = [
    Line2D([], [], color="black", ls="-", lw=lw, label="WGMMA"),
    Line2D([], [], color="black", ls="--", lw=lw, label="WMMA"),
    Line2D([], [], color="black", ls="", marker="D", ms=ms, label="H100"),
    Line2D([], [], color="black", ls="", marker="o", ms=ms, label="FourShadow"),
    *(Line2D([], [], color=c, ls="-", marker="o", lw=lw, ms=ms, label=f"NRC={n}")
      for n, c in NRC_COLOR.items()),
]
ax.legend(handles=handles, loc="upper left", ncol=2, fontsize=7.5,
          handlelength=1.8, handletextpad=0.4, columnspacing=0.9,
          labelspacing=0.25, borderpad=0.3, borderaxespad=0.3, framealpha=0.9)

fig.tight_layout(pad=0.15)
fig.savefig(OUT)
