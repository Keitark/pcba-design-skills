# Circuit evidence adapters

Every adapter states authoritative source, parser/export, editable path,
ERC/lint/simulation, renderer, protected artifacts, and limitations.

- **KiCad:** inspect `.kicad_pro`, `.kicad_sch`, libraries, netlist, and any
  generator. Edit generator/native source and use native ERC/export/render.
- **Altium:** use project, SchDoc libraries, compiler, reports, and automation;
  never hex-edit binary documents.
- **EasyEDA Standard/Pro:** identify the edition and cloud/export source. Do not
  assume the two formats or IDs are interchangeable.
- **EAGLE/Fusion, gEDA/Lepton:** use native text/API and netlist/check tools with
  captured library versions and implicit-power/slotting rules.
- **SPICE/netlist:** connectivity and simulation can be authoritative, but
  footprint, connector, and graphical intent may be absent.
- **PDF/image:** findings are visually guided and transcription-limited. Do not
  implement electrical corrections without native source or trusted netlist.

Use the same evidence path before and after an authorized change.
