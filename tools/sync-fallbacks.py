# -*- coding: utf-8 -*-
"""Rewrite each element's inline English text from en.json.

The inline copy in index.html is the no-JS / SEO fallback; i18n.js overwrites it
at runtime, so drift there is invisible in a browser and easy to miss. This
regenerates it from the source of truth instead of hand-editing.
"""
import io, re, json, sys

h = io.open("index.html", encoding="utf-8").read()
en = json.loads(io.open("i18n/en.json", encoding="utf-8").read())


def look(path):
    n = en
    for k in path.split("."):
        if not isinstance(n, dict) or k not in n:
            return None
        n = n[k]
    return n if isinstance(n, str) else None


TAGS = "h1|h2|h3|h4|p|span|a|button|blockquote|title|label|legend|li"
# an element whose content is plain text (no nested tags) carrying data-i18n
pat = re.compile(
    r'(<(%s)\b[^>]*\bdata-i18n(?:-html)?="([^"]+)"[^>]*>)([^<]*)(</\2>)' % TAGS)

changed, missing = [], []


def fix(m):
    open_tag, tag, key, inline, close = m.groups()
    exp = look(key)
    if exp is None:
        missing.append(key)
        return m.group(0)
    # These values become HTML text nodes, so bare & must be an entity.
    # (< and > never appear in plain-text keys; data-i18n-html keys are
    # excluded by the [^<]* content match above.)
    safe = re.sub(r'&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)', '&amp;', exp)
    if inline.strip() != safe.strip():
        changed.append((key, inline.strip()[:40], safe[:40]))
    return open_tag + safe + close


h2 = pat.sub(fix, h)

if h2 != h:
    io.open("index.html", "w", encoding="utf-8").write(h2)

sys.stdout.write("resynced %d inline fallbacks from en.json\n" % len(changed))
for k, old, new in changed:
    sys.stdout.write(("  %-24s %-42s -> %s\n" % (k, old, new))
                     .encode("ascii", "replace").decode())
if missing:
    sys.stdout.write("keys used in HTML but absent from en.json: %s\n"
                     % sorted(set(missing)))
for tok in (u"Emisa", u"emisayurt"):
    sys.stdout.write("  %-12s still present: %s\n" % (tok, tok in h2))
