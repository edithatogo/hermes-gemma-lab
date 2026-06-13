# Specification: Gemma 4 No-Thinking Dataset Guard

## Problem

Gemma 4 26B A4B and 31B no-thinking fine-tunes require an empty thought channel
at the start of model turns. The shared Hermes training splits were built for
Qwen/Hermes-style adapters and did not encode that Gemma-specific convention.

## Scope

- Materialize Gemma-specific copies of the existing shared splits.
- Prefix assistant turns with the empty Gemma 4 thought channel.
- Retarget only the Gemma 4 26B A4B experimental configs.
- Add a validator and tests so future Gemma 4 training cannot silently use the
  wrong format.

## Out Of Scope

- No Gemma 4 training run.
- No mutation of shared Qwen/Hermes dataset splits.
- No publication or benchmark claim from this formatting work alone.

## Acceptance Criteria

- Gemma-specific datasets exist under `gemma4/data/gemma4_no_thinking`.
- Gemma 4 26B A4B configs point at those datasets and set an explicit format
  flag.
- The global readiness gate validates the format.
- Health remains `>= 9.5 / 10`.
