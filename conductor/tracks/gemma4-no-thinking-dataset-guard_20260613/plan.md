# Plan: Gemma 4 No-Thinking Dataset Guard

## Phase 1: Materialization

- [x] Task: add a Gemma 4 no-thinking dataset materializer.
- [x] Task: materialize Gemma-specific copies of the shared and v6 free-text-copy
  splits.
- [x] Task: preserve the shared Qwen/Hermes splits unchanged.

## Phase 2: Enforcement

- [x] Task: add a Gemma 4 no-thinking dataset/config validator.
- [x] Task: retarget Gemma 4 26B A4B experimental configs to the materialized
  datasets.
- [x] Task: wire the validator into global readiness.

## Phase 3: Evidence

- [x] Task: add unit tests for materialization and validation.
- [x] Task: document materialized row counts and config changes.
- [x] Task: run unit tests and full readiness.

## Health Check

- Target: >= 9.5 / 10
- Current estimate: 9.7 / 10
- Evidence: materialized datasets exist, validation is automated, and the shared
  training splits were not mutated.
- Gaps: this is format readiness only; Gemma 4 training and broad benchmark
  completion remain separate gated work.
