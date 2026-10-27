# Windows packaging

Builds a PyInstaller app folder **and** a customer `Setup.exe` (Inno Setup).

## Prerequisites

- Windows 10/11
- Python 3.10+ with project `.venv` and `requirements.txt` installed
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (for the installer)

If Inno Setup is missing, the bat still produces the portable folder under `dist\NGOFundraising\`.

## Build

From the repo root:

```bat
packaging\build_windows.bat
```

Outputs:

```
dist\NGOFundraising\NGOFundraising.exe          ← portable folder
dist\NGOFundraising-Setup-1.0.0.exe             ← customer installer
```

Ship the **Setup.exe** to customers. They run it, optionally create a desktop shortcut, and launch from the Start Menu.

## What the installer does

- Installs under `%LOCALAPPDATA%\MayleSoft\NGO Fundraising\` (no admin UAC by default)
- Start Menu shortcut (+ optional desktop icon)
- Launch after install
- Uninstall via Windows Settings / Start Menu

App data (database, license, recovery) stays in:

```
%LOCALAPPDATA%\NGOFundraisingManager\
```

Uninstalling the app does **not** delete that data folder (on purpose).

## Notes

- Demo seed is forced off in the frozen build (`packaging/pyi_rth_ngo.py`).
- Icon: `app/assets/app.ico`.
- Bump `#define MyAppVersion` in `NGOFundraising.iss` when releasing.
- Re-run the bat after dependency or asset changes.
