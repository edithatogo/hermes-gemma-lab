# Qwen3 4B Strict Tool-Call V2/V3 Summary

Date: 2026-05-22

## V2 Format Guard

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Config: `scripts/train_config.qwen3-4b.strict-toolcall-v2.yaml`
- Data: `data/strict_tool_call/expanded_splits_v2`
- Adapter: `experiments/qwen3-4b-strict-toolcall-v2/lora_adapter`
- Iterations: 140
- Effective trained tokens: 35,831
- Final validation loss: 0.751
- Best observed validation loss: 0.659 at iteration 90
- Peak memory: 3.785 GB
- Held-out strict pass: 0.250
- Held-out diagnostic empty-think-stripped pass: 0.625
- Raw held-out output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v2-heldout-nothink-20260522`
- Decision: not publishable. Generic format-guard wording did not improve strict output behavior.

## V3 `/no_think` Augmentation

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Config: `scripts/train_config.qwen3-4b.strict-toolcall-v3-no-think.yaml`
- Data: `data/strict_tool_call/expanded_splits_v3_no_think`
- Adapter: `experiments/qwen3-4b-strict-toolcall-v3-no-think/lora_adapter`
- Iterations: 120
- Effective trained tokens: 31,208
- Final validation loss: 0.689
- Best observed validation loss: 0.673 at iteration 80
- Peak memory: 3.785 GB
- Mirrored strict pass: 0.167
- Mirrored diagnostic empty-think-stripped pass: 1.000
- Held-out strict pass: 0.250
- Held-out diagnostic empty-think-stripped pass: 0.875
- Held-out residual strict failures after empty-think stripping: 1, `heldout-argument-correctness-lab-order`
- Raw mirrored output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v3-nothink-mirrored-20260522`
- Raw held-out output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v3-nothink-heldout-20260522`
- Iteration-80 held-out checkpoint: same strict and diagnostic result as the final adapter.
- Decision: not publishable. `/no_think` augmentation improved non-strict recoverability but did not remove the empty-think wrapper, so strict publication remains blocked.

## Next Action

Do not publish adapters. The next model-quality experiment should either use a different base/runtime that obeys no-thinking mode strictly, or add a decoding/runtime control that prevents Qwen thinking wrappers before the model text reaches Hermes. Runtime normalization may help local Hermes usage, but it must remain separate from the strict benchmark gate.
