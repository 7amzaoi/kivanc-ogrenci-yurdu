# -*- coding: utf-8 -*-
"""Rewrite every inline data-i18n-attr fallback from en.json.

These attribute fallbacks (alt, aria-label, content, placeholder, title) are
what a visitor gets before i18n.js runs -- and what social scrapers and
crawlers, which mostly do not run JavaScript, get permanently. They drifted
badly because the drift checker only ever looked at data-i18n text nodes.
"""
import io, json, re, sys

# Keys the generator deliberately suffixes with an index ("Photograph 1").
EXEMPT = {"roomsPage.photoOf"}

fen = {}
def flat(n, p=""):
    if isinstance(n, dict):
        for k, v in n.items(): flat(v, p + "." + k if p else k)
    elif isinstance(n, str):
        fen[p] = n
flat(json.load(io.open("i18n/en.json", encoding="utf-8")))

def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")

TAG = re.compile(r'<[a-zA-Z][^>]*\bdata-i18n-attr="([^"]+)"[^>]*>', re.S)

for page in sys.argv[1:]:
    html = io.open(page, encoding="utf-8").read()
    out, last, fixed, added = [], 0, 0, 0
    for m in TAG.finditer(html):
        tag = m.group(0)
        for pair in m.group(1).split(";"):
            pair = pair.strip()
            if ":" not in pair: continue
            attr, key = (x.strip() for x in pair.split(":", 1))
            if key in EXEMPT or key not in fen: continue
            want = esc(re.sub(r"\s+", " ", fen[key]).strip())
            am = re.search(r'\s\b%s="[^"]*"' % re.escape(attr), tag)
            if am:
                if am.group(0) != ' %s="%s"' % (attr, want):
                    tag = tag[:am.start()] + ' %s="%s"' % (attr, want) + tag[am.end():]
                    fixed += 1
            else:
                # no inline value at all: the element is unnamed until JS runs
                tag = tag[:-1].rstrip() + ' %s="%s"' % (attr, want) + tag[-1]
                added += 1
        out.append(html[last:m.start()]); out.append(tag); last = m.end()
    out.append(html[last:])
    io.open(page, "w", encoding="utf-8").write("".join(out))
    print("%-12s %d attribute fallbacks resynced, %d added" % (page, fixed, added))
