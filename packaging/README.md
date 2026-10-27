# Windows packaging

Builds a folder-based PyInstaller distribution for customer PCs.

## Prerequisites

- Windows 10/11
- Python 3.10+ with project `.venv` created and `requirements.txt` installed

## Build

From the repo root:

```bat
packaging\build_windows.bat
```

Output:

```
dist\NGOFundraising\NGOFundraising.exe
```

Zip the entire `dist\NGOFundraising` folder for delivery. Customers run the `.exe`;
they do not need Python installed.

## Notes

- Demo seed is forced off in the frozen build (`packaging/pyi_rth_ngo.py`).
- App data still lives under `%LOCALAPPDATA%\NGOFundraisingManager\`.
- Icon: `app/assets/app.ico`.
- Re-run the bat after dependency or asset changes.
