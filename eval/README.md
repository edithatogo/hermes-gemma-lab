# Evaluating the Fine-tuned Model

This directory contains evaluation results for the Gemma 4 Hermes LoRA fine-tune.

## Files

- `prompts.jsonl` — A set of Hermes-style test prompts across categories
  (explanation, code, comparison, tool_use, debugging, etc.)
- `results/` — Generated outputs for base model and fine-tuned model

## Running Evaluation

```bash
# Evaluate the base model
python3 scripts/evaluate.py \
    --model google/gemma-4-E4B-it \
    --prompts eval/prompts.jsonl \
    --output eval/results/base_results.jsonl

# Evaluate the fine-tuned model (merged)
python3 scripts/evaluate.py \
    --model experiments/gemma4-e4b/lora_adapter \
    --prompts eval/prompts.jsonl \
    --output eval/results/ft_results.jsonl
```

## Scoring Dimensions

When comparing base vs fine-tuned outputs, check:
1. Instruction following — does it do what's asked?
2. Tool call formatting — correct JSON schema usage?
3. Code correctness — does the code run?
4. Conciseness — Hermes style prefers utility over verbosity
5. Refusal behavior — appropriate safety responses
