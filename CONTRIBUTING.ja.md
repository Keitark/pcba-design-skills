# コントリビューション

[English](CONTRIBUTING.md)

## 基本ルール

- 大きな変更は先に Issue を作成／再利用し、Issue 番号付き短期 branch を使います。
- 各スキルを単独導入可能にし、`SKILL.md` は 500 行以内、詳細は直接参照する
  `references/`、`scripts/`、`assets/` へ分けます。
- 実行スキルは英語で統一し、公開ガイドは英語・日本語を同時更新します。
- 共通ロジックを EDA 非依存にし、ツール固有処理は正本、編集、render、検証、
  制約を明示した adapter にします。
- 接続、電気、目視、DRC/電源、release 整合、CPL 配置、ユーザー承認の境界を
  弱めません。
- 試験には小さな synthetic fixture を使い、機密設計、認証情報、account page、
  独自データを追加しません。
- project 学習は `.pcba-workflow/` に保存し、一般化・再現できる知識だけを
  upstream 提案します。導入済み skill を自動書換えしません。

## 開発手順

1. 新規スキルは OpenAI `skill-creator` で初期化します。
2. 繰り返し処理は長い説明より先に決定的 script 化します。
3. `PYTHONUTF8=1 python scripts/validate_repo.py` を実行します。
4. disposable directory で unit test、install、smoke test を実行します。
5. 複雑な skill は最小限の raw context で forward-test します。
6. PR にコマンド、結果、risk、代表画像を記載します。

コード・独自文書は MIT です。第三者 asset は互換ライセンスと完全な帰属表示なしで
追加しないでください。詳細は [ASSET-LICENSES.md](ASSET-LICENSES.md) を参照します。
