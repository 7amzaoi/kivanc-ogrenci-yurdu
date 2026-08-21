/* ==========================================================================
   main.js — interaction layer
   Sticky header · mobile drawer · FAQ accordion ·
   gallery lightbox · scroll reveal · inquiry form
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
      var roomKeys = { single: "form.roomSingle", twin: "form.roomTwin", triple: "form.roomTriple" };
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
