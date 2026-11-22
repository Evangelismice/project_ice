#!/usr/bin/env python3
with open('app/static/admin/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 113-124 (gallery section, 1-indexed) with new gallery config
# Lines 1-112 stay, then new gallery, then lines 125+ stay
new_gallery_lines = [
    '  gallery: {\n',
    "    title: 'Gallery', single: 'Media', path: '/gallery/', search: true,\n",
    "    filter: { param: 'resource_type', label: 'All types', options: ['image', 'video'] },\n",
    '    cols: [\n',
    '      { h: "Type", v: (r) => label(r.resource_type) },\n',
    '      { h: "Media", v: (r) => r.image_url || r.video_url ? (r.video_url || r.image_url) : "—" },\n',
    '      { h: "Description", v: (r) => r.description },\n',
    '      { h: "Added", v: (r) => (r.created_at || "").slice(0, 10) },\n',
    '    ],\n',
    "    fields: [\n",
    "      { n: 'resource_type', l: 'Type', t: 'select', o: ['image', 'video'], req: true, d: 'image' },\n",
    "      { n: 'image_url', l: 'Image URL', t: 'image', full: true },\n",
    "      { n: 'video_url', l: 'Video URL', t: 'url', full: true },\n",
    "      { n: 'description', l: 'Description', full: true },\n",
    "  },\n",
]

# Keep lines before gallery (1-112) and after gallery (125+)
new_lines = lines[:112] + new_gallery_lines + lines[124:]

with open('app/static/admin/app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Gallery section updated successfully')