#!/usr/bin/env python3
import re

with open('app/static/admin/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the gallery section and replace it
# Looking for the specific pattern
pattern = r'gallery: \{\s*title: .Gallery., single: .Photo., path: .\/gallery., search: true,\s*filter: .*?donor_type.*?cols: \[.*?\]\s*fields: \[.*?\]\s*},'

# Actually, let's just do string replacement with the exact known content
old = """gallery: {
    title: 'Gallery', single: 'Photo', path: '/gallery/', search: true,
    filter: { param: 'donor_type', label: 'All types', options: OPT.donorType },
    cols: [
      { h: 'Photo', v: (r) => r.image_url, img: true },
      { h: 'Description', v: (r) => r.description },
      { h: 'Added', v: (r) => (r.created_at || '').slice(0, 10) },
    ],
    fields: [
      { n: 'image_url', l: 'Photo', t: 'image', req: true, full: true },
      { n: 'description', l: 'Short description', max: 150, full: true },
    ],
  },"""

new = """gallery: {
    title: 'Gallery', single: 'Media', path: '/gallery/', search: true,
    filter: { param: 'resource_type', label: 'All types', options: ['image', 'video'] },
    cols: [
      { h: 'Type', v: (r) => label(r.resource_type) },
      { h: 'Media', v: (r) => r.image_url || r.video_url ? (r.video_url || r.image_url) : '—' },
      { h: 'Description', v: (r) => r.description },
      { h: 'Added', v: (r) => (r.created_at || '').slice(0, 10) },
    ],
    fields: [
      { n: 'resource_type', l: 'Type', t: 'select', o: ['image', 'video'], req: true, d: 'image' },
      { n: 'image_url', l: 'Image URL', t: 'image', full: true },
      { n: 'video_url', l: 'Video URL', t: 'url', full: true },
      { n: 'description', l: 'Description', full: true },
    ],"""

if old in content:
    content = content.replace(old, new)
    with open('app/static/admin/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Gallery section updated')
else:
    print('FAIL: Could not find old gallery section')
    # Debug: show what's around line 113
    lines = content.split('\n')
    for i in range(110, 130):
        if i < len(lines):
            print(f'{i+1}: {lines[i][:100]}')