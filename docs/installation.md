# Installation

[日本語](installation.ja.md) · [Back to README](../README.md)

Install one independently useful specialist or all eight skills. Each installed
directory must end with `<skill-name>/SKILL.md`; do not install the repository
root as one skill.

## Requirements

- Codex with local skill support, or Claude Code with skill support
- Git for clone-based installation
- Python only when using the Codex system installer or bundled validation tools
- The native EDA/viewer required by the task; installing a skill does not
  install KiCad, Altium, EasyEDA, or fabrication tools

Pin production work to release `v1.0.0`. Use `main` only when intentionally
testing unreleased changes.

## Codex: install one skill from GitHub

The simplest method is to ask Codex:

```text
Use $skill-installer to install schematic-humanizer from
Keitark/pcba-design-skills at
.agents/skills/schematic-humanizer, pinned to v1.0.0.
```

The equivalent PowerShell command uses the preinstalled system helper:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$installer = Join-Path $codexHome "skills\.system\skill-installer\scripts\install-skill-from-github.py"
python $installer --repo Keitark/pcba-design-skills --ref v1.0.0 `
  --path .agents/skills/schematic-humanizer
```

macOS/Linux:

```bash
installer="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py"
python "$installer" --repo Keitark/pcba-design-skills --ref v1.0.0 \
  --path .agents/skills/schematic-humanizer
```

The helper aborts when the destination already exists. Remove or rename an old
copy explicitly before updating; do not merge two versions.

## Codex: install all eight personally

The GitHub helper accepts multiple paths:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$installer = Join-Path $codexHome "skills\.system\skill-installer\scripts\install-skill-from-github.py"
python $installer --repo Keitark/pcba-design-skills --ref v1.0.0 `
  --path .agents/skills/manage-pcba-program `
         .agents/skills/plan-electronic-product `
         .agents/skills/qualify-pcba-sourcing `
         .agents/skills/design-and-review-circuit `
         .agents/skills/schematic-humanizer `
         .agents/skills/pcb-layout-review `
         .agents/skills/release-pcba-fabrication `
         .agents/skills/operate-jlcpcb-order
```

Restart or open a new Codex task after installation. The skills become
available on the next turn.

## Clone-based installer: Codex or Claude Code

Clone a tagged release:

```powershell
git clone --branch v1.0.0 --depth 1 https://github.com/Keitark/pcba-design-skills.git
Set-Location pcba-design-skills
```

PowerShell examples:

```powershell
# One personal Codex skill
.\scripts\install-skills.ps1 -Target codex-personal -Skills schematic-humanizer

# All skills in the current project's .agents/skills
.\scripts\install-skills.ps1 -Target codex-project -All -ProjectRoot C:\path\to\project

# One personal Claude Code skill
.\scripts\install-skills.ps1 -Target claude-personal -Skills schematic-humanizer

# All skills in a project's .claude/skills
.\scripts\install-skills.ps1 -Target claude-project -All -ProjectRoot C:\path\to\project
```

macOS/Linux examples:

```bash
./scripts/install-skills.sh codex-personal schematic-humanizer
./scripts/install-skills.sh codex-project --project /path/to/project --all
./scripts/install-skills.sh claude-personal schematic-humanizer
./scripts/install-skills.sh claude-project --project /path/to/project --all
```

Claude Code discovers personal skills at `~/.claude/skills/<name>/SKILL.md`
and project skills at `.claude/skills/<name>/SKILL.md`. Invoke a skill with
`/skill-name`; for example `/schematic-humanizer`. See the official
[Claude Code skill/slash-command documentation](https://code.claude.com/docs/en/slash-commands).
Codex uses `$skill-name`.

## Verify

Expected paths:

```text
$CODEX_HOME/skills/schematic-humanizer/SKILL.md
your-project/.agents/skills/schematic-humanizer/SKILL.md
~/.claude/skills/schematic-humanizer/SKILL.md
your-project/.claude/skills/schematic-humanizer/SKILL.md
```

Test one leaf skill:

```text
Use $schematic-humanizer to inspect this project's schematic sources and
describe the safe readability-improvement plan. Do not edit anything yet.
```

Test the complete suite:

```text
Use $manage-pcba-program to inventory this electronics project, initialize its
program state, identify missing specialist evidence, and stop before edits.
```

Correct behavior identifies source of truth, evidence level, available tools,
and missing gates. It does not claim circuit approval or perform an order.

## Update or uninstall

Install a fresh tagged clone and replace only the selected skill directory.
Review release notes before updating a project in manufacturing.

Uninstall by removing only the installed skill directory. This does not revert
design files previously changed by an agent; use version control or backups.

For troubleshooting, read [SUPPORT.md](../SUPPORT.md).
