# Contributing to hermes-gemma-lab

Contributions improve the Gemma/Qwen model-training track of the Hermes Training Hub, with reproducible dataset preparation, bounded experiments, and explicit promotion evidence.

## Before you start

Read the [README](README.md), [Conductor context](CONDUCTOR.md), and [strict tool-call lane](docs/strict-tool-call-lane.md). Coordinate dataset, configuration, evaluation, and runtime work with the hub and existing track owners.

Search existing issues and pull requests to avoid duplicating work. Describe substantial proposals before implementation, and use repository issue or pull request templates when available. Small corrections can go directly into a focused pull request.

For bug reports, include the affected version or commit, environment, minimal reproduction, expected and actual behavior, and sanitized diagnostics. For feature requests, explain the use case and intended outcome.

## Development and validation

Choose the applicable checked-in training configuration and document the exact model revision, dataset provenance, split policy, seed, environment, and resource envelope. Keep smoke tests, held-out evaluation, runtime-conditioned results, and publication readiness distinct.

Use the existing evaluation and data-contamination rules. Training on benchmark-mirrored examples does not establish generalization. Changes to strict tool-call behavior should include reproducible held-out cases and the precise prompt/runtime conditions. Consult the hub benchmark and documentation gates before any promotion.

Keep adapters, merged models, GGUF exports, caches, and large generated artifacts outside Git under the documented artifact policy. A configuration file or passing smoke run is not a model-quality claim. This guide does not authorize larger training runs, paid compute, or model publication.

Update affected documentation and examples alongside behavior changes. Add a focused regression case for a bug fix where executable tests are appropriate. Record checks that were not run and the reason.

## Submitting a pull request

Create a focused branch from the current `main` branch and open a pull request back to it. Keep unrelated formatting, refactoring, and dependency changes separate.

Include:

- The problem, proposed change, and resulting behavior.
- Related issues or existing track references.
- Exact validation commands or inspection steps, results, and limitations.
- Compatibility implications and any data or dependency provenance.

Inspect the complete diff before submission. Required automated checks must pass before merge. Follow the existing repository and account policies; this guide does not introduce a second-person approval requirement or relax existing checks.

## Security and sensitive information

Follow the [account security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md). Report vulnerabilities privately through GitHub's **Report a vulnerability** option if available. Otherwise request a private reporting contact without disclosing the vulnerability publicly. Keep credentials, personal data, and unredacted logs out of commits, issues, and examples.

## Licensing and conduct

Preserve existing attribution and applicable source or package terms. This guide does not grant a new license. Submit only material you are entitled to contribute, and document unclear permissions before adding third-party content. Follow the [account code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md). This guide adds no CLA, mandatory sign-off, or relicensing condition.

## Reference guidance

- [GitHub contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/en/criteria)
