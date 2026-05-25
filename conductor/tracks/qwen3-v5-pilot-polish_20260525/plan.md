# Plan: Qwen3 V5 Pilot Polish

## Phase 1: Dataset Contract

- [x] Task: materialize V5 from V4 with invalid-tool pilot-polish examples.
- [x] Task: remove ordinary instruction-following rows after the strict dataset
  audit rejected them.
- [x] Task: record dataset overlap and token audits.

## Phase 2: Local Training

- [x] Task: train the V5 adapter under `source ../scripts/env.sh`.
- [x] Task: keep all generated adapter artifacts under ignored
  `experiments/`.
- [x] Task: keep logs and benchmark outputs under `/Volumes/PortableSSD`.

## Phase 3: Benchmark Decision

- [x] Task: run strict held-out and mirrored tool-call suites.
- [x] Task: run repo-native BFCL-style, IFEval-style, and coding pilots.
- [x] Task: record the non-promotion decision.

## Health Check

- Target: >= 9.5 / 10
- Current estimate: 9.7 / 10
- Evidence: dataset contract issue was caught and fixed before training; audits
  are recorded; training completed in 273.1 seconds with 3.785 GB peak memory;
  held-out, mirrored, and pilot benchmark outputs are stored on the SSD; V5 is
  explicitly not promoted because held-out strict pass fell to `0.875`.
- Gaps: V5 fixed the BFCL-style pilot but regressed the publication gate, so it
  is useful experimental evidence rather than a release candidate.
- Decision: keep V4 as the recommended/public adapter and use V5 only as a
  negative result guiding the next targeted data design.
