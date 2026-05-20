# Plan: Qwen3 4B Smoke Training

## Phase 1: Download

- [x] Task: Authenticate or prefetch Qwen3 4B.
- [x] Task: Verify SSD cache location.
- [x] Task: Dry-run Qwen3 smoke config.
- [x] Task: Blockers: note any missing HF auth, inaccessible SSD mount, or stale cache state before training.

## Phase 2: Train

- [x] Task: Run smoke training config.
- [x] Task: Save adapter and run note.

## Phase 3: Evaluate

- [x] Task: Run base vs adapter eval.
- [x] Task: Update hub docs.

## Health Check

- [x] Task: Estimate track health using hub `conductor/health-score.md`.
- [ ] Task: Close or document all gaps below health 9.5.
- [ ] Task: Run hub readiness validation and attach result to the track notes.
- [ ] Task: Confirm health >= 9.5 before marking this track complete.

- Target: >= 9.5 / 10
- Current estimate: 9.7 / 10
- Evidence: Qwen3 4B smoke training completed for 10 iterations / 2,889 trained tokens with final validation loss 2.386 and peak memory 3.944 GB. Base and adapter evaluation completed on 100 prompts and both passed the response-collapse gate. Summary is recorded in `eval/qwen3-4b-smoke-summary.md`.
- Gaps: this is still a smoke proof only, not a publishable quality claim.
- Decision: use Qwen3 4B as the next local MLX candidate after LFM2.5 response collapse.

## Preparation Notes

- Authenticated prefetch path: source `../scripts/env.sh`, export `HF_TOKEN`, then use `huggingface-cli download` or `hf download` with `HF_HOME=$HERMES_STORAGE_ROOT/huggingface` so the cache lands on the SSD-backed volume.
- SSD cache check: confirm `HF_HOME`, `HF_HUB_CACHE`, and `TMPDIR` resolve under `/Volumes/PortableSSD` when that volume is present; otherwise the fallback is `.local-storage` under the hub checkout.
- Dry run command: `source ../scripts/env.sh && ../.venv/bin/python scripts/train.py --config scripts/train_config.qwen3-4b.smoke.yaml --dry-run`
- Current blockers: none for smoke proof. Publication requires larger training data, standardized benchmarks, and runtime endpoint validation.
