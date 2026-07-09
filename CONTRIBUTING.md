# Contributing / コントリビューション

Thank you for helping make schematics easier to review. 回路図を読みやすくする改善へのご協力、ありがとうございます。

## Ground rules / 基本ルール

- Keep the workflow EDA-neutral and place tool-specific behavior in the appropriate adapter documentation or skill resource.
- Never weaken the distinction between exact connectivity validation and visually guided review.
- Do not describe a cleaner drawing as electrically approved.
- Use small, reproducible fixtures when examples are needed. Never contribute proprietary designs without permission.
- Keep the skill concise; put extended adapter details in references rather than bloating `SKILL.md`.

- ワークフロー本体は EDA 非依存にし、ツール固有の動作はアダプター資料またはスキルリソースへ配置してください。
- 厳密な接続検証と目視ベースのレビューを混同しないでください。
- 見やすくなった回路図を「電気的に承認済み」と表現しないでください。
- 例には小さく再現可能なデータを使い、許可のない独自設計を含めないでください。

## Development workflow

1. Search existing issues, then open a focused bug or feature request.
2. Create a short-lived branch.
3. Update English and Japanese documentation together when user-facing behavior changes.
4. Run `python scripts/validate_repo.py` from the repository root.
5. Test the skill against a disposable copy of a representative schematic.
6. Include the input type, validation method, before/after render, and limitations in the pull request.

## Pull-request checklist

- [ ] The skill triggers for the intended request without claiming unsupported tools.
- [ ] Connectivity changes are prohibited by default or explicitly gated.
- [ ] A source-of-truth rule is documented.
- [ ] Exact validation is used only when the format/tooling supports it.
- [ ] PDF/image-only output is marked visually guided and unverified.
- [ ] English and Japanese user-facing pages remain aligned.
- [ ] `python scripts/validate_repo.py` passes.

By contributing, you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
