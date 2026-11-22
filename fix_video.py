with open('app/static/admin/app.js', 'r') as f:
    content = f.read()

# The exact old code block (note: backticks need to be handled carefully)
old_code = """if (f.t === 'image') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="image/jpeg,image/png,image/webp" data-upload="${f.n}"><img class="thumb" data-preview="${f.n}" ${val ? \`src="${esc(val)}"` : 'hidden'}><span class="muted small" data-status="${f.n}"></span>";"""

# The new code block with video support
new_code = """if (f.t === 'image' || f.n === 'video_url') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/x-msvideo" data-upload="${f.n}"><img class="thumb" data-preview="${f.n}" ${val ? \`src="${esc(val)}"` : 'hidden'}><span class="muted small" data-status="${f.n}"></span>";"""

print("Old code length:", len(old_code))
print("New code length:", len(new_code))

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app/static/admin/app.js', 'w') as f:
        f.write(content)
    print('SUCCESS: Added video support to file input')
else:
    print('FAIL: Could not find target code')
    # Debug: print what we're looking for
    print("Looking for this pattern...")
    print(repr(old_code[:50]))