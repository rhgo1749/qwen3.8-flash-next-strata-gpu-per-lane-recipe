# Strata 0.1.39 retained raw evidence — 2026-10-05

Candidate: `rhgo1749/Strata-Lanes@d51d7e9cbc327f90c2fd59b1e20a949033f594e2`, upstream Strata 0.1.39 `6f32ec070f23ced9f50e704d854d775da52591ab`.

Only retained/non-contaminated result files are stored here. Initial workload calls duplicated by a tool replay were discarded and are not copied. The private two-engine PSS attempt is not represented as a result because systemd-oomd terminated the DevSpace cgroup while the second private expert arena was being populated.

## Headline topology evidence

- `layer-split-m2-pipeline.jsonl` — the added M=2 fixed-pipeline point: **147.84 ± 2.26 tok/s**.
- `scaling-n1.jsonl`, `scaling-n2.jsonl`, `scaling-n3.jsonl` — matched independent-lane decode controls.
- `layer-split-batch3-groups3-trim-shared.jsonl` — M=3 fixed-pipeline layer-split.
- `pp-ab-*.jsonl` — 15K/110K cold-prefill crossover.

Everything else in this directory is retained as supporting/control evidence rather than part of the compact headline scorecard.

Key files:

- `campaign-summary.json` — machine-readable campaign summary and caveats.
- `scaling-n{1,2,3}.jsonl` — independent-lane fixed-prompt TG scaling.
- `mixed.jsonl`, `oversub.jsonl`, `hetero.jsonl` — corrected concurrent serving evidence.
- `layer-split-fifo-control.jsonl` — ordinary FIFO control.
- `layer-split-batch3-shared.jsonl` — batch slots without pipeline groups.
- `layer-split-batch3-groups3-trim-shared.jsonl` — explicit 18,34 split, batch3, three groups, stage trim, shared arena.
- `pp-ab-*.jsonl` — cold/no-reuse 15K and 110K three-request PP crossover measurements.
- `pss-shared-*.json` — matched 32K and production 262K shared PSS.
- `workload-*.jsonl` — clean retained workload sensitivity runs.
- `lanes-config.json`, `layer-split-pipeline-config.json`, and the retained harnesses — execution contract used for reproduction.
