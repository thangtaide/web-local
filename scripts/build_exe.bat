@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
where py >nul 2>nul
if errorlevel 1 (
  set "PYTHON=python"
) else (
  set "PYTHON=py -3"
)
%PYTHON% -c "import sys, tkinter; assert sys.version_info >= (3,10); import PyInstaller" >nul 2>nul
if errorlevel 1 (
  echo Cần Python 3.10+ có Tkinter và PyInstaller.
  echo Cài dependency build: %PYTHON% -m pip install pyinstaller
  exit /b 1
)
%PYTHON% -m PyInstaller --noconfirm --clean --distpath "%ROOT%\dist" --workpath "%ROOT%\build" "%ROOT%\packaging\MangaReader.spec"
if errorlevel 1 (
  echo Build thất bại. Xem lỗi phía trên.
  exit /b 1
)
copy /y "%ROOT%\scripts\install_shortcut.ps1" "%ROOT%\dist\MangaReader\install_shortcut.ps1" >nul
if errorlevel 1 exit /b 1
copy /y "%ROOT%\scripts\uninstall_shortcut.ps1" "%ROOT%\dist\MangaReader\uninstall_shortcut.ps1" >nul
if errorlevel 1 exit /b 1
copy /y "%ROOT%\scripts\shortcut_native.ps1" "%ROOT%\dist\MangaReader\shortcut_native.ps1" >nul
if errorlevel 1 exit /b 1
copy /y "%ROOT%\README.md" "%ROOT%\dist\MangaReader\README.md" >nul
if errorlevel 1 exit /b 1
if not exist "%ROOT%\dist\MangaReader\docs" mkdir "%ROOT%\dist\MangaReader\docs"
if errorlevel 1 exit /b 1
for %%F in (PROJECT_CONTEXT.md AI_HANDOFF.md REQUIREMENTS.md VALIDATION.md) do (
  copy /y "%ROOT%\docs\%%F" "%ROOT%\dist\MangaReader\docs\%%F" >nul
  if errorlevel 1 exit /b 1
)
echo Đã build: %ROOT%\dist\MangaReader\MangaReader.exe
echo Giữ nguyên toàn bộ thư mục MangaReader khi sao chép. Build không cài shortcut.
exit /b 0
