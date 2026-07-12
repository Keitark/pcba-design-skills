param(
    [string]$Output = (Join-Path $PSScriptRoot "..\assets\banner.png")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$source = Join-Path $root "assets\case-studies\nescart"
$width = 1600
$height = 600
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

function Brush([string]$color) {
    return New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($color))
}

function Pen([string]$color, [float]$size = 1) {
    return New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml($color), $size)
}

function Font([string]$family, [float]$size, [System.Drawing.FontStyle]$style = [System.Drawing.FontStyle]::Regular) {
    return New-Object System.Drawing.Font($family, $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
}

function Draw-CoverImage([System.Drawing.Image]$image, [System.Drawing.Rectangle]$destination, [System.Drawing.Rectangle]$sourceRect) {
    $sourceRatio = $sourceRect.Width / $sourceRect.Height
    $destRatio = $destination.Width / $destination.Height
    if ($sourceRatio -gt $destRatio) {
        $newWidth = [int]($sourceRect.Height * $destRatio)
        $sourceRect.X += [int](($sourceRect.Width - $newWidth) / 2)
        $sourceRect.Width = $newWidth
    } else {
        $newHeight = [int]($sourceRect.Width / $destRatio)
        $sourceRect.Y += [int](($sourceRect.Height - $newHeight) / 2)
        $sourceRect.Height = $newHeight
    }
    $graphics.DrawImage($image, $destination, $sourceRect, [System.Drawing.GraphicsUnit]::Pixel)
}

function Draw-ContainImage([System.Drawing.Image]$image, [System.Drawing.Rectangle]$destination) {
    $scale = [Math]::Min($destination.Width / $image.Width, $destination.Height / $image.Height)
    $drawWidth = [int]($image.Width * $scale)
    $drawHeight = [int]($image.Height * $scale)
    $x = $destination.X + [int](($destination.Width - $drawWidth) / 2)
    $y = $destination.Y + [int](($destination.Height - $drawHeight) / 2)
    $graphics.DrawImage($image, $x, $y, $drawWidth, $drawHeight)
}

$background = Brush "#071722"
$gridPen = Pen "#123344" 1
$graphics.FillRectangle($background, 0, 0, $width, $height)
for ($x = 0; $x -lt $width; $x += 50) { $graphics.DrawLine($gridPen, $x, 0, $x, $height) }
for ($y = 0; $y -lt $height; $y += 50) { $graphics.DrawLine($gridPen, 0, $y, $width, $y) }

$titleFont = Font "Segoe UI" 48 ([System.Drawing.FontStyle]::Bold)
$subFont = Font "Yu Gothic UI" 22
$smallFont = Font "Segoe UI" 16 ([System.Drawing.FontStyle]::Bold)
$footerFont = Font "Segoe UI" 16
$white = Brush "#F4F7F8"
$cyan = Brush "#39C6F4"
$muted = Brush "#A9BDC8"
$orange = Brush "#FFB238"

$graphics.DrawString("PCBA Design Skills", $titleFont, $white, 48, 28)
$graphics.DrawString("From circuit intent to a reviewed manufacturing order", $subFont, $cyan, 52, 88)
$graphics.DrawString("回路の意図から、検証済みの製造・実装発注レビューまで", $subFont, $muted, 52, 122)

$cards = @(
    @{ Label = "01  NETLIST-LIKE"; Path = "schematic-before.png"; Color = "#FFB238"; Crop = $null; Contain = $false },
    @{ Label = "02  HUMANIZED"; Path = "schematic-humanized.png"; Color = "#39C6F4"; Crop = $null; Contain = $false },
    @{ Label = "03  ARCH + LAYOUT"; Path = "operating-architecture.png"; Color = "#5EE3B5"; Crop = $null; Contain = $true },
    @{ Label = "04  PCB RENDER"; Path = "pcb-render.png"; Color = "#6EB5FF"; Crop = $null; Contain = $true },
    @{ Label = "05  PCBA REVIEW"; Path = "jlc-placement-source.png"; Color = "#B795FF"; Crop = [System.Drawing.Rectangle]::new(0, 430, 860, 610); Contain = $false }
)

$cardY = 182
$cardWidth = 286
$cardHeight = 300
$gap = 18
$startX = 44
$cardBackground = Brush "#0C202D"
$imageBackground = Brush "#EEF0EC"

for ($index = 0; $index -lt $cards.Count; $index++) {
    $card = $cards[$index]
    $x = $startX + $index * ($cardWidth + $gap)
    $outline = Pen $card.Color 2
    $graphics.FillRectangle($cardBackground, $x, $cardY, $cardWidth, $cardHeight)
    $graphics.DrawRectangle($outline, $x, $cardY, $cardWidth, $cardHeight)
    $graphics.FillRectangle($imageBackground, $x + 10, $cardY + 50, $cardWidth - 20, $cardHeight - 62)
    $graphics.DrawString($card.Label, $smallFont, (Brush $card.Color), $x + 14, $cardY + 14)
    $image = [System.Drawing.Image]::FromFile((Join-Path $source $card.Path))
    try {
        $sourceRect = if ($null -eq $card.Crop) {
            [System.Drawing.Rectangle]::new(0, 0, $image.Width, $image.Height)
        } else {
            $card.Crop
        }
        $destination = [System.Drawing.Rectangle]::new($x + 10, $cardY + 50, $cardWidth - 20, $cardHeight - 62)
        if ($card.Contain) {
            Draw-ContainImage $image $destination
        } else {
            Draw-CoverImage $image $destination $sourceRect
        }
    } finally {
        $image.Dispose()
        $outline.Dispose()
    }
    if ($index -lt $cards.Count - 1) {
        $arrowPen = Pen "#FFB238" 3
        $arrowPen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
        $graphics.DrawLine($arrowPen, $x + $cardWidth + 3, $cardY + 150, $x + $cardWidth + $gap - 5, $cardY + 150)
        $arrowPen.Dispose()
    }
}

$footerPen = Pen "#244B5C" 1
$graphics.DrawLine($footerPen, 46, 514, 1554, 514)
$graphics.DrawString("8 MODULAR SKILLS", $smallFont, $orange, 50, 535)
$graphics.DrawString("Codex + Claude Code", $footerFont, $white, 315, 535)
$graphics.DrawString("Multi-EDA adapters", $footerFont, $white, 610, 535)
$graphics.DrawString("Evidence-gated", $footerFont, $white, 880, 535)
$graphics.DrawString("English / 日本語", $footerFont, $white, 1110, 535)
$graphics.DrawString("MIT code · CC BY-SA case study", $footerFont, $muted, 1320, 535)

$outputPath = if ([System.IO.Path]::IsPathRooted($Output)) {
    [System.IO.Path]::GetFullPath($Output)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $root $Output))
}
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($outputPath)) | Out-Null
$bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)

foreach ($item in @($background, $gridPen, $titleFont, $subFont, $smallFont, $footerFont, $white, $cyan, $muted, $orange, $cardBackground, $imageBackground, $footerPen)) {
    $item.Dispose()
}
$graphics.Dispose()
$bitmap.Dispose()
Write-Output $outputPath
