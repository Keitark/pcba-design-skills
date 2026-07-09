# Support

[日本語](SUPPORT.ja.md)

Schematic Humanizer is a community project. The most useful support request is small, reproducible, and explicit about what can and cannot be verified.

## Before opening an issue

1. Read the [installation guide](docs/installation.md) and [adapter guide](docs/adapters.md).
2. Confirm that Codex can see `.agents/skills/schematic-humanizer/SKILL.md` or your personal installation.
3. Start a new Codex task after installing or updating the skill.
4. Reproduce the issue on a copy or clean branch. Do not test against your only copy of a hardware design.
5. Remove credentials, proprietary component data, customer names, and confidential schematics.

## Include this evidence

- Operating system and Codex surface/version
- EDA tool and version, or the source type when no EDA tool is available
- Whether the input is editable source, generated source, netlist/SPICE, PDF, or image
- Exact prompt used
- Relevant source-of-truth rule, such as “edit `gen_sch.py`, never the generated `.kicad_sch`”
- Before and after netlist/ERC evidence when exact validation is expected
- Before and after renders, cropped to the smallest useful area
- Complete error text with sensitive paths or values redacted

For PDF/image-only workflows, say that exact connectivity is unavailable. A visual mismatch is still a valid bug; it simply needs a different evidence standard.

## Where to ask

- [Report a bug](https://github.com/keitark/schematic-humanizer/issues/new?template=bug_report.yml)
- [Request an adapter or feature](https://github.com/keitark/schematic-humanizer/issues/new?template=feature_request.yml)
- [Browse existing issues](https://github.com/keitark/schematic-humanizer/issues)

## Important limitation

Support can help improve the workflow and its output. It cannot certify electrical correctness, regulatory compliance, manufacturing readiness, or product safety. Treat every generated or reorganized schematic as an engineering review artifact.
