/* ==========================================================================
   i18n.js — JSON-driven translation layer
   --------------------------------------------------------------------------
   Markup contract:
     data-i18n="key.path"                     → element.textContent
     data-i18n-html="key.path"                → element.innerHTML (copy with markup)
     data-i18n-attr="attr:key; attr2:key2"    → element.setAttribute(attr, value)

   Adding a language (e.g. Arabic):
     1. Copy i18n/en.json → i18n/ar.json and translate the values.
     2. Add `ar: { label: "عربي", dir: "rtl", ... }` to LOCALES below.
     3. Add a <button data-lang="ar"> to any .lang-switch group.
   No other change is needed — every layout rule uses logical properties, so
   `dir="rtl"` mirrors the page on its own.
   ========================================================================== */

(function () {
  "use strict";

  /* ---------------------------------------------------------------------
     Locale registry — the single place new languages get declared.
     --------------------------------------------------------------------- */
  var LOCALES = {
    tr: { label: "Türkçe",  short: "TR", dir: "ltr", htmlLang: "tr" },
    en: { label: "English", short: "EN", dir: "ltr", htmlLang: "en" }
    // ar: { label: "عربي", short: "AR", dir: "rtl", htmlLang: "ar" }
  };

  var DEFAULT_LANG = "tr";          // Turkish-first: most visitors are local.
  var STORAGE_KEY  = "kivanc.lang";
  var BASE_PATH    = "i18n/";

  var dictionaries = {};            // lang → parsed JSON
  var current      = null;

  /* ---------------------------------------------------------------------
     Helpers
     --------------------------------------------------------------------- */

  /** Resolve "a.b.c" against a nested object. Returns undefined if absent. */
  function lookup(dict, path) {
    var parts = path.split(".");
    var node = dict;
    for (var i = 0; i < parts.length; i++) {
      if (node == null || typeof node !== "object") return undefined;
      node = node[parts[i]];
    }
    return node;
  }

  /** Translate a key. Falls back to the key itself so gaps are visible. */
  function t(path) {
    var value = lookup(dictionaries[current] || {}, path);
    if (typeof value === "string") return value;

    // Fall back to the default language before giving up.
    if (current !== DEFAULT_LANG) {
      var fallback = lookup(dictionaries[DEFAULT_LANG] || {}, path);
      if (typeof fallback === "string") return fallback;
    }
    if (window.console && console.warn) {
      console.warn("[i18n] Missing key: " + path + " (" + current + ")");
    }
    return path;
  }

  /** Pick the initial language: saved choice → browser hint → default. */
  function detectLanguage() {
    var saved;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) { /* private mode */ }
    if (saved && LOCALES[saved]) return saved;

    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    var code = nav.toLowerCase().split("-")[0];
    return LOCALES[code] ? code : DEFAULT_LANG;
  }

  function persist(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }
  }

  /* ---------------------------------------------------------------------
     Loading

     i18n/*.json is the source of truth and is fetched normally over HTTP.
     But browsers refuse fetch() on file:// URLs, so a page opened by
     double-clicking index.html could load neither language and froze on its
     inline English fallback with both buttons dead. i18n/bundle.js carries
     the same data as a plain script, which file:// can load — see
     tools/build-i18n.py.
     --------------------------------------------------------------------- */
  function fromBundle(lang) {
    var b = window.I18N_BUNDLE;
    return b && b[lang] ? b[lang] : null;
  }

  function loadDictionary(lang) {
    if (dictionaries[lang]) return Promise.resolve(dictionaries[lang]);

    // Opened from disk: go straight to the bundle rather than firing a fetch
    // that is guaranteed to fail and log a console error.
    if (location.protocol === "file:") {
      var offline = fromBundle(lang);
      if (offline) {
        dictionaries[lang] = offline;
        return Promise.resolve(offline);
      }
    }

    /* cache: "no-cache" revalidates the *browser* cache but says nothing to a
       CDN edge, which happily served a stale tr.json for an hour after a
       deploy. tools/package.py stamps window.__ASSET_V with a hash of the
       content, so a changed translation is a changed URL and therefore a
       cache miss everywhere. Absent (dev, or file://) it is simply omitted. */
    var v = window.__ASSET_V ? "?v=" + window.__ASSET_V : "";

    return fetch(BASE_PATH + lang + ".json" + v, { cache: "no-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        dictionaries[lang] = json;
        return json;
      })
      .catch(function (err) {
        // Server reachable but the file is missing/broken: the bundle may still
        // be a working (possibly older) copy, which beats an untranslated page.
        var fallback = fromBundle(lang);
        if (!fallback) throw err;
        if (window.console && console.warn) {
          console.warn("[i18n] Could not fetch " + lang +
                       ".json; using i18n/bundle.js instead. It may be stale — " +
                       "run tools/build-i18n.py.", err);
        }
        dictionaries[lang] = fallback;
        return fallback;
      });
  }

  /* ---------------------------------------------------------------------
     Applying translations to the DOM
     --------------------------------------------------------------------- */
  function applyTo(root) {
    var scope = root || document;

    scope.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.textContent = t(el.getAttribute("data-i18n"));
    });

    // Copy that legitimately contains markup (e.g. <em> inside the headline).
    // Values come from our own JSON files, never from user input.
    scope.querySelectorAll("[data-i18n-html]").forEach(function (el) {
      el.innerHTML = t(el.getAttribute("data-i18n-html"));
    });

    // "placeholder:form.namePh; aria-label:a11y.close"
    scope.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
        var bits = pair.split(":");
        if (bits.length < 2) return;
        var attr = bits[0].trim();
        var key  = bits.slice(1).join(":").trim();
        if (attr && key) el.setAttribute(attr, t(key));
      });
    });
  }

  /**
   * Contact details live in the JSON files only, so real values can be
   * dropped in without touching the HTML. This rewrites every tel:, wa.me
   * and mailto: href on the page from those values.
   */
  function applyContactLinks() {
    // Strip only formatting characters — NOT every non-digit. A blanket
    // \D strip would silently turn a half-filled placeholder like
    // "905XXXXXXXXX" into a live-but-wrong link (wa.me/905) instead of an
    // obviously broken one. Real numbers pass through unchanged either way.
    var phoneRaw = t("contact.phoneRaw").replace(/[\s()\-.]/g, "");
    var waNumber = t("contact.waNumber").replace(/[\s+()\-.]/g, "");
    var email    = t("contact.emailRaw");

    document.querySelectorAll("[data-contact-tel]").forEach(function (el) {
      el.setAttribute("href", "tel:" + phoneRaw);
    });
    document.querySelectorAll("[data-contact-wa]").forEach(function (el) {
      el.setAttribute("href", "https://wa.me/" + waNumber);
    });
    document.querySelectorAll("[data-contact-mail]").forEach(function (el) {
      el.setAttribute("href", "mailto:" + email);
    });

    // Google Maps "directions to" deep link, built from the same coordinates
    // the embedded map uses. api=1 is the documented, stable URL form.
    var lat = t("contact.mapLat").trim();
    var lng = t("contact.mapLng").trim();
    document.querySelectorAll("[data-contact-map]").forEach(function (el) {
      el.setAttribute("href",
        "https://www.google.com/maps/search/?api=1&query=" +
        encodeURIComponent(lat + "," + lng));
    });

    // The embedded map, from the same coordinates, with its own UI in the
    // chosen language. Only reassign when the URL actually changes — setting
    // src reloads the iframe, which would flash the map on every switch.
    var embed = "https://www.google.com/maps?q=" + encodeURIComponent(lat + "," + lng) +
                "&z=17&hl=" + encodeURIComponent(LOCALES[current].htmlLang) + "&output=embed";
    document.querySelectorAll("[data-contact-mapframe]").forEach(function (el) {
      if (el.getAttribute("src") !== embed) el.setAttribute("src", embed);
    });
  }

  /** Reflect the active language on every switcher on the page. */
  function syncSwitchers(lang) {
    document.querySelectorAll(".lang-switch__btn").forEach(function (btn) {
      var isActive = btn.getAttribute("data-lang") === lang;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      // The button that switches TO a language should announce that language,
      // not the current one — so screen readers get "Switch to English".
      btn.setAttribute("lang", btn.getAttribute("data-lang"));
    });
  }

  /* ---------------------------------------------------------------------
     Public API
     --------------------------------------------------------------------- */
  /**
   * @param {string} lang
   * @param {boolean} [remember]  Persist as the visitor's choice. Only true
   *   when they actually pick a language — writing the auto-detected one to
   *   storage would freeze a first-visit guess in place, so a later change to
   *   their browser language would never be picked up.
   */
  function setLanguage(lang, remember) {
    if (!LOCALES[lang]) lang = DEFAULT_LANG;

    return loadDictionary(lang)
      .then(function () {
        current = lang;
        var meta = LOCALES[lang];

        document.documentElement.setAttribute("lang", meta.htmlLang);
        document.documentElement.setAttribute("dir", meta.dir);

        applyTo(document);
        applyContactLinks();
        syncSwitchers(lang);
        if (remember) persist(lang);

        // Lets main.js re-render anything it owns (e.g. lightbox captions).
        document.dispatchEvent(new CustomEvent("i18n:changed", {
          detail: { lang: lang, dir: meta.dir }
        }));
      })
      .catch(function (err) {
        // The page still reads correctly: index.html ships with English copy
        // inline, so a failed fetch degrades rather than blanking the site.
        if (window.console) {
          console.error(
            "[i18n] Could not load '" + lang + "'. Neither i18n/" + lang +
            ".json nor i18n/bundle.js was available. If bundle.js is missing, " +
            "run: python tools/build-i18n.py", err
          );
        }
      });
  }

  var I18N = {
    t: t,
    setLanguage: setLanguage,
    applyTo: applyTo,
    locales: LOCALES,
    get current() { return current; },
    get dir() { return current && LOCALES[current] ? LOCALES[current].dir : "ltr"; }
  };

  window.I18N = I18N;

  /* ---------------------------------------------------------------------
     Wire up the switchers and boot
     --------------------------------------------------------------------- */
  function init() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest(".lang-switch__btn");
      if (!btn) return;
      e.preventDefault();
      var lang = btn.getAttribute("data-lang");
      if (lang && lang !== current) setLanguage(lang, true);
    });

    // Left/Right arrows move between the two options, matching native
    // radio-group behaviour for keyboard users.
    document.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var btn = e.target.closest(".lang-switch__btn");
      if (!btn) return;
      var group = Array.prototype.slice.call(
        btn.closest(".lang-switch").querySelectorAll(".lang-switch__btn")
      );
      var step = e.key === "ArrowRight" ? 1 : -1;
      var next = group[(group.indexOf(btn) + step + group.length) % group.length];
      next.focus();
      e.preventDefault();
    });

    setLanguage(detectLanguage());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
