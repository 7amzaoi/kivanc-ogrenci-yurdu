#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate rooms.html.

The site has no build step and no templating, so a second page would normally
mean copy-pasting the header, drawer, icon sprite and footer and then keeping
four copies of them in step by hand. Instead this script lifts those blocks
straight out of index.html and writes rooms.html around them, so the shell is
identical by construction.

Run it after changing anything in index.html's header, drawer, sprite or
footer, or after editing room copy in i18n/*.json:

    python tools/build-rooms-page.py

The verify script fails if rooms.html is out of date with respect to either.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

html = io.open("index.html", encoding="utf-8").read()
en = json.loads(io.open("i18n/en.json", encoding="utf-8").read())
R, P = en["rooms"], en["roomsPage"]


def block(start_marker, end_marker, inclusive_end=True):
    a = html.index(start_marker)
    b = html.index(end_marker, a) + (len(end_marker) if inclusive_end else 0)
    return html[a:b]


sprite = block('<svg width="0" height="0"', "</svg>")
header = block('<header class="header"', "</header>")
drawer = block('<div class="drawer" id="mobile-drawer"', "<main id=\"main\">", False).rstrip()
footer = block('<footer class="footer">', "</footer>")
fab = block('<a class="wa-fab"', "</a>")

# In-page anchors have to reach back to the homepage from a subpage.
def relink(s):
    s = re.sub(r'href="#(top|rooms|universities|amenities|about|gallery|faq|contact)"',
               lambda m: 'href="index.html#%s"' % m.group(1)
               if m.group(1) != "top" else 'href="index.html"', s)
    # the Rooms entry now has a page of its own
    s = s.replace('href="index.html#rooms" data-i18n="nav.rooms"',
                  'href="rooms.html" aria-current="page" data-i18n="nav.rooms"')
    return s


header, drawer, footer = relink(header), relink(drawer), relink(footer)

PHOTOS = {
    "f1": ("photo-1595526114035-0d45ed16cfbf", "single room"),
    "f2": ("photo-1631049307264-da0ec9d70304", "double room"),
    "f3": ("photo-1555854877-bab0e564b8d5", "triple room"),
    "f4": ("photo-1540518614846-7eded433c457", "quad room"),
}
CHIPS = [("i-wifi", "wifi"), ("i-tv", "tv"), ("i-fridge", "fridge"), ("i-bath", "ensuite")]
INCLUDED = [("i-coffee", "inc1"), ("i-wifi", "inc2"), ("i-sparkle", "inc3"),
            ("i-bath", "inc4"), ("i-shield", "inc5"), ("i-laundry", "inc6")]
FEATURES = ["feat1", "feat2", "feat3", "feat4"]


def room_row(key, i):
    r = R[key]
    pid, label = PHOTOS[key]
    chips = "\n".join(
        '            <li><svg class="icon icon--sm" aria-hidden="true"><use href="#%s"></use></svg>'
        '<span data-i18n="rooms.amen.%s">%s</span></li>' % (ic, ak, R["amen"][ak])
        for ic, ak in CHIPS)
    return u'''        <article class="room-row" data-reveal>
          <div class="media media--4x3 room-row__media">
            <!-- PLACEHOLDER IMAGE: replace with real property photo (%s) -->
            <img src="https://images.unsplash.com/%s?auto=format&fit=crop&w=1100&q=80"
                 data-i18n-attr="alt:rooms.%s.alt" alt="%s"
                 loading="lazy" width="1100" height="825" />
          </div>

          <div class="room-row__body">
            <p class="room-row__cap">
              <svg class="icon icon--sm" aria-hidden="true"><use href="#i-users"></use></svg>
              <span data-i18n="rooms.%s.capacity">%s</span>
            </p>
            <h2 class="room-row__title" data-i18n="rooms.%s.name">%s</h2>
            <p class="room-row__desc" data-i18n="rooms.%s.desc">%s</p>

            <ul class="amenity-chips">
%s
            </ul>

            <dl class="rate">
              <div class="rate__cell">
                <dt data-i18n="roomsPage.colMonthly">%s</dt>
                <dd class="rate__value" data-i18n="rooms.%s.price">%s</dd>
                <dd class="rate__note" data-i18n="rooms.priceFrom">%s</dd>
              </div>
              <div class="rate__cell">
                <dt data-i18n="roomsPage.colTerm">%s</dt>
                <dd class="rate__value" data-i18n="rooms.%s.priceTerm">%s</dd>
                <dd class="rate__note" data-i18n="roomsPage.termLength">%s</dd>
              </div>
              <div class="rate__cell">
                <dt data-i18n="roomsPage.colPayment">%s</dt>
                <dd class="rate__plan" data-i18n="rooms.%s.payment">%s</dd>
              </div>
            </dl>

            <div class="room-row__actions">
              <a class="btn" href="index.html#contact" data-i18n="rooms.apply">%s</a>
              <a class="link-arrow" href="#" data-contact-wa target="_blank" rel="noopener">
                <span data-i18n="roomsPage.ctaSecondary">%s</span>
                <svg class="icon icon--sm" aria-hidden="true"><use href="#i-arrow"></use></svg>
              </a>
            </div>
          </div>
        </article>''' % (label, pid, key, r.get("alt", ""), key, r["capacity"], key, r["name"],
                         key, r["desc"], chips, P["colMonthly"], key, r["price"], R["priceFrom"],
                         P["colTerm"], key, r["priceTerm"], P["termLength"], P["colPayment"],
                         key, r["payment"], R["apply"], P["ctaSecondary"])


rows = "\n\n".join(room_row(k, i) for i, k in enumerate(("f1", "f2", "f3", "f4")))

table_rows = "\n".join(
    u'''              <tr>
                <th scope="row" data-i18n="rooms.%s.name">%s</th>
                <td data-i18n="rooms.%s.price">%s</td>
                <td data-i18n="rooms.%s.priceTerm">%s</td>
                <td data-i18n="rooms.%s.payment">%s</td>
              </tr>''' % (k, R[k]["name"], k, R[k]["price"], k, R[k]["priceTerm"], k, R[k]["payment"])
    for k in ("f1", "f2", "f3", "f4"))

features = "\n".join(
    u'''          <li class="feature" data-reveal>
            <svg class="icon feature__icon" aria-hidden="true"><use href="#i-check"></use></svg>
            <span data-i18n="roomsPage.%s">%s</span>
          </li>''' % (f, P[f]) for f in FEATURES)

included = "\n".join(
    u'''          <li class="included__item" data-reveal>
            <svg class="icon icon--lg included__icon" aria-hidden="true"><use href="#%s"></use></svg>
            <span data-i18n="roomsPage.%s">%s</span>
          </li>''' % (ic, k, P[k]) for ic, k in INCLUDED)

page = u'''<!DOCTYPE html>
<!-- AUTO-GENERATED by tools/build-rooms-page.py — do not edit by hand.
     The header, drawer, icon sprite and footer are lifted from index.html so
     the two pages cannot drift apart. Edit those in index.html, the copy in
     i18n/*.json, then re-run the script. -->
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title data-i18n="roomsPage.metaTitle">%(metaTitle)s</title>
  <meta name="description" data-i18n-attr="content:roomsPage.metaDescription"
        content="%(metaDescription)s" />
  <meta name="theme-color" content="#191411" />
  <meta name="robots" content="index, follow" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Kıvanç Öğrenci Yurdu" />
  <meta property="og:title" data-i18n-attr="content:roomsPage.metaTitle" content="%(metaTitle)s" />
  <meta property="og:description" data-i18n-attr="content:roomsPage.metaDescription"
        content="%(metaDescription)s" />

  <link rel="icon" type="image/png" sizes="64x64" href="assets/brand/favicon.png" />
  <link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="css/main.css" />
</head>

<body class="page-rooms">
  <a class="skip-link" href="#main" data-i18n="a11y.skipToContent">Skip to content</a>

%(sprite)s

%(header)s

%(drawer)s

  <main id="main">

    <!-- ================================================================
         PAGE HEAD
         ================================================================ -->
    <section class="page-head">
      <div class="container">
        <a class="page-head__back link-arrow link-arrow--back" href="index.html">
          <svg class="icon icon--sm" aria-hidden="true"><use href="#i-arrow"></use></svg>
          <span data-i18n="roomsPage.backHome">%(backHome)s</span>
        </a>
        <p class="eyebrow eyebrow--light" data-i18n="roomsPage.eyebrow">%(eyebrow)s</p>
        <h1 class="page-head__title" data-i18n="roomsPage.title">%(title)s</h1>
        <p class="page-head__lede" data-i18n="roomsPage.lede">%(lede)s</p>

        <ul class="page-stats">
          <li><span class="page-stats__value">45</span><span class="page-stats__label" data-i18n="roomsPage.statRooms">%(statRooms)s</span></li>
          <li><span class="page-stats__value">4</span><span class="page-stats__label" data-i18n="roomsPage.statTypes">%(statTypes)s</span></li>
          <li><span class="page-stats__value">10</span><span class="page-stats__label" data-i18n="roomsPage.statTerm">%(statTerm)s</span></li>
        </ul>
      </div>
    </section>

    <!-- ================================================================
         ROOM TYPES
         ================================================================ -->
    <section class="section room-rows">
      <div class="container">
%(rows)s

        <p class="rooms__disclaimer" data-reveal data-i18n="rooms.disclaimer">%(disclaimer)s</p>
      </div>
    </section>

    <!-- ================================================================
         PRICE TABLE
         ================================================================ -->
    <section class="section section--sand rates">
      <div class="container container--tight">
        <div class="section-head" data-reveal>
          <p class="eyebrow" data-i18n="roomsPage.eyebrow">%(eyebrow)s</p>
          <h2 data-i18n="roomsPage.tableTitle">%(tableTitle)s</h2>
        </div>

        <div class="rate-table__wrap" data-reveal>
          <table class="rate-table">
            <thead>
              <tr>
                <th scope="col" data-i18n="roomsPage.colRoom">%(colRoom)s</th>
                <th scope="col" data-i18n="roomsPage.colMonthly">%(colMonthly)s</th>
                <th scope="col" data-i18n="roomsPage.colTerm">%(colTerm)s</th>
                <th scope="col" data-i18n="roomsPage.colPayment">%(colPayment)s</th>
              </tr>
            </thead>
            <tbody>
%(table_rows)s
            </tbody>
          </table>
        </div>
        <p class="rate-table__note" data-reveal data-i18n="roomsPage.perPersonNote">%(perPersonNote)s</p>
      </div>
    </section>

    <!-- ================================================================
         ROOM FEATURES
         ================================================================ -->
    <section class="section features">
      <div class="container">
        <div class="section-head" data-reveal>
          <p class="eyebrow" data-i18n="roomsPage.eyebrow">%(eyebrow)s</p>
          <h2 data-i18n="roomsPage.featuresTitle">%(featuresTitle)s</h2>
          <p class="section-head__lede" data-i18n="roomsPage.featuresLede">%(featuresLede)s</p>
        </div>
        <ul class="feature-list">
%(features)s
        </ul>
      </div>
    </section>

    <!-- ================================================================
         INCLUDED IN THE PRICE
         ================================================================ -->
    <section class="section section--ink included">
      <div class="container">
        <div class="section-head" data-reveal>
          <p class="eyebrow eyebrow--light" data-i18n="roomsPage.eyebrow">%(eyebrow)s</p>
          <h2 data-i18n="roomsPage.includedTitle">%(includedTitle)s</h2>
          <p class="section-head__lede" data-i18n="roomsPage.includedLede">%(includedLede)s</p>
        </div>
        <ul class="included__grid">
%(included)s
        </ul>
      </div>
    </section>

    <!-- ================================================================
         VIDEO TOUR + CTA
         ================================================================ -->
    <section class="section section--sand room-cta">
      <div class="container">
        <div class="room-cta__grid">
          <div class="room-cta__card" data-reveal>
            <svg class="icon icon--lg room-cta__icon" aria-hidden="true"><use href="#i-camera"></use></svg>
            <h2 class="room-cta__title" data-i18n="roomsPage.videoTitle">%(videoTitle)s</h2>
            <p data-i18n="roomsPage.videoLede">%(videoLede)s</p>
            <a class="btn btn--ghost" href="#" data-contact-wa target="_blank" rel="noopener"
               data-i18n="roomsPage.videoCta">%(videoCta)s</a>
          </div>

          <div class="room-cta__card room-cta__card--accent" data-reveal style="--reveal-delay:80ms">
            <h2 class="room-cta__title" data-i18n="roomsPage.ctaTitle">%(ctaTitle)s</h2>
            <p data-i18n="roomsPage.ctaLede">%(ctaLede)s</p>
            <div class="room-cta__actions">
              <a class="btn btn--light" href="index.html#contact" data-i18n="roomsPage.ctaPrimary">%(ctaPrimary)s</a>
              <a class="link-arrow link-arrow--light" href="#" data-contact-wa target="_blank" rel="noopener">
                <span data-i18n="roomsPage.ctaSecondary">%(ctaSecondary)s</span>
                <svg class="icon icon--sm" aria-hidden="true"><use href="#i-arrow"></use></svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

%(footer)s

  %(fab)s

  <script src="i18n/bundle.js"></script>
  <script src="js/i18n.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
''' % dict(P, sprite=sprite, header=header, drawer=drawer, footer=footer, fab=fab,
           rows=rows, table_rows=table_rows, features=features, included=included,
           disclaimer=R["disclaimer"])

io.open("rooms.html", "w", encoding="utf-8").write(page)
print("rooms.html written: %d room rows, %d table rows, %.1f KB"
      % (page.count('<article class="room-row"'), page.count("<th scope=\"row\""),
         os.path.getsize("rooms.html") / 1024.0))
