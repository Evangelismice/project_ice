with open('app/static/admin/app.js', 'r') as f:
    content = f.read()
# Check if video_url already has image type
if "t: 'image'" in content and 'video_url' in content:
    print('video_url already set to image type')
    # Check if it has data-upload attribute
    if 'data-upload' in content:
        print('data-upload attribute found')
    else:
        print('data-upload attribute NOT found - need to add')
else:
    print('video_url type not set to image')
PYEOF