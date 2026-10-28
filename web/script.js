(() => {
  const LOCAL_INSTALLER_PATH = "downloads/MayleSoft-Installer-1.1.0.exe";
  const DEFAULT_NAME = "MayleSoft-Installer-1.1.0.exe";
  const DEFAULT_VERSION = "1.1.0";

  const header = document.querySelector(".site-header");
  const nav = document.querySelector("#site-nav");
  const toggle = document.querySelector(".nav-toggle");
  const revealables = document.querySelectorAll(".reveal");
  const downloadLinks = document.querySelectorAll("[data-download-link]");
  const statusEl = document.querySelector("[data-download-status]");
  const metaEls = document.querySelectorAll("[data-download-meta]");
  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  let installer = {
    version: DEFAULT_VERSION,
    fileName: DEFAULT_NAME,
    href: LOCAL_INSTALLER_PATH,
    viaBlob: false,
  };

  const setStatus = (text, kind) => {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.remove("is-ok", "is-warn", "is-err");
    if (kind) statusEl.classList.add(kind);
  };

  const applyDownloadLinks = (enabled) => {
    downloadLinks.forEach((link) => {
      link.setAttribute("href", installer.href);
      if (installer.viaBlob) {
        // Cross-origin Blob CDN: force attachment via ?download=1
        link.removeAttribute("download");
        link.setAttribute("rel", "noopener");
      } else {
        link.setAttribute("download", installer.fileName);
      }
      if (enabled) {
        link.classList.remove("is-disabled");
        link.removeAttribute("aria-disabled");
        link.removeAttribute("tabindex");
      } else {
        link.classList.add("is-disabled");
        link.setAttribute("aria-disabled", "true");
        link.setAttribute("tabindex", "-1");
      }
    });
  };

  const loadDownloadConfig = async () => {
    try {
      const res = await fetch("download-config.json", { cache: "no-store" });
      if (!res.ok) return;
      const cfg = await res.json();
      const remote =
        (cfg.downloadUrl || cfg.url || "").trim();
      if (remote) {
        installer = {
          version: String(cfg.version || DEFAULT_VERSION),
          fileName: String(cfg.fileName || DEFAULT_NAME),
          href: remote,
          viaBlob: /blob\.vercel-storage\.com/i.test(remote),
        };
      }
    } catch (_err) {
      // Keep local fallback.
    }
  };

  const i18n = () => window.NGO_I18N;

  const verifyInstaller = async () => {
    const tr = i18n()?.t || ((k, v) => k);
    metaEls.forEach((el) => {
      el.textContent = tr("ctaMeta", { version: installer.version });
    });

    if (location.protocol === "file:") {
      applyDownloadLinks(true);
      setStatus(
        installer.viaBlob
          ? tr("statusBlobPreview", { file: installer.fileName })
          : tr("statusFilePreview"),
        "is-warn"
      );
      return;
    }

    try {
      let verified = null;
      const head = await fetch(installer.href, {
        method: "HEAD",
        cache: "no-store",
        mode: "cors",
      });
      if (head.ok) {
        verified = head;
      } else {
        const ranged = await fetch(installer.href, {
          method: "GET",
          headers: { Range: "bytes=0-0" },
          cache: "no-store",
          mode: "cors",
        });
        if (!(ranged.ok || ranged.status === 206)) {
          throw new Error(`HTTP ${head.status}`);
        }
        verified = ranged;
      }

      let sizeHint = "";
      const length = verified.headers.get("content-length");
      const range = verified.headers.get("content-range");
      const totalFromRange = range && /\/(\d+)$/.exec(range);
      const bytes = totalFromRange
        ? Number(totalFromRange[1])
        : length && Number(length) > 1
          ? Number(length)
          : 0;
      if (bytes > 1024 * 1024) {
        sizeHint = ` · ${(bytes / (1024 * 1024)).toFixed(0)} MB`;
      }

      applyDownloadLinks(true);
      setStatus(
        installer.viaBlob
          ? tr("statusBlobOk", { file: installer.fileName, size: sizeHint })
          : tr("statusLocalOk", { file: installer.fileName, size: sizeHint }),
        "is-ok"
      );
    } catch (_err) {
      applyDownloadLinks(true);
      setStatus(
        installer.viaBlob
          ? tr("statusBlobWarn")
          : tr("statusMissing", { file: installer.fileName }),
        "is-warn"
      );
    }
  };

  const closeNav = () => {
    if (!header || !toggle) return;
    header.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute(
      "aria-label",
      i18n()?.t("openMenu") || "Open menu"
    );
  };

  const openNav = () => {
    if (!header || !toggle) return;
    header.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute(
      "aria-label",
      i18n()?.t("closeMenu") || "Close menu"
    );
  };

  if (toggle && header) {
    toggle.addEventListener("click", () => {
      if (header.classList.contains("is-open")) closeNav();
      else openNav();
    });
  }

  if (nav) {
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => closeNav());
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeNav();
  });

  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("is-solid", window.scrollY > 24);
  };

  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const animateCount = (el, target) => {
    const duration = 1100;
    const start = performance.now();
    const from = 0;
    const step = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = String(Math.round(from + (target - from) * eased));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const BAR_SETS = [
    [39, 65, 50, 77, 67, 92],
    [48, 58, 72, 61, 84, 70],
    [34, 71, 55, 88, 62, 79],
    [52, 44, 68, 73, 81, 95],
  ];

  const activateMock = (mock) => {
    if (!mock || mock.dataset.animated === "1") return;
    mock.dataset.animated = "1";
    mock.classList.add("is-alive");

    mock.querySelectorAll("[data-count]").forEach((el) => {
      const target = Number(el.getAttribute("data-count") || "0");
      if (reduceMotion) {
        el.textContent = String(target);
        return;
      }
      animateCount(el, target);
    });

    if (reduceMotion) return;

    const bars = [...mock.querySelectorAll(".mock-bar")];
    let setIndex = 0;
    window.setInterval(() => {
      setIndex = (setIndex + 1) % BAR_SETS.length;
      bars.forEach((bar, i) => {
        bar.style.setProperty("--h", `${BAR_SETS[setIndex][i]}%`);
      });
    }, 3200);
  };

  const showAllReveals = () => {
    revealables.forEach((el) => {
      el.classList.add("is-visible");
      if (el.hasAttribute("data-mock")) activateMock(el);
    });
  };

  if (reduceMotion || !("IntersectionObserver" in window)) {
    showAllReveals();
  } else {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            if (entry.target.hasAttribute("data-mock")) {
              activateMock(entry.target);
            }
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18, rootMargin: "0px 0px -6% 0px" }
    );

    revealables.forEach((el, index) => {
      el.style.transitionDelay = `${index * 70}ms`;
      observer.observe(el);
    });
  }

  let sloganTimer = null;
  let sloganSwapTimer = null;

  const stopSloganRoll = () => {
    if (sloganTimer) window.clearInterval(sloganTimer);
    if (sloganSwapTimer) window.clearTimeout(sloganSwapTimer);
    sloganTimer = null;
    sloganSwapTimer = null;
  };

  const startSloganRoll = () => {
    const viewport = document.querySelector(".slogan-viewport");
    const sr = document.querySelector(".slogan-sr");
    if (!viewport) return;

    stopSloganRoll();
    const pack = i18n()?.getPack?.();
    const slogans = pack?.slogans || [
      "Every pledge accounted for.",
      "Every project clear.",
      "Every gift tracked locally.",
      "Every report ready to print.",
    ];

    viewport.innerHTML = "";
    let index = 0;
    let current = document.createElement("span");
    current.className = "slogan-line is-current";
    current.textContent = slogans[0];
    viewport.appendChild(current);

    if (sr) sr.textContent = slogans.join(" ");
    if (reduceMotion || slogans.length < 2) return;

    const holdMs = 2800;
    const swapMs = 700;

    const tick = () => {
      const nextIndex = (index + 1) % slogans.length;
      const next = document.createElement("span");
      next.className = "slogan-line is-enter";
      next.textContent = slogans[nextIndex];
      viewport.appendChild(next);

      current.classList.remove("is-current");
      current.classList.add("is-exit");

      const outgoing = current;
      sloganSwapTimer = window.setTimeout(() => {
        outgoing.remove();
        next.classList.remove("is-enter");
        next.classList.add("is-current");
        current = next;
        index = nextIndex;
      }, swapMs);
    };

    sloganTimer = window.setInterval(tick, holdMs + swapMs);
  };

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const lang = btn.getAttribute("data-lang");
      if (!lang || !i18n()) return;
      i18n().applyLocale(lang);
      closeNav();
    });
  });

  if (i18n()) {
    i18n().setOnLocaleChange(() => {
      startSloganRoll();
      verifyInstaller();
      applyDownloadLinks(true);
    });
    i18n().applyLocale(i18n().detectLocale());
  }

  loadDownloadConfig()
    .then(() => verifyInstaller())
    .catch(() => {
      applyDownloadLinks(true);
      verifyInstaller();
    });
  startSloganRoll();
})();
