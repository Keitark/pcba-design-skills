---
name: schematic-humanizer
description: Reorganize label-heavy or netlist-like electronic schematics into human-readable functional diagrams with visible local wiring while preserving proven connectivity. Use for schematic readability correction, overlapping wires or symbols, visually floating connectors or IC support logic, functional-sheet restructuring, diagram cleanup, or bilingual English/Japanese handoff across KiCad, Altium, EasyEDA, Eagle/Fusion, gEDA/Lepton, SPICE/netlist sources, and PDF/image references.
---

# Schematic Humanizer

Turn an electrically connected but label-heavy schematic into a diagram a human can trace. Preserve the circuit unless the user separately authorizes an electrical change.

ラベルとネットリスト表示に依存した回路図を、人が信号経路を追える図へ改善する。ユーザーが別途許可しない限り、電気的接続は変更しない。

## Adapter contract / アダプター契約

Before editing, identify the EDA format and create an evidence path with these six stages:

1. **Detect** the native source of truth, generator, libraries, project rules, and protected board/layout files.
2. **Export** baseline connectivity with the native tool or a documented parser.
3. **Normalize** it to `schematic-connectivity-v1`: component reference and identity, named net, and every `(reference, pin)` membership.
4. **Edit** only the authoritative source through its generator, native API, supported text format, or controlled GUI workflow.
5. **Render** every sheet and inspect the resulting PDF/PNG visually.
6. **Normalize and compare** post-edit connectivity with the same adapter. Report any property the adapter cannot verify; never call an unverified conversion equivalent.

編集前に EDA と正本を特定し、同じ方法で変更前後の接続情報を正規化・比較する。検証できない項目は明記し、「同一」と断定しない。

Each adapter must state its accepted source, exporter/parser, canonical field mapping, renderer, ERC/lint path, protected artifacts, and known limitations. Read [references/adapters.md](references/adapters.md) for KiCad, Altium, EasyEDA, Eagle/Fusion, gEDA/Lepton, SPICE, and image-only guidance.

Before editing, also read the mandatory [visual audit checklist](references/visual-audit-checklist.md). When the user requests layout guidance, or when clocks, buses, power rails, high-current paths, RF, USB, memory, or other placement-sensitive interfaces are obvious, also read [layout handoff annotations](references/layout-handoff-annotations.md).

## Workflow / 作業手順

1. **Capture the baseline / 変更前基準を保存する**
   - Read repository instructions and design documents. If a generator owns the schematic, edit the generator rather than only its output.
   - Save canonical connectivity, ERC/lint results, and a hash or clean diff for protected PCB/layout files.
   - リポジトリの指示を読み、生成物ではなく正本を特定する。接続、ERC、PCB 未変更確認を保存する。

2. **Plan functional sheets / 機能単位でシートを設計する**
   - Group by signal flow: connector/input → protection or translation → processing/control → memory/output. Isolate power/reset and decoupling when useful.
   - Put dominant flow left-to-right, power at the top, and ground at the bottom. Divide crowded designs into hierarchical sheets with a simple root index.
   - 信号の流れと機能で分割し、主要な流れは左から右、電源は上、GND は下を基本とする。

3. **Show connectivity / 接続を見えるようにする**
   - Draw direct wires for nearby relationships: connectors, USB, oscillators, MCU support, memory controls, level shifters, glue logic, reset/boot, pulls, LEDs, and local power chains.
   - Use the EDA tool's real buses and entries for repeated address/data groups. Keep bus spines outside symbols and use short pin branches.
   - Reserve hierarchical/global labels for cross-sheet, repeated-rail, or genuinely long-distance connections. A label is not a substitute for a clear local path.
   - Rotate or mirror connectors toward the circuits they serve. Orient logic inputs left and outputs right where practical.
   - 近接する部品間は実配線で接続する。ページ間接続以外を安易なラベルで済ませず、コネクタを接続先へ向ける。

4. **Enforce drawing hygiene / 図面品質を守る**
   - Never route wires or buses under symbols, values, references, titles, notes, or unrelated labels.
   - Avoid ambiguous wire-through-pin paths, unintended T-junctions, four-way junctions, long loops, stacked labels, and crowded bus entries.
   - Keep orthogonal routes, consistent grid alignment, generous whitespace, and visible junctions. Do not claim completion while any overlap remains.
   - 配線を部品や文字の下へ通さない。直交配線、十分な余白、明確な接続点を維持する。

5. **Add layout handoff guidance when justified / 必要な場合はレイアウト注記を追加する**
   - Add concise callouts when the user clearly asks, or when the source makes clocks/data rates, parallel buses, controlled-impedance pairs, power-current paths, reference planes, antenna keepouts, or manufacturer placement rules easy to identify.
   - Mark every value as `[SPEC]` (authoritative requirement), `[TARGET]` (project routing allocation), or `[TBD-MEASURE]` (requires measurement or engineering signoff). Never present an estimate as a verified limit.
   - Record rate plus edge-rate caveat, topology/stub rule, reference plane, loose skew target, provisional current allocation, trace/via intent, and authoritative component guidance URL when applicable. Keep full URLs in a companion document, not across the drawing.
   - ユーザーの明示要求、または回路からクロック、バス、電源、RF、USB、配置制約を明確に判断できる場合に注記する。仕様・設計目標・要実測を区別し、推定値を確定値として書かない。

6. **Render and iterate / 画像で反復確認する**
   - Export all sheets to PDF after each meaningful pass. Render every page to PNG at readable resolution and inspect page edges plus dense areas around large ICs, connectors, memories, and buses.
   - Correct overlap, apparent floating pins, reversed flow, clipped text, and excessive label dependence; render again.
   - Inspect the whole page and dense crops after annotations are added. Reject any callout covering signal flow, clipped link, text over a wire/bus, or bus spine under a symbol even if ERC is clean.
   - Follow every item in the mandatory visual audit checklist; wire count is not a success metric.
   - 全ページと高密度部分を PNG 化して目視確認し、重なりや見た目上の未接続がなくなるまで修正する。注記追加後も必ず再確認する。

7. **Prove what can be proved / 検証可能な範囲を証明する**
   - Normalize baseline and final exports, then run:

     ```text
     python scripts/compare_connectivity.py before.json after.json
     ```

     For KiCad, the same command accepts XML netlists directly.
   - Require identical component identities, net names, and ref/pin memberships. Ignore only presentation data and explicitly documented unstable export IDs.
   - Require no new ERC/lint findings. Confirm protected PCB/layout files are unchanged.
   - If only PDF/image evidence exists, report visual improvements as visual only and request native source/netlist for equivalence proof.
   - 変更前後の部品、ネット名、全ピン所属を比較する。画像しかない場合は電気的同一性を証明できないと明記する。

## Completion report / 完了報告

Report the adapter and authoritative files used, canonical comparison counts, ERC/lint before and after, protected-file proof, rendered pages inspected, and unverifiable limitations. Show the final snapshot. Keep circuit-audit findings separate: improved readability is not electrical approval.

使用アダプター、正本、接続比較、ERC、PCB 未変更、目視確認ページ、検証不能項目、最終画像を報告する。読みやすさの合格と電気設計の合格を混同しない。

For a ready-to-copy request, read [references/prompt-template.md](references/prompt-template.md).
