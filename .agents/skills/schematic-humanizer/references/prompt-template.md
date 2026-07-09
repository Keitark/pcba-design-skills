# Prompt templates / プロンプト例

Replace bracketed text before use. / 角括弧の部分を置き換えて使用してください。

## English

```text
Use $schematic-humanizer to improve the human readability of the schematic in [repository/path]. The source format is [KiCad/Altium/EasyEDA/EAGLE/Fusion/gEDA/Lepton/SPICE/PDF/image/unknown].

First detect the EDA format and authoritative source. If a generator owns the schematic, edit the generator rather than only its output. Before editing, export connectivity and normalize it to a component-reference, pin, and named-net model. Save the ERC/lint baseline and proof that protected PCB/layout files are unchanged. If the available format cannot prove connectivity, tell me exactly what is unverifiable before proceeding with visual-only work.

Reorganize the drawing into functional sheets and show signal flow with visible native wires, buses, and entries. Directly connect nearby connectors, USB, MCU support, memory, level shifters, glue logic, reset/boot, pulls, LEDs, and power paths. Reserve labels mainly for cross-sheet or genuinely long connections. Rotate connectors toward the circuits they serve. Do not route wires or buses under symbols or text, leave visually floating logic, or accept any overlap.

If I request layout guidance, or the circuit clearly exposes clocks, buses, power rails, high-current paths, controlled interfaces, RF/antenna constraints, or vendor placement rules, add concise layout callouts. Mark each value `[SPEC]`, `[TARGET]`, or `[TBD-MEASURE]`; never guess an unknown. Put calculations and authoritative URLs in a companion document. Render again after adding comments and reject any text/wire/bus overlap.

Export every final sheet to PDF, render every page to PNG, inspect them yourself, and iterate until the diagram is clear. Normalize post-edit connectivity with the same adapter and compare it exactly with the baseline. Require no new ERC/lint findings and no protected-file changes. Show the final snapshot and report the adapter, equivalence result, visual inspection, and every remaining limitation separately from any circuit-design audit.
```

## 日本語

```text
$schematic-humanizer を使って、[リポジトリ／パス] の回路図を人が読みやすい図へ改善してください。元データ形式は [KiCad／Altium／EasyEDA／EAGLE／Fusion／gEDA／Lepton／SPICE／PDF／画像／不明] です。

最初に EDA 形式と正本を特定してください。生成スクリプトが正本なら、生成後の回路図だけでなく生成スクリプトを編集してください。編集前に接続情報をエクスポートし、部品リファレンス、ピン、名前付きネットの共通モデルへ正規化してください。ERC／lint の基準結果と、保護対象の PCB／レイアウトファイルが未変更である証拠を保存してください。形式上、接続の証明ができない場合は、目視改善を始める前に検証不能な項目を明記してください。

機能単位のシートへ整理し、標準の配線、バス、バスエントリで信号経路を見えるようにしてください。近くにあるコネクタ、USB、MCU 周辺、メモリ、レベルシフタ、グルーロジック、リセット／ブート、プル抵抗、LED、電源経路は直接接続してください。ラベルは主にページ間または本当に離れた接続だけに使い、コネクタは接続先へ向けてください。配線を部品や文字の下へ通さず、見た目上未接続のロジックや重なりを残さないでください。

レイアウト注記を依頼した場合、またはクロック、バス、電源、大電流、インピーダンス管理、RF／アンテナ、メーカー配置規則を回路から明確に判断できる場合は、短い注記を追加してください。値は `[SPEC]`、`[TARGET]`、`[TBD-MEASURE]` に区分し、不明値を推測しないでください。計算と公式 URL は別文書へ置き、注記追加後に再レンダリングして重なりを不合格にしてください。

最終全シートを PDF 出力し、全ページを PNG 化して自分で目視確認し、明確になるまで修正してください。同じアダプターで変更後の接続を正規化し、変更前と厳密比較してください。ERC／lint を増やさず、保護ファイルを変更しないでください。最終画像を提示し、アダプター、同一性、目視確認、残る制約を報告してください。回路設計自体の監査は読みやすさ改善と分けてください。
```
