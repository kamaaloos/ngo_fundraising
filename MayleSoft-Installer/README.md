# MayleSoft Installer (NGO Fundraising)

Electron installer that copies the **real** PyInstaller app (`NGOFundraising.exe`)
into the chosen folder. Install stays inside this window (no Inno Setup popup).

## Start (dev)

```bat
cd MayleSoft-Installer
npm start
```

This syncs `..\dist\NGOFundraising` → `payload\`, then opens the installer.

Requires a built app first:

```bat
packaging\build_windows.bat
```

This folder is the **canonical customer ship channel**. Legacy Inno Setup is not used.

## Build customer .exe

```bat
cd MayleSoft-Installer
npm run dist
```

Output: `dist\MayleSoft-Installer-1.1.0.exe`

## Welcome.html test only

```bat
npm run start:welcome-test
```

(Only if `payload\` still has `Welcome.html` / `MayleSoft.cmd` — normal `npm start` replaces payload with the real app.)
