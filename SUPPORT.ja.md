# サポート

[English](SUPPORT.md) · [README に戻る](README.ja.md)

PCBA Design Skills はコミュニティの設計ワークフローです。対象スキル、成果物契約、
入力から証明できる範囲を明示した再現可能な報告が有効です。

## Issue の前に

1. [インストール](docs/installation.ja.md)、[スキル選択](docs/choose-a-skill.ja.md)、
   関連する adapter/contract を確認します。
2. 導入先が `<skill-name>/SKILL.md` で終わることを確認します。Codex は必要に応じ
   新しいタスクを開き、Claude Code は `/skill-name` で表示されるか確認します。
3. コピーまたは作業ブランチで再現し、唯一の設計データを直接試験しません。
4. 認証情報、住所、注文番号、顧客名、機密回路、supplier token、非公開 BOM を除去します。

## 添付情報

- OS、Codex/Claude Code、スキル、EDA のバージョン
- 使用プロンプトと入力形式
- 正本または generator のルール
- 最小の安全な fixture または編集済み成果物
- 期待状態と実際の `PASS`/`BLOCKED`/`USER_REVIEW`
- エラー全文とコマンド出力
- 関係する接続、ERC/DRC、hash、画像、見積、配置の変更前後証拠
- 厳密、部分、目視のみのどの検証か

一つの配置不具合を示すために非公開の製造ページ全体を公開しないでください。
基板・部品へ crop し、個人情報と商業情報を伏せます。

## 問い合わせ先

- [バグ報告](https://github.com/Keitark/pcba-design-skills/issues/new?template=bug_report.yml)
- [機能・アダプター提案](https://github.com/Keitark/pcba-design-skills/issues/new?template=feature_request.yml)
- [既存 Issue](https://github.com/Keitark/pcba-design-skills/issues)

このプロジェクトは設計手順と検証ツールを提供しますが、電気、安全、規格、製造、
実装、supplier 作業を認証しません。最終製品は適格な技術者と製造者が確認します。
