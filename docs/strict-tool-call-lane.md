# Strict Tool-Call Lane

This lane is a small, checked-in seed set for supervised strict tool-call training. It is intentionally isolated from the broader `data/raw/` and `data/splits/` corpora so it can be rebuilt or expanded without changing the general-purpose dataset.

## Location

- Raw seed: `gemma4/data/strict_tool_call/raw/seed.jsonl`
- Materialized splits: `gemma4/data/strict_tool_call/splits/{train,val,test,valid}.jsonl`

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

For the current 10-example seed, that yields 8 train examples, 1 validation example, and 1 test example.

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
