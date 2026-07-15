# プロンプト例

[English](prompts.md) · [README に戻る](../README.ja.md)

角括弧を置き換えてください。Codex は `$skill-name`、Claude Code は
`/skill-name` を使います。

## 全体

```text
$manage-pcba-program を使って [プロジェクト/パス] の説明、回路図/ネットリスト、
BOM、PCB を確認してください。.pcba-workflow/program-state.json を作成し、
導入済みの専門スキルだけを呼び出し、BLOCKED または USER_REVIEW で停止して
ください。発注・支払いは行わないでください。
```

## 製品計画

```text
$plan-electronic-product を使って [説明] を product-brief.yaml と architecture.md
へ整理してください。SPEC、TARGET、ASSUMPTION、TBD_MEASURE を分け、安全性や
構成を大きく変える選択だけ質問してください。
```

## 部品調達

```text
$qualify-pcba-sourcing を使って [BOM/パス] を [数量] 台分検証してください。
最新の公式データシートと販売元証拠を使い、MPN、物理ピン、パッケージ、
フットプリント、CAD/3D、ライフサイクル、在庫、MOQ、総費用、代替品を確認し、
設計は変更しないでください。
```

## 回路監査

```text
$design-and-review-circuit を使って [回路図/ネットリスト] を製品ブリーフと
sourcing lock に照らして監査してください。動作、部品役割、電源、電圧領域、
reset/boot、バス所有権、タイミング、保護、レイアウト制約を説明し、まだ編集しないでください。
```

## 回路図の人間可読化

```text
$schematic-humanizer を使って [ソース/パス] を実配線された機能別シートへ
整理してください。接続を維持し、本物のバスを使い、重なりと浮いて見える
ローカル回路を全て除去し、全ページと高密度部を画像確認して接続/ERC を比較してください。
```

## PCB レイアウト

```text
$pcb-layout-review を使って [PCB/パス] を人間可読化した構成と回路制約から
監査してください。配置、デカップリング、層/基準面、電源、配線、RF/機構、
raw 接続、実 DRC、ドリル費用、2D/3D を確認し、0 open だけで合格にしないでください。
```

## 製造リリース

```text
$release-pcba-fabrication を使って不変の [リビジョン] リリースを作成してください。
Gerber、ドリル、BOM、CPL、制約、実装図、画像を独立確認し、全ハッシュを
release-manifest.json に記録し、混在リビジョンを拒否してください。
```

## JLCPCB

```text
$operate-jlcpcb-order を [release-manifest/パス] で使ってください。リリース済み
設定だけを入力し、費用異常、全ての部品割当、CPL の物理 pad、表裏の全配置を
確認し、代替品・配置・最終価格・支払いを別々に承認待ちしてください。
manifest に任意の現物ステンシル指定がある場合は、Paste 面、フレーム有無、
外形寸法、厚さ、価格も確認してください。注文外形寸法を指定するだけのために、
別のステンシル外形図面は作らないでください。
```
