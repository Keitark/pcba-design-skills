# インストール

[English](installation.md) · [README に戻る](../README.ja.md)

Schematic Humanizer は Codex スキルとして配布されます。リポジトリのルートではなく、スキルパッケージを配置してください。最終パスが `schematic-humanizer/SKILL.md` になれば正しい状態です。

## 必要なもの

- ローカルスキルに対応した Codex
- リポジトリをクローンするための Git
- 編集可能な出力が必要な場合は、入力形式に対応する EDA アプリまたはレンダラー
- 回路設計のバックアップ、または破棄可能な作業ブランチ

KiCad はテキスト形式のソースと CLI エクスポートにより強い自動検証ができるため、第一級対応です。他のツールは検証能力の異なるアダプターを使います。[アダプターガイド](adapters.ja.md)を確認してください。

## 方法 A: プロジェクト単位でインストール

チームリポジトリで共通利用する場合や、プロジェクトごとにバージョンを固定したい場合に選びます。

### PowerShell

対象プロジェクトのルートで実行します。

```powershell
$source = Join-Path $env:TEMP "schematic-humanizer"
git clone https://github.com/keitark/schematic-humanizer.git $source
New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
Copy-Item -Recurse -Force "$source\.agents\skills\schematic-humanizer" ".agents\skills\"
```

### macOS / Linux

対象プロジェクトのルートで実行します。

```bash
source_dir="$(mktemp -d)/schematic-humanizer"
git clone https://github.com/keitark/schematic-humanizer.git "$source_dir"
mkdir -p .agents/skills
cp -R "$source_dir/.agents/skills/schematic-humanizer" .agents/skills/
```

配置結果:

```text
your-project/.agents/skills/schematic-humanizer/SKILL.md
```

チームで同じバージョンをリポジトリに保存したい場合のみ、スキル本体をコミットしてください。外部ファイルの同梱に関する組織ルールも確認してください。

## 方法 B: 個人用としてインストール

複数のプロジェクトで利用する場合に選びます。

### PowerShell

```powershell
$source = Join-Path $env:TEMP "schematic-humanizer"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
git clone https://github.com/keitark/schematic-humanizer.git $source
New-Item -ItemType Directory -Force (Join-Path $codexHome "skills") | Out-Null
Copy-Item -Recurse -Force "$source\.agents\skills\schematic-humanizer" (Join-Path $codexHome "skills")
```

### macOS / Linux

```bash
source_dir="$(mktemp -d)/schematic-humanizer"
codex_home="${CODEX_HOME:-$HOME/.codex}"
git clone https://github.com/keitark/schematic-humanizer.git "$source_dir"
mkdir -p "$codex_home/skills"
cp -R "$source_dir/.agents/skills/schematic-humanizer" "$codex_home/skills/"
```

配置結果:

```text
$CODEX_HOME/skills/schematic-humanizer/SKILL.md
```

`CODEX_HOME` が未設定の場合、上記の `$CODEX_HOME` は `~/.codex` を意味します。

## 有効化と確認

インストール後、新しい Codex タスクを開始して次のように依頼します。

```text
$schematic-humanizer を使って、このプロジェクトの回路図ソースを確認し、
安全に読みやすくする計画を説明してください。まだファイルは編集しないでください。
```

正しく動作すると、最初に入力形式、正本ルール、使用可能なレンダー／エクスポート手段、厳密な接続検証が可能かを確認します。電気的な承認を約束してはいけません。

## 更新

リポジトリの最新版を取得し、インストール済みの `schematic-humanizer` ディレクトリだけを置き換えます。その後、新しい Codex タスクを開始してください。

同じディレクトリへ異なるバージョンを混在させないでください。古い参照ファイルが残ると動作が不整合になる可能性があります。

## アンインストール

インストールした次のディレクトリだけを削除します。

- プロジェクト単位: `.agents/skills/schematic-humanizer`
- 個人用: `$CODEX_HOME/skills/schematic-humanizer`。未設定の場合は `~/.codex/skills/schematic-humanizer`

この操作では、Codex が過去に変更した回路図ファイルは元に戻りません。バージョン管理履歴またはバックアップを使って戻してください。

## トラブルシューティング

### Codex がスキルを認識しない

- `SKILL.md` が `schematic-humanizer` ディレクトリ直下にあるか確認します。
- `schematic-humanizer/schematic-humanizer/SKILL.md` のように二重になっていないか確認します。
- インストール後に新しいタスクを開始します。
- 個人用とプロジェクト用が両方ある場合、バージョン固定が必要ならプロジェクト用を優先します。

### 対象 EDA ツールを利用できない

可能であれば、ネイティブツールからネットリストと PDF/SVG を出力してください。編集可能なソースまたは信頼できるネットリストがない場合、スキルは目視ベースのワークフローを使う必要があり、接続維持を証明できません。

困ったときは [SUPPORT.ja.md](../SUPPORT.ja.md) を参照してください。
