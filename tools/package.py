# -*- coding: utf-8 -*-
"""Build the zip to upload to Hostinger's public_html/.

    python tools/package.py

Ships only what the browser asks for. The generators, the README and the git
history stay in the repository -- there is no reason for the server to hold
the Python that built the pages.

Refuses to build if the site still has no origin configured, because a site
uploaded without a canonical and without an absolute og:image is a site you
will have to upload again.
"""
import io
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = "kivanc-site.zip"

# Files at the root that belong on the server.
ROOT_FILES = ["index.html", "rooms.html", "404.html", ".htaccess",
              "robots.txt", "sitemap.xml"]
# Whole directories that belong on the server.
DIRS = ["css", "js", "i18n", "assets"]
# Never ship these, wherever they turn up.
SKIP_EXT = {".py", ".md", ".bak", ".psd", ".zip"}
SKIP_NAME = {"site.config.json", ".DS_Store", "Thumbs.db", ".gitignore"}


def origin():
    try:
        return (json.load(io.open("site.config.json", encoding="utf-8"))
                .get("origin") or "").rstrip("/")
    except (IOError, ValueError):
        return ""


def collect():
    for f in ROOT_FILES:
        if os.path.exists(f):
            yield f
        elif f in ("robots.txt", "sitemap.xml"):
            pass                      # only exist once an origin is set
        else:
            raise SystemExit("missing required file: %s" % f)

    for d in DIRS:
        for base, _dirs, files in os.walk(d):
            if ".git" in base:
                continue
            for name in sorted(files):
                if name in SKIP_NAME:
                    continue
                if os.path.splitext(name)[1].lower() in SKIP_EXT:
                    continue
                yield os.path.join(base, name).replace("\\", "/")


def main():
    o = origin()
    if not o:
        raise SystemExit(
            "site.config.json has no origin.\n"
            "Run  python tools/set-domain.py https://your-domain  first, so the\n"
            "canonical links, og:image, robots.txt and sitemap.xml are stamped\n"
            "before the files are packaged.")

    files = sorted(set(collect()))
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f)

    total = sum(os.path.getsize(f) for f in files)
    print("%s  --  %d files, %.2f MB raw, %.2f MB zipped"
          % (OUT, len(files), total / 1048576.0,
             os.path.getsize(OUT) / 1048576.0))
    print("origin: %s" % o)
    print()
    print("Upload it in hPanel -> File Manager -> public_html, then use the")
    print("Extract action. Make sure hidden files are shown so .htaccess lands too.")


if __name__ == "__main__":
    main()
