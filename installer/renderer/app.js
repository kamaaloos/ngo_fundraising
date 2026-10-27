const SLOGANS = [
  {
    title: "Sadaqah with clarity.\nEvery gift accounted.",
    sub: "Islamic fundraising · Projects · Donors · Reports",
  },
  {
    title: "Trust earned in every\npledge and payment.",
    sub: "Collect · Track · Report — with full transparency",
  },
  {
    title: "From donor to impact,\nclearly recorded.",
    sub: "MayleSoft NGO-fund · Built for community care",
  },
];

const state = {
  installDir: "",
  exePath: "",
  sloganIndex: 0,
  sloganTimer: null,
  offProgress: null,
};

function $(id) {
  return document.getElementById(id);
}

function showPanel(name) {
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.panel === name);
  });
}

function renderSlogan(index, animate) {
  const slide = SLOGANS[index % SLOGANS.length];
  const title = $("slogan-text");
  const sub = $("slogan-sub");
  const dots = $("slogan-dots");

  const apply = () => {
    title.textContent = slide.title;
    sub.textContent = slide.sub;
    title.classList.remove("is-exit");
    sub.classList.remove("is-exit");
    [...dots.children].forEach((dot, i) => {
      dot.classList.toggle("on", i === index % SLOGANS.length);
    });
  };

  if (!animate) {
    apply();
    return;
  }

  title.classList.add("is-exit");
  sub.classList.add("is-exit");
  window.setTimeout(apply, 280);
}

function startSlogans() {
  const dots = $("slogan-dots");
  dots.innerHTML = "";
  SLOGANS.forEach(() => dots.appendChild(document.createElement("span")));
  renderSlogan(0, false);
  window.clearInterval(state.sloganTimer);
  state.sloganTimer = window.setInterval(() => {
    state.sloganIndex = (state.sloganIndex + 1) % SLOGANS.length;
    renderSlogan(state.sloganIndex, true);
  }, 4200);
}

function formatBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

async function init() {
  const defaults = await window.installer.getDefaults();
  state.installDir = defaults.defaultDir;
  $("install-path").value = defaults.defaultDir;
  $("footer-version").textContent = `v${defaults.version}`;

  if (!defaults.payloadReady) {
    showPanel("error");
    $("error-message").textContent =
      "Application payload is missing. Build dist\\NGOFundraising first, then run npm run sync-payload in the installer folder.";
  }

  startSlogans();

  $("btn-min").addEventListener("click", () => window.installer.minimize());
  $("btn-close").addEventListener("click", () => window.installer.close());
  $("btn-error-close").addEventListener("click", () => window.installer.close());
  $("btn-finish").addEventListener("click", () => window.installer.close());

  $("btn-begin").addEventListener("click", () => showPanel("path"));
  $("btn-back-welcome").addEventListener("click", () => showPanel("welcome"));
  $("btn-retry").addEventListener("click", () => showPanel("path"));

  $("btn-browse").addEventListener("click", async () => {
    const chosen = await window.installer.chooseDirectory($("install-path").value);
    if (chosen) {
      state.installDir = chosen;
      $("install-path").value = chosen;
    }
  });

  $("btn-cancel").addEventListener("click", async () => {
    await window.installer.cancel();
  });

  $("btn-install").addEventListener("click", async () => {
    const installDir = ($("install-path").value || "").trim();
    if (!installDir) return;

    showPanel("progress");
    $("progress-status").textContent = "Copying application files…";
    $("meter-fill").style.width = "0%";
    $("progress-pct").textContent = "0%";
    $("progress-file").textContent = "—";
    $("progress-count").textContent = "0 / 0 files";

    if (state.offProgress) state.offProgress();
    state.offProgress = window.installer.onProgress((data) => {
      $("meter-fill").style.width = `${data.percent}%`;
      $("progress-pct").textContent = `${data.percent}%`;
      $("progress-file").textContent = data.file || "—";
      $("progress-count").textContent = `${data.copiedFiles} / ${data.totalFiles} files · ${formatBytes(
        data.copiedBytes
      )}`;
      document.querySelector(".meter").setAttribute("aria-valuenow", String(data.percent));
    });

    try {
      const result = await window.installer.start({
        installDir,
        desktopShortcut: $("opt-desktop").checked,
        startMenuShortcut: $("opt-startmenu").checked,
      });
      state.installDir = result.installDir;
      state.exePath = result.exePath;
      $("done-path").textContent = result.installDir;
      showPanel("done");
    } catch (err) {
      showPanel("error");
      $("error-message").textContent = err?.message || String(err);
    }
  });

  $("btn-launch").addEventListener("click", async () => {
    try {
      await window.installer.launch(state.exePath);
      window.installer.close();
    } catch (err) {
      showPanel("error");
      $("error-message").textContent = err?.message || String(err);
    }
  });

  $("btn-open-folder").addEventListener("click", () => {
    window.installer.openFolder(state.installDir);
  });
}

init().catch((err) => {
  showPanel("error");
  $("error-message").textContent = err?.message || String(err);
});
