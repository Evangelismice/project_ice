with open('app/static/admin/app.js', 'r') as f:
    content = f.read()

# Replace the image input block to also accept video files
old_code = """if (f.t === 'image') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="image/jpeg,image/png,image/webp" data-upload="${f.n}"><img class="thumb" data-preview="${f.n}" ${val ? \`src="${esc(val)}"` : 'hidden'}><span class="muted small" data-status="${f.n}"></span>";"""

new_code = """if (f.t === 'image' || f.n === 'video_url') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/x-msvideo" data-upload="${f.n}"><img class="thumb" data-preview="${f.n}" ${val ? \`src="${esc(val)}"` : 'hidden'}><span class="muted small" data-status="${f.n}"></span>";"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app/static/admin/app.js', 'w') as f:
        f.write(content)
    print('SUCCESS: Added video support to file input')
else:
    print('FAIL: Could not find target code')
    # Debug: show what's around the target
    idx = content.find("if (f.t === 'image')")
    if idx >= 0:
        print("Found at position", idx)
        print("Context:", content[idx:idx+200])
PY