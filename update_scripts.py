import os

html_dir = 'app/static/site'
for f in sorted(os.listdir(html_dir)):
    if not f.endswith('.html'):
        continue
    path = os.path.join(html_dir, f)
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'main.js?v=2' in content:
            print(f'{f}: FOUND v=2')
        else:
            # Try the replacement
            new_content = content.replace('js/main.js"', 'js/main.js?v=2"')
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(new_content)
                print(f'{f}: UPDATED to v=2')
            else:
                print(f'{f}: ALREADY HAS v=2 or different pattern')
    except Exception as e:
        print(f'{f}: ERROR - {e}')