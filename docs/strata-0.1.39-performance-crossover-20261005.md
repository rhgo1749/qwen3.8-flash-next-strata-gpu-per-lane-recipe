# Strata 0.1.39 Lanes ↔ pipelined layer-split recheck — 2026-10-05

## Status

This is **candidate performance evidence**, not a software-baseline promotion. The recipe's promoted baseline remains Strata 0.1.38 until the fork explicitly promotes 0.1.39.

## Provenance

```text
Strata-Lanes branch  sync/upstream-0.1.39
fork commit          d51d7e9cbc327f90c2fd59b1e20a949033f594e2
upstream Strata      6f32ec070f23ced9f50e704d854d775da52591ab (v0.1.39)
binary sha256        9aa71607ca3c322c61e75e2fbbb0cbd8f1816f663c9c856b6df342ecd9e18c05
model/quant          Qwen3.8-Flash-Next GSQ-RCO IQ3_S
host                 Ryzen 9 9950X3D / 128 GB DDR5
primary GPUs         RTX 5070 Ti 16 GB x3
driver/CUDA          615.71.09 / CUDA 13.4
lane order           0,2,1
lane context/KV      262144 / 32768
sampling             temperature=0, seed=1234
```

The current frontend tokenizes the fixed ~1.5K reasoning scaling prompt to 1469 tokens with hash `429fe691f25560a1`. The earlier 0.1.38 recipe recorded 1456 tokens under its then-current frontend path, so 0.1.38↔0.1.39 percentages are contract-matched rather than byte-identical. The 0.1.39 fixed-prompt decode challenger arms are matched to each other.

## Independent-lane campaign

Five retained scaling repetitions per point:

| Active lanes | Common-wall aggregate TG |
| ---: | ---: |
| 1 | **73.63 ± 1.67 tok/s** |
| 2 | **143.19 ± 3.06 tok/s** |
| 3 | **192.16 ± 4.11 tok/s** |

Three lanes are 2.610x the one-lane rate (87.0% scaling efficiency). Corrected mixed fiction/coding/reasoning serving measured **189.25 ± 5.07 tok/s** across nine retained warm rotations.

Oversubscription retained:

| Requests | Aggregate TG |
| ---: | ---: |
| 3 | **190.26 ± 3.07** |
| 4 | **141.55 ± 0.90** |
| 6 | **191.06 ± 2.67** |
| 9 | **191.86 ± 1.52** |

Heterogeneous ABBA retained:

| Measurement | TG |
| --- | ---: |
| RTX 5070 Ti solo | **75.80 ± 2.21** |
| RTX 5070 Ti concurrent | **75.24 ± 1.56** |
| RTX 5060 Ti concurrent | **59.98 ± 1.23** |
| Common-wall aggregate | **118.68 ± 2.35** |

The raw fast-lane delta is -0.74%.

## Workload sensitivity

| Workload | Cold PP | Warm TG |
| --- | ---: | ---: |
| fiction short | 878.6 | 72.28 |
| coding short | 840.6 | 85.70 |
| reasoning short | 872.2 | 79.24 |
| fiction medium | 2799.1 | 69.22 |
| coding medium | 2791.5 | 83.84 |
| reasoning medium | 2803.4 | 70.48 |
| long_review ~110K | **2719.02 ± 1.12** | **66.20 ± 0.50** |

The ~15K cold-PP region is essentially flat against the 0.1.38 campaign, while warm decode generally moves upward. The long warm-TG arm does not improve, so this is not evidence for a universal decode speedup.

## Shared-arena memory

| Context / resident KV | 0.1.39 shared two-engine PSS |
| --- | ---: |
| 32K / 8192 | **52.113 GiB** |
| 262K / 32768 | **58.038 GiB** |

A 0.1.39 private two-engine PSS number is intentionally absent. The second private ~46.8 GiB arena drove the DevSpace cgroup into memory pressure and systemd-oomd killed it. The historical 0.1.38 private PSS must not be relabeled as a 0.1.39 measurement.

## Correcting the layer-split concurrency baseline

The initial 0.1.39 layer-split three-request test used the ordinary FIFO path:

| Layer-split control | Result |
| --- | ---: |
| One warm request | **120.62 ± 1.24 tok/s** |
| Three requests, FIFO common wall | **118.75 ± 5.98 tok/s** |
| Short cold PP | **1047.45 ± 3.20 tok/s** |

The three-request FIFO result is a **serial control**, not the 0.1.39 concurrency ceiling.

With `--batch 3` plus the shared expert arena but no pipeline groups, three fixed requests reached **132.46 ± 3.61 tok/s**. A private-arena repeat was 133.33 ± 3.41, so shared backing itself did not materially move batch3 TG.

## Pipelined layer split

The strongest measured upstream-native challenger used:

```text
GPU order               0,2,1
--layer-split           18,34
stages                  0-17 / 18-33 / 34-47
--batch                 3
--batch-groups          3
--trim-stage-weights
--shared-expert-arena   enabled
```

The engine log explicitly reported:

```text
strata batch (pipelined, 3 groups of 1)
```

Five retained fixed-prompt 512-output runs measured **209.66 ± 4.02 tok/s** common-wall aggregate TG. Against the matched three-independent-lane result of **192.16 ± 4.11**, this is **+9.1%** in this decode region.

The stage-weight trim increased available expert residency; retained decode logs were generally 97.3–100% expert-cache hit. This is an execution-path result, not evidence that one topology is universally better.

## Cold-prefill crossover

Every retained PP request used a unique nonce and reported `cache_n=0`. Three cold prompts were submitted simultaneously; common-wall PP is the sum of newly processed prompt tokens divided by the wall time until all three one-token responses completed.

| Cold prompt regime | Lanes 1+1+1 | Pipeline split | Result |
| --- | ---: | ---: | --- |
| ~15K x3 | **5901.34 ± 55.16 tok/s** | 3289.19 ± 18.83 | **Lanes +79.4%** |
| ~110K x3 | 5822.71 ± 4.49 | **6028.09 ± 14.50** | **Pipeline +3.5%** |

At ~15K, each pipelined-split prompt itself processes around 3.3K PP, but admissions finish in a near-serial staircase (~4.6 s, ~9.1 s, ~13.7 s). Independent lanes process all three prompts at once, so aggregate PP is much higher.

At ~110K, the intra-prompt chunk pipeline is saturated. Each layer-split prompt processes around 6.08–6.12K PP; even with near-serial request admission, the three-request common wall is ~54.7 s and narrowly beats the independent-lane aggregate.

The medium/long PP arms are workload/length matched but **not byte-identical** because the unique nonce encoded the arm name; retain that caveat with percentage comparisons.

## Interpretation

The 0.1.39 challenger landscape is no longer described correctly by “layer split wins one request, lanes win concurrency.”

A better statement for this host is:

- independent lanes dominate multiple medium-length cold prompts;
- upstream pipelined layer split can beat independent lanes for matched three-request decode;
- very long prompts can cross over toward the pipelined split because intra-prompt chunk pipelining becomes highly efficient;
- ordinary FIFO layer split remains a useful control but is not the concurrency ceiling;
- production topology should not change on these micro-regions alone: mixed prompt/output lengths, queue/tail latency, power, failure isolation, and topology-reconfiguration cost remain open gates.

Machine-readable summary and retained raw evidence live under [`bench/raw/0.1.39-20261005/`](../bench/raw/0.1.39-20261005/).
