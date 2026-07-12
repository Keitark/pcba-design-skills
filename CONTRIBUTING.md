# Contributing

[日本語](CONTRIBUTING.ja.md)

## Ground rules

- Open or reuse an issue before non-trivial work; use a short issue-linked branch.
- Keep each skill self-contained, its `SKILL.md` under 500 lines, and detailed
  material in directly linked `references/`, `scripts/`, or `assets/`.
- Keep executable skill instructions in English. Update paired English/Japanese
  public guides together.
- Keep workflow logic EDA-neutral and place tool-specific behavior behind an
  explicit adapter with source, edit, render, validation, and limitation rules.
- Never weaken connectivity, electrical, visual, DRC/power, release integrity,
  CPL placement, or user-approval boundaries.
- Use small synthetic fixtures for tests. Never contribute confidential designs,
  credentials, account pages, or proprietary data.
- Project learning belongs in `.pcba-workflow/`; propose a sanitized,
  reproducible lesson upstream instead of making an installed skill self-modify.

## Development

1. Initialize new skill folders with OpenAI `skill-creator`.
2. Add deterministic helpers before long procedural explanations.
3. Run `PYTHONUTF8=1 python scripts/validate_repo.py`.
4. Run the unit tests and install/smoke tests on disposable directories.
5. Forward-test complex skill behavior with minimal raw context.
6. Include test commands/results, risk, and representative visual evidence in
   the pull request.

## Pull-request checklist

- [ ] Trigger description is specific and does not collide with another skill.
- [ ] Standalone installation contains every required local resource.
- [ ] Exact validation is claimed only for supported evidence.
- [ ] Circuit readability and correctness remain separate.
- [ ] Raw/power connectivity and real DRC are not hidden by a zero-open summary.
- [ ] Source CPL correction and complete preview review remain mandatory.
- [ ] No private paths, credentials, account data, or tracked cache files exist.
- [ ] English/Japanese guides and asset licensing are aligned.
- [ ] Repository validation and tests pass.

Contributions are MIT unless a file is explicitly listed under
[asset licensing](ASSET-LICENSES.md). Do not add third-party assets without a
compatible license and complete attribution.
