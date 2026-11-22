"""Video gallery fix for the ICE project (version 2).

Run from the project root (the folder that contains the "app" folder):
    python apply_video_fix.py

What it does
  * Admin gallery form: a proper video picker. The "Type" dropdown is removed:
    the type is now worked out from what you upload (a video file -> video, a
    photo -> image), so you can no longer be told to "upload a photo first"
    while uploading a video.
  * Public gallery page: shows videos (any record that has a video address),
    and no longer crashes on records that have no image.
  * Gallery styles for videos.

It works on the original files AND on files that already have version 1 of this
fix. It is safe to run twice. Windows and Linux line endings are kept.
If it cannot find the code it expects it changes nothing in that file and says so.
"""
import re
import sys
from pathlib import Path

ADMIN = Path("app/static/admin/app.js")
SITE_JS = Path("app/static/site/js/main.js")
CSS = Path("app/static/site/css/style.css")

GALLERY_FIELDS = (
    "      { n: 'image_url', l: 'Photo', t: 'image', full: true },\n"
    "      { n: 'video_url', l: 'Video (MP4, MOV or AVI, up to 50 MB)', t: 'video', full: true },\n"
    "      { n: 'description', l: 'Description', full: true },"
)

VIDEO_INPUT = (
    "    if (f.t === 'video') return `<input type=\"hidden\" name=\"${f.n}\" value=\"${esc(val)}\">"
    "<input type=\"file\" accept=\"video/mp4,video/quicktime,video/x-msvideo\" data-upload=\"${f.n}\">"
    "<video class=\"thumb\" data-preview=\"${f.n}\" controls preload=\"metadata\" ${val ? `src=\"${esc(val)}\"` : 'hidden'}></video>"
    "<span class=\"muted small\" data-status=\"${f.n}\"></span>`;\n"
)

OLD_V1_CHECK = (
    "    if (e === ENT.gallery) {\n"
    "      if (body.resource_type === 'video' && !body.video_url) return toast('Please upload a video first', true);\n"
    "      if (body.resource_type !== 'video' && !body.image_url) return toast('Please upload a photo first', true);\n"
    "    }\n"
)
NEW_CHECK = (
    "    if (e === ENT.gallery) {\n"
    "      if (body.video_url) { body.resource_type = 'video'; body.image_url = null; }\n"
    "      else if (body.image_url) { body.resource_type = 'image'; }\n"
    "      else return toast('Please upload a photo or a video first', true);\n"
    "    }\n"
)
PHOTO_CHECK_LINE = "    if (e.fields.some((f) => f.t === 'image' && f.req && !body[f.n])) return toast('Please upload a photo first', true);\n"

SITE_OLD_START = "    box.innerHTML = items.length\n      ? items.map((i) => `<figure><img"
SITE_OLD_END = "      : '<p class=\"muted\">Photos will be added soon.</p>';\n"
SITE_NEW = (
    "    const card = (i) => {\n"
    "      const cap = i.description ? `<figcaption>${esc(i.description)}</figcaption>` : '';\n"
    "      if (i.video_url) {\n"
    "        return `<figure><video src=\"${esc(i.video_url)}\" controls preload=\"metadata\" playsinline></video>${cap}</figure>`;\n"
    "      }\n"
    "      if (!i.image_url) return '';\n"
    "      return `<figure><img src=\"${esc(i.image_url.replace('/upload/', '/upload/w_700,q_auto,f_auto/'))}\" "
    "alt=\"${esc(i.description || 'ICE gallery photo')}\" loading=\"lazy\">${cap}</figure>`;\n"
    "    };\n"
    "    box.innerHTML = items.length ? items.map(card).join('') : '<p class=\"muted\">Photos and videos will be added soon.</p>';\n"
)

CSS_OLD = ".gallery img{width:100%;aspect-ratio:4/3;object-fit:cover}"
CSS_NEW = ".gallery img,.gallery video{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#000}"


def read(path):
    raw = path.read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def write(path, text, crlf):
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def need(path):
    if not path.exists():
        print(f"[FAIL] {path} not found. Run this from the project root folder.")
        return False
    return True


def fix_admin():
    label = "admin gallery form (app.js)"
    if not need(ADMIN):
        return False
    text, crlf = read(ADMIN)
    if "body.video_url) { body.resource_type = 'video'" in text and "{ n: 'resource_type', l: 'Type'" not in text:
        print(f"[skip] {label}: already applied")
        return True

    # 1. gallery fields: photo picker, video picker, description (no Type dropdown)
    pat = re.compile(r"(  gallery: \{.*?    fields: \[\n)(.*?)(\n    \],\n  \},)", re.S)
    m = pat.search(text)
    if not m:
        print(f"[FAIL] {label}: could not find the gallery form. Nothing was changed in {ADMIN}.")
        return False
    text = text[:m.start(2)] + GALLERY_FIELDS + text[m.end(2):]

    # 2. video picker rendering
    if "f.t === 'video'" not in text:
        anchor = "    if (f.t === 'textarea') return `<textarea"
        if text.count(anchor) != 1:
            print(f"[FAIL] {label}: could not find where to add the video picker. Nothing was changed in {ADMIN}.")
            return False
        text = text.replace(anchor, VIDEO_INPUT + anchor)

    # 3. save check: work out the type from what was uploaded
    text = text.replace(OLD_V1_CHECK, "")
    if text.count(PHOTO_CHECK_LINE) != 1:
        print(f"[FAIL] {label}: could not find the save step. Nothing was changed in {ADMIN}.")
        return False
    text = text.replace(PHOTO_CHECK_LINE, PHOTO_CHECK_LINE + NEW_CHECK)

    write(ADMIN, text, crlf)
    print(f"[done] {label}")
    return True


def fix_site_js():
    label = "public gallery page (main.js)"
    if not need(SITE_JS):
        return False
    text, crlf = read(SITE_JS)
    if "const card = (i) =>" not in text:
        a, b = text.find(SITE_OLD_START), text.find(SITE_OLD_END)
        if a == -1 or b == -1 or b < a:
            print(f"[FAIL] {label}: could not find the gallery code. Nothing was changed in {SITE_JS}.")
            return False
        text = text[:a] + SITE_NEW + text[b + len(SITE_OLD_END):]
    elif "i.resource_type === 'video' && i.video_url" in text:
        text = text.replace("i.resource_type === 'video' && i.video_url", "i.video_url")
    else:
        print(f"[skip] {label}: already applied")
        return True
    write(SITE_JS, text, crlf)
    print(f"[done] {label}")
    return True


def fix_css():
    label = "gallery styles (style.css)"
    if not need(CSS):
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
    ok = [fix_admin(), fix_site_js(), fix_css()]
    print()
    if all(ok):
        print("All set. Now run: python bump_versions.py   then commit and push.")
    else:
        print("Some edits were not applied. Read the [FAIL] lines above.")
        sys.exit(1)
