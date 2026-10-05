# Strata 0.1.39 topology crossover — 2026-10-05

## Status

This evidence now belongs to the **promoted Strata 0.1.39 software baseline**. The measurements themselves were collected on the validated pre-promotion source generation; promotion does not relabel their provenance.

This document is intentionally limited to the measurements that decide the current topology question. Broader 0.1.39 workload, oversubscription, heterogeneous-GPU, memory, FIFO, and batch-only controls remain in `bench/raw/0.1.39-20261005/` for auditability but are not headline architecture benchmarks.

## Provenance

```text
measured Strata-Lanes  d51d7e9cbc327f90c2fd59b1e20a949033f594e2
branch                 sync/upstream-0.1.39
upstream Strata        6f32ec070f23ced9f50e704d854d775da52591ab (v0.1.39)
binary sha256          9aa71607ca3c322c61e75e2fbbb0cbd8f1816f663c9c856b6df342ecd9e18c05
model/quant            Qwen3.8-Flash-Next GSQ-RCO IQ3_S
host                   Ryzen 9 9950X3D / 128 GB DDR5
primary GPUs           RTX 5070 Ti 16 GB x3
driver/CUDA            615.71.09 / CUDA 13.4
GPU order              0,2,1
sampling               temperature=0, seed=1234
```

The fixed decode prompt tokenizes to 1469 tokens with hash `429fe691f25560a1`. Independent-lane and layer-split decode arms use the same current prompt contract.

## Decode concurrency envelope

The strongest three-GPU layer-split server is kept fixed at:

```text
--layer-split 18,34
--batch 3
--batch-groups 3
--trim-stage-weights
--shared-expert-arena <file>
```

The engine reports `strata batch (pipelined, 3 groups of 1)`. For M=2 the same server remains in the pipelined execution mode with one group unused.

| Concurrent decode requests | Independent lanes | Three-GPU layer split | Layer-split delta |
| ---: | ---: | ---: | ---: |
| 1 | 73.63 ± 1.67 tok/s | **120.62 ± 1.24 tok/s**¹ | **+63.8%** |
| 2 | 143.19 ± 3.06 tok/s | **147.84 ± 2.26 tok/s** | **+3.25%** |
| 3 | 192.16 ± 4.11 tok/s | **209.66 ± 4.02 tok/s** | **+9.11%** |

¹ The M=1 value is the retained three-GPU layer-split single-request control from the same 0.1.39 binary, but it was not rerun with the exact batch3/groups3/trim config. M=2 and M=3 are exact measurements of the fixed pipelined config above.

M=2 retained runs were 144.36 / 147.04 / 148.66 / 150.26 / 148.88 tok/s. Both requests completed together at roughly 6.9 s mean E2E, rather than as a FIFO staircase.

The M=2 result closes the missing concurrency point: on this fixed decode workload, the measured three-GPU layer-split path is ahead at M=2 and M=3, while the existing single-request layer-split control is also substantially ahead of one independent lane.

## Cold-prefill crossover

Every retained PP request used a unique nonce and reported `cache_n=0`. Three cold prompts were submitted simultaneously; common-wall PP is total newly processed prompt tokens divided by the time until all three one-token responses completed.

| Cold prompt regime | Lanes 1+1+1 | Pipelined layer split | Result |
| --- | ---: | ---: | --- |
| ~15K x3 | **5901.34 ± 55.16 tok/s** | 3289.19 ± 18.83 | **Lanes +79.4%** |
| ~110K x3 | 5822.71 ± 4.49 | **6028.09 ± 14.50** | **Layer split +3.5%** |

At ~15K, independent lanes win because all three prompts prefill concurrently while layer-split admissions remain close to serial. At ~110K, the intra-prompt chunk pipeline becomes efficient enough that each layer-split prompt runs around 6.1K PP and the layer-split common wall narrowly crosses the independent-lane result.

The 15K/110K arms are workload/length matched but not byte-identical because the unique nonce encoded the topology arm. Keep this caveat with exact percentage claims.

## Supporting controls retained, not headline benchmarks

The following measurements remain in raw evidence because they explain or falsify specific interpretations, but they are no longer part of the compact topology scorecard:

- ordinary layer-split FIFO three-request control: 118.75 ± 5.98 tok/s;
- `--batch 3` without pipeline groups/trim: 132.46 ± 3.61 tok/s;
- short (~1.5K) cold-prefill admission probe;
- broad workload-sensitivity, oversubscription, heterogeneous-isolation and shared-PSS probes.

The FIFO and batch-only controls show that the M=3 gain comes from the 0.1.39 pipeline-group/stage-trim execution path, not from merely putting three requests behind one layer-split server.

## Interpretation

The current evidence no longer supports “independent lanes are the default performance winner whenever requests are concurrent.”

On this reference host:

- the fixed three-GPU layer-split server is ahead in the measured M=2 and M=3 decode regions;
- a retained single-request layer-split control is much faster than one independent lane;
- independent lanes still dominate the important medium-length multi-cold-prefill region;
- very long cold prompts cross back toward layer split.

So the remaining reason to keep independent lanes as production default is no longer a simple throughput claim. It is workload mix, medium cold-prefill bursts, session/failure isolation, heterogeneous request lengths, and operational flexibility. Those are separate production gates, not reasons to keep repeating already-settled microbenchmarks.

Machine-readable summary and retained raw evidence: [`bench/raw/0.1.39-20261005/`](../bench/raw/0.1.39-20261005/).
