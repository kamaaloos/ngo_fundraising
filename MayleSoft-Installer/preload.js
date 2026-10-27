const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("mayle", {
  action: (a) => ipcRenderer.invoke("window-action", a),
  getDefaults: () => ipcRenderer.invoke("get-defaults"),
  checkInstall: (dir) => ipcRenderer.invoke("check-install", dir),
  chooseDirectory: (current) => ipcRenderer.invoke("choose-directory", current),
  install: (options) => ipcRenderer.invoke("install", options),
  launch: (exePath) => ipcRenderer.invoke("launch", exePath),
  openFolder: (dir) => ipcRenderer.invoke("open-folder", dir),
  onProgress: (cb) => {
    const handler = (_event, data) => cb(data);
    ipcRenderer.on("install-progress", handler);
    return () => ipcRenderer.removeListener("install-progress", handler);
  },
});
