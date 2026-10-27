const { app, BrowserWindow, ipcMain, dialog, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const os = require("os");

const PUBLISHER = "MayleSoft";

let win = null;
let installing = false;
let installAborted = false;
let APP_EXE = "MayleSoft.cmd";
let APP_DISPLAY_NAME = "MayleSoft";

function payloadRoot() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "payload");
  }
  return path.join(__dirname, "payload");
}

function resolveAppIdentity() {
  const root = payloadRoot();
  // Never treat Inno/NSIS setup as the app payload.
  const setup = path.join(root, "NGOFundraising-Setup-1.0.0.exe");
  if (fs.existsSync(setup)) {
    try {
      fs.unlinkSync(setup);
    } catch (_) {
      /* ignore */
    }
  }

  if (fs.existsSync(path.join(root, "NGOFundraising.exe"))) {
    APP_EXE = "NGOFundraising.exe";
    APP_DISPLAY_NAME = "NGO Fundraising";
  } else if (fs.existsSync(path.join(root, "MayleSoft.cmd"))) {
    APP_EXE = "MayleSoft.cmd";
    APP_DISPLAY_NAME = "MayleSoft";
  } else if (fs.existsSync(path.join(root, "Welcome.html"))) {
    APP_EXE = "Welcome.html";
    APP_DISPLAY_NAME = "MayleSoft";
  } else {
    APP_EXE = "NGOFundraising.exe";
    APP_DISPLAY_NAME = "NGO Fundraising";
  }
}

function defaultInstallDir() {
  return path.join(os.homedir(), "AppData", "Local", PUBLISHER, APP_DISPLAY_NAME);
}

function sendProgress(data) {
  if (win && !win.isDestroyed()) {
    win.webContents.send("install-progress", data);
  }
}

function walkFiles(dir, base = dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const name of fs.readdirSync(dir)) {
    // Skip leftover setup wrappers if present.
    if (/setup.*\.exe$/i.test(name)) continue;
    const full = path.join(dir, name);
    const st = fs.statSync(full);
    if (st.isDirectory()) walkFiles(full, base, out);
    else out.push({ abs: full, rel: path.relative(base, full), size: st.size });
  }
  return out;
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function looksLikeInstall(dir) {
  if (!dir || !fs.existsSync(dir)) return false;
  const markers = [
    "NGOFundraising.exe",
    "MayleSoft.cmd",
    "Welcome.html",
    "unins000.exe",
    "Uninstall-MayleSoft.ps1",
  ];
  return markers.some((name) => fs.existsSync(path.join(dir, name)));
}

function knownInstallDirs() {
  resolveAppIdentity();
  const local = path.join(os.homedir(), "AppData", "Local", PUBLISHER);
  return [
    defaultInstallDir(),
    path.join(local, "NGO Fundraising"),
    path.join(local, "MayleSoft"),
  ].filter((v, i, arr) => v && arr.indexOf(v) === i);
}

function removeFileQuiet(filePath) {
  try {
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
  } catch (_) {
    /* ignore locked/missing */
  }
}

function removeDirQuiet(dir) {
  try {
    if (fs.existsSync(dir)) fs.rmSync(dir, { recursive: true, force: true });
  } catch (_) {
    /* ignore */
  }
}

function removeShortcuts() {
  const names = ["NGO Fundraising", "MayleSoft"];
  for (const name of names) {
    removeFileQuiet(path.join(os.homedir(), "Desktop", `${name}.lnk`));
    removeFileQuiet(
      path.join(
        os.homedir(),
        "AppData",
        "Roaming",
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        PUBLISHER,
        `${name}.lnk`
      )
    );
  }
}

function killRunningApp() {
  return new Promise((resolve) => {
    const child = spawn(
      "taskkill",
      ["/IM", "NGOFundraising.exe", "/F", "/T"],
      { windowsHide: true }
    );
    child.on("close", () => resolve());
    child.on("error", () => resolve());
  });
}

function runInnoUninstaller(installDir) {
  const unins = path.join(installDir, "unins000.exe");
  if (!fs.existsSync(unins)) return Promise.resolve();
  return new Promise((resolve) => {
    const child = spawn(unins, ["/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES"], {
      windowsHide: true,
      cwd: installDir,
    });
    const timer = setTimeout(() => {
      try {
        child.kill();
      } catch (_) {
        /* ignore */
      }
      resolve();
    }, 45000);
    child.on("close", () => {
      clearTimeout(timer);
      resolve();
    });
    child.on("error", () => {
      clearTimeout(timer);
      resolve();
    });
  });
}

async function uninstallExisting(installDir) {
  const targets = new Set();
  if (looksLikeInstall(installDir)) targets.add(path.resolve(installDir));
  for (const dir of knownInstallDirs()) {
    if (looksLikeInstall(dir)) targets.add(path.resolve(dir));
  }
  if (!targets.size) return { removed: [] };

  sendProgress({
    percent: 3,
    message: "Closing running NGO Fundraising…",
    file: "",
    copiedFiles: 0,
    totalFiles: 0,
  });
  await killRunningApp();
  await new Promise((r) => setTimeout(r, 400));

  const removed = [];
  for (const dir of targets) {
    if (installAborted) throw new Error("Installation cancelled.");
    sendProgress({
      percent: 6,
      message: "Uninstalling previous version…",
      file: dir,
      copiedFiles: 0,
      totalFiles: 0,
    });
    await runInnoUninstaller(dir);
    removeShortcuts();
    removeDirQuiet(dir);
    removed.push(dir);
  }
  removeShortcuts();
  return { removed };
}

function createWindowsShortcut({ shortcutPath, target, workingDir, icon, description }) {
  const psPath = path.join(
    os.tmpdir(),
    `maylesoft-shortcut-${Date.now()}-${Math.random().toString(16).slice(2)}.ps1`
  );
  const lines = [
    "$ws = New-Object -ComObject WScript.Shell",
    `$s = $ws.CreateShortcut(${JSON.stringify(shortcutPath)})`,
    `$s.TargetPath = ${JSON.stringify(target)}`,
    `$s.WorkingDirectory = ${JSON.stringify(workingDir)}`,
    `$s.Description = ${JSON.stringify(description || APP_DISPLAY_NAME)}`,
  ];
  if (icon && fs.existsSync(icon) && /\.(ico|exe)$/i.test(icon)) {
    lines.push(`$s.IconLocation = ${JSON.stringify(icon)}`);
  }
  lines.push("$s.Save()");
  fs.writeFileSync(psPath, lines.join("\r\n"), "utf8");

  return new Promise((resolve, reject) => {
    const child = spawn(
      "powershell.exe",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", psPath],
      { windowsHide: true }
    );
    let err = "";
    child.stderr.on("data", (d) => {
      err += d.toString();
    });
    child.on("close", (code) => {
      try {
        fs.unlinkSync(psPath);
      } catch (_) {
        /* ignore */
      }
      if (code === 0) resolve();
      else reject(new Error(err || `Shortcut creation failed (${code})`));
    });
  });
}

function shortcutTarget(installDir) {
  const cmd = path.join(installDir, "MayleSoft.cmd");
  const exe = path.join(installDir, "NGOFundraising.exe");
  const welcome = path.join(installDir, "Welcome.html");
  if (fs.existsSync(exe)) return exe;
  if (fs.existsSync(cmd)) return cmd;
  return welcome;
}

async function installApp({ installDir, desktopShortcut, startMenuShortcut }) {
  installAborted = false;
  resolveAppIdentity();
  const source = payloadRoot();
  const exeSource = path.join(source, APP_EXE);
  if (!fs.existsSync(exeSource)) {
    throw new Error(
      `Application payload missing (${APP_EXE}). For welcome test, keep Welcome.html + MayleSoft.cmd in payload\\.`
    );
  }

  const files = walkFiles(source);
  if (!files.length) throw new Error("Payload folder is empty.");
  const totalBytes = files.reduce((n, f) => n + f.size, 0) || 1;
  let copiedBytes = 0;
  let copiedFiles = 0;

  sendProgress({
    percent: 1,
    message: "Checking for previous installation…",
    file: "",
    copiedFiles: 0,
    totalFiles: files.length,
  });
  const prior = await uninstallExisting(installDir);
  if (prior.removed.length) {
    sendProgress({
      percent: 10,
      message: `Removed previous install (${prior.removed.length})`,
      file: prior.removed[0],
      copiedFiles: 0,
      totalFiles: files.length,
    });
  }

  ensureDir(installDir);
  sendProgress({
    percent: prior.removed.length ? 12 : 0,
    message: "Preparing files…",
    file: "",
    copiedFiles: 0,
    totalFiles: files.length,
  });

  for (const file of files) {
    if (installAborted) throw new Error("Installation cancelled.");
    const dest = path.join(installDir, file.rel);
    ensureDir(path.dirname(dest));
    fs.copyFileSync(file.abs, dest);
    copiedBytes += file.size;
    copiedFiles += 1;
    // Leave headroom after uninstall phase (12% → 99%).
    const copyPct = Math.round((copiedBytes / totalBytes) * 87);
    const percent = Math.min(99, 12 + copyPct);
    sendProgress({
      percent,
      message: `Copying ${copiedFiles} / ${files.length} files`,
      file: file.rel.replace(/\\/g, "/"),
      copiedFiles,
      totalFiles: files.length,
    });
    await new Promise((r) => setImmediate(r));
  }

  const target = shortcutTarget(installDir);

  if (desktopShortcut) {
    sendProgress({
      percent: 99,
      message: "Creating desktop shortcut…",
      file: "",
      copiedFiles,
      totalFiles: files.length,
    });
    await createWindowsShortcut({
      shortcutPath: path.join(os.homedir(), "Desktop", `${APP_DISPLAY_NAME}.lnk`),
      target,
      workingDir: installDir,
    });
  }

  if (startMenuShortcut) {
    sendProgress({
      percent: 99,
      message: "Creating Start Menu shortcut…",
      file: "",
      copiedFiles,
      totalFiles: files.length,
    });
    const programs = path.join(
      os.homedir(),
      "AppData",
      "Roaming",
      "Microsoft",
      "Windows",
      "Start Menu",
      "Programs",
      PUBLISHER
    );
    ensureDir(programs);
    await createWindowsShortcut({
      shortcutPath: path.join(programs, `${APP_DISPLAY_NAME}.lnk`),
      target,
      workingDir: installDir,
    });
  }

  sendProgress({
    percent: 100,
    message: "Installation complete.",
    file: "",
    copiedFiles: files.length,
    totalFiles: files.length,
  });

  return { installDir, exePath: target };
}

app.whenReady().then(() => {
  resolveAppIdentity();

  win = new BrowserWindow({
    width: 960,
    height: 640,
    minWidth: 800,
    minHeight: 550,
    frame: false,
    backgroundColor: "#070a16",
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });
  win.loadFile(path.join(__dirname, "index.html"));
  win.once("ready-to-show", () => win.show());

  ipcMain.handle("window-action", (_e, action) => {
    if (action === "minimize") win.minimize();
    if (action === "close" && !installing) win.close();
    if (action === "close" && installing) {
      installAborted = true;
      win.close();
    }
  });

  ipcMain.handle("get-defaults", () => {
    resolveAppIdentity();
    const defaultDir = defaultInstallDir();
    const existing = knownInstallDirs().filter((d) => looksLikeInstall(d));
    return {
      defaultDir,
      payloadReady: fs.existsSync(path.join(payloadRoot(), APP_EXE)),
      version: app.getVersion(),
      appName: APP_DISPLAY_NAME,
      testMode: APP_EXE !== "NGOFundraising.exe",
      alreadyInstalled: existing.length > 0,
      existingDirs: existing,
    };
  });

  ipcMain.handle("check-install", (_e, dir) => {
    resolveAppIdentity();
    const target = (dir || "").trim() || defaultInstallDir();
    const existing = [
      ...(looksLikeInstall(target) ? [path.resolve(target)] : []),
      ...knownInstallDirs().filter((d) => looksLikeInstall(d)),
    ].filter((v, i, arr) => arr.indexOf(v) === i);
    return {
      alreadyInstalled: existing.length > 0,
      existingDirs: existing,
      target,
    };
  });

  ipcMain.handle("choose-directory", async (_e, current) => {
    const result = await dialog.showOpenDialog(win, {
      title: "Choose installation folder",
      defaultPath: current || defaultInstallDir(),
      properties: ["openDirectory", "createDirectory"],
    });
    if (result.canceled || !result.filePaths[0]) return null;
    return result.filePaths[0];
  });

  ipcMain.handle("install", async (_e, options) => {
    if (installing) throw new Error("Installation is already running.");
    installing = true;
    try {
      return await installApp(options || {});
    } finally {
      installing = false;
    }
  });

  ipcMain.handle("launch", async (_e, exePath) => {
    if (!exePath || !fs.existsSync(exePath)) {
      throw new Error("Installed application not found.");
    }
    await shell.openPath(exePath);
    return true;
  });

  ipcMain.handle("open-folder", async (_e, dir) => {
    if (dir && fs.existsSync(dir)) await shell.openPath(dir);
    return true;
  });
});

app.on("window-all-closed", () => app.quit());
