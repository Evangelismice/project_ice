#!/usr/bin/env python3
with open('app/static/admin/app.js', 'r') as f:
    content = f.read()

# Find the position of the accept string
old_accept = 'accept="image/jpeg,image/png,image/webp"'
new_accept = 'accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/x-msvideo"'

if old_accept in content:
    content = content.replace(old_accept, new_accept)
    with open('app/static/admin/app.js', 'w') as f:
        f.write(content)
    print('SUCCESS: Updated accept string to include video types')
else:
    print('FAIL: Could not find accept string in file')
    # Debug: print what we have around the file input
    idx = content.find('data-upload')
    if idx >= 0:
        print('Found data-upload at position', idx)
        print('Context:', content[idx-100:idx+100])