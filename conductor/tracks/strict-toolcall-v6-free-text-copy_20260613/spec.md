# Specification: Strict Tool-Call V6 Free-Text Copy Setup

Create a narrow follow-on dataset/config slice after Gemma 4 26B A4B reached
`7/8` on the held-out strict Hermes tool-call suite. The only observed failure
was an exact-argument miss where the model expanded the requested free-text
message instead of copying the user-provided phrase exactly.

Acceptance criteria:

- V6 data is materialized from v5 plus non-heldout free-text-copy repair
  examples.
- V6 repair rows are training-only and include `/no_think` variants.
- The repair examples avoid held-out prompts, ids, argument strings, and final
  assistant targets.
- Qwen3 4B and Gemma 4 26B A4B training configs point at the v6 splits.
- The strict tool-call lane docs record the v6 purpose and contamination
  boundary.
- The repo readiness gate compiles the v6 materializer.

Out of scope:

- Claiming a promoted adapter before training and benchmark reruns complete.
- Relaxing exact held-out argument matching.
- Copying or paraphrasing held-out benchmark cases into training data.
