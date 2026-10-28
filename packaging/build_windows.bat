@echo off
setlocal
cd /d "%~dp0.."

echo === NGO Fundraising Windows build (app payload) ===
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

echo Running PyInstaller...
python -m PyInstaller --noconfirm NGOFundraising.spec
if errorlevel 1 exit /b 1

echo.
echo Build OK: dist\NGOFundraising\NGOFundraising.exe
echo.
echo Customer installer channel: MayleSoft Electron installer
echo   cd MayleSoft-Installer
echo   npm install
echo   npm run dist
echo Or one-shot: installer\build_installer.bat  (same Electron packager)
echo.
echo Demo data is OFF in this build.
echo Legacy Inno Setup (packaging\NGOFundraising.iss) is not used for shipping.
endlocal
