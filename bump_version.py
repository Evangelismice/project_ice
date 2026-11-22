with open('app/static/admin/index.html', 'r') as f:
    content = f.read()

old = '<script src="app.js"></script>'
new = '<script src="app.js?v=2"></script>'

if old in content:
    content = content.replace(old, new)
    with open('app/static/admin/index.html', 'w') as f:
        f.write(content)
    print('SUCCESS: Script version bumped to v=2')
else:
    print('FAIL: Could not find script tag')