# サポート

[English](SUPPORT.md)

Schematic Humanizer はコミュニティプロジェクトです。小さく再現可能で、検証できる範囲とできない範囲が明確な報告ほど、早く問題を特定できます。

## Issue を作成する前に

1. [インストールガイド](docs/installation.ja.md)と[アダプターガイド](docs/adapters.ja.md)を確認します。
2. `.agents/skills/schematic-humanizer/SKILL.md` または個人用インストールを Codex が参照できることを確認します。
3. インストールまたは更新後は、新しい Codex タスクを開始します。
4. コピーまたはクリーンなブランチで再現します。唯一の回路設計データを直接テストに使わないでください。
5. 認証情報、独自部品データ、顧客名、機密回路図を除去してください。

## 添付してほしい情報

- OS、利用している Codex の画面／バージョン
- EDA ツールとバージョン。EDA ツールがない場合は入力形式
- 編集可能ソース、生成ソース、ネットリスト／SPICE、PDF、画像のどれか
- 使用したプロンプト全文
- 「生成済み `.kicad_sch` ではなく `gen_sch.py` を編集する」のような正本ルール
- 厳密検証を期待する場合は変更前後のネットリスト／ERC 結果
- 問題が分かる最小範囲の変更前後レンダー画像
- 機密のパスや値を伏せた完全なエラー全文

PDF／画像のみの場合は、厳密な接続検証ができないことを明記してください。視覚上の不具合も有効なバグ報告ですが、必要な証拠が異なります。

## 問い合わせ先

- [バグを報告](https://github.com/keitark/schematic-humanizer/issues/new?template=bug_report.yml)
- [アダプター／機能を提案](https://github.com/keitark/schematic-humanizer/issues/new?template=feature_request.yml)
- [既存 Issue を検索](https://github.com/keitark/schematic-humanizer/issues)

## 重要な制約

サポート対象はワークフローと出力の改善です。電気的正しさ、規格適合、製造可能性、製品安全性を認証するものではありません。生成・整理された回路図は、必ずエンジニアリングレビュー用資料として扱ってください。
