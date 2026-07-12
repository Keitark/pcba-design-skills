# インストール

[English](installation.md) · [README に戻る](../README.ja.md)

必要な 1 スキルだけ、または 8 スキル全部を導入できます。最終パスが必ず
`<skill-name>/SKILL.md` になるようにしてください。リポジトリ全体を 1 個の
スキルとして導入しないでください。

## 必要なもの

- ローカルスキル対応 Codex、またはスキル対応 Claude Code
- クローン方式では Git
- Codex システムインストーラー／検証スクリプトでは Python
- 実作業に必要な EDA／ビューアー。スキル導入だけでは KiCad 等は入りません

製造作業では `v1.0.0` に固定してください。`main` は未リリース版の評価用です。

## Codex: GitHub から 1 スキルを導入

Codex へ次のように依頼するのが簡単です。

```text
$skill-installer を使って、Keitark/pcba-design-skills の
.agents/skills/schematic-humanizer を v1.0.0 に固定して
schematic-humanizer としてインストールしてください。
```

同等の PowerShell コマンド:

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

既存の導入先がある場合、インストーラーは停止します。更新時は古いディレクトリを
明示的に退避または削除し、複数バージョンを混ぜないでください。

## Codex: 8 スキルを個人用に一括導入

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

導入後は新しい Codex タスクを開いてください。次のターンから利用できます。

## クローン方式: Codex / Claude Code

```powershell
git clone --branch v1.0.0 --depth 1 https://github.com/Keitark/pcba-design-skills.git
Set-Location pcba-design-skills
```

PowerShell:

```powershell
# 個人用 Codex に 1 スキル
.\scripts\install-skills.ps1 -Target codex-personal -Skills schematic-humanizer

# 指定プロジェクトの .agents/skills に全部
.\scripts\install-skills.ps1 -Target codex-project -All -ProjectRoot C:\path\to\project

# 個人用 Claude Code に 1 スキル
.\scripts\install-skills.ps1 -Target claude-personal -Skills schematic-humanizer

# 指定プロジェクトの .claude/skills に全部
.\scripts\install-skills.ps1 -Target claude-project -All -ProjectRoot C:\path\to\project
```

macOS/Linux:

```bash
./scripts/install-skills.sh codex-personal schematic-humanizer
./scripts/install-skills.sh codex-project --project /path/to/project --all
./scripts/install-skills.sh claude-personal schematic-humanizer
./scripts/install-skills.sh claude-project --project /path/to/project --all
```

Claude Code の個人用は `~/.claude/skills/<name>/SKILL.md`、プロジェクト用は
`.claude/skills/<name>/SKILL.md` です。`/schematic-humanizer` のように実行します。
公式の [Claude Code skill / slash command ドキュメント](https://code.claude.com/docs/en/slash-commands)
も参照してください。Codex では `$schematic-humanizer` を使います。

## 動作確認

```text
$schematic-humanizer を使って、このプロジェクトの回路図ソースを確認し、
安全な可読性改善計画を説明してください。まだ編集しないでください。
```

全部を確認する場合:

```text
$manage-pcba-program を使って、電子回路プロジェクトの入力を調査し、
program-state を初期化し、不足している専門証拠を示してください。
編集前に停止してください。
```

正しい動作では、正本、証拠レベル、利用可能なツール、不足ゲートを特定し、
勝手に回路合格や発注を行いません。

## 更新・削除

新しいタグをクローンし、選択したスキルディレクトリだけを置き換えます。製造中の
プロジェクトではリリースノートを確認してください。

削除時は導入したスキルディレクトリだけを削除します。過去に変更された設計ファイルは
戻らないため、Git またはバックアップを使ってください。

問題がある場合は [SUPPORT.ja.md](../SUPPORT.ja.md) を参照してください。
