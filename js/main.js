/* ==========================================================================
   main.js — interaction layer
   Sticky header · hero entrance · mobile drawer · FAQ accordion ·
   gallery lightbox · room slider · scroll reveal · scroll-expand · inquiry form
   All modules are independent; a missing element simply skips its module.
   ========================================================================== */

(function () {
  "use strict";

  var $  = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ======================================================================
     STICKY HEADER
     Transparent over the hero, solid once the user scrolls past it.
     ====================================================================== */
  function initHeader() {
    var header = $("[data-header]");
    var hero   = $(".hero");
    if (!header) return;

    var ticking = false;

    function update() {
      var threshold = hero ? Math.min(hero.offsetHeight * 0.6, 420) : 40;
      header.classList.toggle("is-scrolled", window.scrollY > threshold);
      header.classList.toggle("is-lifted", window.scrollY > 8);
      ticking = false;
    }

    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    window.addEventListener("resize", update, { passive: true });
    update();
  }

  /* ======================================================================
     HERO ENTRANCE
     The headline reveals word by word and the stat numbers count up.

     Both have to run AFTER i18n has written the copy, because i18n replaces
     the headline's innerHTML (it contains an <em>) and the stat values. So
     they hang off the i18n:changed event rather than DOMContentLoaded, and
     re-run whenever the language changes.
     ====================================================================== */
  function afterTranslation(fn) {
    // If i18n already applied before we got here, run now as well.
    if (window.I18N && window.I18N.current) fn();
    document.addEventListener("i18n:changed", fn);
  }

  /* ---- headline ------------------------------------------------------- */
  function splitWords(el) {
    var index = 0;

    function walk(node) {
      var kids = Array.prototype.slice.call(node.childNodes);
      kids.forEach(function (child) {
        if (child.nodeType === 3) {
          // Split on spaces but keep them, so the sentence still reads as one
          // run of text to a screen reader and copies correctly.
          var frag = document.createDocumentFragment();
          child.nodeValue.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var outer = document.createElement("span");
            outer.className = "word";
            var inner = document.createElement("span");
            inner.className = "word__in";
            inner.style.setProperty("--i", index++);
            inner.textContent = part;
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    }

    walk(el);
    return index;
  }

  function initHeadline() {
    var title = $(".hero__title");
    if (!title) return;

    afterTranslation(function () {
      if (prefersReducedMotion) { title.classList.add("is-shown"); return; }
      // i18n has just rewritten innerHTML, so the previous spans are gone.
      splitWords(title);
      title.classList.remove("is-shown");
      // Next frame, so the starting transform is committed before it animates.
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { title.classList.add("is-shown"); });
      });
    });
  }

  /* ---- stat numbers --------------------------------------------------- */
  /**
   * Split "500+" into {prefix:"", digits:"500", suffix:"+"}. Values without a
   * countable number — "7/24" is a phrase, not a quantity — return null and
   * are left alone.
   */
  function parseStat(text) {
    if (text.indexOf("/") !== -1) return null;
    var m = /^(\D*?)([\d][\d.,]*)(.*)$/.exec(text);
    if (!m) return null;
    var raw = m[2];
    var sep = /[.,]/.test(raw) ? raw.replace(/[^.,]/g, "").charAt(0) : "";
    var value = parseInt(raw.replace(/[^\d]/g, ""), 10);
    if (!isFinite(value)) return null;
    return { prefix: m[1], value: value, suffix: m[3], sep: sep };
  }

  function format(n, sep) {
    var s = String(n);
    if (!sep) return s;
    return s.replace(/\B(?=(\d{3})+(?!\d))/g, sep);
  }

  function countUp(el, spec, duration) {
    var start = null;
    function frame(now) {
      if (start === null) start = now;
      var t = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - t, 3);           // easeOutCubic
      el.textContent = spec.prefix + format(Math.round(spec.value * eased), spec.sep) + spec.suffix;
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function initStats() {
    var values = $$(".trust__value");
    if (!values.length) return;

    var played = false;

    afterTranslation(function () {
      // The figures are re-rendered on every language switch; only animate the
      // first time, so switching language doesn't replay the whole hero.
      if (played || prefersReducedMotion) return;
      played = true;

      values.forEach(function (el, i) {
        var spec = parseStat(el.textContent.trim());
        if (!spec) return;
        el.textContent = spec.prefix + "0" + spec.suffix;
        setTimeout(function () { countUp(el, spec, 1400); }, 200 + i * 110);
      });
    });
  }

  /* ---- figures further down the page ---------------------------------- */
  /**
   * Anything marked [data-count] counts up the first time it scrolls into
   * view, rather than on load like the hero figures — a number that finished
   * counting before the reader arrived may as well not have animated.
   */
  function initFacts() {
    var els = $$("[data-count]");
    if (!els.length || prefersReducedMotion || !("IntersectionObserver" in window)) return;

    var armed = false;
    afterTranslation(function () {
      if (armed) return;            // i18n:changed fires again on every switch
      armed = true;

      var played = false;
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting || played) return;
          played = true;
          io.disconnect();
          els.forEach(function (el, i) {
            var spec = parseStat(el.textContent.trim());
            if (!spec) return;
            el.textContent = spec.prefix + "0" + spec.suffix;
            setTimeout(function () { countUp(el, spec, 1200); }, i * 130);
          });
        });
      }, { threshold: 0.5 });

      els.forEach(function (el) { io.observe(el); });
    });
  }

  /* ======================================================================
     SCROLL EXPAND
     A framed image that opens to full bleed as the page scrolls past it,
     with a headline that lifts away and overlay content that fades in.

     Ported from the React ScrollExpand component (reactbits.dev) — this
     project has no framework and no build step, so the technique is kept
     and the implementation is rewritten: same smoothstep easing, clip-path
     inset frame, counter-zoom on the media, and a sticky stage inside a
     tall track that supplies the scroll distance.
     ====================================================================== */
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  function smoothstep(edge0, edge1, x) {
    var t = clamp((x - edge0) / ((edge1 - edge0) || 1e-6), 0, 1);
    return t * t * (3 - 2 * t);
  }

  function initScrollExpand() {
    var root = $("[data-scroll-expand]");
    if (!root) return;

    var track   = $(".scroll-expand__track", root);
    var stage   = $(".scroll-expand__stage", root);
    var frame   = $(".scroll-expand__frame", root);
    var media   = $(".scroll-expand__media", root);
    var scrim   = $(".scroll-expand__scrim", root);
    var title   = $(".scroll-expand__title", root);
    var hint    = $(".scroll-expand__hint", root);
    var overlay = $(".scroll-expand__overlay", root);
    if (!track || !stage || !frame || !media) return;

    function num(name, fallback) {
      var v = parseFloat(root.getAttribute("data-" + name));
      return isFinite(v) ? v : fallback;
    }

    var cfg = {
      startWidth:     num("start-width", 42),
      startHeight:    num("start-height", 58),
      startRadius:    num("start-radius", 10),
      endRadius:      num("end-radius", 0),
      mediaZoom:      num("media-zoom", 1.35),
      scrollDistance: num("scroll-distance", 1.2),
      holdDistance:   num("hold-distance", 0.35),
      smoothing:      num("smoothing", 0.1),
      overlayScrim:   num("overlay-scrim", 0.45)
    };

    var raf = 0, current = 0, target = 0, stageH = 0, running = false;

    function applyProgress(p) {
      var e = smoothstep(0, 1, p);

      var w = cfg.startWidth + (100 - cfg.startWidth) * e;
      var h = cfg.startHeight + (100 - cfg.startHeight) * e;
      var ix = Math.max(0, (100 - w) / 2);
      var iy = Math.max(0, (100 - h) / 2);
      var r = cfg.startRadius + (cfg.endRadius - cfg.startRadius) * e;
      frame.style.clipPath = "inset(" + iy + "% " + ix + "% " + iy + "% " + ix + "% round " + r + "px)";

      // The media counter-zooms as the frame opens, so the picture appears to
      // sit still while the window onto it grows.
      media.style.transform = "scale(" + (cfg.mediaZoom + (1 - cfg.mediaZoom) * e) + ")";

      if (scrim) scrim.style.opacity = String(cfg.overlayScrim * e);

      if (title) {
        var out = smoothstep(0.4, 0.88, p);
        title.style.opacity = String(1 - out);
        title.style.transform = "translate3d(0," + (-28 * out) + "px,0) scale(" + (1 + 0.06 * out) + ")";
      }
      if (hint) {
        var gone = smoothstep(0, 0.12, p);
        hint.style.opacity = String(1 - gone);
        hint.style.transform = "translate3d(0," + (8 * gone) + "px,0)";
      }
      if (overlay) {
        var inn = smoothstep(0.68, 1, p);
        overlay.style.opacity = String(inn);
        overlay.style.transform = "translate3d(0," + (18 * (1 - inn)) + "px,0)";
        // Only clickable once it has actually arrived.
        overlay.style.pointerEvents = inn > 0.9 ? "auto" : "none";
      }
    }

    function measure() {
      stageH = window.innerHeight;
      stage.style.height = stageH + "px";
      track.style.height =
        (stageH * (1 + Math.max(0, cfg.scrollDistance) + Math.max(0, cfg.holdDistance))) + "px";
      stage.style.setProperty("--se-title-size",
        clamp(root.clientWidth * 0.06, 24, 68) + "px");
    }

    function readProgress() {
      var span = stageH * Math.max(0.01, cfg.scrollDistance);
      return clamp(-track.getBoundingClientRect().top / span, 0, 1);
    }

    function tick(){
      var k = cfg.smoothing <= 0 ? 1 : 1 - Math.exp(-1 / (60 * cfg.smoothing));
      current += (target - current) * k;
      if (Math.abs(target - current) < 0.0004) { current = target; running = false; }
      applyProgress(current);
      raf = running ? requestAnimationFrame(tick) : 0;
    }

    function onScroll() {
      target = readProgress();
      if (cfg.smoothing <= 0) { current = target; applyProgress(current); return; }
      if (running) return;
      running = true;
      if (!raf) raf = requestAnimationFrame(tick);
    }

    function onResize() {
      measure();
      target = current = readProgress();
      applyProgress(current);
    }

    if (prefersReducedMotion) {
      // No scroll choreography: show the finished state and collapse the
      // track so the section does not become a long stretch of empty scroll.
      root.classList.add("is-static");
      stage.style.height = "";
      track.style.height = "";
      applyProgress(1);
      return;
    }

    root.classList.add("is-live");
    measure();
    target = current = readProgress();
    applyProgress(current);

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    if ("ResizeObserver" in window) new ResizeObserver(onResize).observe(root);

    // The overlay holds translated copy; a language switch can reflow it.
    document.addEventListener("i18n:changed", onResize);
  }

  /* ======================================================================
     MOBILE DRAWER
     ====================================================================== */
  function initDrawer() {
    var toggle = $("#nav-toggle");
    var drawer = $("#mobile-drawer");
    if (!toggle || !drawer) return;

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute(
        "aria-label",
        window.I18N ? window.I18N.t(open ? "a11y.closeMenu" : "a11y.openMenu")
                    : (open ? "Close menu" : "Open menu")
      );
      document.body.classList.toggle("is-locked", open);
      document.documentElement.classList.toggle("drawer-open", open);

      if (open) {
        drawer.hidden = false;
        // Next frame, so the transition has a starting state to animate from.
        requestAnimationFrame(function () { drawer.classList.add("is-open"); });
      } else {
        drawer.classList.remove("is-open");
        var done = function () { drawer.hidden = true; };
        if (prefersReducedMotion) done();
        else setTimeout(done, 280);
      }
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    // Any navigation closes the drawer.
    $$(".drawer__link, .drawer .btn", drawer).forEach(function (link) {
      link.addEventListener("click", function () { setOpen(false); });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });

    // Returning to desktop width should never leave the drawer stuck open.
    // Must match the nav breakpoint in _header.css.
    window.matchMedia("(min-width: 1080px)").addEventListener("change", function (e) {
      if (e.matches) setOpen(false);
    });

    // Keep the label correct after a language switch.
    document.addEventListener("i18n:changed", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-label", window.I18N.t(open ? "a11y.closeMenu" : "a11y.openMenu"));
    });
  }

  /* ======================================================================
     FAQ ACCORDION — one panel at a time, height animated from real content
     ====================================================================== */
  function initAccordion() {
    var root = $("[data-accordion]");
    if (!root) return;

    var triggers = $$(".faq-item__trigger", root);

    function close(trigger) {
      var panel = document.getElementById(trigger.getAttribute("aria-controls"));
      trigger.setAttribute("aria-expanded", "false");
      trigger.closest(".faq-item").classList.remove("is-open");
      if (!panel) return;
      panel.style.maxHeight = panel.scrollHeight + "px";
      requestAnimationFrame(function () { panel.style.maxHeight = "0px"; });
      var done = function () { panel.hidden = true; panel.style.maxHeight = ""; };
      if (prefersReducedMotion) done();
      else setTimeout(done, 300);
    }

    function open(trigger) {
      var panel = document.getElementById(trigger.getAttribute("aria-controls"));
      trigger.setAttribute("aria-expanded", "true");
      trigger.closest(".faq-item").classList.add("is-open");
      if (!panel) return;
      panel.hidden = false;
      panel.style.maxHeight = "0px";
      requestAnimationFrame(function () {
        panel.style.maxHeight = panel.scrollHeight + "px";
      });
      // Release the fixed height so the panel reflows if the text wraps
      // differently after a language switch or a resize.
      setTimeout(function () {
        if (trigger.getAttribute("aria-expanded") === "true") panel.style.maxHeight = "none";
      }, 320);
    }

    triggers.forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var isOpen = trigger.getAttribute("aria-expanded") === "true";
        triggers.forEach(function (other) {
          if (other.getAttribute("aria-expanded") === "true") close(other);
        });
        if (!isOpen) open(trigger);
      });

      trigger.addEventListener("keydown", function (e) {
        var i = triggers.indexOf(trigger);
        var next = null;
        if (e.key === "ArrowDown")    next = triggers[(i + 1) % triggers.length];
        else if (e.key === "ArrowUp") next = triggers[(i - 1 + triggers.length) % triggers.length];
        else if (e.key === "Home")    next = triggers[0];
        else if (e.key === "End")     next = triggers[triggers.length - 1];
        else return;
        e.preventDefault();
        next.focus();
      });
    });
  }

  /* ======================================================================
     ROOM PHOTO SLIDER
     The track is a scroll-snap container, so touch swipe, trackpad gestures
     and keyboard scrolling all work natively. JS only adds the buttons and
     dots and keeps them in step with the scroll position — it never becomes
     the source of truth for which slide is showing.
     ====================================================================== */
  function initSliders() {
    $$("[data-slider]").forEach(function (root) {
      var track = $("[data-slider-track]", root);
      var slides = $$(".room-slider__slide", root);
      var dots = $$("[data-slider-dot]", root);
      var current = $("[data-slider-current]", root);
      var prev = $("[data-slider-prev]", root);
      var next = $("[data-slider-next]", root);
      if (!track || slides.length < 2) return;

      var index = 0;

      function go(i) {
        i = Math.max(0, Math.min(slides.length - 1, i));
        track.scrollTo({
          left: slides[i].offsetLeft - track.offsetLeft,
          behavior: prefersReducedMotion ? "auto" : "smooth"
        });
      }

      function sync() {
        // Derive the active slide from where the track actually is, so a
        // swipe and a button press cannot disagree.
        var mid = track.scrollLeft + track.clientWidth / 2;
        var best = 0, bestDist = Infinity;
        slides.forEach(function (s, i) {
          var c = s.offsetLeft - track.offsetLeft + s.clientWidth / 2;
          var d = Math.abs(c - mid);
          if (d < bestDist) { bestDist = d; best = i; }
        });
        if (best === index) return;
        index = best;
        dots.forEach(function (d, i) {
          d.classList.toggle("is-active", i === index);
          d.setAttribute("aria-current", i === index ? "true" : "false");
        });
        if (current) current.textContent = String(index + 1);
        if (prev) prev.disabled = index === 0;
        if (next) next.disabled = index === slides.length - 1;
      }

      if (prev) prev.addEventListener("click", function () { go(index - 1); });
      if (next) next.addEventListener("click", function () { go(index + 1); });
      dots.forEach(function (d, i) {
        d.addEventListener("click", function () { go(i); });
      });

      var ticking = false;
      track.addEventListener("scroll", function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () { sync(); ticking = false; });
      }, { passive: true });

      track.addEventListener("keydown", function (e) {
        var rtl = document.documentElement.getAttribute("dir") === "rtl";
        var fwd = rtl ? "ArrowLeft" : "ArrowRight";
        var back = rtl ? "ArrowRight" : "ArrowLeft";
        if (e.key === fwd)       { e.preventDefault(); go(index + 1); }
        else if (e.key === back) { e.preventDefault(); go(index - 1); }
      });

      window.addEventListener("resize", sync);
      // Set the initial state (dot 1 active, prev disabled).
      index = -1;
      sync();
    });
  }

  /* ======================================================================
     GALLERY LIGHTBOX
     ====================================================================== */
  function initLightbox() {
    var grid = $("[data-lightbox]");
    var box  = $("#lightbox");
    if (!grid || !box) return;

    var buttons = $$(".gallery-item__btn", grid);
    var img     = $(".lightbox__img", box);
    var caption = $(".lightbox__caption", box);
    var index   = 0;
    var lastFocused = null;

    function render() {
      var source = $("img", buttons[index]);
      img.src = source.currentSrc || source.src;
      img.alt = source.alt || "";
      caption.textContent = source.alt || "";
    }

    function open(i) {
      index = i;
      lastFocused = document.activeElement;
      box.hidden = false;
      document.body.classList.add("is-locked");
      render();
      requestAnimationFrame(function () { box.classList.add("is-open"); });
      $("[data-lightbox-close]", box).focus();
    }

    function close() {
      box.classList.remove("is-open");
      document.body.classList.remove("is-locked");
      // removeAttribute, not src = "" — an empty src re-requests the page.
      var done = function () { box.hidden = true; img.removeAttribute("src"); };
      if (prefersReducedMotion) done();
      else setTimeout(done, 240);
      if (lastFocused) lastFocused.focus();
    }

    function step(delta) {
      index = (index + delta + buttons.length) % buttons.length;
      render();
    }

    buttons.forEach(function (btn, i) {
      btn.addEventListener("click", function () { open(i); });
    });

    $("[data-lightbox-close]", box).addEventListener("click", close);
    $("[data-lightbox-prev]", box).addEventListener("click", function () { step(-1); });
    $("[data-lightbox-next]", box).addEventListener("click", function () { step(1); });

    // Clicking the backdrop (but not the photo or a control) closes it.
    box.addEventListener("click", function (e) {
      if (e.target === box || e.target.classList.contains("lightbox__figure")) close();
    });

    document.addEventListener("keydown", function (e) {
      if (box.hidden) return;
      if (e.key === "Escape")          { close(); }
      else if (e.key === "ArrowRight") { step(1); }
      else if (e.key === "ArrowLeft")  { step(-1); }
      else if (e.key === "Tab")        { trapFocus(e); }
    });

    // Keeps Tab inside the dialog while it is open.
    function trapFocus(e) {
      var focusable = $$("button", box);
      if (!focusable.length) return;
      var first = focusable[0];
      var last  = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    }

    // Alt text is translated, so the caption has to refresh with the language.
    document.addEventListener("i18n:changed", function () {
      if (!box.hidden) render();
    });
  }

  /* ======================================================================
     SCROLL REVEAL
     ====================================================================== */
  function initReveal() {
    var items = $$("[data-reveal]");
    if (!items.length) return;

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* ======================================================================
     ACTIVE NAV LINK
     ====================================================================== */
  function initScrollSpy() {
    var links = $$(".nav__link[href^='#']");
    if (!links.length || !("IntersectionObserver" in window)) return;

    var map = {};
    var sections = [];
    links.forEach(function (link) {
      var id = link.getAttribute("href").slice(1);
      var section = document.getElementById(id);
      if (!section) return;
      map[id] = link;
      sections.push(section);
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (l) { l.classList.remove("is-current"); });
        var link = map[entry.target.id];
        if (link) link.classList.add("is-current");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });

    sections.forEach(function (s) { observer.observe(s); });
  }

  /* ======================================================================
     FLOATING WHATSAPP BUTTON
     It is fixed to the bottom corner, so at the end of the page it sits on
     top of the footer's legal links. Retire it once the footer is in view —
     the footer carries its own WhatsApp link anyway.
     ====================================================================== */
  function initFab() {
    var fab = $(".wa-fab");
    var footer = $(".footer");
    if (!fab || !footer || !("IntersectionObserver" in window)) return;

    new IntersectionObserver(function (entries) {
      fab.classList.toggle("is-tucked", entries[0].isIntersecting);
    }, { threshold: 0 }).observe(footer);
  }

  /* ======================================================================
     INQUIRY FORM
     Client-side validation, then hand off to the visitor's mail client.
     ====================================================================== */
  function initForm() {
    var form = $("#inquiry-form");
    if (!form) return;

    var status = $("#form-status");
    var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    // Turkish mobile numbers, tolerant of spaces, dashes and +90 / 0 prefixes.
    var PHONE_RE = /^[+\d][\d\s()\-.]{7,}$/;

    function fieldError(name) { return $('[data-error-for="' + name + '"]', form); }

    function setError(input, errorEl, hasError) {
      if (input) {
        input.classList.toggle("has-error", hasError);
        input.setAttribute("aria-invalid", hasError ? "true" : "false");
      }
      if (errorEl) errorEl.hidden = !hasError;
    }

    function validate() {
      var problems = [];

      var name = $("#f-name");
      var nameBad = !name.value.trim();
      setError(name, fieldError("f-name"), nameBad);
      if (nameBad) problems.push(name);

      var phone = $("#f-phone");
      var phoneBad = !PHONE_RE.test(phone.value.trim());
      setError(phone, fieldError("f-phone"), phoneBad);
      if (phoneBad) problems.push(phone);

      var email = $("#f-email");
      var emailBad = !EMAIL_RE.test(email.value.trim());
      setError(email, fieldError("f-email"), emailBad);
      if (emailBad) problems.push(email);

      var roomType = form.querySelector('input[name="roomType"]:checked');
      var roomBad = !roomType;
      setError(null, fieldError("roomType"), roomBad);
      if (roomBad) problems.push(form.querySelector('input[name="roomType"]'));

      return problems;
    }

    // Clear a field's error as soon as the visitor starts fixing it.
    $$(".field__input", form).forEach(function (input) {
      input.addEventListener("input", function () {
        if (input.classList.contains("has-error")) {
          setError(input, fieldError(input.id), false);
        }
      });
    });
    $$('input[name="roomType"]', form).forEach(function (radio) {
      radio.addEventListener("change", function () {
        setError(null, fieldError("roomType"), false);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var problems = validate();
      if (problems.length) {
        status.textContent = "";
        status.className = "form__status";
        problems[0].focus();
        return;
      }

      var t = window.I18N ? window.I18N.t : function (k) { return k; };
      var roomKeys = { single: "form.roomSingle", twin: "form.roomTwin",
                       triple: "form.roomTriple", quad: "form.roomQuad" };
      var roomType = form.querySelector('input[name="roomType"]:checked').value;
      var roomLabel = t(roomKeys[roomType] || "form.roomSingle");

      var body = [
        t("form.name")     + ": " + $("#f-name").value.trim(),
        t("form.phone")    + ": " + $("#f-phone").value.trim(),
        t("form.email")    + ": " + $("#f-email").value.trim(),
        t("form.interest") + ": " + roomLabel,
        "",
        t("form.message")  + ":",
        $("#f-message").value.trim()
      ].join("\n");

      /* TODO: connect to backend.
         Replace the mailto hand-off below with a POST once an endpoint exists:

           fetch(ENDPOINT, {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             body: JSON.stringify(payload)
           })

         Keep the validation above and the status messages as they are. */
      var mailto = "mailto:" + t("contact.emailRaw") +
                   "?subject=" + encodeURIComponent(t("form.mailSubject")) +
                   "&body="    + encodeURIComponent(body);

      status.className = "form__status is-pending";
      status.textContent = t("form.sending");

      window.location.href = mailto;

      setTimeout(function () {
        status.className = "form__status is-success";
        status.textContent = t("form.success");
        form.reset();
      }, 600);
    });
  }

  /* ======================================================================
     BOOT
     ====================================================================== */
  function init() {
    initHeader();
    initHeadline();
    initStats();
    initFacts();
    initScrollExpand();
    initSliders();
    initDrawer();
    initAccordion();
    initLightbox();
    initReveal();
    initScrollSpy();
    initForm();
    initFab();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
