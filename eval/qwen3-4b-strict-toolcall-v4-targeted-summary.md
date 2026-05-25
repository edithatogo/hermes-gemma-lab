# Qwen3 4B Strict Tool-Call V4 Targeted Summary

Date: 2026-05-25

## Targeted V4 Attempt

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Config: `scripts/train_config.qwen3-4b.strict-toolcall-v4-targeted.yaml`
- Data: `data/strict_tool_call/expanded_splits_v4_targeted`
- Adapter: `experiments/qwen3-4b-strict-toolcall-v4-targeted/lora_adapter`
- Iterations: 140
- Effective trained tokens: 37,936
- Final validation loss: 0.709
- Best observed validation loss: 0.643 at iteration 100
- Peak memory: 3.785 GB
- Raw training log: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v4-targeted-train-20260525.log`

## Held-Out Result

- Suite: `benchmarks/tool_call_local/heldout_suite.json`
- User prefix: `/no_think`
- No-prefill held-out strict pass: 0.250
- No-prefill diagnostic empty-think-stripped pass: 1.000
- No-prefill responses with leading empty-think wrapper: 8 / 8
- Prefill condition: `<think>\n\n</think>\n\n`
- Prefill held-out strict pass: 1.000
- Prefill held-out JSON validity: 1.000
- Prefill held-out argument correctness: 1.000
- Prefill held-out invalid-tool handling: 1.000
- Prefill held-out multi-turn repair: 1.000
- Raw no-prefill held-out output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v4-targeted-heldout-nothink-20260525`
- Raw prefill held-out output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v4-targeted-heldout-prefill-20260525`
- Raw prefill mirrored output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v4-targeted-mirrored-prefill-20260525`

## Decision

Do not publish this adapter without the runtime prompt condition. The no-prefill
strict gate remains blocked because Qwen3 still emits an empty
`<think></think>` wrapper before otherwise correct tool-call payloads.

With the recorded assistant prefill, this is the first local Qwen3 adapter in
this project to pass the strict held-out gate at `1.000`. Publication still
requires dataset/source redistribution review and a model card that states the
required `/no_think` plus assistant-prefill runtime condition.

## Next Action

Use this adapter only where Hermes or the serving layer can apply the recorded
runtime prompt condition. The next engineering step is packaging/evaluation
through the normalizing proxy or a Hermes runtime shim that injects the
assistant prefill deterministically.
