# Installation

[日本語](installation.ja.md) · [Back to README](../README.md)

Schematic Humanizer is distributed as a Codex skill. Install the package directory—not the repository root—so that the final path ends in `schematic-humanizer/SKILL.md`.

## Requirements

- Codex with local skill support
- Git for cloning the repository
- An EDA application or renderer appropriate to your source when you expect editable output
- A disposable branch or backup of the design

KiCad is first-class because its text source and CLI exports support strong automation. Other tools use adapters with different validation capabilities; see [Adapters](adapters.md).

## Option A: project-local installation

Choose this for a team repository or when the workflow should travel with the project.

### PowerShell

Run from the target project root:

```powershell
$source = Join-Path $env:TEMP "schematic-humanizer"
git clone https://github.com/keitark/schematic-humanizer.git $source
New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
Copy-Item -Recurse -Force "$source\.agents\skills\schematic-humanizer" ".agents\skills\"
```

### macOS or Linux

Run from the target project root:

```bash
source_dir="$(mktemp -d)/schematic-humanizer"
git clone https://github.com/keitark/schematic-humanizer.git "$source_dir"
mkdir -p .agents/skills
cp -R "$source_dir/.agents/skills/schematic-humanizer" .agents/skills/
```

Expected result:

```text
your-project/.agents/skills/schematic-humanizer/SKILL.md
```

Commit the skill package only if your team wants the same version stored with the project. Review your organization’s policy before vendoring third-party files.

## Option B: personal installation

Choose this when you want the skill available across projects.

### PowerShell

```powershell
$source = Join-Path $env:TEMP "schematic-humanizer"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
git clone https://github.com/keitark/schematic-humanizer.git $source
New-Item -ItemType Directory -Force (Join-Path $codexHome "skills") | Out-Null
Copy-Item -Recurse -Force "$source\.agents\skills\schematic-humanizer" (Join-Path $codexHome "skills")
```

### macOS or Linux

```bash
source_dir="$(mktemp -d)/schematic-humanizer"
codex_home="${CODEX_HOME:-$HOME/.codex}"
git clone https://github.com/keitark/schematic-humanizer.git "$source_dir"
mkdir -p "$codex_home/skills"
cp -R "$source_dir/.agents/skills/schematic-humanizer" "$codex_home/skills/"
```

Expected result:

```text
$CODEX_HOME/skills/schematic-humanizer/SKILL.md
```

When `CODEX_HOME` is unset, `$CODEX_HOME` in that example means `~/.codex`.

## Activate and verify

Start a new Codex task after installation. Ask:

```text
Use $schematic-humanizer to inspect this project's schematic sources and
describe the safe readability-improvement plan. Do not edit anything yet.
```

A correct response should first identify the source type, source-of-truth rules, available render/export tools, and whether exact connectivity validation is possible. It should not promise electrical approval.

## Update

Pull a fresh copy of the repository and replace only the installed `schematic-humanizer` directory. Start a new Codex task so the updated instructions are loaded.

Do not merge two skill versions into the same directory; stale references can produce inconsistent behavior.

## Uninstall

Remove only the installed directory:

- Project-local: `.agents/skills/schematic-humanizer`
- Personal: `$CODEX_HOME/skills/schematic-humanizer`, or `~/.codex/skills/schematic-humanizer`

This does not revert schematic files previously changed by Codex. Use your version-control history or backup for that.

## Troubleshooting

### Codex does not recognize the skill

- Confirm that `SKILL.md` is directly inside the `schematic-humanizer` directory.
- Check for accidental nesting such as `schematic-humanizer/schematic-humanizer/SKILL.md`.
- Start a new task after installation.
- Prefer the project-local copy when both installations exist and you need a pinned version.

### The requested EDA tool is unavailable

Export a netlist plus PDF/SVG renders from the native tool when possible. Without editable source or a trustworthy netlist, the skill must use the visually guided workflow and cannot prove connectivity preservation.

For help, read [SUPPORT.md](../SUPPORT.md).
