# Plan: Strict Tool-Call V6 Free-Text Copy Setup

## Phase 1: Dataset Materialization

- [x] Task: add deterministic v6 materializer.
- [x] Task: append 8 training-only free-text-copy rows plus `/no_think`
  variants to v5.
- [x] Task: regenerate `expanded_splits_v6_free_text_copy`.

## Phase 2: Contracts And Configs

- [x] Task: audit v6 splits with the strict tool-call data guard.
- [x] Task: add Qwen3 4B v6 training config.
- [x] Task: add Gemma 4 26B A4B experimental v6 training config.
- [x] Task: include the v6 source class in publication dataset
  materialization allow-lists.

## Phase 3: Documentation And Gates

- [x] Task: document the v6 failure class and contamination boundary.
- [x] Task: add the v6 materializer to the readiness Python syntax gate.
- [x] Task: run structural readiness checks with SSD-backed environment
  variables.

## Health Check

- Target: >= 9.5 / 10
- Current estimate: 9.6 / 10
- Evidence: v6 is deterministic, audited with zero structural errors, has no
  held-out user prompt overlap, and is wired into Qwen3/Gemma configs plus the
  repo readiness gate.
- Gaps: training and held-out benchmark reruns are intentionally not marked
  complete in this setup track; they should run as the next execution slice
  before any model is promoted.
- Decision: proceed to a bounded v6 train/benchmark run, starting with Qwen3 4B
  on local MLX and using Gemma 4 26B A4B as an experimental runtime-dependent
  candidate.

## Follow-On Execution

- [x] Task: train Qwen3 4B v6 locally under SSD-backed environment variables.
- [x] Task: compare iter100, iter125, and final170 against the held-out strict
  tool-call gate.
- [x] Task: run mirrored strict regression and local BFCL-style, coding, and
  IFEval-style pilots for the viable checkpoints.
- [x] Task: create a local adapter alias for the selected checkpoint.

Result: promote iteration 125 for local Hermes strict tool-call integration.
It passes held-out and mirrored strict suites at `1.000`; final170 is rejected
because it regresses to `0.875` on the held-out lab-order case.
