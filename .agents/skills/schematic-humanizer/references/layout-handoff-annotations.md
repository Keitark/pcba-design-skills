# Layout handoff annotations / レイアウト引き継ぎ注記

Add layout annotations when the user explicitly requests them or when the source
clearly exposes placement-sensitive interfaces. Do not guess hidden electrical
requirements. Ask the user only when the missing choice would materially change
the design; otherwise mark it for measurement or engineering review.

ユーザーの明示要求、または回路から配置・配線制約を明確に判断できる場合に
注記を追加する。不明な電気条件を推測しない。設計を大きく変える選択だけを
質問し、それ以外は要実測・要レビューとして明記する。

## Evidence classes / 根拠区分

- `[SPEC]`: manufacturer datasheet, interface standard, approved project
  requirement, or verified measured value. Include the source in the companion
  document.
- `[TARGET]`: conservative project routing allocation chosen for this revision,
  such as loose group skew, firmware-rate ceiling, current capacity, or layer
  preference. Explain that it is not certified timing or measured current.
- `[TBD-MEASURE]`: source capability, thermal rise, real current, unknown clock,
  enclosure RF performance, or another item that cannot be proven from the
  schematic.

- `[SPEC]`: データシート、規格、承認済み要件、確認済み実測値。
- `[TARGET]`: この版の保守的な設計目標。タイミング保証や実測値ではない。
- `[TBD-MEASURE]`: 電流、温度、電源能力、未知クロック、筐体 RF など要確認項目。

## What to capture / 記載項目

For each meaningful interface or rail, capture only applicable items:

1. Clock, data rate, or access cadence, plus the warning that edge rate can set
   signal-integrity risk even when the clock is slow.
2. Required topology and stub rule: source → buffer/termination → receiver,
   point-to-point, daisy chain, star, or explicitly forbidden branches.
3. Reference plane, layer preference, controlled impedance, spacing, and return
   transition guidance.
4. Group skew or pair mismatch target. Avoid meanders when the timing budget
   does not require them.
5. Provisional current allocation, shared-trunk capacity, trace/pour and via
   intent, voltage-drop/thermal signoff, and measurement state.
6. Component placement: decoupling escape path, regulator loop, crystal, antenna
   keepout, connector ESD, exposed-interface protection, and mechanical keepouts.
7. Authoritative manufacturer or standards URL in a companion layout guide.

クロック/データレート、エッジレート、トポロジ、スタブ、基準面、層、
インピーダンス、長さ差、暫定電流、配線幅・ビア、配置、メーカー資料を、
該当する範囲だけ記載する。

## Presentation / 表示方法

- Put short, local callouts near the relevant functional region, but outside
  wires, buses, symbols, labels, and the dominant visual flow.
- Keep full calculations, current-budget tables, URLs, assumptions, and signoff
  checklists in a companion Markdown/PDF document. Link it with a short on-sheet
  note.
- Do not label an entire design with one clock when domains differ. Separate CPU,
  memory, loader, RF, USB, and other interfaces.
- Do not add a generic impedance width/gap before the final fabricator stackup is
  known. State the impedance and reference plane, then require stackup-derived
  geometry.
- Treat a vendor module with an integrated antenna as a placement/keepout problem;
  do not invent an RF feed trace that is not in the circuit.

注記は関連機能の近くに短く置き、配線や信号の流れを隠さない。計算、表、
完全な URL、前提、承認項目は別文書へ移す。異なるクロック領域を一つの速度
で表現せず、最終スタックアップ前に汎用線幅を固定しない。

## Required final gate / 必須最終確認

Annotations can introduce new overlaps. After adding them, follow the complete
[visual audit checklist](visual-audit-checklist.md), including every full page
and dense crops around the annotated regions. Then repeat connectivity comparison
and ERC/lint. A clean netlist does not excuse a visually obscured schematic.

注記追加後は全ページと高密度部分を再レンダリングし、目視監査、接続比較、
ERC を繰り返す。ネットリストが正しくても、注記が回路を隠す場合は不合格。

