"""Fig. iw_area_scaling: WGMMA speedup over IW=1 against standalone-TCU area.

Areas are from the earlier standalone-TCU ASAP7 synthesis at NT=16 (IW=8
projected from IW<=4), recovered from the original iw_area_speedup_short.pdf;
speedups are the NT=16 column of Fig. eval_nt_iw_heatmaps (b). Styled to match
asic_nt_area_speedup.pdf (asic_figs.py).

Run from the repo root:
    python3 hpca2027-latex-template/fig/src/asic_iw.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).parents[1] / "iw_area_speedup_short.pdf"

plt.rcParams.update({"font.size": 7, "pdf.fonttype": 42, "ps.fonttype": 42})
LABEL = dict(fontsize=8.5, fontweight="bold")

IW = [1, 2, 4, 8]
TCU_K = [58.6, 115.6, 230.6, 460.6]  # k um^2; IW=8 projected
SPEEDUP = {  # Fig. eval_nt_iw_heatmaps (b), NT=16
    128: [1.00, 1.37, 1.67, 1.70],
    256: [1.00, 1.39, 1.68, 1.77],
    512: [1.00, 1.41, 1.71, 1.79],
    1024: [1.00, 1.41, 1.69, 1.81],
}
STYLE = {128: ("#1f77b4", "o"), 256: ("#ff7f0e", "s"),
         512: ("#2ca02c", "^"), 1024: ("#d62728", "D")}

fig, ax = plt.subplots(figsize=(3.4, 1.7))
for k, ys in SPEEDUP.items():
    c, m = STYLE[k]
    ax.plot(TCU_K, ys, "--", marker=m, color=c, lw=1.2, ms=3.5, label=f"$K$={k}")
for n, x, y in zip(IW, TCU_K, [max(v[i] for v in SPEEDUP.values()) for i in range(4)]):
    ax.annotate(f"IW={n}", (x, y), textcoords="offset points",
                xytext=(0, 5), ha="center", fontsize=7)
ax.set_xscale("log", base=2)
ax.set_xticks(TCU_K)
ax.set_xticklabels([f"{x:.1f}" for x in TCU_K])
ax.minorticks_off()
ax.set_xlim(44, 610)
ax.set_ylim(0.9, 2.12)
ax.set_yticks([1.0, 1.2, 1.4, 1.6, 1.8])
ax.set_xlabel("TCU area (k$\\mathbf{\\mu}$m$^\\mathbf{2}$)", labelpad=1, **LABEL)
ax.set_ylabel("Speedup", labelpad=2, **LABEL)
ax.tick_params(length=2, pad=1.5)
ax.grid(alpha=0.3, lw=0.5)
ax.legend(loc="lower right", ncol=2, fontsize=7.5, handlelength=1.8,
          columnspacing=1.0, labelspacing=0.2, borderpad=0.3, framealpha=0.9)
fig.tight_layout(pad=0.15)
fig.savefig(OUT)
