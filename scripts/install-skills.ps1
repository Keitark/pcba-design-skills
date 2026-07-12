param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex-personal", "codex-project", "claude-personal", "claude-project")]
    [string]$Target,
    [string[]]$Skills,
    [switch]$All,
    [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = Join-Path $repoRoot ".agents\skills"
$available = @(Get-ChildItem -LiteralPath $sourceRoot -Directory | Sort-Object Name | Select-Object -ExpandProperty Name)

if ($All -and $Skills) { throw "Use either -All or -Skills, not both." }
if (-not $All -and -not $Skills) { throw "Provide -Skills <name> or -All." }
$selected = if ($All) { $available } else { @($Skills) }
$duplicates = @($selected | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
if ($duplicates) { throw "Duplicate skill arguments: $($duplicates -join ', ')" }
$unknown = @($selected | Where-Object { $_ -notin $available })
if ($unknown) { throw "Unknown skill(s): $($unknown -join ', '). Available: $($available -join ', ')" }

$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$destinationRoot = switch ($Target) {
    "codex-personal" { Join-Path $codexHome "skills" }
    "codex-project" { Join-Path $ProjectRoot ".agents\skills" }
    "claude-personal" { Join-Path $HOME ".claude\skills" }
    "claude-project" { Join-Path $ProjectRoot ".claude\skills" }
}
$plans = @($selected | ForEach-Object {
    [PSCustomObject]@{
        Name = $_
        Source = Join-Path $sourceRoot $_
        Destination = Join-Path $destinationRoot $_
    }
})
foreach ($plan in $plans) {
    if (-not (Test-Path -LiteralPath $plan.Source -PathType Container)) {
        throw "Source skill is missing: $($plan.Source)"
    }
    if (Test-Path -LiteralPath $plan.Destination) {
        throw "Destination already exists: $($plan.Destination). Remove or rename it explicitly before updating."
    }
}

New-Item -ItemType Directory -Force $destinationRoot | Out-Null
foreach ($plan in $plans) {
    Copy-Item -LiteralPath $plan.Source -Destination $plan.Destination -Recurse
    Write-Output "Installed $($plan.Name) -> $($plan.Destination)"
}
