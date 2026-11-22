"""Updates the cache-busting version numbers so browsers fetch the new files.

Run from the project root (the folder that contains the "app" folder):
    python bump_versions.py

It sets fixed version numbers, so running it twice does no harm.
Windows and Linux line endings are kept as they are.
"""
import re
from pathlib import Path

SITE = Path("app/static/site")
ADMIN_INDEX = Path("app/static/admin/index.html")

SITE_RULES = [
    (re.compile(r'js/main\.js(\?v=\d+)?"'), 'js/main.js?v=3"'),
    (re.compile(r'css/style\.css(\?v=\d+)?"'), 'css/style.css?v=2"'),
]
ADMIN_RULES = [
    (re.compile(r'app\.js(\?v=\d+)?"'), 'app.js?v=3"'),
]


def apply(path, rules):
    raw = path.read_bytes().decode("utf-8")
    text = raw
    for pattern, replacement in rules:
        text = pattern.sub(replacement, text)
    if text != raw:
        path.write_bytes(text.encode("utf-8"))
        print(f"[updated] {path}")
    else:
        print(f"[no change] {path}")


if not SITE.exists() or not ADMIN_INDEX.exists():
    raise SystemExit("Run this from the project root folder (the one that contains the app folder).")

for page in sorted(SITE.glob("*.html")):
    apply(page, SITE_RULES)
apply(ADMIN_INDEX, ADMIN_RULES)
print("\nDone. Now commit and push.")
