#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the six SEO landing pages.

Same approach as build-rooms-page.py: the icon sprite, header, drawer, footer
and WhatsApp button are lifted straight out of index.html, so the shell cannot
drift. Each page then renders its own prose from i18n/*.json plus a selection
of shared factual blocks -- universities, room rates, facilities -- built from
the same data the homepage renders, so a price or a travel time can never say
one thing here and another thing there.

Two things worth knowing:

* Every generated string carries a data-i18n key. Without them the page came
  out half English (the keyed H1) and half Turkish (the unkeyed section
  headings) as soon as a visitor's browser asked for English.

* The pages live in directories (istanbul-kiz-yurdu/index.html) to give clean
  trailing-slash URLs, so every path in the lifted shell has to become
  root-absolute. relink() does that.

    python tools/build-seo-pages.py
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

NL = chr(10)

html = io.open("index.html", encoding="utf-8").read()
TR = json.loads(io.open("i18n/tr.json", encoding="utf-8").read())

# Inline fallbacks are Turkish here, unlike the rest of the site: these pages
# target Turkish queries, so the copy a crawler sees before JavaScript runs
# must be the Turkish copy.
D = TR
SEO = D["seo"]
C = SEO["common"]

try:
    ORIGIN = (json.load(io.open("site.config.json", encoding="utf-8"))
              .get("origin") or "").rstrip("/")
except (IOError, ValueError):
    ORIGIN = ""

PAGES = [
    ("istanbul-kiz-yurdu",
     ["location", "transport", "rooms", "facilities"], ["1", "2", "4"],
     ["istanbul-kiz-ogrenci-yurdu", "guvenli-kiz-yurdu-istanbul", "kiz-yurdu-fiyatlari"]),
    ("istanbul-ogrenci-yurdu",
     ["rooms", "included", "facilities"], ["2", "3", "5"],
     ["istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari", "universitelere-yakin-kiz-yurdu"]),
    ("istanbul-kiz-ogrenci-yurdu",
     ["security", "facilities", "rooms"], ["4", "6", "1"],
     ["guvenli-kiz-yurdu-istanbul", "istanbul-kiz-yurdu", "universitelere-yakin-kiz-yurdu"]),
    ("guvenli-kiz-yurdu-istanbul",
     ["security", "location"], ["4", "6", "5"],
     ["istanbul-kiz-ogrenci-yurdu", "istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari"]),
    ("universitelere-yakin-kiz-yurdu",
     ["universities", "transport", "location"], ["1", "2"],
     ["istanbul-ogrenci-yurdu", "istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari"]),
    ("kiz-yurdu-fiyatlari",
     ["rates", "included"], ["3", "5", "2"],
     ["istanbul-ogrenci-yurdu", "istanbul-kiz-yurdu", "guvenli-kiz-yurdu-istanbul"]),
]

# One real photograph per page, chosen for what the page is about. The alt text
# is the alt already written for that photograph elsewhere on the site, so no
# photograph gets described twice, differently.
LEAD = {
    "istanbul-kiz-yurdu":             ("assets/images/hero.webp", "hero.imageAlt", 1717, 916),
    "istanbul-ogrenci-yurdu":         ("assets/images/room-double-3.jpg", "rooms.f2.alt", 1050, 1400),
    "istanbul-kiz-ogrenci-yurdu":     ("assets/images/corridor.jpg", "gallery.1.alt", 1050, 1400),
    "guvenli-kiz-yurdu-istanbul":     ("assets/images/hero.webp", "hero.imageAlt", 1717, 916),
    "universitelere-yakin-kiz-yurdu": ("assets/images/room-doorway.jpg", "gallery.6.alt", 1050, 1400),
    "kiz-yurdu-fiyatlari":            ("assets/images/room-quad-1.webp", "rooms.f4.alt", 1400, 1050),
}

SECURITY_KEYS = ["1", "2", "11", "9"]
FACILITY_KEYS = ["4", "3", "5", "6", "8", "12"]
ROOM_KEYS = ["f1", "f2", "f3", "f4"]
INCLUDED_KEYS = ["inc1", "inc2", "inc3", "inc4", "inc5", "inc6"]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def val(key):
    """Turkish value for a dotted key, used as the inline fallback.

    Numeric segments index into lists (seo.<slug>.intro.0.p.1). JavaScript
    reaches those with node["0"] happily; Python needs the int.
    """
    node = D
    for part in key.split("."):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def T(tag, key, cls=None):
    """An element whose text is translated; fallback text is the TR value."""
    c = ' class="%s"' % cls if cls else ""
    return '<%s%s data-i18n="%s">%s</%s>' % (tag, c, key, esc(val(key)), tag)


# ---------------------------------------------------------------------------
# Shell, lifted from index.html
# ---------------------------------------------------------------------------
def block(start, end, inclusive=True):
    a = html.index(start)
    b = html.index(end, a) + (len(end) if inclusive else 0)
    return html[a:b]


sprite = block('<svg width="0" height="0"', "</svg>")
header = block('<header class="header"', "</header>")
drawer = block('<div class="drawer" id="mobile-drawer"', '<main id="main">', False).rstrip()
footer = block('<footer class="footer">', "</footer>")
fab = block('<a class="wa-fab"', "</a>")


def relink(s):
    """Rewrite the lifted shell for a page one directory deep."""
    s = re.sub(r'href="#(top|rooms|universities|amenities|about|gallery|faq|contact)"',
               lambda m: 'href="/"' if m.group(1) == "top" else 'href="/#%s"' % m.group(1), s)
    s = s.replace('href="rooms.html"', 'href="/rooms.html"')
    s = s.replace('href="index.html"', 'href="/"')
    s = s.replace('src="assets/', 'src="/assets/')
    s = s.replace('href="assets/', 'href="/assets/')
    return s


sprite, header, drawer, footer, fab = (relink(x) for x in
                                       (sprite, header, drawer, footer, fab))

ARROW = ('<svg class="icon icon--sm" aria-hidden="true">'
         '<use href="#i-arrow"></use></svg>')


# ---------------------------------------------------------------------------
# Shared factual blocks -- every value comes from the JSON the site renders
# ---------------------------------------------------------------------------
def section(inner, cls="seo-block"):
    return '        <section class="%s">%s%s%s        </section>' % (cls, NL, inner, NL)


def prose_keyed(h_key, p_keys):
    body = NL.join("          " + T("p", k) for k in p_keys)
    return section("          " + T("h2", h_key) + NL + body)


def link_arrow(href, key):
    return ('          <p><a class="link-arrow" href="%s">%s%s</a></p>'
            % (href, T("span", key), ARROW))


def blk_location():
    return section("          " + T("h2", "seo.common.locationH") + NL +
                   "          " + T("p", "seo.common.locationP") + NL +
                   link_arrow("/#contact", "contact.directions"))


def blk_transport():
    return prose_keyed("seo.common.transportH", ["seo.common.transportP"])


def table(head_keys, rows):
    head = "".join("<th>%s</th>" % T("span", k) for k in head_keys)
    body = NL.join(
        "              <tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r)
        for r in rows)
    return ('          <div class="seo-table-wrap">' + NL +
            '            <table class="seo-table">' + NL +
            '              <thead><tr>' + head + '</tr></thead>' + NL +
            '              <tbody>' + NL + body + NL + '              </tbody>' + NL +
            '            </table>' + NL + '          </div>')


def blk_universities():
    keys = [k for k in sorted(D["uni"])
            if isinstance(D["uni"][k], dict) and "name" in D["uni"][k]]
    rows = [(T("span", "uni.%s.name" % k), T("span", "uni.%s.time" % k)) for k in keys]
    return section("          " + T("h2", "seo.common.universitiesH") + NL +
                   "          " + T("p", "seo.common.universitiesP") + NL +
                   table(["seo.common.tblUni", "seo.common.tblTime"], rows))


def rate_table():
    # "1 + 10" needs no translation, which is why the plan cell is written that
    # way rather than as a sentence with a number substituted into it.
    rows = [(T("span", "rooms.%s.name" % k),
             T("span", "rooms.%s.capacity" % k),
             T("span", "rooms.%s.price" % k),
             "1 + " + esc(D["rooms"][k]["instalments"]))
            for k in ROOM_KEYS]
    return table(["seo.common.tblRoom", "seo.common.tblCap",
                  "seo.common.tblPrice", "seo.common.tblPlan"], rows)


def blk_rooms():
    return section("          " + T("h2", "seo.common.roomsH") + NL +
                   "          " + T("p", "seo.common.roomsP") + NL +
                   rate_table() + NL +
                   link_arrow("/rooms.html", "seo.common.seeRooms"))


def blk_rates():
    return section("          " + T("h2", "seo.common.ratesH") + NL +
                   rate_table() + NL +
                   link_arrow("/rooms.html", "seo.common.seeRooms"))


def amen_list(h_key, keys):
    items = NL.join(
        '            <li>%s %s</li>'
        % (T("strong", "amen.%s.title" % k), T("span", "amen.%s.desc" % k))
        for k in keys)
    return section("          " + T("h2", h_key) + NL +
                   '          <ul class="seo-list">' + NL + items + NL +
                   '          </ul>')


def blk_facilities():
    return amen_list("seo.common.facilitiesH", FACILITY_KEYS)


def blk_security():
    return amen_list("seo.common.securityH", SECURITY_KEYS)


def blk_included():
    items = NL.join('            %s' % T("li", "roomsPage." + k) for k in INCLUDED_KEYS)
    return section("          " + T("h2", "seo.common.includedH") + NL +
                   '          <ul class="seo-chips">' + NL + items + NL +
                   '          </ul>')


BLOCKS = {"location": blk_location, "transport": blk_transport,
          "universities": blk_universities, "rooms": blk_rooms, "rates": blk_rates,
          "facilities": blk_facilities, "security": blk_security,
          "included": blk_included}


def lead_image(slug):
    src, key, w, h = LEAD[slug]
    return ('        <figure class="seo-figure">' + NL +
            '          <img src="/%s" data-i18n-attr="alt:%s" alt="%s"'
            % (src, key, esc(val(key))) + NL +
            '               loading="lazy" decoding="async" width="%d" height="%d" />'
            % (w, h) + NL +
            '        </figure>')


def faq_section(keys):
    items = NL.join(
        '          <details class="seo-faq__item">' + NL +
        '            <summary>' + T("h3", "faq.%s.q" % k) + '</summary>' + NL +
        '            ' + T("p", "faq.%s.a" % k) + NL +
        '          </details>' for k in keys)
    return section("          " + T("h2", "seo.common.faqH") + NL + items,
                   "seo-block seo-faq")


def related_section(slugs):
    items = NL.join(
        '            <li><a href="/%s/" data-i18n="seo.%s.navLabel">%s</a></li>'
        % (s, s, esc(SEO[s]["navLabel"])) for s in slugs)
    return section("          " + T("h2", "seo.common.relatedH") + NL +
                   '          <ul class="seo-list seo-list--plain">' + NL +
                   items + NL + '          </ul>',
                   "seo-block seo-related")


def cta_section():
    wa = ('            <a class="btn btn--primary" href="https://wa.me/%s" data-contact-wa '
          'target="_blank" rel="noopener" data-i18n="seo.common.ctaWa">%s</a>'
          % (esc(D["contact"]["waNumber"]), esc(C["ctaWa"])))
    form = ('            <a class="btn btn--ghost" href="/#contact" '
            'data-i18n="seo.common.ctaForm">%s</a>' % esc(C["ctaForm"]))
    return section("          " + T("h2", "seo.common.ctaH") + NL +
                   "          " + T("p", "seo.common.ctaP") + NL +
                   '          <div class="seo-cta__actions">' + NL +
                   wa + NL + form + NL + '          </div>',
                   "seo-block seo-cta")


def schema(slug, faq_keys):
    url = "%s/%s/" % (ORIGIN, slug) if ORIGIN else ""
    crumb2 = {"@type": "ListItem", "position": 2, "name": SEO[slug]["h1"]}
    if url:
        crumb2["item"] = url
    graph = [{
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": C["breadcrumbHome"],
             "item": (ORIGIN + "/") if ORIGIN else "/"},
            crumb2,
        ],
    }]
    if faq_keys:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": D["faq"][k]["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": D["faq"][k]["a"]}}
                for k in faq_keys
            ],
        })
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph},
                         ensure_ascii=False, indent=2)
    return ('  <script type="application/ld+json">' + NL +
            NL.join("  " + ln for ln in payload.split(NL)) + NL + '  </script>')


TEMPLATE = u'''<!DOCTYPE html>
<!-- GENERATED by tools/build-seo-pages.py -- do not edit by hand.
     Copy lives in i18n/tr.json and i18n/en.json under seo.%(slug)s -->
<html lang="tr" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title data-i18n="seo.%(slug)s.title">%(title)s</title>
  <meta name="description" data-i18n-attr="content:seo.%(slug)s.description"
        content="%(description)s" />
  <meta name="theme-color" content="#191411" />
  <meta name="robots" content="index, follow" />
%(canonical)s
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Kıvanç Kız Yurdu" />
  <meta property="og:title" data-i18n-attr="content:seo.%(slug)s.title" content="%(title)s" />
  <meta property="og:description" data-i18n-attr="content:seo.%(slug)s.description"
        content="%(description)s" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:locale:alternate" content="en_US" />
%(ogurl)s
%(schema)s

  <link rel="icon" type="image/png" sizes="64x64" href="/assets/brand/favicon.png" />
  <link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="/css/main.css" />
</head>

<body class="page-seo">
  <a class="skip-link" href="#main" data-i18n="a11y.skipToContent">İçeriğe geç</a>

%(sprite)s

%(header)s

%(drawer)s

  <main id="main">
    <article class="seo-page">
      <div class="container">

        <nav class="crumbs" data-i18n-attr="aria-label:seo.common.breadcrumbLabel" aria-label="%(crumbLabel)s">
          <ol>
            <li><a href="/" data-i18n="seo.common.breadcrumbHome">%(crumbHome)s</a></li>
            <li aria-current="page" data-i18n="seo.%(slug)s.h1">%(h1)s</li>
          </ol>
        </nav>

        <header class="seo-hero">
          <h1 data-i18n="seo.%(slug)s.h1">%(h1)s</h1>
          <p class="seo-hero__lede" data-i18n="seo.%(slug)s.lede">%(lede)s</p>
        </header>

%(body)s

      </div>
    </article>
  </main>

%(footer)s

%(fab)s

  <!-- These pages target Turkish queries, so they open in Turkish unless the
       visitor has chosen otherwise, rather than following the browser. Without
       it a crawler asking for en-US reads English body copy under a Turkish
       <title>, which is exactly the mismatch that sinks a landing page. -->
  <script>window.__LANG_DEFAULT = "tr";</script>
  <script src="/i18n/bundle.js"></script>
  <script src="/js/i18n.js"></script>
  <script src="/js/main.js"></script>
</body>
</html>
'''


def build(slug, blocks, faq_keys, related):
    page = SEO[slug]
    body = [lead_image(slug)]

    for i, sec in enumerate(page.get("intro", [])):
        body.append(prose_keyed(
            "seo.%s.intro.%d.h" % (slug, i),
            ["seo.%s.intro.%d.p.%d" % (slug, i, j) for j in range(len(sec["p"]))]))

    for name in blocks:
        body.append(BLOCKS[name]())

    if "close" in page:
        body.append(prose_keyed(
            "seo.%s.close.h" % slug,
            ["seo.%s.close.p.%d" % (slug, j) for j in range(len(page["close"]["p"]))]))

    if faq_keys:
        body.append(faq_section(faq_keys))
    body.append(cta_section())
    body.append(related_section(related))

    canonical = ogurl = ""
    if ORIGIN:
        url = "%s/%s/" % (ORIGIN, slug)
        canonical = '  <link rel="canonical" href="%s" />%s' % (url, NL)
        ogurl = ('  <meta property="og:url" content="%s" />' % url + NL +
                 '  <meta property="og:image" content="%s/assets/images/og-card.jpg" />' % ORIGIN + NL +
                 '  <meta property="og:image:width" content="1200" />' + NL +
                 '  <meta property="og:image:height" content="630" />')

    out = TEMPLATE % {
        "slug": slug,
        "title": esc(page["title"]),
        "description": esc(page["description"]),
        "h1": esc(page["h1"]),
        "lede": esc(page["lede"]),
        "canonical": canonical,
        "ogurl": ogurl,
        "schema": schema(slug, faq_keys),
        "sprite": sprite, "header": header, "drawer": drawer,
        "footer": footer, "fab": fab,
        "crumbHome": esc(C["breadcrumbHome"]),
        "crumbLabel": esc(C["breadcrumbLabel"]),
        "body": (NL + NL).join(body),
    }

    if not os.path.isdir(slug):
        os.makedirs(slug)
    io.open(os.path.join(slug, "index.html"), "w", encoding="utf-8").write(out)
    return out


def main():
    for slug, blocks, faqs, related in PAGES:
        out = build(slug, blocks, faqs, related)
        print("  %-34s %2d blocks, %d FAQ, %3d i18n keys, %.1f KB"
              % (slug + "/", len(blocks), len(faqs),
                 out.count("data-i18n"), len(out) / 1024.0))
    print("%d SEO pages written%s" % (len(PAGES),
          "" if ORIGIN else "  (no origin set: canonical/og:url omitted)"))


if __name__ == "__main__":
    main()
