# Contracts — Gemma/Qwen/Hermes Track

## GQH-DOWNLOAD-001

Model downloads must use SSD-backed Hugging Face cache and should use `HF_TOKEN` or prefetching when unauthenticated downloads stall.

## GQH-TRAIN-001

Smoke training must save adapter artifacts under ignored `experiments/` paths.

## GQH-EVAL-001

Evaluation must compare base model, adapter, and available Hermes baseline where practical.

## GQH-HEALTH-001

The track cannot be marked complete until health is estimated at `>= 9.5 / 10`.

## GQH-GEMMA4-DATA-001

Gemma 4 26B A4B and 31B no-thinking training configs must use datasets whose
assistant turns begin with the empty Gemma 4 thought channel. Shared Qwen/Hermes
splits must not be mutated to satisfy this contract.
