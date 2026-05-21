# Strict Tool-Call Expansion

This directory contains non-heldout expansion material for the strict tool-call lane.

## Files

- `raw/seed.jsonl`: original 10-example seed, intentionally aligned with `benchmarks/tool_call_local/suite.json`.
- `raw/expansion_seed_v1.jsonl`: 32 new synthetic expansion examples.
- `raw/expansion_seed_v2.jsonl`: 8 format-guard examples that explicitly forbid `<think>` and `</think>` wrappers.
- `tools/build_expansion_seed.py`: deterministic generator for `raw/expansion_seed_v1.jsonl`.
- `tools/build_format_guard_seed.py`: deterministic generator for `raw/expansion_seed_v2.jsonl`.
- `splits/{train,val,test,valid}.jsonl`: current materialized training splits. These are not automatically changed by adding an expansion seed.
- `expanded_splits_v2/{train,val,test,valid}.jsonl`: seed + v1 + v2 materialized splits.
- `expanded_splits_v3_no_think/{train,val,test,valid}.jsonl`: v2 splits with `/no_think`-prefixed training duplicates.

## Expansion Coverage

`expansion_seed_v1` contains 32 examples:

- `json_validity`: 8 examples
- `argument_correctness`: 8 examples
- `invalid_tool_handling`: 8 examples
- `multi_turn_repair`: 8 examples

The examples target strict JSON formatting, exact argument capture, refusal when a requested tool is absent, and multi-turn correction after incomplete or malformed prior tool calls.

`expansion_seed_v2` adds 8 `format_guard` examples. These do not copy held-out prompts or tools; they target the observed Qwen failure mode where otherwise correct tool calls are preceded by empty or malformed thinking wrappers.

`expanded_splits_v3_no_think` duplicates the v2 training rows with `/no_think` prefixed to the first user turn. Validation and test rows are not augmented. This matches the held-out benchmark invocation shape while preserving the same strict assistant targets.

## Split Policy

Keep held-out benchmark suites out of training data.

When promoting this expansion into materialized splits, build from checked-in raw training seeds only:

1. Include `raw/seed.jsonl` and approved `raw/expansion_seed_*.jsonl` files.
2. Sort examples lexicographically by `id`.
3. Split deterministically as `80% train`, `10% val`, `10% test`.
4. Write `valid.jsonl` as an exact alias of `val.jsonl`.
5. Do not copy examples from `benchmarks/tool_call_local/heldout_suite.json` into any raw or split training file.

For publication evidence, `benchmarks/tool_call_local/heldout_suite.json` remains the strict local held-out gate. Results from `suite.json` or training-derived splits are regression checks only.

## Contamination Guard

Before training on an expansion seed, run a guard that compares the candidate data against both local benchmark suites:

- exact `id` overlap
- exact normalized message overlap
- exact final assistant target overlap
- exact first user prompt overlap
- exact tool-name set plus first user prompt overlap

Any overlap with `benchmarks/tool_call_local/heldout_suite.json` blocks promotion. Overlap with `suite.json` is allowed only for the original mirrored seed and must be documented as non-heldout training data.

`expansion_seed_v1` was designed to avoid the heldout domains and identifiers:

- no inventory, freight, lab order, billing credit, payroll, security incident, purchase order, or weather-alert tasks
- no heldout tool names
- no heldout user prompts, expected outputs, entity IDs, or argument values

## Regeneration

Regenerate the expansion file with:

```bash
python3 gemma4/data/strict_tool_call/tools/build_expansion_seed.py
python3 gemma4/data/strict_tool_call/tools/build_format_guard_seed.py
python3 gemma4/data/strict_tool_call/tools/materialize_expanded_splits_v2.py
python3 gemma4/data/strict_tool_call/tools/materialize_no_think_splits_v3.py
```

The generator writes deterministic compact JSONL. Review the diff after regeneration and rerun JSONL plus overlap validation before using the data for training.
