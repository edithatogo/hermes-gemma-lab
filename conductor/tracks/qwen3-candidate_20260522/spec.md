# Specification: Qwen3 4B Candidate Training

Validate a local-safe follow-on configuration for `Qwen/Qwen3-4B-MLX-4bit` that expands beyond the 2,889-token smoke run while keeping SSD-first cache paths and early response-gate checkpoints.

Acceptance criteria:

- Candidate config uses SSD-backed cache defaults and an adapter path under ignored `experiments/`.
- Training schedule is longer than the smoke run while staying within the M1/32 GB local lane.
- Early response-gate checkpoints remain available through the candidate schedule.
- Candidate readiness notes are captured in hub docs before any longer run is attempted.
