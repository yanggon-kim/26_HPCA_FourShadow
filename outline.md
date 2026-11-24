# FourShadow (ISPASS 2027): outline
Synced with: the commit that shortens the prior-work part of Section IV to one paragraph and widens the FourShadow distinction to two; captured so far: Sections II, III and IV.
The other sections carry no `% P:` anchors yet and are to be captured before their next structural change.
Check: `main.tex` inputs files relative to the repo root, so run the check on a copy of `main.tex` placed at the repo root
(e.g. in a scratch copy of the repo): `python3 <skill-dir>/scripts/check_outline.py outline.md main_check.tex`.

## II. Background  (hpca2027-latex-template/2_background.tex)
Sources (read-only): main's `00_doc/ispass_direction/riscv_vs_nvidia/PRELIM_REPORT.md` [PR] (§3.1 ISA, §3.2 scheduling, §3.3 T1,
§3.3a occupancy, §3.5 configurability, §5 do-not-claim list) and `web_facts.md` [WF]; part4 `00_doc/vortex-wgdxa2k/results/RISCV_VS_NVIDIA_VORTEX_SIDE.md`
[P4] (§1 static ISA, §3 architecture facts, pinned `d6426cca1`); part1 `02_nvidia/runs/riscv-vs-nvidia-20261118/tables.md` [T1];
`00_doc/ispass_direction/reference_repos.md` [RR]; Vortex sources (pinned `01_github/vortex-wgdxa2k`, master README `7300bc849`).
Rules (user, 2026-11-23): about one page; one message and its own data per paragraph; Vortex vs NVIDIA speed is never stated; Background defines and
stops (no FourShadow design preview); FourShadow named once, last. Do-not-claim [PR §5]: Vortex slower/worse; NVIDIA has no scoreboard;
Turing/Ampere reverse engineering extended to Blackwell.

- **[bg-roadmap]** (section opener, no head)
  - Message: Vortex is the GPU this paper builds on, and the section describes its organization, the research that builds on it, and how it differs from NVIDIA GPUs.
  - Floats: —
  - Numbers: —
  - Cites: —
  - Links: → bg-vortex-stack, bg-platform, bg-nv-frame
- **[bg-vortex-stack]** (II-A "The Vortex GPU", `sec:bg_hierarchy`)
  - Message: Vortex is an open-source RISC-V GPU released as a full stack of synthesizable RTL, a cycle-level simulator and an LLVM-based compiler, so a design can be prototyped in SimX and then implemented in the RTL.
  - Floats: —
  - Numbers: —
  - Sources: master `README.md:5-7` (full stack, SimX, RTL simulator, FPGAs; prototype in SimX then RTL), `:44-48` (OpenCL 1.2, Vulkan, HIP), `:134` (VOLT); pinned `hw/syn/{altera,xilinx,synopsys,yosys}` [S]
  - Cites: vortex, 10.1145/3771775.3786275 (VOLT)
  - Links: ← bg-roadmap
- **[bg-vortex-hierarchy]**
  - Message: A Vortex processor nests cores in sockets and clusters, each core runs NW warps of NT threads and issues from IW warps per cycle, NT sets the width of every per-thread structure, and all of these are build-time parameters.
  - Floats: —
  - Numbers: — (symbols NT, NW, IW defined here)
  - Sources: pinned `hw/rtl/VX_socket.sv:142-148,194-196` (I- and D-cache clusters per socket), `VX_cluster.sv:211-237` (L2 per cluster), `VX_config.toml:4-6,47-55,92` [S]
  - Cites: —
  - Links: → sec:bg_issue (issue slots), bg-nv-config
- **[bg-platform]** (II-B "Vortex as a Research Platform", `sec:bg_platform`)
  - Message: Prior work uses the open Vortex stack in three ways, as a base for new hardware units, as RTL to synthesize, and as a platform for design-space exploration; tensor-core work on Vortex is left to Section IV.
  - Floats: —
  - Numbers: 10× fewer dynamic instructions on average ← Sarda et al. arXiv 2512.00032 abstract + §VI-2; 32 cores on Stratix 10 ← vortex (MICRO'21 abstract); 16 nm ← e-GPU arXiv 2505.08421 abstract
  - Sources: Gouk et al.: HotStorage'24 abstract (CXL root ports, controller at RTL level) + CXL-GPU (arXiv 2506.15601v1 = IEEE Micro 45(6)) "our controller's RTL design was embedded" in Vortex; Sarda et al. arXiv 2512.00032 abstract, §VI-1 (extensions in the cycle-accurate model and the RTL), §VI-4 (Vortex RTL ported to ASIC); METASAT arXiv 2502.21027 abstract + §II (VCU118, one compute unit, 4 warps, 4 threads), OSSMPIC 2025 workshop; e-GPU arXiv 2505.08421 abstract + §III-A ("The compute unit is based on the Vortex core"); Pu et al. arXiv 2505.03102 abstract; Han et al. arXiv 2109.00673 §1 (CUDA → NVVM → SPIR-V → POCL → RISC-V GPU), Table 2 (Vortex v0.2.2); VortexSynth arXiv 2610.12661 abstract + §3 (Vortex candidates run on SimX). Skybox (ASPLOS'23) still omitted: no readable primary source states its Vortex basis (par.nsf.gov 10518427 is the Vortex MICRO'21 paper; web.archive.org unreachable)
  - Cites: gouk2024breaking, gouk2025cxlgpu, sarda2025decoupled, vortex, bonet2025metasat, machetti2025egpu, pu2025warplevel, han2021cuda, pu2026vortexsynth
  - Links: ← bg-vortex-stack; → sec:related (tensor-core work on Vortex: Virgo, CoopWarp, Ten-Four, RoadBlock moved there)
- **[bg-nv-frame]** (II-C "Vortex and NVIDIA GPUs", `sec:bg_nvidia`; opener, no head)
  - Message: Vortex adopts the SIMT programming model of NVIDIA GPUs but not the machine beneath it, which differs in ISA, registers per thread and configurability.
  - Floats: —
  - Numbers: —
  - Sources: [WF] §C items 1, 3 (abstractions borrowed on purpose); [PR] §2
  - Cites: —
  - Links: → bg-nv-isa, bg-nv-registers, bg-nv-config
- **[bg-nv-isa]** "ISA."
  - Message: Vortex runs standard RISC-V with its GPU instructions in the custom opcode space and resolves hazards with a hardware scoreboard, whereas NVIDIA's documented ISA is the virtual PTX and its machine instructions carry compiler-set scheduling fields, so NVIDIA's timing is partly in the binary and Vortex's in open RTL and SimX.
  - Floats: —
  - Numbers: 16 B per SASS instruction [M, sm_120 and sm_90, PR §3.1]; 4 B per Vortex instruction [M, P4 §1, RVC off]; control fields [R Huerta, Turing/Ampere; validated on sm_120/sm_90, PR §3.2]
  - Cites: nvidia2026ptxisa (Section 1.1), nvidia2026binutils (Section 4), 10.1145/3725843.3756041 (Huerta)
  - Links: —
- **[bg-nv-registers]** "Registers per thread."
  - Message: A RISC-V thread has a fixed 32 + 32 registers that Vortex builds for every warp, against up to 255 allocated from a shared per-SM file on NVIDIA, and on the same GEMM source this budget alone sets where register tiling stops.
  - Floats: —
  - Numbers: 32 int + 32 FP [S, `VX_gpu_pkg.sv:52-65`, `VX_opc_unit.sv:49`]; 255 per thread, 64K per SM ← nvidia2026cudaguide Table 34; 16×8 tile = 128 accumulators, 255 regs, no spill [M, T1 sm_120]; Vortex 4×4: 29/29 int + 32/32 FP, 48/41 spill ld/st [M, T1/P4 §1] — text says the FP file runs out at 4×4 (2×2: 15 FP regs, integer spills 11/12 already; not printed) [M, T1]; NVIDIA maxrregcount 32 at 4×4: 160 B spill stores [M, T1]
  - Cites: nvidia2026cudaguide
  - Links: → mot-setting (thread tile defined there; Background uses it with a forward pointer); mot-register-reads owns the spill-driven register reads (no datum repeated)
- **[bg-nv-config]** "Configurability."
  - Message: The warp shape and issue width of Vortex are build-time parameters, whereas every NVIDIA warp has 32 threads and each chip fixes its SM organization.
  - Floats: Table tab:config (pointer; NT 4–32, IW 1–8)
  - Numbers: warp size 32 ← nvidia2026cudaguide Table 33
  - Cites: nvidia2026cudaguide
  - Links: ← bg-vortex-hierarchy
- **[bg-nv-bridge]** (closing, no head)
  - Message: Because an NVIDIA GPU is a different machine, the paper evaluates FourShadow's tensor cores against the SIMT-only Vortex they extend, not against an NVIDIA GPU.
  - Floats: —
  - Numbers: —
  - Cites: —
  - Links: → sec:motivation; TODO(ispass): Intro Q1, tab:config and the evaluation still compare with RTX 5080/H100

## III. Motivation  (hpca2027-latex-template/2_3_motivation.tex)
Sources (Part 4, read-only): `00_doc/vortex-wgdxa2k/results/MOTIVATION_MASTER.md` [MM], `MOTIV_MASTER_FQ16.md` [FQ16],
`MOTIV_MASTER_TC_TABLES.md` [TCT], `MOTIV_FIG1_DATA.md` + `motiv_fig1_data.json` [F1D]; plan `00_doc/ispass_direction/motivation/MOTIVATION_PAGE_PLAN.md` §0, §3.0 (point/paragraph matrix).
Rule (user, 2026-11-23): one point = one paragraph = one message and its own data; no datum appears in two point paragraphs.
Selection rule: only inefficiencies a SIMT design cannot tune away are points; the tunable limits form the baseline.

- **[mot-setting]** (opener, no head)
  - Message: Even the best of 45 FP32 SIMT kernels reaches a small share of SIMT-only Vortex's lane peak, so the section first tunes the core and then measures four inefficiencies tuning leaves; it defines the thread tile (each thread computes an r×c block of C, so a larger tile reuses each loaded element in more MACs).
  - Floats: —
  - Numbers: 8 threads, 4 warps, IW 1, peak 16 FLOP/cycle [S]; 45 FP32 variants ← F1D §3 (MM's 55 rows = 45 FP32 + 10 BF16/INT8-storage); 17 % (2.71 FLOP/cycle, 128×128×512) ← FQ16 §2 ref row
  - Cites: —
  - Links: → mot-tuned-baseline, mot-work-per-instr, mot-load-granularity, mot-register-reads, mot-gemv-bytes
- **[mot-tuned-baseline]** "Tuned baseline."
  - Message: Four limits of the reference core (FPU queue, flags ordering, dispatch credits, register banks) are microarchitectural, and removing them lifts the GEMM to under half of the peak, below an ideal-SIMT cap of 57 % (explained by mot-work-per-instr).
  - Floats: Fig. fig:motiv_simt(a) (first cite)
  - Numbers: 17 % → 45 % (44.9, b8x2-gl) ← FQ16 §2, §5b.4; 57 % [D] = 2·4.54/16 ← TCT F; tuned core NW 16, FQ 16, DQ 8, 8 GPR banks
  - Cites: —
  - Links: ← mot-setting; → mot-work-per-instr (why 57 %); TODO(main): evaluation SIMT baseline differs (sec:eval_threads)
- **[mot-work-per-instr]** "Work per instruction."
  - Message: Only FMAs perform MACs (at most 8 per warp instruction), and only 57 % of the fastest kernel's instructions are FMAs, so it averages 4.5 MACs per warp instruction and even one instruction per cycle reaches only 57 % of the peak; no thread tile raises the FMA share.
  - Floats: Fig. fig:motiv_simt(b) (first cite): share of warp instructions by role per thread tile
  - Numbers: 8 MACs per FMA warp instruction [S] (NT 8); FMA share 57 % (56.7, direct 4×4 `rt-t4x4-b8x1-k8-gl`, the highest of the five tiles: 21 / 42 / 57 / 37 / 32 %) ← F1D §1.3; 4.5 MACs per warp instruction (4.536 = 8 × 0.567) ← F1D §1.3; 57 % of peak = 2·4.54/16 ← mot-tuned-baseline
  - Cites: —
  - Links: ← mot-tuned-baseline; → mot-common-cause (sec:eval_threads, sec:eval_iw)
- **[mot-load-granularity]** "Load granularity."
  - Message: A load moves one element per lane, so every operand enters the register file element by element: a larger tile loads fewer words per MAC, a warp-shared value is loaded into every lane, and a narrow element costs the same load plus a conversion; shared-memory staging does not remove the loads.
  - Floats: Fig. fig:motiv_simt(c), lower series (words loaded per MAC)
  - Numbers: words loaded per MAC 2 → 0.25 (tile 1×1 → 8×8) [S, measured within 0.5 %] ← F1D §2; FP16 `flh` + `fcvt.s.h`, INT8 byte load + integer arithmetic [S] (plan §3.0); no speeds or bytes of narrow formats (mot-gemv-bytes owns them)
  - Cites: —
  - Links: → mot-gemv-bytes (per-element mechanism), mot-common-cause (sec:bg_smem, sec:eval_delay_a)
- **[mot-register-reads]** "Register-file reads."
  - Message: Once loaded, an operand is read from the register file at every MAC that uses it: never fewer than three reads per MAC at any thread tile, with the minimum at a mid-size tile between address arithmetic (small tiles) and spills (large tiles).
  - Floats: Fig. fig:motiv_simt(c), upper series (register reads per MAC)
  - Numbers: 3 reads per FMA [S, measured 3.00]; minimum 3.9 GPR lane-reads per MAC at 4×4 (3.935) ← F1D §2 (curve 7.96 / 4.69 / 3.94 / 5.38 / 6.05); no words-loaded numbers (mot-load-granularity owns them)
  - Cites: —
  - Links: ← mot-load-granularity; → mot-common-cause (sec:eval_nrc)
- **[mot-gemv-bytes]** "Narrow weights in decode GEMV."
  - Message: In decode GEMV, where DRAM bytes should set the speed, SIMT is bound by instructions, so narrow weights take fewer bytes without running faster.
  - Floats: —
  - Numbers: FP32 GEMV 9.4 B/cycle from DRAM = a quarter (23.9 %) of the 39.5 B/cycle of a load-only streaming kernel on the same tuned core ← F1D §4 (DQ 8 with 4 or 8 banks); INT8 a quarter of the FP32 bytes (storage 0.25×; measured 0.25× on the 4-bank cores) and 0.8× speed (0.788 / 0.792 / 0.789 on three cores) ← F1D §4
  - Cites: —
  - Links: ← mot-load-granularity (per-element mechanism); → mot-common-cause (sec:eval_sparse)
- **[mot-common-cause]** (closing, no head)
  - Message: The four inefficiencies share one cause, a scalar MAC per lane as SIMT's unit of work, which a tensor core replaces with a tile operation and a sparse tensor core extends to compressed weights; FourShadow builds them and the evaluation varies the parameter behind each (in the order work per instruction, loads, register reads, bytes).
  - Floats: —
  - Numbers: —
  - Cites: —
  - Links: ← mot-work-per-instr, mot-load-granularity, mot-register-reads, mot-gemv-bytes; → sec:design, sec:eval_threads, sec:eval_iw, sec:bg_smem, sec:eval_delay_a, sec:eval_nrc, sec:eval_sparse (gaps: plan §4)

## IV. Related Work  (hpca2027-latex-template/2_5_related_work.tex)
Sources (primary, read 2026-11-24): Virgo arXiv 2408.12073v2 (= ASPLOS'25) [V]; CoopWarp HPCA'25 abstract (imec repository; full text
behind "request a copy", not read) [CW] and its authors' artifact repository `01_github/coopwarp-vortex` @ `4f9134cb` [CWR] (read-only clone,
`00_doc/ispass_direction/reference_repos.md` §2); Ten-Four arXiv 2512.00053v4 [TF]; RoadBlock arXiv 2611.08526v1 (PACT'26, 2 pages) [RB].
Rules (user via main, 2026-11-24): only tensor-core work built on Vortex, distinguished from FourShadow; all are open source; only
FourShadow has warp-group MMA, 2:4 sparsity, and both RTL and SimX; FourShadow named only after the prior work. Non-Vortex tensor cores (RM-STC,
VEGETA, SIMD², Sparse TC) and the simulators stay in the Introduction only.

Rules (user, 2026-11-24, second pass): describe the prior work briefly, one or two sentences per work (mechanism and the limit FourShadow
changes); spend the words on the distinction; superiority as capabilities and as results this paper measures (printed numbers only, with
section pointers), never a head-to-head with Virgo/CoopWarp/Ten-Four. Ten-Four v4 overlap is open (user): the distinction does not rest on
FEDP-2K; "Ten-Four is the dot-product unit" carries a `% TODO(user)`. RTL–SimX agreement is not printed (no printed evidence; the A fetch
differs, `TODO(ispass)` at `sec:eval_delay_a`).

- **[rel-prior]** (section opener, no head; merges the former rel-frame, rel-virgo, rel-coopwarp and rel-datapath)
  - Message: Each prior tensor core on Vortex extends one level of the GPU: Virgo moves the matrix unit to the cluster (trading flexibility on small matrices for larger operations), CoopWarp's warps share an accumulator buffer but issue one MMA each, and Ten-Four and RoadBlock change the dot-product arithmetic.
  - Floats: Table tab:related_work_comparison (first cite in this section; the Introduction points here)
  - Numbers: — (the power, speedup, area and clock figures of the works were dropped by the user's request; no other section uses them)
  - Sources: [V] §3 (Vortex SIMT core, Gemmini array at cluster level), §4 (threadblock-level atom; "sacrifices flexibility for workloads that use smaller matrix dimensions"); [V] §1 for the core-coupled family limit ("restricting operation size due to register file capacity and bandwidth constraints"); [CW] abstract (integration in Vortex, cooperative warp execution); [CWR] `cooperative_kernel.cpp:80-91` (per-warp `tc_mma_acc_buf`, `vx_barrier`, `tc_flush_wg`) [source-derived]; [TF] abstract, §3.2; [RB] §1–2
  - Cites: kim2025virgo, nada2025cooperative, rout2026tenfouropensourcefuseddot, rout2026roadblock
  - Links: ← intro (platform sentence); → table rows Virgo, CoopWarp, Ten-Four; → rel-fs-organization
- **[rel-fs-organization]** (no head)
  - Message: FourShadow changes the organization itself, with the two features no other row of Table I has: a warp-group MMA that is one instruction for the warps of a warpgroup, with B (and A in SS mode) from shared memory and one B fetch shared by all tensor blocks, and 2:4 sparsity on both warp-level and warp-group MMA.
  - Floats: Table tab:related_work_comparison (Warp-group MMA and 2:4 sparsity columns)
  - Numbers: —
  - Sources: `sec:design_wgmma` (one tensor block per issue slot, RS/SS, shared B buffer, one B refill serves all IW blocks); `sec:design_sparse` (compressed A, metadata by `TCU_LD` into the per-block metadata SRAM, Sparse MUX Array, halved K steps); `para:datatypes-fedp` (FEDP = Ten-Four)
  - Cites: — (FourShadow's own sections)
  - Links: ← rel-prior; → sec:design_wgmma, sec:design_sparse
- **[rel-fs-platform]** (closing, no head)
  - Message: FourShadow is also the platform to measure these features: RTL and SimX, FPGA runs and ASAP7 area, and six build parameters, so the paper pairs one-parameter cycle sweeps with area and reports results no other row can produce (16-thread peak, issue-width optimum at 4, the shrinking halvable share of sparse warp-group MMA, FPGA end-to-end gains).
  - Floats: Table tab:related_work_comparison (RTL, Cycle sim., Threads per warp columns); Table tab:config (parameters)
  - Numbers (all printed in the evaluation, copied, not re-derived): per-lane WGMMA peak at 16 threads ← `sec:eval_threads`; 32 threads double the TCU area (2.00×) while the BF16 speedup falls by 21–38 % ← `sec:eval_asic`; IW 4 practical optimum, front end limits a wider warpgroup ← `sec:eval_asic`, `sec:eval_iw`; halvable share shrinks as the warp-group tile widens ← `sec:eval_sparse_wg`; Llama-3.2-1B prefill 10.18× (WGMMA) and 12.39× (+2:4) over the dense base TCU on the U55C ← `sec:eval_fpga`
  - Sources: Virgo threads 8 ← [V] Table 2, cycles from RTL simulation ← [V] artifact appendix A; CoopWarp SimX only ← [CWR] (`tensor_rtl/` not referenced from `hw/rtl`) [source-derived]. CoopWarp also relates utilization to the GPU's parameters in SimX ([CW] abstract), so parameter sweeps are not claimed as exclusive; the contrast is sweeps paired with synthesized area.
  - Cites: kim2025virgo, nada2025cooperative (contrast clauses)
  - Links: ← rel-fs-organization; → sec:eval_threads, sec:eval_iw, sec:eval_asic, sec:eval_sparse_wg, sec:eval_fpga, sec:design

## Float map (Section III)
| float | label | source | first-citing id | lands |
|---|---|---|---|---|
| Fig. 1, figure*, (a)(b)(c) in one row, `fig/motiv_simt3.pdf` (script `fig/src/motiv_simt3.py`) | fig:motiv_simt | 2_3_motivation.tex | mot-tuned-baseline ((b) mot-work-per-instr, (c) mot-load-granularity, then mot-register-reads) | PDF p. 4 top, both columns (section starts p. 3 right, after the one-page Background) |

## Float map (Section IV)
| float | label | source | first-citing id | lands |
|---|---|---|---|---|
| Table I, one-column `table` | tab:related_work_comparison | 2_5_related_work.tex (moved from 1_intro.tex) | rel-frame (the Introduction cites it first) | PDF p. 5 top of the left column (source placed at the end of the section, after rel-fs-platform; placed before a paragraph that starts on p. 4 it floats above the IV heading onto the page of the Fig. 1 figure*); Section IV starts p. 4 right |
