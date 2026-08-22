# Kıvanç Öğrenci Yurdu — Marketing Website

Static marketing site for **Kıvanç Öğrenci Yurdu** (Özel Yüksek Öğrenim Kız Öğrenci
Yurdu, est. 2013) — a private residence for **female students** in Avcılar, İstanbul.

Vanilla HTML / CSS / JS. No build step, no framework, no dependencies. Deploy the folder
as-is to any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, nginx, cPanel).

---

## Running it locally

**Double-clicking `index.html` works.** Translations come from `i18n/bundle.js`, a plain
script, when the page is opened from disk — see *Translations and the bundle* below.

For anything beyond a quick look, serve it over HTTP so the JSON files are used directly
and you don't have to regenerate the bundle after each copy edit:

```bash
# Python 3 — no install needed
python -m http.server 8000

# or Node
npx serve .
```

Then open <http://localhost:8000>.

---

## File structure

```
index.html                 Homepage — all sections, semantic markup with data-i18n keys
rooms.html                 GENERATED rooms & prices page (see Rooms page below)
css/
  _foundation.css          Design tokens ONLY — colors, type scale, spacing, shadows, motion
  _base.css                Reset, element defaults, shared primitives (.container, .btn, .eyebrow…)
  _header.css              Header, nav, language switcher, mobile drawer
  _hero.css                Hero + trust bar
  _rooms.css               Room cards
  _universities.css        University card grid + transit strip
  _amenities.css           Facilities icon grid
  _about.css               About / value props
  _gallery.css             Gallery grid + lightbox
  _testimonials.css        Testimonial cards
  _faq.css                 FAQ accordion
  _contact.css             Contact details, map, inquiry form
  _footer.css              Footer + floating WhatsApp button
  _roomspage.css           rooms.html: page head, room rows, rate table, features
  main.css                 @imports the partials in order
js/
  i18n.js                  Translation loader / DOM applier / language persistence
  main.js                  Header state, drawer, accordion, lightbox, reveal, form, FAB
i18n/
  en.json                  English copy      <- source of truth
  tr.json                  Turkish copy      <- source of truth
  bundle.js                GENERATED from the two above; makes file:// work
tools/
  build-i18n.py            Regenerates i18n/bundle.js
  build-rooms-page.py      Regenerates rooms.html
assets/
  brand/                   Kıvanç logo, favicons (see Brand assets)
  logos/                   University logos
  images/                  Drop real property photography here
```

**One residence.** The site describes a single, female-only residence, matching the logo
(`KIZ ÖĞRENCİ YURDU`). There is no residence switcher and no second tone in the palette —
the room grid is a plain four-card grid (single, double, triple, quad). If a second building is ever added, that means
reintroducing a tab UI, a second set of room keys, and a way to tell the two apart; it is
not a copy change.

**Where to put things.** Design decisions (a color, a font size, a shadow) belong in
`_foundation.css` as a token. Anything visual that is specific to one section belongs in
that section's partial. Nothing but `@import` lines belong in `main.css`.

---

## Copy and translations

All user-visible text lives in `i18n/en.json` and `i18n/tr.json`. **Do not edit copy in
`index.html`** — the English strings there are only a no-JS fallback, and `i18n.js`
overwrites them on load.

Three attributes drive translation:

| Attribute | Effect |
|---|---|
| `data-i18n="key.path"` | sets `textContent` |
| `data-i18n-html="key.path"` | sets `innerHTML` — for copy containing markup, e.g. the `<em>` in the hero headline |
| `data-i18n-attr="placeholder:form.namePh; aria-label:a11y.close"` | sets attributes; semicolon-separated pairs |

Language choice is saved to `localStorage` under `kivanc.lang`. On a first visit the
browser language decides; Turkish is the fallback. Switching is instant — no reload.

Missing keys log a warning to the console and fall back to Turkish, then to the key name
itself, so gaps are obvious rather than silent.

### Translations and the bundle

`i18n/en.json` and `i18n/tr.json` are the source of truth. Over HTTP they are fetched
directly, so edits show up on reload with nothing else to do.

Browsers refuse `fetch()` on `file://` URLs, though. Before, that meant opening
`index.html` from disk froze the page on its inline English copy with **both language
buttons dead** — it looked like "the English translation is stuck". `i18n/bundle.js` fixes
that: it is the same data as an ordinary `<script>`, which `file://` can load.

```
i18n/en.json   i18n/tr.json     <- edit these
        |
        v  python tools/build-i18n.py
i18n/bundle.js                  <- generated; never edit by hand
```

`js/i18n.js` picks the source automatically: the bundle on `file://`, the JSON over HTTP
(falling back to the bundle with a console warning if a fetch fails).

**After editing either JSON file, run:**

```bash
python tools/build-i18n.py
```

Skipping it only affects the `file://` preview — HTTP always reads the JSON — but the
preview will quietly show the old copy, so it is worth doing every time.

---

## The rooms page

`rooms.html` is **generated** — do not edit it by hand. The site has no templating,
so a second page would otherwise mean four hand-maintained copies of the header,
drawer, icon sprite and footer. Instead `tools/build-rooms-page.py` lifts those blocks
straight out of `index.html` and writes the page around them, so the shell is identical
by construction and in-page links are rewritten to point back at the homepage.

```
index.html  (header, drawer, sprite, footer)  ─┐
i18n/en.json  (rooms.*, roomsPage.*)          ─┼─> tools/build-rooms-page.py ─> rooms.html
```

Re-run it after touching either input:

```bash
python tools/build-rooms-page.py
```

The verify pass regenerates the page and fails if the committed copy differs, and
separately checks that the header and footer still match `index.html` and that every
cross-page link and anchor resolves.

**Prices live in the JSON**, per room type: `price` (monthly), `priceTerm` (per term),
`instalments` and the assembled `payment` string. They came from the client's campaign
poster and are **per person** — the poster shows the rate falling as occupancy rises,
which only makes sense per person. Worth confirming in writing before launch.

---

## The About section's scroll-expand

The photograph in About starts as a small framed rectangle and opens to full
bleed as the page scrolls past it, while the brand tagline lifts away and the
four value props fade in over the picture.

The technique is taken from the React `ScrollExpand` component on
[reactbits.dev](https://reactbits.dev). This project has no framework and no
build step, so the component was **not** copied — it was reimplemented in
`js/main.js` (`initScrollExpand`) keeping the same maths: smoothstep easing, a
`clip-path: inset()` frame, a counter-zoom on the media so the picture appears
to sit still while the window onto it grows, and a sticky stage inside a tall
track that supplies the scroll distance.

Tuning lives in `data-*` attributes on the element in `index.html`, so it can be
adjusted without touching the script:

| attribute | default | meaning |
|---|---|---|
| `data-start-width` / `data-start-height` | 46 / 62 | resting frame size, % of the stage |
| `data-start-radius` / `data-end-radius` | 10 / 0 | corner radius, px |
| `data-media-zoom` | 1.3 | zoom at rest; eases to 1 |
| `data-scroll-distance` | 1.15 | length of the expansion, in viewport heights |
| `data-hold-distance` | 0.4 | extra scroll held at full bleed |
| `data-smoothing` | 0.09 | follow time in seconds; 0 locks to the scrollbar |
| `data-overlay-scrim` | 1 | strength of the scrim that fades in behind the copy |

**The scrim is not decoration.** The value props sit on top of a photograph, so
the copy band is weighted to near-opaque ink rather than a light wash — contrast
there has to be predictable rather than lucky. Measured against the rendered
pixels, the worst pairing is 9.9:1 and the rest 10–16:1, and it stays safe if the
photograph is swapped.

Three states, all verified:

- **normal** — the expansion runs on scroll
- **`prefers-reduced-motion`** — the script collapses the track and shows the
  finished state, so the section becomes an ordinary full-bleed band instead of
  a long stretch of empty scrolling
- **no JavaScript** — nothing sets the inline styles, so CSS falls back to a
  plain framed image with the copy visible over it

---

## Contact details — change them in ONE place

The phone, WhatsApp number and email are **not** hardcoded in the HTML. They live at the
bottom of the `contact` block in **both** `i18n/en.json` and `i18n/tr.json`:

```json
"phoneRaw": "+905415904445",                  // used for tel: links
"waNumber": "905415904445",                   // https://wa.me/ — digits only, no +
"emailRaw": "kivancogrenciyurtlari@gmail.com" // used for mailto: links
```

These are the real details, already in place, alongside the human-readable display
strings just above them (`contact.phone` renders as `+90 541 590 44 45`).

`i18n.js` writes those values into every element marked `data-contact-tel`,
`data-contact-wa` and `data-contact-mail` on the page — the header, the contact section,
the footer and the floating WhatsApp button. Change the JSON, the whole site updates.

**Address and map.** The residence is pinned at **40.9833101, 28.7098463** —
**Cihangir Mah., Kirazlı Cad. No:18, 34310 Avcılar / İstanbul**, as printed on the
client's price poster. The street was independently confirmed twice: reverse-geocoded
from the coordinates, and rendered on Kirazlı Cd. by Google's own map.

The coordinates live in `contact.mapLat` / `contact.mapLng`, and `js/i18n.js` builds every
"Get directions" link from them — the contact card, the strip under the map, and the
footer address, all marked `data-contact-map`.

The embedded map is **Google Maps** (`output=embed`, no API key). `js/i18n.js` rebuilds
its `src` from the same coordinates and appends `hl=tr` / `hl=en`, so the map's own
controls follow the chosen language.

The iframe in `index.html` also carries the coordinates literally, as a no-JS fallback.
That duplication is checked automatically rather than trusted — the verify script fails if
the iframe and the JSON disagree — but if you move the pin, update both:

```
i18n/en.json + i18n/tr.json   contact.mapLat / contact.mapLng
index.html                    the map iframe src:  maps?q=<lat>,<lng>
```

The map is pinned by **coordinates, not by place name**, on purpose: the nearest Google
place at that spot is a school (see the checklist), and querying it by name would label
the residence with the school's name.

> **Privacy note.** A Google Maps iframe sets cookies and contacts Google as soon as the
> page loads. If you add a KVKK/GDPR cookie banner, this is the embed it needs to cover.
> For a no-cookie alternative, OpenStreetMap takes the same coordinates:
> `https://www.openstreetmap.org/export/embed.html?bbox=<l>,<b>,<r>,<t>&layer=mapnik&marker=<lat>,<lng>`

---

## Brand assets

```
assets/brand/logo-source.webp   the original file, untouched — keep it
assets/brand/logo.png           gold on transparent, 640px — used in the page
assets/brand/logo-sm.png        the same at 240px
assets/brand/logo-dark.png      solid bronze silhouette, for LIGHT backgrounds
assets/brand/favicon.png        64px, badge on a charcoal rounded square
assets/brand/apple-touch-icon.png  180px
```

The supplied logo is gold artwork on a near-black background with no alpha channel. It was
keyed to transparency by deriving alpha from luminance and un-multiplying the colour, which
is exact for artwork composited on black.

**The gold only works on dark.** Measured against the page's own surfaces, the logo gold is
7.43:1 on the charcoal ink but **2.28:1 on the cream** — nowhere near legible. That single
fact drives three decisions you should not undo casually:

1. The **header stays charcoal at every scroll position** (it used to turn cream). See the
   comment at the top of `css/_header.css`.
2. The **footer and testimonials stay dark**, which is where the badge and the bright gold
   live.
3. The body accent is **not** the literal logo gold. `--c-accent` is a deepened antique gold
   (`#8A6524`) chosen to pass WCAG AA as text on both light surfaces — 5.00:1 on cream,
   4.59:1 on sand. The literal gold is a separate token, `--c-gold`, reserved for dark
   surfaces only. Both are documented in `css/_foundation.css`.

If you ever need the mark on a light background, use `logo-dark.png`.

---

## Replacing the placeholder images

Every photo is currently a direct Unsplash URL and is marked in the HTML with:

```html
<!-- PLACEHOLDER IMAGE: replace with real property photo -->
```

Search `index.html` for `PLACEHOLDER IMAGE` to find all of them — 7 remain, since the
brand logo is now real. Each is a single `src` on a single `<img>`; replacing one is a
one-line edit.

**Recommended workflow for real photography:**

1. Drop the files into `assets/images/`.
2. Replace each `src="https://images.unsplash.com/…"` with `src="assets/images/your-photo.jpg"`.
3. Keep the `width`/`height` attributes accurate — they reserve layout space and prevent
   the page from jumping while images load.
4. Update the matching `alt` text in **both** JSON files (the `alt` values are translated
   via `data-i18n-attr="alt:…"`).

| Where | Count | What to shoot |
|---|---|---|
| Hero | 1 | Wide, landscape. Building exterior or a lifestyle shot in a common area. Leave the left third relatively uncluttered — the headline sits there. Also used as the social preview (`og:image`). |
| Rooms | 3 | One per room type: single, twin, triple. Shoot 4:3, tidy, daylight. |
| About | 1 | Portrait crop, 4:5. Students or staff, not an empty room. |
| Gallery | 8 | Lounge, lounge corner, study desk, kitchen, study lounge, gym, exterior, bathroom. **Shape matters:** on desktop items 1 and 6 render tall (portrait crop) and items 3 and 7 render wide (landscape crop) — see the tiling note at the top of `_gallery.css` before reordering. |

The `og:image` in `<head>` is separate from the hero `<img>` — update both.

### University logos

All six are in place, taken from the supplied asset pack and prepared for the web
(cropped to artwork, downscaled to a 200px long edge, palette-encoded where safe —
~700 KB of source down to 140 KB total):

```
assets/logos/gelisim.png     İstanbul Gelişim
assets/logos/beykent.png     Beykent
assets/logos/aydin.png       İstanbul Aydın
assets/logos/arel.png        İstanbul Arel
assets/logos/biruni.png      Biruni
assets/logos/bahcesehir.png  Bahçeşehir (the İstanbul mark, NOT one of the Cyprus files)
```

If a file is ever missing, its `<img>` removes itself via `onerror` and the card falls back
to a monogram tile, so there are never broken-image icons. See `assets/logos/README.md`
for replacement requirements and why the logo well is 92×64px rather than square.

> Note: university logos are trademarks. Get permission before publishing them.

---

## The inquiry form

Client-side validated (name, phone, email, residence choice), then handed to the visitor's
mail client via `mailto:`. **There is no backend.**

To connect one, see the block marked `// TODO: connect to backend` in `js/main.js`. Replace
the `mailto:` hand-off with a `fetch()` POST; leave the validation and the status messages
above it alone. Status strings live under `form.*` in the JSON files.

---

## Adding Arabic (or any other language)

The site was built RTL-ready from the start: every layout rule uses CSS **logical
properties** (`margin-inline-start`, `inset-inline-end`, `padding-block`) instead of
left/right, and directional elements (nav underlines, link arrows, the hero scrim, the
lightbox arrows) already have `[dir="rtl"]` overrides. Adding a language is three steps
and no rewrite:

1. `cp i18n/en.json i18n/ar.json` and translate the values.
2. In `js/i18n.js`, uncomment / add the entry in `LOCALES`:
   ```js
   ar: { label: "عربي", short: "AR", dir: "rtl", htmlLang: "ar" }
   ```
3. Add a button to any `.lang-switch` group:
   ```html
   <button type="button" class="lang-switch__btn" data-lang="ar" lang="ar">AR</button>
   ```

`i18n.js` sets `<html lang>` and `<html dir>` from the locale entry, and the page mirrors
itself. An Arabic webfont is already stubbed in `_foundation.css` under `[dir="rtl"] body`
— point it at whichever face you license.

---

## Design system, briefly

- **Palette.** Warm-neutral base (`--c-cream`, `--c-sand`) with **one** accent: antique
  gold taken from the logo (`--c-accent: #8A6524` on light, `--c-gold: #C9A227` on dark —
  see Brand assets for why there are two). Charcoal (`--c-ink`) carries the header,
  testimonials and footer. `--c-forest` survives for exactly one thing: the WhatsApp
  button, where a green reads as the platform.
- **Type.** Fraunces (variable serif) for display, Inter for UI and body. Committed
  pairing — don't add a third family. Sizes are fluid `clamp()` values, so there are no
  typography media queries.
- **Motion.** Fade-and-rise on scroll (`[data-reveal]`, driven by `IntersectionObserver`),
  plus hover transitions. No animation libraries. Everything respects
  `prefers-reduced-motion`, and content is visible without JS.
- **Breakpoints are measured, not guessed.** The room grid goes 2-up at 800px and
  3-up at 1240px because that is where a card is finally wide enough to hold the
  price block and the Apply button on one line *in Turkish* — "BAŞLANGIÇ" is
  meaningfully longer than "FROM". If you shorten `rooms.priceFrom`, or change the
  card padding, re-check those two breakpoints in both languages. The same logic is
  commented inline in `_rooms.css` and `_gallery.css`.

---

## Accessibility notes

- Skip link, landmark elements, and a visible focus ring on every interactive element.
- Residence tabs implement the full ARIA tab pattern (arrow keys, Home/End, roving
  `tabindex`); arrow direction follows the text direction.
- FAQ accordion uses `aria-expanded` / `aria-controls` with arrow-key navigation.
- Lightbox is a modal dialog with Escape to close, arrow keys to navigate, and a focus
  trap.
- Language switchers are keyboard-operable and expose `aria-pressed`.
- Alt text is translated along with the rest of the copy.
- Form errors are tied to their inputs and set `aria-invalid`; the status message is an
  `aria-live` region.

---

## Before launch — checklist

Done since the first build: real logo and brand identity, real phone/WhatsApp/email,
Avcılar location and travel times, all six university logos, female-only structure.

- [ ] Replace the remaining placeholder photos (`grep -c "PLACEHOLDER IMAGE" index.html rooms.html`)
- [ ] **Ask the client for the original building photograph.** The price poster contains a
      real night shot of the building with its signage, but only at 443x418px with the logo
      across it — too small to use. The full-resolution original would beat every stock photo
      on the site, starting with the hero
- [ ] Confirm prices are **per person** (assumed from the poster's falling rate), and that
      the single room really is "1 peşin + 10 taksit" while the others are +9 — that asymmetry
      is printed on the poster and may be a typo
- [ ] Two homepage facilities were replaced because the poster contradicted or omitted them:
      "breakfast **and dinner**" became breakfast only, and the gym and study lounges gave way
      to hotel-style rooms and the video tour. Add them back if the building really has them
- [ ] Real testimonials — currently sample copy; remove `test.note` once replaced
- [ ] Confirm the trust-bar figures: `500+` students and `since 2013` are placeholders
      built around the logo's date; the curfew times in `faq.6.a` are assumed too
- [ ] Verify university travel times against current İETT/Metrobüs schedules
- [ ] Sanity-check the pin itself: both Google links you sent resolve to **Özel Nilgün
      Eroğlu Ortaokul**, a school. If the residence is on that campus this is right; if the
      school was only a nearby landmark, move `contact.mapLat` / `mapLng` (and the iframe)
- [ ] Register the domain, then add `<link rel="canonical">` and point the `og:` tags at it
- [ ] Real Privacy / Terms pages (footer links are `#`) and real social URLs
- [ ] Connect the inquiry form to a backend, or confirm `mailto:` is acceptable
- [ ] Get written permission for the six university logos, or keep monograms
