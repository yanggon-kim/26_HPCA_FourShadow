# FourShadow (ISPASS 2027): outline
Synced with: the commit that adds the three-panel Fig. 1 (Section III); captured so far: Section III only. The other sections carry no
`% P:` anchors yet and are to be captured before their next structural change.
Check: `main.tex` inputs files relative to the repo root, so run the check on a copy of `main.tex` placed at the repo root
(e.g. in a scratch copy of the repo): `python3 <skill-dir>/scripts/check_outline.py outline.md main_check.tex`.

## III. Motivation  (hpca2027-latex-template/2_3_motivation.tex)
Sources (Part 4, read-only): `00_doc/vortex-wgdxa2k/results/MOTIVATION_MASTER.md` [MM], `MOTIV_MASTER_FQ16.md` [FQ16],
`MOTIV_MASTER_TC_TABLES.md` [TCT], `MOTIV_FIG1_DATA.md` + `motiv_fig1_data.json` [F1D]; plan `00_doc/ispass_direction/motivation/MOTIVATION_PAGE_PLAN.md` §0, §3.1.
Selection rule: only inefficiencies a SIMT design cannot tune away are points; the tunable limits form the baseline.

- **[mot-setting]** (opener, no head)
  - Message: Even the best of 45 FP32 SIMT kernels reaches a small share of SIMT-only Vortex's lane peak, so the section first tunes the core and then measures four inefficiencies tuning leaves.
  - Floats: —
  - Numbers: 8 threads, 4 warps, IW 1, peak 16 FLOP/cycle [S]; 45 FP32 variants ← F1D §3 (MM's 55 rows = 45 FP32 + 10 BF16/INT8-storage); 17 % (2.71 FLOP/cycle, 128×128×512) ← FQ16 §2 ref row
  - Cites: —
  - Links: → mot-tuned-baseline, mot-work-per-instr, mot-register-reads, mot-load-granularity, mot-gemv-bytes
- **[mot-tuned-baseline]** "Tuned baseline."
  - Message: Four limits of the reference core (FPU queue, flags ordering, dispatch credits, register banks) are microarchitectural, and removing them lifts the GEMM to under half of the peak, below an ideal-SIMT cap that the instruction mix sets.
  - Floats: Fig. fig:motiv_simt(a) (first cite)
  - Numbers: 17 % → 45 % (44.9, b8x2-gl) ← FQ16 §2, §5b.4; 57 % [D] = 2·4.54/16 ← TCT F; tuned core NW 16, FQ 16, DQ 8, 8 GPR banks
  - Cites: —
  - Links: ← mot-setting; TODO(main): evaluation SIMT baseline differs (sec:eval_threads)
- **[mot-work-per-instr]** "Work per instruction."
  - Message: A SIMT instruction does at most one MAC per lane, and loads, address arithmetic, spills and control, which perform no MAC, make up over 40 % of even the fastest kernel's instructions; this mix sets the ideal-SIMT cap.
  - Floats: Fig. fig:motiv_simt(b) (first cite)
  - Numbers: > 40 % non-FMA (100 − 56.7 = 43.3 %, direct RT 4×4 `rt-t4x4-b8x1-k8-gl`) ← F1D §1; 4.5 MACs per warp instruction (4.536) vs 8 ← F1D §1 / TCT F; 57 % ← mot-tuned-baseline
  - Cites: —
  - Links: → mot-common-cause (sec:eval_threads, sec:eval_iw)
- **[mot-register-reads]** "Register-file reads."
  - Message: A larger thread tile cuts the operand words loaded per MAC, but register reads per MAC never fall below the three of an FMA and bottom out at a mid-size tile, between address arithmetic (small tiles) and spills (large tiles).
  - Floats: Fig. fig:motiv_simt(c) (first cite)
  - Numbers: 3 reads per FMA [S, measured 3.00]; words loaded per MAC 2 → 0.25 (tile 1×1 → 8×8) [S, measured within 0.5 %] ← F1D §2; minimum 3.9 GPR lane-reads per MAC at 4×4 (3.935) ← F1D §2 (curve 7.96 / 4.69 / 3.94 / 5.38 / 6.05)
  - Cites: —
  - Links: → mot-common-cause (sec:eval_nrc)
- **[mot-load-granularity]** "Load granularity."
  - Message: Operands enter the register file one element per lane per load instruction, so warp-shared values are copied into every lane, and shared-memory staging adds instructions instead of removing loads.
  - Floats: —
  - Numbers: one load/store instruction per 13 MACs (0.0745) ← TCT G; a third of instructions are LSU (33.8 %) ← TCT F; copies printed without a number (28 of 64 words is [D] from the kernel source)
  - Cites: —
  - Links: → mot-common-cause (sec:bg_smem, sec:eval_delay_a)
- **[mot-gemv-bytes]** "Bytes in decode GEMV."
  - Message: Decode GEMV can gain only from fewer bytes, but on SIMT its load instructions bind before DRAM does, so narrow and compressed weights add instructions per element without saving time.
  - Floats: —
  - Numbers: a quarter of the DRAM bandwidth = FP32 GEMV 9.4 B/cycle of the same-core streaming rate 39.5 B/cycle (24 %) ← F1D §4; INT8 a quarter of the FP32 bytes (storage 0.25×; measured 0.25× on the 4-bank cores) and 0.8× speed (0.788 / 0.792 / 0.789 on three cores) ← F1D §4
  - Cites: —
  - Links: → mot-common-cause (sec:eval_sparse)
- **[mot-common-cause]** (closing, no head)
  - Message: The four inefficiencies share one cause, a scalar MAC per lane as SIMT's unit of work, which a tensor core replaces with a tile operation and a sparse tensor core extends to compressed weights; FourShadow builds them and the evaluation varies the parameter behind each.
  - Floats: —
  - Numbers: —
  - Cites: —
  - Links: ← mot-work-per-instr, mot-register-reads, mot-load-granularity, mot-gemv-bytes; → sec:design, sec:eval_threads, sec:eval_iw, sec:eval_nrc, sec:bg_smem, sec:eval_delay_a, sec:eval_sparse (gaps: plan §4)

## Float map (Section III)
| float | label | source | first-citing id | lands |
|---|---|---|---|---|
| Fig. 1, figure*, (a)(b)(c) in one row, `fig/motiv_simt3.pdf` (script `fig/src/motiv_simt3.py`) | fig:motiv_simt | 2_3_motivation.tex | mot-tuned-baseline ((b) mot-work-per-instr, (c) mot-register-reads) | PDF p. 3 top, both columns (section starts p. 2 right) |
