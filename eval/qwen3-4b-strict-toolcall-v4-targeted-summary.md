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
- Held-out strict pass: 0.250
- Held-out diagnostic empty-think-stripped pass: 1.000
- Held-out diagnostic JSON validity after empty-think stripping: 1.000
- Held-out diagnostic argument correctness after empty-think stripping: 1.000
- Responses with leading empty-think wrapper: 8 / 8
- Residual semantic strict failures after empty-think stripping: 0
- Raw held-out output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v4-targeted-heldout-nothink-20260525`

## Decision

Do not publish this adapter as a strict Hermes tool-call model. The strict
gate remains blocked because Qwen3 still emits an empty `<think></think>`
wrapper before otherwise correct tool-call payloads.

This is useful runtime evidence for a local Hermes route that applies
empty-think normalization before the response reaches the agent. Under that
runtime-normalized path, the held-out payloads are JSON-valid and argument
correct, but that diagnostic score must stay separate from the publication
gate.

## Next Action

Use this adapter only behind the normalizing proxy or an equivalent Hermes
response-normalization layer. The next publishable attempt should either use a
runtime/base model that can suppress Qwen thinking wrappers at generation time
or add a stricter decoding control before investing in more local Qwen3 LoRA
training.
