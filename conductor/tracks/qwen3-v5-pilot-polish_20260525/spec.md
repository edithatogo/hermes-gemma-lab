# Specification: Qwen3 V5 Pilot Polish

Run a narrow follow-on experiment after the V4 strict gate passed. V5 should test
whether adding non-heldout invalid-tool refusal examples can improve the local
BFCL-style pilot without weakening the strict held-out Hermes tool-call gate.

Acceptance criteria:

- V5 data is materialized from V4 plus strict-compatible invalid-tool examples.
- Ordinary instruction-following rows are excluded from the strict tool-call
  dataset because they violate the strict tool-call audit contract.
- Dataset overlap and token audits are recorded before interpreting training
  results.
- Training runs locally with SSD-backed cache and artifact paths.
- Held-out, mirrored, BFCL-style, IFEval-style, and coding pilot results are
  recorded.
- V5 is not promoted if the strict held-out pass rate is below `1.000`.

Out of scope:

- Public Hugging Face publication of V5.
- Replacing the V4 public adapter unless V5 strictly dominates V4 on the
  publication gate and pilot suites.
- Training a mixed general instruction-following adapter in this strict
  tool-call dataset.
