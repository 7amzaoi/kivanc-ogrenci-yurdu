# -*- coding: utf-8 -*-
"""Point the site at its public URL. One command, run once before launch.

    python tools/set-domain.py https://kivancyurdu.com

Writes the origin into site.config.json, then regenerates the canonical
links, the absolute og:image, robots.txt and sitemap.xml from it.
"""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

if len(sys.argv) != 2:
    raise SystemExit("usage: python tools/set-domain.py https://your-domain")

origin = sys.argv[1].strip().rstrip("/")
if not origin.startswith(("http://", "https://")):
    raise SystemExit("origin must start with https:// (or http://), got %r" % origin)
if origin.startswith("http://"):
    print("warning: http:// -- browsers flag it as insecure; prefer https://")

io.open("site.config.json", "w", encoding="utf-8").write(
    json.dumps({"origin": origin}, indent=2) + "\n")
print("site.config.json: origin = %s" % origin)

subprocess.check_call([sys.executable, "tools/build-seo.py"])
