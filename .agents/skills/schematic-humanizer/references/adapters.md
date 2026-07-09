# EDA adapters / EDA アダプター

Use native exporters whenever possible. An adapter is acceptable only when it can repeat the same normalization before and after editing.

可能な限り EDA の標準エクスポートを使い、変更前後で同じ正規化手順を再現できる場合だけ同一性を判定します。

| Source | Safe source/edit path | Connectivity and render evidence | Limitations / 注意点 |
|---|---|---|---|
| **KiCad — first class / 最優先対応** | Detect `.kicad_pro`, `.kicad_sch`, symbol tables, and any generator. Edit generator or native schematic. | Export KiCad XML netlists before/after; compare directly with `compare_connectivity.py`. Run native ERC. Export PDF and render all pages. | Preserve references, net names, pin numbers, and PCB bytes. Net codes, coordinates, timestamps, and sheet paths are presentation/export metadata. |
| **Altium Designer** | Treat `.PrjPcb`, `.SchDoc`, libraries, parameters, and scripts as authoritative. Use Altium UI/automation; do not hex-edit binary documents. | Export a netlist/report containing designator, pin, and net; write a deterministic adapter to canonical JSON. Publish schematic PDF and ERC/compiler report. | Export dialects vary by version/template. Prove field mapping on a small sample; state if hidden harness, variant, or multi-part data is omitted. |
| **EasyEDA Standard/Pro** | Identify Standard vs Pro and whether JSON/source export or cloud project is authoritative. Edit through the matching editor or documented project format. | Export netlist/design data and PDF from the same edition; normalize references, pin numbers, and net names to canonical JSON. Run its design checks. | Standard and Pro formats differ. Do not assume a third-party parser preserves internal IDs, net ties, or multi-unit semantics. |
| **EAGLE / Autodesk Fusion Electronics** | For legacy EAGLE XML `.sch`, use a tested XML adapter or native editor. For Fusion-managed projects, use Fusion export/API rather than editing cache files. | Normalize `<parts>`, `<nets>`, `<segment>`, and `<pinref>` from EAGLE XML, or use a Fusion netlist export. Print/export every schematic sheet. | Supply pins and implicit nets may need library resolution. Fusion exports can differ from legacy EAGLE XML; document the version. |
| **gEDA / Lepton EDA** | Treat text `.sch`, symbol libraries, and project scripts as source. Use native tools or deliberate text edits that preserve attributes. | Use `gnetlist` or `lepton-netlist` output plus a documented normalizer; render with the matching native tool and run available checks. | Slotting, inherited attributes, and library search paths affect pin identity. Capture tool and library versions. |
| **SPICE or other netlist source** | Treat the text netlist and included models/subcircuits as source. Preserve node order and `.include` resolution. A newly drawn schematic may be a companion artifact rather than the source. | Parse instances, node positions, and subcircuit pin definitions into canonical refs/pins/nets; compare source text semantics and run the simulator/parser. | SPICE node order is device/model dependent and may not contain PCB footprints or display names. State the pin-mapping assumptions. |
| **PDF/image only / PDF・画像のみ** | Do not overwrite the only evidence. Trace into a new native schematic or create a visual companion diagram. | Render/inspect visually and keep a transcription log. Compare OCR/manual observations only as review aids. | Electrical equivalence is **unverifiable** without native source or a trusted netlist. Mark uncertain pins/nets and request better source material. |

## Canonical JSON

Use UTF-8 JSON with this shape:

```json
{
  "schema": "schematic-connectivity-v1",
  "components": [
    {"ref": "R1", "value": "1k", "footprint": "R_0603", "device": "Device:R"}
  ],
  "nets": [
    {"name": "SIGNAL", "pins": [{"ref": "R1", "pin": "1"}, {"ref": "U1", "pin": "4"}]}
  ]
}
```

Sort order is irrelevant. References, pin identifiers, net names, and component identity strings are exact and case-sensitive. Adapters may leave `value`, `footprint`, or `device` empty only when the source does not provide them; use the same policy before and after.

並び順は不問です。リファレンス、ピン、ネット名、部品情報は大文字小文字を含めて厳密比較します。取得できない項目は変更前後で同じ空欄ポリシーを使います。
