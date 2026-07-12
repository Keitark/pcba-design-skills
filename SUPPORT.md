# Support

[日本語](SUPPORT.ja.md) · [Back to README](README.md)

PCBA Design Skills is a community engineering-workflow project. Useful reports
are reproducible, identify the exact skill and artifact contract, and state what
the available source can actually prove.

## Before opening an issue

1. Read the [installation](docs/installation.md),
   [skill selection](docs/choose-a-skill.md), and relevant adapter/contract guide.
2. Confirm the installed path ends in `<skill-name>/SKILL.md` and start a new
   Codex task when required. For Claude Code, confirm the skill appears under
   `/skill-name`.
3. Reproduce on a disposable copy or branch, never the only hardware source.
4. Remove credentials, account pages, addresses, order IDs, customer names,
   proprietary designs, supplier tokens, and confidential BOM data.

## Include

- OS, Codex or Claude Code version, skill name/version, EDA tool/version
- Exact prompt and input type
- Authoritative source or generator rule
- Smallest safe fixture or redacted artifact
- Expected and actual gate/status
- Complete error and command output
- Relevant before/after connectivity, ERC/DRC, hash, render, quote, or placement
  evidence
- Whether the workflow is exact, partial, or visually guided only

Never publish a full private manufacturing page just to show one placement
problem. Crop to the board/component and redact personal or commercial data.

## Links

- [Report a bug](https://github.com/Keitark/pcba-design-skills/issues/new?template=bug_report.yml)
- [Request a feature or adapter](https://github.com/Keitark/pcba-design-skills/issues/new?template=feature_request.yml)
- [Browse issues](https://github.com/Keitark/pcba-design-skills/issues)

## Limit

The project supplies review procedures and deterministic checks; it does not
certify electrical correctness, safety, regulatory compliance, fabrication,
assembly, or supplier work. A qualified engineer and manufacturer remain
responsible for the released product.
