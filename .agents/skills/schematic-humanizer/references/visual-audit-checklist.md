# Visual audit checklist / 目視監査チェックリスト

This checklist is mandatory after every meaningful schematic rearrangement and
again after adding comments or layout guidance. Passing ERC does not pass the
visual audit.

このチェックリストは、回路図の再配置後と注記追加後に必ず実施する。ERC
が合格しても、目視監査の代わりにはならない。

## Routing and buses / 配線とバス

- Do not maximize wire count. Prefer direct local wiring where it clarifies a
  relationship, and matched labels where a long wire would create a loop or
  spaghetti.
- Keep every bus spine outside symbol bodies, values, references, notes, and
  unrelated labels. Large MCUs and modules need extra clearance.
- Never place two different bus spines collinearly on top of one another.
- Avoid wire-through-pin paths that can look connected or create accidental
  connectivity. Make branches and junctions explicit.
- Use the native grid and snap bus entries to it. Keep entry pitch and direction
  consistent.
- In tools where wires are two-point segments, emit a separate segment for each
  bend. Split bus backbones at T-tap endpoints when the format requires explicit
  junction geometry.
- Move pulls, termination parts, decouplers, and interface passives near the
  circuit they support when this makes the function readable.

- 配線本数を増やすことを目標にしない。近接関係は実配線で示し、長い迂回
  配線がスパゲッティ化する場合は対応ラベルを使う。
- バス幹線を部品、値、リファレンス、注記の下へ通さない。異なるバスを
  同一直線上で重ねず、T 分岐と接続点を明確にする。
- グリッドとスナップを使い、バスエントリの間隔と方向を統一する。

## Full-page inspection / 全体確認

Render every page to PNG at a resolution where pin labels remain readable.
Inspect:

- dominant left-to-right signal flow;
- functional grouping and sheet titles;
- apparent floating connectors, MCU support logic, power chains, and controls;
- long loops, excessive labels, clipped text, title-block collisions, and empty
  areas that hide a broken flow;
- each page edge and every cross-sheet endpoint.

全ページをピン名が読める解像度で PNG 化し、信号方向、機能グループ、
見た目上の未接続、長い迂回、ラベル過多、文字切れ、ページ端を確認する。

## Dense-area crops / 高密度部分

Inspect enlarged crops around:

- large MCUs, FPGAs, modules, and memories;
- USB, Ethernet, RF, clock, and external connectors;
- bus entries and places where multiple spines pass;
- power OR-ing, regulators, reset/boot, glue logic, and ownership controls;
- any area changed after the previous render.

大規模 IC、メモリ、外部インターフェース、バスエントリ、電源、リセット、
制御回路、直前に変更した場所を拡大して確認する。

## Annotation gate / 注記の合格条件

After comments or layout callouts are added, render again. Reject the result if
any note hides a wire, bus, pin, reference, value, or functional heading; if a
URL is clipped; if the callout interrupts the visual signal path; or if the
annotation density makes the sheet harder to scan. Move detailed tables and full
links into a companion document and leave only concise pointers on-sheet.

注記追加後は必ず再レンダリングする。注記が配線、バス、ピン、部品名、
見出しを隠す場合、URL が切れる場合、信号経路を遮る場合、情報過多で読みに
くくなる場合は不合格。詳細表と完全な URL は別文書へ移す。

## Acceptance / 完了条件

Completion requires all of the following:

1. Full-page inspection passed for every sheet.
2. Dense crops passed for every relevant interface and edited region.
3. No visible overlap, ambiguous junction, or apparent floating local function.
4. Connectivity comparison and ERC/lint also pass independently.
5. Final snapshots are shown or linked in the completion report.

全シート全体、高密度部分、重なり、接続の見え方、接続比較、ERC、最終画像
のすべてが合格して初めて完了とする。

