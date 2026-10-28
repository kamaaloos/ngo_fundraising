# Windows packaging

Builds the **PyInstaller app folder** used as payload by the MayleSoft Electron installer.

Customer shipping channel: **MayleSoft-Installer** (Electron). Legacy Inno Setup
(`NGOFundraising.iss`) is kept in-repo for reference only and is **not** part of the
customer build path.

## Prerequisites

- Windows 10/11
- Python 3.10+ with project `.venv` and `requirements.txt` installed
- Node.js 18+ (to build the Electron installer)

## Build app payload

From the repo root:

```bat
packaging\build_windows.bat
```

Output:

```
dist\NGOFundraising\NGOFundraising.exe
```

## Build customer installer

```bat
cd MayleSoft-Installer
npm install
npm run dist
```

Or from repo root (builds payload if needed, then Electron installer):

```bat
installer\build_installer.bat
```

Ship: `MayleSoft-Installer\dist\MayleSoft-Installer-1.1.0.exe`  
(or `installer\dist\…` when using that folder).

The installer copies files inside its own UI (no separate Inno Setup popup).

App data (database, license, recovery) stays in:

```
%LOCALAPPDATA%\NGOFundraisingManager\
```

Uninstalling the app does **not** delete that data folder (on purpose).

## Notes

- Demo seed is forced off in the frozen build (`packaging/pyi_rth_ngo.py`).
- Icon: `app/assets/app.ico`.
- Re-run the bat after dependency or asset changes.
