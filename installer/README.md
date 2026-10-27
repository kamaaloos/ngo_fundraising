# MayleSoft Installer — Futuristic Windows Edition

Custom Electron installer for **NGO Fundraising**.

The install runs **inside this window** (directory picker, real file copy + progress,
shortcuts, launch). It does **not** open a separate Inno Setup / “Setup - NGO Fundraising”
wizard.

## Prerequisites

1. Node.js 18+
2. Built desktop app folder:

```bat
packaging\build_windows.bat
```

Must produce `dist\NGOFundraising\NGOFundraising.exe` (the app itself — **not** `*-Setup-*.exe`).

## Preview

```bat
cd installer
npm install
npm start
```

## Build customer exe

```bat
cd installer
npm run dist
```

or:

```bat
installer\build_installer.bat
```

Output:

```text
installer\dist\MayleSoft-Installer-1.1.0.exe
```

## Payload rule

`scripts\sync-payload.js` copies `..\dist\NGOFundraising\` → `payload\`.

Never put `NGOFundraising-Setup-*.exe` in `payload\` — that is what caused the second
setup window.
