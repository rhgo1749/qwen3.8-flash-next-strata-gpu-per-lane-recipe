# Independent GPU Lanes — Reproducibility & Experiment Record

**English** | [한국어](README.ko.md)

> **Research record, not a deployment recommendation.**
>
> This repository preserves the experiments, raw measurements, harnesses, and version provenance behind the Strata-Lanes work. For normal Strata installation and serving, use **[Niko1221/Strata](https://github.com/Niko1221/Strata)**.
>
> ✅ Part of this research was adopted upstream: `--shared-expert-arena` shipped in [Strata v0.1.30](https://github.com/Niko1221/Strata/releases/tag/v0.1.30).

This repository originally documented a practical GPU-per-lane serving setup: one independent Strata engine per GPU, with the large host expert arena physically shared across processes. That architecture remains reproducible, but upstream Strata 0.1.39 changed the performance landscape enough that this repository is now maintained primarily as an **experimental record**.

## Current conclusion

On the reference 3×RTX 5070 Ti host, the current evidence is a **workload-dependent topology crossover**.

| Region | Independent lanes | Pipelined layer split |
| --- | ---: | ---: |
| M=1 fixed decode | 73.63 ± 1.67 tok/s | **120.62 ± 1.24 tok/s**¹ |
| M=2 fixed decode | 143.19 ± 3.06 tok/s | **147.84 ± 2.26 tok/s** |
| M=3 fixed decode | 192.16 ± 4.11 tok/s | **209.66 ± 4.02 tok/s** |
| three ~15K cold prompts | **5901.34 ± 55.16 tok/s** | 3289.19 ± 18.83 tok/s |
| three ~110K cold prompts | 5822.71 ± 4.49 tok/s | **6028.09 ± 14.50 tok/s** |

¹ M=1 is the retained same-binary three-GPU layer-split single-request control; M=2 and M=3 use the exact fixed pipeline configuration.

The evidence no longer supports presenting GPU-per-lane serving as a generally superior or recommended Strata deployment. Independent lanes still have an important medium-length simultaneous cold-prefill advantage and useful isolation properties, while upstream pipelined layer split now wins several decode and very-long-prefill regions.

## What this repository is for

The repository preserves:

- versioned benchmark contracts;
- retained raw JSON/JSONL measurements;
- exact benchmark harnesses and configs;
- independent-lane scaling evidence;
- shared expert-arena memory evidence;
- queue/oversubscription and scheduler experiments;
- heterogeneous-GPU and interference experiments;
- conversation-parking experiments;
- matched independent-lane ↔ upstream layer-split comparisons;
- paper/revision evidence and provenance.

It is intended for **reproduction, audit, and future comparison**, not as an install guide for ordinary users.

## Current evidence map

Start here:

- [RESULTS.md](RESULTS.md) — compact current result plus retained historical generations
- [0.1.39 topology crossover](docs/strata-0.1.39-performance-crossover-20261005.md)
- [Benchmark/reporting contract](bench/README.md)
- [0.1.39 retained raw evidence](bench/raw/0.1.39-20261005/)
- [Compact 0.1.39 topology table](bench/layer-split-ab-0.1.39-20261005.csv)

Implementation fork:

- [rhgo1749/Strata-Lanes](https://github.com/rhgo1749/Strata-Lanes)

Upstream:

- [Niko1221/Strata](https://github.com/Niko1221/Strata)

## Evidence generations

The repository intentionally keeps measurements attached to the engine/source generation that produced them.

- **0.1.39** — current topology crossover: M=1/M=2/M=3 decode plus 15K/110K three-request cold-prefill
- **0.1.38** — full architecture campaign and software-sync gate
- **0.1.31** — serving-control / lifecycle validation
- **0.1.30** — retained full architecture matrix
- older records remain in Git history and named evidence files

Old conclusions are not silently rewritten. When upstream behavior changed, the newer evidence superseded the interpretation while the older raw result remained preserved.

## Reference host

    CPU                 Ryzen 9 9950X3D
    RAM                 128 GB DDR5
    primary GPUs        RTX 5070 Ti 16 GB ×3
    driver              NVIDIA 615.71.09
    CUDA                13.4
    model/quant         Qwen3.8-Flash-Next GSQ-RCO IQ3_S

These are measurement conditions, not portable defaults.

## Reproducing historical Lanes experiments

Historical launch/config material remains available:

- [docs/USAGE.md](docs/USAGE.md)
- [recipe/launch-3lane.sh.example](recipe/launch-3lane.sh.example)

These are now **reproduction instructions**. They should not be read as a recommendation to prefer Strata-Lanes over upstream Strata.

## Paper evidence

The companion implementation repository uses:

- paper-v1 — submitted v1 state
- paper-v2-evidence — current post-v1 experimental evidence snapshot
- paper-v2 — reserved for an actual revised manuscript/submission state

## Repository status

- **Mode:** active experimental record / reproducibility archive
- **General user recommendation:** upstream Strata
- **Lanes code and configs:** preserved for reproduction
- **New work:** evidence-driven comparisons, provenance fixes, and revision support

## License

Recipe documentation and helper material in this repository are MIT licensed. Strata, model files, and third-party components retain their own licenses.
