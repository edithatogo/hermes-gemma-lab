# Strict Tool-Call Seed Data

This directory contains a tiny seed set generated from the local tool-call benchmark suite. It is intended for shape-repair experiments only.

The required assistant target shape is:

```text
<tool_call>{"name":"tool_name","arguments":{...}}</tool_call>
```

For unavailable tools, the target is plain refusal text and must not include a tool call.

This seed is not a publishable dataset. It is too small and intentionally overlaps the local benchmark suite. Use it to prove the training lane can learn the output format, then replace it with a larger licensed dataset before any Hugging Face publication.
