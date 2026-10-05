# Strata 0.1.39 retained raw evidence — 2026-10-05

Candidate: `rhgo1749/Strata-Lanes@d51d7e9cbc327f90c2fd59b1e20a949033f594e2`, upstream Strata 0.1.39 `6f32ec070f23ced9f50e704d854d775da52591ab`.

Only retained/non-contaminated result files are stored here. Initial workload calls duplicated by a tool replay were discarded and are not copied. The private two-engine PSS attempt is not represented as a result because systemd-oomd terminated the DevSpace cgroup while the second private expert arena was being populated.

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
