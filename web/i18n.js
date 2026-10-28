(() => {
  const LOCALES = {
    en: {
      dir: "ltr",
      label: "English",
      short: "EN",
      metaTitle: "NGO Fundraising | MayleSoft",
      metaDescription:
        "NGO Fundraising by MayleSoft — manage projects, donors, donations and reports on Windows. Data stays on your PC.",
      skip: "Skip to content",
      brandHome: "NGO Fundraising home",
      openMenu: "Open menu",
      closeMenu: "Close menu",
      navPrimary: "Primary",
      navFeatures: "Features",
      navDownload: "How to download",
      navSupport: "Support",
      navCta: "Get the app",
      langLabel: "Language",
      heroIntro: "Introduction",
      eyebrow: "Fundraising management made simple",
      brand: "NGO Fundraising",
      slogans: [
        "Every pledge accounted for.",
        "Every project clear.",
        "Every gift tracked locally.",
        "Every report ready to print.",
      ],
      lede:
        "From the first pledge to the final report, keep your projects, donors, payments and expenses organized in one easy-to-use Windows application. Built by MayleSoft.",
      downloadWindows: "Download for Windows",
      ctaMeta: "Windows 10 / 11 · MayleSoft Installer {version} · 30-day trial",
      trustLocal: "Works locally on your PC",
      trustNoCloud: "No cloud account required",
      trustReports: "Printable reports",
      previewLabel: "Product preview",
      mockAria:
        "Illustrative dashboard preview showing projects, donors and fundraising progress; not an actual application screenshot",
      mockTitle: "NGO Fundraising · Dashboard",
      mockLabel: "Overview",
      mockHeading: "Your impact at a glance",
      mockProjects: "Active projects",
      mockDonors: "Donor records",
      mockActivity: "Fundraising activity",
      mockTrend: "↗ Progress",
      mockNote: "Illustrative figures · Not actual data",
      featuresEyebrow: "Everything in one place",
      featuresTitle: "Less paperwork. More impact.",
      featuresLede:
        "Purpose-built tools to help your team stay organized, accountable and focused on the work that matters.",
      feature1Title: "Projects & goals",
      feature1Body:
        "Monitor fundraising targets, raised amounts and project status in one organized workspace.",
      feature2Title: "Donors & donations",
      feature2Body:
        "Record donor pledges, installments, payments and the team member who collected each gift.",
      feature3Title: "Clear, printable reports",
      feature3Body:
        "Generate charts and PDF reports for your organization or individual projects.",
      downloadTitle: "Ready to make a bigger impact?",
      downloadBody:
        "Install NGO Fundraising on your Windows PC and start organizing your fundraising work. Application data is stored locally under AppData — this is a single-PC install, not a cloud or multi-workstation service.",
      downloadNote:
        "30-day trial begins automatically. First launch: sign in as admin / admin123, then set your own password.",
      downloadChecking: "Checking installer availability…",
      downloadInstaller: "Download installer",
      downloadExpected: "Expected file:",
      footerHelp: "Need help?",
      statusBlobOk: "Installer on MayleSoft Blob: {file}{size}.",
      statusLocalOk: "Installer verified: {file}{size}.",
      statusBlobWarn:
        "Could not verify Blob URL yet. Check the MayleSoft store upload and CORS.",
      statusMissing:
        "{file} not on this host. Upload to MayleSoft Blob: npm run upload:installer",
      statusFilePreview:
        "Local preview: prefer http:// host, or upload the installer to MayleSoft Blob.",
      statusBlobPreview: "Using MayleSoft Blob URL for {file}. Open via http:// to verify.",
    },
    ar: {
      dir: "rtl",
      label: "العربية",
      short: "ع",
      metaTitle: "جمع التبرعات للمنظمات | MayleSoft",
      metaDescription:
        "تطبيق MayleSoft لجمع التبرعات — إدارة المشاريع والمتبرعين والتبرعات والتقارير على ويندوز. البيانات تبقى على جهازك.",
      skip: "تخطّ إلى المحتوى",
      brandHome: "الصفحة الرئيسية لجمع التبرعات",
      openMenu: "فتح القائمة",
      closeMenu: "إغلاق القائمة",
      navPrimary: "التنقل الرئيسي",
      navFeatures: "الميزات",
      navDownload: "طريقة التحميل",
      navSupport: "الدعم",
      navCta: "احصل على التطبيق",
      langLabel: "اللغة",
      heroIntro: "مقدمة",
      eyebrow: "إدارة جمع التبرعات بسهولة",
      brand: "جمع التبرعات",
      slogans: [
        "كل تعهد موثّق بدقة.",
        "كل مشروع واضح للعيان.",
        "كل تبرع يُتتبّع محلياً.",
        "كل تقرير جاهز للطباعة.",
      ],
      lede:
        "من أول تعهد حتى التقرير النهائي، نظّم مشاريعك ومتبرعيك ومدفوعاتك ومصروفاتك في تطبيق ويندوز سهل الاستخدام. من تطوير MayleSoft.",
      downloadWindows: "تحميل لنظام ويندوز",
      ctaMeta: "ويندوز 10 / 11 · مثبّت MayleSoft {version} · تجربة 30 يوماً",
      trustLocal: "يعمل محلياً على جهازك",
      trustNoCloud: "بدون حساب سحابي",
      trustReports: "تقارير قابلة للطباعة",
      previewLabel: "معاينة المنتج",
      mockAria:
        "معاينة توضيحية للوحة التحكم تعرض المشاريع والمتبرعين وتقدم جمع التبرعات؛ ليست لقطة شاشة حقيقية",
      mockTitle: "جمع التبرعات · لوحة التحكم",
      mockLabel: "نظرة عامة",
      mockHeading: "أثرُك في لمحة",
      mockProjects: "مشاريع نشطة",
      mockDonors: "سجلات المتبرعين",
      mockActivity: "نشاط جمع التبرعات",
      mockTrend: "↗ تقدّم",
      mockNote: "أرقام توضيحية · ليست بيانات حقيقية",
      featuresEyebrow: "كل شيء في مكان واحد",
      featuresTitle: "أوراق أقل. أثر أكبر.",
      featuresLede:
        "أدوات مصممة لمساعدة فريقك على التنظيم والمساءلة والتركيز على ما يهم.",
      feature1Title: "المشاريع والأهداف",
      feature1Body:
        "تابع أهداف جمع التبرعات والمبالغ المحصّلة وحالة المشروع في مساحة عمل واحدة.",
      feature2Title: "المتبرعون والتبرعات",
      feature2Body:
        "سجّل التعهدات والأقساط والمدفوعات والعضو الذي جمع كل تبرع.",
      feature3Title: "تقارير واضحة للطباعة",
      feature3Body:
        "أنشئ رسوماً بيانية وتقارير PDF للمنظمة أو لمشروع واحد.",
      downloadTitle: "مستعد لأثر أكبر؟",
      downloadBody:
        "ثبّت تطبيق جمع التبرعات على ويندوز وابدأ تنظيم عملك. تُحفظ البيانات محلياً ضمن AppData — تثبيت لجهاز واحد وليس خدمة سحابية أو متعددة الأجهزة.",
      downloadNote:
        "تبدأ تجربة 30 يوماً تلقائياً. عند أول تشغيل: سجّل الدخول بـ admin / admin123 ثم عيّن كلمة مرورك.",
      downloadChecking: "جارٍ التحقق من المثبّت…",
      downloadInstaller: "تحميل المثبّت",
      downloadExpected: "الملف المتوقع:",
      footerHelp: "تحتاج مساعدة؟",
      statusBlobOk: "المثبّت على MayleSoft Blob: {file}{size}.",
      statusLocalOk: "تم التحقق من المثبّت: {file}{size}.",
      statusBlobWarn:
        "تعذّر التحقق من رابط Blob بعد. راجع رفع المتجر وإعدادات CORS.",
      statusMissing:
        "{file} غير متوفر على هذا المضيف. ارفعه إلى MayleSoft Blob.",
      statusFilePreview:
        "معاينة محلية: يُفضّل فتح الصفحة عبر http:// أو رفع المثبّت إلى Blob.",
      statusBlobPreview:
        "يُستخدم رابط MayleSoft Blob لـ {file}. افتح عبر http:// للتحقق.",
    },
    so: {
      dir: "ltr",
      label: "Soomaali",
      short: "SO",
      metaTitle: "Ururinta Lacagaha NGO | MayleSoft",
      metaDescription:
        "NGO Fundraising ee MayleSoft — maamul mashaariicda, deeq-bixiyayaasha, deeqaha iyo warbixinnada Windows. Xogtu waxay ku jirtaa kombiyuutarkaaga.",
      skip: "U gudub waxa ku jira",
      brandHome: "Bogga hore ee Ururinta Lacagaha",
      openMenu: "Fur liiska",
      closeMenu: "Xir liiska",
      navPrimary: "Navigation-ka ugu muhiimsan",
      navFeatures: "Astaamaha",
      navDownload: "Sida loo soo dejiyo",
      navSupport: "Taageero",
      navCta: "Hel app-ka",
      langLabel: "Luqadda",
      heroIntro: "Hordhac",
      eyebrow: "Maamulka ururinta lacagaha si fudud",
      brand: "Ururinta Lacagaha NGO",
      slogans: [
        "Ballan kasta waa la xisaabiyaa.",
        "Mashruuc kasta waa cad.",
        "Deeq kasta waa meel-gudaha lagu raadraacaa.",
        "Warbixin kasta diyaar bay u tahay daabacaad.",
      ],
      lede:
        "Laga bilaabo ballankii ugu horreeyay ilaa warbixinta ugu dambaysa, ku haya mashaariicdaada, deeq-bixiyayaasha, lacag-bixinta iyo kharashaadka app Windows ah oo fudud. Waxaa sameeyay MayleSoft.",
      downloadWindows: "Ka soo deg Windows",
      ctaMeta: "Windows 10 / 11 · MayleSoft Installer {version} · tijaabo 30 maalmood",
      trustLocal: "Wuxuu ka shaqeeyaa PC-gaaga",
      trustNoCloud: "Looma baahna akoon daruur ah",
      trustReports: "Warbixino la daabacan karo",
      previewLabel: "Horudhac alaabta",
      mockAria:
        "Muujin tusaale ah oo dashboard ah oo muujinaya mashaariic, deeq-bixiyayaal iyo horumarka ururinta; ma aha sawir dhab ah",
      mockTitle: "Ururinta Lacagaha · Dashboard",
      mockLabel: "Dulmar",
      mockHeading: "Saamayntaada si degdeg ah",
      mockProjects: "Mashaariic firfircoon",
      mockDonors: "Diiwaanka deeq-bixiyayaasha",
      mockActivity: "Dhaqdhaqaaqa ururinta",
      mockTrend: "↗ Horumar",
      mockNote: "Tirooyin tusaale ah · Ma aha xog dhab ah",
      featuresEyebrow: "Wax walba meel keliya",
      featuresTitle: "Waraaqo yar. Saamayn badan.",
      featuresLede:
        "Qalab loogu talagalay in kooxdaadu ku ahaato nidaam, mas'uuliyad iyo diiradda shaqada muhiimka ah.",
      feature1Title: "Mashaariic & yoolal",
      feature1Body:
        "La soco yoolalka ururinta, lacagaha la ururiyay iyo xaaladda mashruuca meel shaqo oo keliya.",
      feature2Title: "Deeq-bixiyayaal & deeqo",
      feature2Body:
        "Diiwaangeli ballanka, qaybaha, lacag-bixinta iyo xubinta ururisay deeq kasta.",
      feature3Title: "Warbixino cad oo la daabaci karo",
      feature3Body:
        "Samee jaantusyo iyo warbixino PDF ururkaaga ama mashruuc keliya.",
      downloadTitle: "Diyaar ma u tahay saamayn weyn?",
      downloadBody:
        "Ku rakib NGO Fundraising PC-ga Windows ah oo bilow nidaaminta shaqadaada. Xogtu waxaa lagu kaydiyaa meel-gudaha AppData — waa rakibid hal PC ah, ma aha adeeg daruur ama dhowr qalab.",
      downloadNote:
        "Tijaabada 30-ka maalmood si toos ah ayay u bilowdaa. Furitaanka ugu horreeya: gal admin / admin123, ka dibna dooro eraygaaga sirta ah.",
      downloadChecking: "La hubinayaa installer-ka…",
      downloadInstaller: "Soo deg installer-ka",
      downloadExpected: "Faylka la filayo:",
      footerHelp: "Caawimaad miyaad u baahan tahay?",
      statusBlobOk: "Installer-ka MayleSoft Blob: {file}{size}.",
      statusLocalOk: "Installer la xaqiijiyay: {file}{size}.",
      statusBlobWarn:
        "Weli lama xaqiijin URL-ka Blob. Hubi upload-ka iyo CORS.",
      statusMissing:
        "{file} kuma jiro host-kan. Ku soo rar MayleSoft Blob.",
      statusFilePreview:
        "Horudhac maxalli ah: dooro http:// ama ku soo rar installer-ka Blob.",
      statusBlobPreview:
        "Waxaa la isticmaalayaa URL-ka MayleSoft Blob ee {file}. Fur http:// si aad u xaqiijiso.",
    },
  };

  const STORAGE_KEY = "ngo_landing_lang";

  const t = (locale, key, vars = {}) => {
    const table = LOCALES[locale] || LOCALES.en;
    let text = table[key] ?? LOCALES.en[key] ?? key;
    Object.entries(vars).forEach(([k, v]) => {
      text = text.replaceAll(`{${k}}`, String(v));
    });
    return text;
  };

  const detectLocale = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && LOCALES[saved]) return saved;
    const nav = (navigator.language || "en").toLowerCase();
    if (nav.startsWith("ar")) return "ar";
    if (nav.startsWith("so")) return "so";
    return "en";
  };

  let current = "en";
  let onLocaleChange = null;

  const applyLocale = (locale) => {
    if (!LOCALES[locale]) locale = "en";
    current = locale;
    const pack = LOCALES[locale];
    localStorage.setItem(STORAGE_KEY, locale);

    document.documentElement.lang = locale;
    document.documentElement.dir = pack.dir;
    document.title = pack.metaTitle;

    const desc = document.querySelector('meta[name="description"]');
    if (desc) desc.setAttribute("content", pack.metaDescription);
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) ogTitle.setAttribute("content", pack.metaTitle);
    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) ogDesc.setAttribute("content", pack.metaDescription);

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      el.textContent = t(locale, key);
    });

    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const key = el.getAttribute("data-i18n-aria");
      if (!key) return;
      el.setAttribute("aria-label", t(locale, key));
    });

    document.querySelectorAll("[data-lang]").forEach((btn) => {
      const active = btn.getAttribute("data-lang") === locale;
      btn.setAttribute("aria-pressed", active ? "true" : "false");
      btn.classList.toggle("is-active", active);
    });

    if (typeof onLocaleChange === "function") onLocaleChange(locale, pack);
  };

  window.NGO_I18N = {
    LOCALES,
    t: (key, vars) => t(current, key, vars),
    getLocale: () => current,
    getPack: () => LOCALES[current],
    detectLocale,
    applyLocale,
    setOnLocaleChange(fn) {
      onLocaleChange = fn;
    },
  };
})();
