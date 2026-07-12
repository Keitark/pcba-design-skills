# スキルの選び方

[English](choose-a-skill.md) · [README に戻る](../README.ja.md)

必要な成果物だけなら専門スキルを 1 個導入します。複数段階を連携し、証拠・
無効化・承認状態を維持する場合は 8 個全部を導入します。

| 入力・依頼 | 最初に使うスキル | 単独利用できる条件 |
|---|---|---|
| アイデア、機能説明、曖昧な要件 | `plan-electronic-product` | 製品ブリーフと構成だけが必要 |
| BOM、高価／入手不能部品、パッケージ相談 | `qualify-pcba-sourcing` | 回路要件と数量が分かる |
| 回路図／ネットリストが正しいか監査 | `design-and-review-circuit` | 製品動作と正確な部品情報がある |
| ラベル過多、重なり、浮いて見える回路図 | `schematic-humanizer` | 電気変更なしで表示を改善する |
| PCB 配置、配線、層、open、DRC | `pcb-layout-review` | 回路制約とネイティブ PCB がある |
| Gerber、ドリル、BOM、CPL を発注用に統一 | `release-pcba-fabrication` | 上流の回路・レイアウトが合格済み |
| リリース済みデータと JLCPCB 画面 | `operate-jlcpcb-order` | 不変リリースと承認ゲートがある |
| 複数段階、説明から発注レビューまで | `manage-pcba-program` と必要な全専門スキル | 必要な専門スキルが導入済み |

## よく使う組み合わせ

- 読みにくい回路図だけ: `schematic-humanizer`
- 読みにくく回路バグも心配: humanizer + circuit review（結果は分離）
- レイアウト前の既存設計: sourcing → circuit → humanizer → layout
- 発注前の既存 PCB: layout → release → JLCPCB operator
- 新規製品全体: manager + 7 専門スキル

マネージャーは未導入の専門スキルを代行しません。各専門スキルは単独で使え、
`.pcba-workflow/` に成果物を書きます。

回路図の見やすさ、電気設計、部品調達、PCB、製造データ、実装プレビュー、
価格、支払いを一つの「OK」にまとめないでください。
