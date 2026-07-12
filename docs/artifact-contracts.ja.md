# 成果物契約とステージゲート

[English](artifact-contracts.md) · [README に戻る](../README.ja.md)

連携用状態は既定で `.pcba-workflow/` に保存します。エージェント間の翻訳ずれを
避けるため、機械可読フィールドと状態値は英語で統一します。

## 状態

- `PASS`: 必要な証拠が合格
- `BLOCKED`: 証拠不足、不一致、期限切れ、検証失敗により進行不可
- `USER_REVIEW`: 技術証拠は揃ったが、所有者の明示判断が必要

## 主な成果物

| ファイル | 所有スキル | 内容 |
|---|---|---|
| `program-state.json` | manager | 各ゲート、証拠、ハッシュ、リスク、承認、無効化履歴 |
| `product-brief.yaml`, `architecture.md` | planner | 動作、状態、I/F、電源、機構、数量、費用、構成 |
| `sourcing-lock.csv` | sourcing | 要求/選定 MPN、販売元、package、pinout、CAD、寿命、在庫、費用、代替承認の証拠 |
| `circuit-review.md` | circuit | 動作、部品役割、電源、タイミング、指摘、制約 |
| `schematic-visual-audit.json` | humanizer | アダプター、全ページ/拡大画像、重なり、接続の見え方 |
| `layout-review.json`, `layout-experiments.jsonl` | layout | 配置、層、接続、実 DRC、電源、画像、DFM、実験採点 |
| `release-manifest.json` | release | リビジョン、制約、検証、承認、全 SHA-256 |
| `assembly-placement-review.json` | JLCPCB | CPL hash、校正、全行比較、目視結果、ユーザー承認 |

## 接続と物理 pad

`schematic-connectivity-v1` は部品識別と、全ネットの `(reference, pin)` 所属を
厳密に表します。並び順以外は大文字小文字も含めて一致が必要です。

`pcba-footprint-geometry-v1` は、各部品の配置、面、回転、物理 pin 1、全物理 pad
instance を表します。同じ電気 pad 番号を持つ複数端子や tab を平均しては
いけません。

## 無効化

- netlist/回路変更: circuit 以降を再実施
- MPN/パッケージ変更: sourcing 以降
- footprint/配置変更: placement 以降
- 配線/zone変更: routing、release、placement preview、order
- BOM/CPL変更: release と downstream（BOM は sourcing も）
- ブラウザの X/Y/回転変更: CPL ソースへ反映し、全配置レビューを再実施
- 同一部品の在庫/価格だけ: sourcing と最終価格承認

重要部品代替、実装配置、最終価格、支払いは独立した `PENDING`、`APPROVED`、
`REJECTED` として保存し、一つの承認を他へ流用しません。
