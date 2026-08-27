# -*- coding: utf-8 -*-
"""Static integrity checks: i18n parity, fallback drift, CSS, asset refs."""
import io, re, json, os, sys, glob

# Runnable from anywhere: the generators all chdir to the repo root, and so
# does this, so `python tools/verify.py` works from any directory.
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fail = []
SEO_SLUGS = ["istanbul-kiz-yurdu", "istanbul-ogrenci-yurdu",
             "istanbul-kiz-ogrenci-yurdu", "guvenli-kiz-yurdu-istanbul",
             "universitelere-yakin-kiz-yurdu", "kiz-yurdu-fiyatlari"]
PAGES = (["index.html", "rooms.html"] +
         [s + "/index.html" for s in SEO_SLUGS])
pages = {f: io.open(f, encoding="utf-8").read() for f in PAGES}
html = chr(10).join(pages.values())

# Markup inside an HTML comment is not on the page. The withheld
# testimonials block would otherwise report its classes as unstyled and its
# i18n keys as used -- neither is true while it stays commented out.
live = re.sub(r"<!--.*?-->", "", html, flags=re.S)
en = json.loads(io.open("i18n/en.json", encoding="utf-8").read())
tr = json.loads(io.open("i18n/tr.json", encoding="utf-8").read())


def flat(o, p="", out=None):
    """Flatten to dotted keys, indexing lists as well as objects.

    seo.<slug>.intro is a list, so its entries only have keys at all if the
    numeric index is walked -- without this the parity check reported thirty
    keys as missing from both languages while they sat in both files."""
    if out is None:
        out = {}
    items = enumerate(o) if isinstance(o, list) else o.items()
    for k, v in items:
        key = "%s.%s" % (p, k) if p else str(k)
        if isinstance(v, (dict, list)):
            flat(v, key, out)
        else:
            out[key] = v
    return out


fen, ftr = flat(en), flat(tr)

# --- keys referenced anywhere -------------------------------------------
used = set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', live))
for m in re.findall(r'data-i18n-attr="([^"]+)"', live):
    for pair in m.split(";"):
        if ":" in pair:
            used.add(pair.split(":", 1)[1].strip())
js = io.open("js/main.js", encoding="utf-8").read()
used |= set(re.findall(r'\bt\("([a-zA-Z0-9_.]+)"\)', js))
used |= set(re.findall(r'I18N\.t\("([a-zA-Z0-9_.]+)"\)', js))
used |= set(re.findall(r'"(form\.room[A-Za-z]+)"', js))

miss_en = sorted(k for k in used if k not in fen)
miss_tr = sorted(k for k in used if k not in ftr)
only_en = sorted(k for k in fen if k not in ftr)
only_tr = sorted(k for k in ftr if k not in fen)
unused = sorted(k for k in fen if k not in used and "_comment" not in k)

print("i18n: %d keys used | en %d | tr %d" % (len(used), len(fen), len(ftr)))
for label, lst in (("missing in en", miss_en), ("missing in tr", miss_tr),
                   ("in en not tr", only_en), ("in tr not en", only_tr)):
    if lst:
        fail.append("%s: %s" % (label, lst))
        print(("  *** %s: %s" % (label, lst)).encode("ascii","replace").decode())
print("  defined but unused (dynamic keys expected): %s" % (unused or "none"))

# --- inline fallback drift ----------------------------------------------
TAGS = "h1|h2|h3|h4|p|span|a|button|blockquote|title|label|legend|li"
pat = re.compile(r'<(%s)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>([^<]*)</\1>' % TAGS)
# Each page is compared against ITS OWN language, not always English: the SEO
# landing pages ship Turkish inline fallbacks on purpose, because they target
# Turkish queries and that is what a crawler reads before JavaScript runs.
def page_dict(doc):
    m = re.search(r'<html[^>]*\blang="([a-z]{2})"', doc)
    return ftr if (m and m.group(1) == "tr") else fen


drift = []
checked = 0
for _page, _doc in pages.items():
    ref = page_dict(_doc)
    for tag, key, inline in pat.findall(_doc):
        exp = ref.get(key)
        if exp is None:
            continue
        checked += 1
        a = re.sub(r"\s+", " ", inline).replace("&amp;", "&").strip()
        b = re.sub(r"\s+", " ", exp).strip()
        if a != b:
            drift.append((key, a[:40], b[:40]))
print("inline fallbacks: %d checked, %d drifted" % (checked, len(drift)))
for d in drift:
    fail.append("drift %s" % (d,))
    print(("  *** %s  page=%r json=%r" % d).encode("ascii","replace").decode())

# --- inline data-i18n-attr fallback drift --------------------------------
# alt / aria-label / content / placeholder fallbacks are what crawlers and
# social scrapers see permanently, since they mostly do not run JavaScript.
# The text check above never covered them, and they had drifted 21 ways.
ATTR_EXEMPT = {"roomsPage.photoOf"}          # generator appends an index
ATAG = re.compile(r'<[a-zA-Z][^>]*\bdata-i18n-attr="([^"]+)"[^>]*>', re.S)
achecked = 0
for _page, _html in pages.items():
    aref = page_dict(_html)   # same rule as the text check above
    for m in ATAG.finditer(_html):
        tag = m.group(0)
        for pair in m.group(1).split(";"):
            if ":" not in pair:
                continue
            attr, key = (x.strip() for x in pair.strip().split(":", 1))
            if key in ATTR_EXEMPT or key not in aref:
                continue
            achecked += 1
            am = re.search(r'\s\b%s="([^"]*)"' % re.escape(attr), tag)
            if not am:
                fail.append("%s: %s has no inline %s=" % (_page, key, attr))
                print("  *** %s: %s has no inline %s=" % (_page, key, attr))
                continue
            got = re.sub(r"\s+", " ", am.group(1)).replace("&amp;", "&").strip()
            want = re.sub(r"\s+", " ", aref[key]).strip()
            if got != want:
                fail.append("attr drift %s/%s" % (_page, key))
                print(("  *** attr drift %s %s | page=%r json=%r"
                       % (_page, key, got[:60], want[:60])).encode("ascii", "replace").decode())
print("inline attribute fallbacks: %d checked" % achecked)
if achecked < 60:
    fail.append("attribute-fallback check matched only %d tags" % achecked)
    print("  *** attribute-fallback check matched almost nothing -- regex broken?")

# --- assets referenced by the page exist ---------------------------------
refs = set(re.findall(r'(?:src|href)="((?:assets|css|js|i18n)/[^"]+)"', html))
for r in sorted(refs):
    if not os.path.exists(r):
        fail.append("missing asset %s" % r)
        print("  *** missing asset: %s" % r)
print("local asset refs: %d, all present: %s" % (len(refs), not any("missing asset" in f for f in fail)))

# --- CSS ------------------------------------------------------------------
allcss = ""
for p in sorted(glob.glob("css/*.css")):
    t = io.open(p, encoding="utf-8").read()
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", t)
    if stripped.count("{") != stripped.count("}"):
        fail.append("unbalanced braces in %s" % p)
        print("  *** unbalanced braces: %s" % p)
    if p != "css/main.css":
        allcss += stripped + "\n"
defined = set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", allcss))
usedcls = set()
for m in re.findall(r'class="([^"]+)"', live):
    usedcls.update(m.split())
undef = sorted(c for c in usedcls if c not in defined)
print("CSS: %d classes in markup, %d with no rule: %s" % (len(usedcls), len(undef), undef or "none"))

# dangling custom properties
declared = set(re.findall(r"(--[\w-]+)\s*:", allcss))
# a var() with a fallback is legitimately allowed to be set elsewhere
# (e.g. --reveal-delay comes from an inline style attribute in the markup)
referenced = set(re.findall(r"var\((--[\w-]+)\s*\)", allcss))
dangling = sorted(referenced - declared)
if dangling:
    fail.append("undeclared custom properties: %s" % dangling)
    print("  *** undeclared custom properties: %s" % dangling)
else:
    print("custom properties: every var() resolves")

# --- map iframe fallback coords must match the JSON -----------------------
mm = re.search(r'data-contact-mapframe[\s\S]{0,200}?src="[^"]*?maps\?q=([\d.]+),([\d.]+)', html)
if not mm:
    fail.append("could not find the map iframe coordinates in index.html")
    print("  *** map iframe coordinates not found in index.html")
else:
    got = (mm.group(1), mm.group(2))
    want = (fen.get("contact.mapLat"), fen.get("contact.mapLng"))
    if got != want:
        fail.append("map iframe %s != JSON %s" % (got, want))
        print("  *** map iframe coords %s do not match JSON %s" % (got, want))
    else:
        print("map iframe: coordinates match contact.mapLat/mapLng (%s, %s)" % want)
        if want != (json.loads(io.open("i18n/tr.json", encoding="utf-8").read())["contact"]["mapLat"],
                    json.loads(io.open("i18n/tr.json", encoding="utf-8").read())["contact"]["mapLng"]):
            fail.append("tr.json coordinates differ from en.json")
            print("  *** tr.json coordinates differ from en.json")

# --- generated i18n bundle must match the JSON ---------------------------
import re as _re
bundle_path = "i18n/bundle.js"
if not os.path.exists(bundle_path):
    fail.append("i18n/bundle.js missing - run: python tools/build-i18n.py")
    print("  *** i18n/bundle.js missing")
else:
    raw = io.open(bundle_path, encoding="utf-8").read()
    m = _re.search(r"window\.I18N_BUNDLE\s*=\s*(\{[\s\S]*\});\s*$", raw)
    if not m:
        fail.append("i18n/bundle.js is not in the expected shape")
        print("  *** i18n/bundle.js is not in the expected shape")
    else:
        bundled = json.loads(m.group(1))
        stale = []
        for lang, src in (("en", en), ("tr", tr)):
            if bundled.get(lang) != src:
                stale.append(lang)
        if stale:
            fail.append("bundle.js stale for %s" % stale)
            print("  *** i18n/bundle.js is STALE for %s - run: python tools/build-i18n.py" % stale)
        else:
            print("i18n/bundle.js: in sync with both JSON files")

# --- rooms.html must be current with its generator ------------------------
import subprocess
before = io.open("rooms.html", encoding="utf-8").read()
subprocess.run([sys.executable, "tools/build-rooms-page.py"],
               capture_output=True, check=True)
after = io.open("rooms.html", encoding="utf-8").read()
if before != after:
    fail.append("rooms.html was stale - regenerated")
    print("  *** rooms.html was STALE (regenerated now); commit the new file")
else:
    print("rooms.html: up to date with tools/build-rooms-page.py")

# --- the SEO landing pages must be current too ---------------------------
# Without this the pages drift silently: edit the footer in index.html and
# the six landing pages keep the old one until someone remembers to rebuild.
seo_files = [s + "/index.html" for s in SEO_SLUGS]
seo_before = {f: io.open(f, encoding="utf-8").read() for f in seo_files}
subprocess.run([sys.executable, "tools/build-seo-pages.py"],
               capture_output=True, check=True)
seo_stale = [f for f in seo_files
            if io.open(f, encoding="utf-8").read() != seo_before[f]]
if seo_stale:
    fail.append("SEO pages were stale: %s" % seo_stale)
    print("  *** STALE (regenerated now), commit them: %s" % ", ".join(seo_stale))
else:
    print("SEO pages: %d up to date with tools/build-seo-pages.py" % len(seo_files))

# the checks below must see the regenerated file, not the copy read at startup
pages["rooms.html"] = after

# --- the shared shell must be identical on both pages ---------------------
def shell(doc):
    out = []
    for a, b in (('<header class="header"', "</header>"),
                 ('<footer class="footer">', "</footer>")):
        i = doc.index(a); j = doc.index(b, i) + len(b)
        out.append(doc[i:j])
    return out
ih, ifo = shell(pages["index.html"])
rh, rfo = shell(pages["rooms.html"])
def norm(x):
    # subpage links are rewritten to reach back to the homepage on purpose
    return (x.replace('href="index.html#', 'href="#')
             .replace('href="index.html"', 'href="#top"')
             .replace('href="rooms.html" aria-current="page"', 'href="#rooms"'))
for name, a, b in (("header", ih, rh), ("footer", ifo, rfo)):
    if norm(a) != norm(b):
        fail.append("%s differs between index.html and rooms.html" % name)
        print("  *** %s differs between the two pages" % name)
    else:
        print("shared %s: identical on both pages" % name)

# --- cross-page links resolve --------------------------------------------
import os as _os
for f, doc in pages.items():
    ids = set(re.findall(r'\bid="([^"]+)"', doc))
    for href in set(re.findall(r'href="([^"#]*\.html)(#[^"]*)?"', doc)):
        target, frag = href[0], href[1]
        # absolute URLs (canonical, og:url) are not local files
        if "://" in target or target.startswith("//"):
            continue
        # the SEO pages sit one directory deep, so they link root-absolutely;
        # "/rooms.html" is rooms.html relative to the repo root
        target = target.lstrip("/")
        if not _os.path.exists(target):
            fail.append("%s links to missing page %s" % (f, target))
            print("  *** %s links to missing page %s" % (f, target))
        elif frag:
            tdoc = pages.get(target) or io.open(target, encoding="utf-8").read()
            if frag[1:] not in set(re.findall(r'\bid="([^"]+)"', tdoc)):
                fail.append("%s -> %s%s: no such anchor" % (f, target, frag))
                print("  *** %s -> %s%s : anchor not found" % (f, target, frag))
print("cross-page links: checked")

# --- every journey strip must live inside its own university card ---------
# A generator once inserted the last strip after the grid's </ul> instead of
# the card's own times list, so it sat outside every .uni-card and its hover
# rule could never match. The markup stayed well-formed, so only this catches it.
from html.parser import HTMLParser as _HP

class _Cards(_HP):
    VOID = {"area","base","br","col","embed","hr","img","input","link","meta",
            "param","source","track","wbr"}
    def __init__(self):
        _HP.__init__(self, convert_charrefs=True)
        self.stack = []; self.cards = 0; self.inside = 0; self.outside = 0
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag not in self.VOID:
            self.stack.append(cls)
        if "uni-card" in cls.split():
            self.cards += 1
        if "uni-journey" == cls.strip():
            depth = any("uni-card" in c.split() for c in self.stack)
            if depth: self.inside += 1
            else: self.outside += 1
    def handle_endtag(self, tag):
        if tag not in self.VOID and self.stack:
            self.stack.pop()

_c = _Cards(); _c.feed(pages["index.html"])
if _c.outside or _c.inside != _c.cards:
    fail.append("journey strips: %d inside, %d outside, %d cards" % (_c.inside, _c.outside, _c.cards))
    print("  *** journey strips: %d inside / %d OUTSIDE a card / %d cards"
          % (_c.inside, _c.outside, _c.cards))
else:
    print("journey strips: %d, one inside each of the %d university cards" % (_c.inside, _c.cards))

# --- old brand must be gone ----------------------------------------------
for f in ["index.html", "i18n/en.json", "i18n/tr.json"] + sorted(glob.glob("css/*.css")) + sorted(glob.glob("js/*.js")):
    t = io.open(f, encoding="utf-8").read()
    for tok in (u"Emisa", u"emisayurt", u"terracotta", u"residence tabs"):
        if tok in t:
            fail.append("%s still contains %r" % (f, tok))
            print("  *** %s still contains %r" % (f, tok))

print("\n%s" % ("ALL STATIC CHECKS PASSED" if not fail else "%d FAILURES" % len(fail)))
sys.exit(1 if fail else 0)
