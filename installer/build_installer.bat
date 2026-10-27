@echo off
setlocal
cd /d "%~dp0"

if not exist "..\dist\NGOFundraising\NGOFundraising.exe" (
  echo Desktop app payload missing. Building it first...
  call ..\packaging\build_windows.bat
  if errorlevel 1 exit /b 1
)

if not exist "node_modules\electron\package.json" (
  echo Installing npm dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)

echo Building MayleSoft Installer...
call npm run dist
if errorlevel 1 exit /b 1

if exist "dist\MayleSoft-Installer-1.1.0.exe" (
  if not exist "..\web\downloads" mkdir "..\web\downloads"
  copy /Y "dist\MayleSoft-Installer-1.1.0.exe" "..\web\downloads\MayleSoft-Installer-1.1.0.exe" >nul
)

echo.
echo Done: dist\MayleSoft-Installer-1.1.0.exe
echo This installer copies the app inside its own UI (does not open Inno Setup).
endlocal
