const $ = (id) => document.getElementById(id);

const SLOGANS = [
  "Sadaqah with clarity. Every gift accounted.",
  "Trust earned in every pledge and payment.",
  "From donor to impact, clearly recorded.",
];

const CIRCUMFERENCE = 2 * Math.PI * 74;

const state = {
  sloganIndex: 0,
  installDir: "",
  exePath: "",
};

function show(id, step) {
  document.querySelectorAll(".screen").forEach((x) => x.classList.toggle("active", x.id === id));
  [1, 2, 3].forEach((n) => $(`step${n}`).classList.toggle("active", n === step));
}

function setProgress(percent, message, file) {
  const pct = Math.max(0, Math.min(100, Number(percent) || 0));
  $("percentage").textContent = `${pct}%`;
  $("bar").style.width = `${pct}%`;
  const circle = $("progress-circle");
  circle.style.strokeDasharray = String(CIRCUMFERENCE);
  circle.style.strokeDashoffset = String(CIRCUMFERENCE * (1 - pct / 100));
  if (message) $("status").textContent = file ? `${message} — ${file}` : message;
}

function rotate() {
  state.sloganIndex = (state.sloganIndex + 1) % SLOGANS.length;
  const text = SLOGANS[state.sloganIndex];
  const el = $("slogan");
  const install = $("install-slogan");
  el.classList.add("out");
  install.classList.add("out");
  setTimeout(() => {
    el.textContent = text;
    el.classList.remove("out");
    document.querySelectorAll(".slogan-dots b").forEach((d, i) => {
      d.classList.toggle("on", i === state.sloganIndex);
    });
    setTimeout(() => {
      install.textContent = text;
      install.classList.remove("out");
    }, 260);
  }, 260);
}

async function init() {
  for (let i = 0; i < 36; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    p.style.left = `${Math.random() * 100}%`;
    p.style.top = `${Math.random() * 100}%`;
    p.style.animationDelay = `${Math.random() * 4}s`;
    $("particles").appendChild(p);
  }

  const defaults = await window.mayle.getDefaults();
  state.installDir = defaults.defaultDir;
  $("install-path").value = defaults.defaultDir;
  if (!defaults.payloadReady) {
    $("error-message").textContent =
      "Application payload is missing. Build dist\\NGOFundraising, then run npm run sync-payload.";
    show("failure", 2);
  }

  async function refreshReinstallNote() {
    const info = await window.mayle.checkInstall($("install-path").value);
    const note = $("reinstall-note");
    const text = $("reinstall-text");
    if (info.alreadyInstalled) {
      note.hidden = false;
      text.textContent =
        `Existing install found (${info.existingDirs.length}). It will be uninstalled first, ` +
        "then this version will be installed cleanly.";
      $("begin").textContent = "Uninstall & reinstall →";
    } else {
      note.hidden = true;
      $("begin").innerHTML = 'Install now <span>→</span>';
    }
  }

  await refreshReinstallNote();

  setInterval(rotate, 3600);
  setProgress(0, "Preparing…", "");

  $("minimize").onclick = () => window.mayle.action("minimize");
  $("close").onclick = () => window.mayle.action("close");
  $("next").onclick = async () => {
    show("configure", 2);
    await refreshReinstallNote();
  };
  $("back").onclick = () => show("welcome", 1);
  $("retry").onclick = () => show("configure", 2);
  $("finish").onclick = () => window.mayle.action("close");

  $("install-path").addEventListener("change", () => {
    refreshReinstallNote();
  });

  $("browse").onclick = async () => {
    const chosen = await window.mayle.chooseDirectory($("install-path").value);
    if (chosen) {
      state.installDir = chosen;
      $("install-path").value = chosen;
      await refreshReinstallNote();
    }
  };

  window.mayle.onProgress((data) => {
    setProgress(data.percent, data.message, data.file);
  });

  $("begin").onclick = async () => {
    const installDir = ($("install-path").value || "").trim();
    if (!installDir) return;

    const info = await window.mayle.checkInstall(installDir);
    if (info.alreadyInstalled) {
      const ok = window.confirm(
        "NGO Fundraising is already installed.\n\n" +
          "The existing install will be removed, then this version will be installed.\n\n" +
          "Continue?"
      );
      if (!ok) return;
    }

    show("installing", 2);
    setProgress(0, info.alreadyInstalled ? "Uninstalling previous version…" : "Preparing files…", "");
    try {
      const result = await window.mayle.install({
        installDir,
        desktopShortcut: $("opt-desktop").checked,
        startMenuShortcut: $("opt-startmenu").checked,
      });
      state.installDir = result.installDir;
      state.exePath = result.exePath;
      $("done-path").textContent = `✓  Installed to ${result.installDir}`;
      show("complete", 3);
    } catch (err) {
      $("error-message").textContent = err.message || String(err);
      show("failure", 2);
    }
  };

  $("launch").onclick = async () => {
    try {
      await window.mayle.launch(state.exePath);
      window.mayle.action("close");
    } catch (err) {
      $("error-message").textContent = err.message || String(err);
      show("failure", 2);
    }
  };

  $("open-folder").onclick = () => window.mayle.openFolder(state.installDir);
}

init().catch((err) => {
  $("error-message").textContent = err.message || String(err);
  show("failure", 2);
});
