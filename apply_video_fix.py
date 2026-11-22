"""Applies the video gallery fix to the ICE project.

Run from the project root (the folder that contains the "app" folder):
    python apply_video_fix.py

Safe to run twice: it skips anything already applied. It handles Windows (CRLF)
and Linux (LF) line endings, and does not touch any file unless every edit for
that file can be found.
"""
import sys
from pathlib import Path

ADMIN = Path("app/static/admin/app.js")
SITE_JS = Path("app/static/site/js/main.js")
CSS = Path("app/static/site/css/style.css")

# ---------------------------------------------------------------- admin/app.js
ADMIN_EDITS = [
    (
        "      { n: 'image_url', l: 'Image URL', t: 'image', full: true },\n"
        "      { n: 'video_url', l: 'Video URL', t: 'image', full: true },\n",
        "      { n: 'image_url', l: 'Photo', t: 'image', full: true },\n"
        "      { n: 'video_url', l: 'Video (MP4, MOV or AVI, up to 50 MB)', t: 'video', full: true },\n",
    ),
    (
        "    if (f.t === 'textarea') return `<textarea",
        "    if (f.t === 'video') return `<input type=\"hidden\" name=\"${f.n}\" value=\"${esc(val)}\">"
        "<input type=\"file\" accept=\"video/mp4,video/quicktime,video/x-msvideo\" data-upload=\"${f.n}\">"
        "<video class=\"thumb\" data-preview=\"${f.n}\" controls preload=\"metadata\" ${val ? `src=\"${esc(val)}\"` : 'hidden'}></video>"
        "<span class=\"muted small\" data-status=\"${f.n}\"></span>`;\n"
        "    if (f.t === 'textarea') return `<textarea",
    ),
    (
        "    if (e.fields.some((f) => f.t === 'image' && f.req && !body[f.n])) return toast('Please upload a photo first', true);\n",
        "    if (e.fields.some((f) => f.t === 'image' && f.req && !body[f.n])) return toast('Please upload a photo first', true);\n"
        "    if (e === ENT.gallery) {\n"
        "      if (body.resource_type === 'video' && !body.video_url) return toast('Please upload a video first', true);\n"
        "      if (body.resource_type !== 'video' && !body.image_url) return toast('Please upload a photo first', true);\n"
        "    }\n",
    ),
]

# ---------------------------------------------------------------- site/js/main.js
SITE_OLD_START = "    box.innerHTML = items.length\n      ? items.map((i) => `<figure><img"
SITE_OLD_END = "      : '<p class=\"muted\">Photos will be added soon.</p>';\n"
SITE_NEW = (
    "    const card = (i) => {\n"
    "      const cap = i.description ? `<figcaption>${esc(i.description)}</figcaption>` : '';\n"
    "      if (i.resource_type === 'video' && i.video_url) {\n"
    "        return `<figure><video src=\"${esc(i.video_url)}\" controls preload=\"metadata\" playsinline></video>${cap}</figure>`;\n"
    "      }\n"
    "      if (!i.image_url) return '';\n"
    "      return `<figure><img src=\"${esc(i.image_url.replace('/upload/', '/upload/w_700,q_auto,f_auto/'))}\" "
    "alt=\"${esc(i.description || 'ICE gallery photo')}\" loading=\"lazy\">${cap}</figure>`;\n"
    "    };\n"
    "    box.innerHTML = items.length ? items.map(card).join('') : '<p class=\"muted\">Photos and videos will be added soon.</p>';\n"
)

# ---------------------------------------------------------------- style.css
CSS_OLD = ".gallery img{width:100%;aspect-ratio:4/3;object-fit:cover}"
CSS_NEW = ".gallery img,.gallery video{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#000}"


def read(path):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def write(path, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def patch_file(path, edits, done_marker, label):
    if not path.exists():
        print(f"[FAIL] {path} not found. Run this from the project root folder.")
        return False
    text, crlf = read(path)
    if done_marker in text:
        print(f"[skip] {label}: already applied")
        return True
    for old, new in edits:
        if text.count(old) != 1:
            print(f"[FAIL] {label}: could not find the expected code. Nothing was changed in {path}.")
            print("       Your file may differ from the one this fix was written for. Send me the file.")
            return False
        text = text.replace(old, new)
    write(path, text, crlf)
    print(f"[done] {label}")
    return True


def patch_site_js():
    label = "public gallery page (main.js)"
    if not SITE_JS.exists():
        print(f"[FAIL] {SITE_JS} not found. Run this from the project root folder.")
        return False
    text, crlf = read(SITE_JS)
    if "const card = (i) =>" in text:
        print(f"[skip] {label}: already applied")
        return True
    a = text.find(SITE_OLD_START)
    b = text.find(SITE_OLD_END)
    if a == -1 or b == -1 or b < a:
        print(f"[FAIL] {label}: could not find the expected code. Nothing was changed in {SITE_JS}.")
        return False
    text = text[:a] + SITE_NEW + text[b + len(SITE_OLD_END):]
    write(SITE_JS, text, crlf)
    print(f"[done] {label}")
    return True


def patch_css():
    label = "gallery styles (style.css)"
    if not CSS.exists():
        print(f"[FAIL] {CSS} not found. Run this from the project root folder.")
        return False
    text, crlf = read(CSS)
    if ".gallery video" in text:
        print(f"[skip] {label}: already applied")
        return True
    if text.count(CSS_OLD) != 1:
        print(f"[FAIL] {label}: could not find the expected rule. Nothing was changed in {CSS}.")
        return False
    write(CSS, text.replace(CSS_OLD, CSS_NEW), crlf)
    print(f"[done] {label}")
    return True


if __name__ == "__main__":
    results = [
        patch_file(ADMIN, ADMIN_EDITS, "t: 'video'", "admin gallery form (app.js)"),
        patch_site_js(),
        patch_css(),
    ]
    print()
    if all(results):
        print("All set. Next: bump the version numbers, commit and push (see the steps in the chat).")
    else:
        print("Some edits were not applied. Read the [FAIL] lines above.")
        sys.exit(1)
