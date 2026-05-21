# Strict Tool-Call Lane

This lane is a small, checked-in seed set for supervised strict tool-call training. It is intentionally isolated from the broader `data/raw/` and `data/splits/` corpora so it can be rebuilt or expanded without changing the general-purpose dataset.

## Location

- Raw seed: `gemma4/data/strict_tool_call/raw/seed.jsonl`
- Expansion policy and seed docs: `gemma4/data/strict_tool_call/EXPANSION.md`
- Original seed materialized splits: `gemma4/data/strict_tool_call/splits/{train,val,test,valid}.jsonl`
- Expanded materialized splits: `gemma4/data/strict_tool_call/expanded_splits_v1/{train,val,test,valid}.jsonl`

## Format

Each JSONL line is a single chat example with the same schema used by the rest of the track:

```json
{
  "id": "string",
  "messages": [
    { "role": "system", "content": "string" },
    { "role": "user", "content": "string" },
    { "role": "assistant", "content": "string" }
  ]
}
```

Strict cases must keep the assistant target exact:

- valid tool cases use only `<tool_call>` blocks
- multi-call answers keep one block per call
- invalid-tool cases use plain text refusal or clarification and must not invent a tool call
- no prose wrapper, no markdown fencing, and no extra commentary around the target

## Split Policy

The seed is split deterministically by sorted `id`:

1. order the examples lexicographically by `id`
2. take the first 80% as `train`
3. take the next 10% as `val`
4. take the remainder as `test`

For the current 10-example materialized seed, that yields 8 train examples, 1 validation example, and 1 test example.

Expansion seeds under `gemma4/data/strict_tool_call/raw/expansion_seed_*.jsonl` are staged data until explicitly promoted into materialized splits. The original 10-example seed remains materialized under `splits/`; approved expanded raw seeds materialize to `expanded_splits_v1/` for expanded retrain attempts. Promotion must follow the same deterministic split policy across the approved raw seed files and must preserve `valid.jsonl` as an exact alias of `val.jsonl`.

## Contamination Guard

The held-out benchmark suite must never be copied, paraphrased, or mechanically transformed into training data. Before promoting any expansion seed, compare candidate records against both `benchmarks/tool_call_local/suite.json` and `benchmarks/tool_call_local/heldout_suite.json` for:

- exact `id` overlap
- exact normalized message overlap
- exact final assistant target overlap
- exact first user prompt overlap
- exact tool-name set plus first user prompt overlap

Any overlap with `heldout_suite.json` blocks promotion. Overlap with `suite.json` is allowed only for the original benchmark-mirrored seed and must be documented as non-heldout regression data, not publication evidence.

## SSD And Artifact Policy

Keep all generated training, evaluation, and export artifacts on the SSD-backed storage root exposed by `scripts/env.sh`.

- caches go under `$HERMES_STORAGE_ROOT`
- eval outputs go under `$HERMES_EVAL_ROOT`
- exports go under `$HERMES_EXPORT_ROOT`
- nothing under those generated paths should be committed

Only the tiny checked-in seed JSONL and the associated docs/contracts belong in Git.

## Benchmark Link

The local mirrored benchmark suite in `benchmarks/tool_call_local/suite.json` is the regression target for this lane. The seed examples should stay aligned with those categories and exact-output expectations.

The publication gate is separate: `benchmarks/tool_call_local/heldout_suite.json` contains held-out strict examples that do not overlap the benchmark-mirrored seed. A strict tool-call adapter cannot be marked publishable unless that held-out suite passes at `1.000`.
