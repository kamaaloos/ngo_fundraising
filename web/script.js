(() => {
  const INSTALLER_PATH = "downloads/MayleSoft-Installer-1.1.0.exe";
  const INSTALLER_NAME = "MayleSoft-Installer-1.1.0.exe";
  const INSTALLER_VERSION = "1.1.0";

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

  const setStatus = (text, kind) => {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.remove("is-ok", "is-warn", "is-err");
    if (kind) statusEl.classList.add(kind);
  };

  const setDownloadEnabled = (enabled) => {
    downloadLinks.forEach((link) => {
      link.setAttribute("href", INSTALLER_PATH);
      link.setAttribute("download", INSTALLER_NAME);
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

  const verifyInstaller = async () => {
    metaEls.forEach((el) => {
      el.textContent = `Windows 10 / 11 · MayleSoft Installer ${INSTALLER_VERSION} · 30-day trial`;
    });

    if (location.protocol === "file:") {
      setDownloadEnabled(true);
      setStatus(
        `Local preview: cannot verify ${INSTALLER_NAME} over file://. Host this folder to confirm the file is served.`,
        "is-warn"
      );
      return;
    }

    try {
      let verified = null;
      const head = await fetch(INSTALLER_PATH, {
        method: "HEAD",
        cache: "no-store",
      });
      if (head.ok) {
        verified = head;
      } else {
        const ranged = await fetch(INSTALLER_PATH, {
          method: "GET",
          headers: { Range: "bytes=0-0" },
          cache: "no-store",
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
        sizeHint = ` · ${(bytes / (1024 * 1024)).toFixed(0)} MB reported`;
      }

      setDownloadEnabled(true);
      setStatus(
        `Installer verified on this site: ${INSTALLER_NAME}${sizeHint}.`,
        "is-ok"
      );
    } catch (_err) {
      setDownloadEnabled(false);
      setStatus(
        `${INSTALLER_NAME} is not available from this host yet. Place it in web/downloads/ before publishing.`,
        "is-err"
      );
    }
  };

  const closeNav = () => {
    if (!header || !toggle) return;
    header.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
  };

  const openNav = () => {
    if (!header || !toggle) return;
    header.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close menu");
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

  const slogans = [
    "Every pledge accounted for.",
    "Every project clear.",
    "Every gift tracked locally.",
    "Every report ready to print.",
  ];

  const startSloganRoll = () => {
    const viewport = document.querySelector(".slogan-viewport");
    const sr = document.querySelector(".slogan-sr");
    if (!viewport) return;

    let index = 0;
    let current = viewport.querySelector(".slogan-line");
    if (!current) {
      current = document.createElement("span");
      current.className = "slogan-line is-current";
      current.textContent = slogans[0];
      viewport.appendChild(current);
    } else {
      current.textContent = slogans[0];
      current.className = "slogan-line is-current";
    }

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
      window.setTimeout(() => {
        outgoing.remove();
        next.classList.remove("is-enter");
        next.classList.add("is-current");
        current = next;
        index = nextIndex;
      }, swapMs);
    };

    window.setInterval(tick, holdMs + swapMs);
  };

  verifyInstaller();
  startSloganRoll();
})();
