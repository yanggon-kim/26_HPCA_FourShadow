# FourShadow (ISPASS 2027): outline
Synced with: the commit that adds Section III (Motivation); body ends p. 13 col R (refs heading y 629); captured so far: Section III only. The other sections carry no
`% P:` anchors yet and are to be captured before their next structural change.
Check: `main.tex` inputs files relative to the repo root, so run the check on a copy of `main.tex` placed at the repo root
(e.g. in a scratch copy of the repo): `python3 <skill-dir>/scripts/check_outline.py outline.md main_check.tex`.

## III. Motivation  (hpca2027-latex-template/2_3_motivation.tex)
Sources (Part 4, read-only): `00_doc/vortex-wgdxa2k/results/MOTIVATION_MASTER.md` [MM], `MOTIV_MASTER_FQ16.md` [FQ16],
`MOTIV_MASTER_TC_TABLES.md` [TCT]; plan `00_doc/ispass_direction/motivation/MOTIVATION_PAGE_PLAN.md` §0, §3.1.
Selection rule: only inefficiencies a SIMT design cannot tune away are points; the tunable limits form the baseline.

- **[mot-setting]** (opener, no head)
  - Message: Even the best of 55 SIMT kernels reaches a small share of SIMT-only Vortex's lane peak, so the section first tunes the core and then measures four inefficiencies tuning leaves.
  - Floats: —
  - Numbers: 8 threads, 4 warps, IW 1, peak 16 FLOP/cycle [S]; 55 variants ← MM §0/§2 (FQ16 §6 says 45: open); 17 % (2.71 FLOP/cycle, 128×128×512) ← FQ16 §2 ref row
  - Cites: —
  - Links: → mot-tuned-baseline, mot-work-per-instr, mot-register-reads, mot-load-granularity, mot-gemv-bytes
- **[mot-tuned-baseline]** "Tuned baseline."
  - Message: Four limits of the reference core (FPU queue, flags ordering, dispatch credits, register banks) are microarchitectural, and removing them lifts the GEMM to under half of the peak, below an ideal-SIMT cap that the instruction mix sets.
  - Floats: Fig. fig:motiv_simt(a) (first cite)
  - Numbers: 17 % → 45 % (44.9, b8x2-gl) ← FQ16 §2, §5b.4; 57 % [D] = 2·4.54/16 ← TCT F; tuned core NW 16, FQ 16, DQ 8, 8 GPR banks
  - Cites: —
  - Links: ← mot-setting; TODO(main): evaluation SIMT baseline differs (sec:eval_threads)
- **[mot-work-per-instr]** "Work per instruction."
  - Message: A SIMT instruction does at most one MAC per lane, and non-FMA instructions lower the average, which sets the ideal-SIMT cap.
  - Floats: — (refers to Fig. fig:motiv_simt(a))
  - Numbers: 4.5 MACs per warp instruction (4.54) vs 8 ← TCT F; 57 % ← mot-tuned-baseline
  - Cites: —
  - Links: → mot-common-cause (sec:eval_threads, sec:eval_iw)
- **[mot-register-reads]** "Register-file reads."
  - Message: Every SIMT MAC reads its operands from the register file, three registers per FMA, whatever the thread tile.
  - Floats: —
  - Numbers: 3 reads per FMA [S]; 3.9 GPR lane-reads per MAC (3.935) ← TCT F/J; FMA share of bank conflicts 708,352 / 725,648 (printed as "almost all") ← TCT F
  - Cites: —
  - Links: → mot-common-cause (sec:eval_nrc)
- **[mot-load-granularity]** "Load granularity."
  - Message: Operands enter the register file one element per lane per load instruction, so warp-shared values are copied into every lane, and shared-memory staging adds instructions instead of removing loads.
  - Floats: —
  - Numbers: one load/store instruction per 13 MACs (0.0745) ← TCT G; a third of instructions are LSU (33.8 %) ← TCT F; copies printed without a number (28 of 64 words is [D] from the kernel source)
  - Cites: —
  - Links: → mot-common-cause (sec:bg_smem, sec:eval_delay_a)
- **[mot-gemv-bytes]** "Bytes in decode GEMV."
  - Message: Decode GEMV can gain only from fewer bytes, and on SIMT narrow and compressed weight formats add instructions and run slower than FP32.
  - Floats: Fig. fig:motiv_simt(b) (first cite)
  - Numbers: weight bytes 0.25–0.53× [S/D]; speed 0.7–0.8× (0.70/0.73/0.79/0.72 from cycles) ← TCT B gpr8 rows
  - Cites: —
  - Links: → mot-common-cause (sec:eval_sparse); TODO(main): measured DRAM bytes on the tuned core 0.95/0.69/0.29/0.56×
- **[mot-common-cause]** (closing, no head)
  - Message: The four inefficiencies share one cause, a scalar MAC per lane as SIMT's unit of work, which a tensor core replaces with a tile operation and a sparse tensor core extends to compressed weights; FourShadow builds them and the evaluation varies the parameter behind each.
  - Floats: —
  - Numbers: —
  - Cites: —
  - Links: ← mot-work-per-instr, mot-register-reads, mot-load-granularity, mot-gemv-bytes; → sec:design, sec:eval_threads, sec:eval_iw, sec:eval_nrc, sec:bg_smem, sec:eval_delay_a, sec:eval_sparse (gaps: plan §4)

## Float map (Section III)
| float | label | source | first-citing id | lands |
|---|---|---|---|---|
| Fig. 1, one column, (a)(b) | fig:motiv_simt | 2_3_motivation.tex | mot-tuned-baseline | PDF p. 3, left column top (section starts p. 2 right) |
