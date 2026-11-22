with open('app/static/admin/app.js', 'r') as f:
    c = f.read()
print('video_url type check:', "t: 'image'" in c and 'video_url' in c)
print('data-upload found:', 'data-upload' in c)