param([string]$ExePath = '')
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $ExePath = Join-Path $PSScriptRoot 'MangaReader.exe'
    if (-not (Test-Path -LiteralPath $ExePath -PathType Leaf)) {
        $ExePath = Join-Path $PSScriptRoot '..\dist\MangaReader\MangaReader.exe'
    }
}
$resolvedExe = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
if ([IO.Path]::GetExtension($resolvedExe) -ne '.exe') { throw 'Cần chọn file MangaReader.exe.' }
$programs = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
New-Item -ItemType Directory -Path $programs -Force | Out-Null
$shortcutPath = Join-Path $programs 'Manga Reader.lnk'
. (Join-Path $PSScriptRoot 'shortcut_native.ps1')
[MangaShortcut]::Create($shortcutPath, $resolvedExe, (Split-Path -LiteralPath $resolvedExe))
Write-Output "Đã tạo shortcut: $shortcutPath"
Write-Output 'Nhấn Windows, gõ Manga Reader. Windows Search có thể cần thời gian cập nhật chỉ mục.'
