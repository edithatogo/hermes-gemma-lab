# Plan: Qwen3 4B Candidate Training

## Phase 1: Candidate Config

- [x] Task: add a local-safe Qwen3 candidate config with SSD-first adapter path and 5-step eval/save cadence.
- [x] Task: dry-run the candidate config under `scripts/env.sh` defaults.

## Phase 2: Response-Gate Ready

- [x] Task: run the 60-step local candidate pass.
- [x] Task: run the 100-prompt Hermes-local eval and response-collapse gate.
- [x] Task: run the local tool-call benchmark and record the negative result.
- [x] Task: confirm the candidate schedule still fits the local MLX lane before promoting it past planning.

## Phase 3: Track Notes

- [x] Task: record the candidate handoff and validation notes in the gemma4 hub docs.
- [x] Task: keep the track incomplete until a real candidate run and gate result exist.

## Health Check

- [x] Task: estimate track health using the hub readiness rules.
- [x] Task: confirm health >= 9.5 before marking this track complete.

- Target: >= 9.5 / 10
- Current estimate: 9.7 / 10
- Evidence: smoke proof exists, the candidate config stays on the same SSD-first MLX lane, the 60-step candidate run completed at 25,094 trained tokens with 3.962 GB peak memory, the 100-prompt response gate passed, and the local tool-call benchmark was recorded.
- Gaps: tool-call benchmark failed at 1/6 cases, so this is not a publishable Hermes tool-calling adapter.
- Decision: keep Qwen3 4B as the next local candidate path, but add explicit tool-call target data before any longer run.

## Preparation Notes

- Use `source ../scripts/env.sh` so `HF_HOME`, `HF_HUB_CACHE`, and `TMPDIR` stay on the SSD-backed volume.
- Dry run command: `source ../scripts/env.sh && ../.venv/bin/python scripts/train.py --config scripts/train_config.qwen3-4b.candidate.yaml --dry-run`
- The candidate schedule should remain checkpointable before any longer training is attempted.
- Do not run long training as part of this planning update.
