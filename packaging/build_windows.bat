@echo off
setlocal
cd /d "%~dp0.."

echo === NGO Fundraising Windows build ===
if not exist ".venv\Scripts\python.exe" (
  echo Create .venv first: py -3.10 -m venv .venv
  exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install -q -r requirements-build.txt
if errorlevel 1 exit /b 1

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist\NGOFundraising rmdir /s /q dist\NGOFundraising
if exist dist\NGOFundraising-Setup-*.exe del /q dist\NGOFundraising-Setup-*.exe

echo Running PyInstaller...
python -m PyInstaller --noconfirm NGOFundraising.spec
if errorlevel 1 exit /b 1

echo.
echo Build OK: dist\NGOFundraising\NGOFundraising.exe

rem ---- Inno Setup installer ----
set "ISCC="
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
  echo.
  echo WARNING: Inno Setup 6 not found — skipped Setup.exe.
  echo Install from https://jrsoftware.org/isdl.php then re-run this script.
  echo Portable folder is still ready: dist\NGOFundraising\
  echo Demo data is OFF in this build.
  endlocal
  exit /b 0
)

echo.
echo Compiling installer with Inno Setup...
"%ISCC%" "packaging\NGOFundraising.iss"
if errorlevel 1 exit /b 1

echo.
echo Installer OK.
echo Customer file: dist\NGOFundraising-Setup-1.0.0.exe
echo (Also available: dist\NGOFundraising\ folder)

if exist "dist\NGOFundraising-Setup-1.0.0.exe" (
  if not exist "web\downloads" mkdir "web\downloads"
  copy /Y "dist\NGOFundraising-Setup-1.0.0.exe" "web\downloads\NGOFundraising-Setup-1.0.0.exe" >nul
  echo Landing page download updated: web\downloads\
)

echo Demo data is OFF in this build.
endlocal
