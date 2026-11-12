$ErrorActionPreference = 'Stop'
$shortcutPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Manga Reader.lnk'
if (Test-Path -LiteralPath $shortcutPath -PathType Leaf) {
    Remove-Item -LiteralPath $shortcutPath
    Write-Output 'Đã gỡ shortcut Manga Reader. Dữ liệu và ứng dụng được giữ nguyên.'
} else {
    Write-Output 'Không có shortcut Manga Reader để gỡ.'
}
