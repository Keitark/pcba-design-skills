# PCB layout adapters

An adapter must identify native source/project, supported edit method,
connectivity query, raw/classified DRC, layer/zone inspection, renderer,
manufacturing export, protected artifacts, and known limitations.

- **KiCad:** first-class text project/board plus `kicad-cli` and supported
  native API/IPC. Pair board and project rules when snapshotting.
- **Altium:** use PCB project, rules, native DRC, layer stack, Draftsman/outputs,
  and automation. Do not modify binary PCB documents with a generic parser.
- **EasyEDA Standard/Pro:** use the matching editor/export and distinguish the
  editions. Capture rule, layer, and origin conventions.
- **EAGLE/Fusion Electronics:** use legacy XML only when it is authoritative;
  otherwise use Fusion's native project/export path.
- **IPC-2581/ODB++:** useful structured review/manufacturing evidence when the
  exporter is trusted, but not automatically an editable source.
- **Gerber/drill/CPL or images only:** permit DFM and visual review. They cannot
  safely prove full net connectivity or support arbitrary layout edits.

For unsupported tools, require equivalent evidence or mark the affected gate
BLOCKED; do not fall back to visual plausibility.
