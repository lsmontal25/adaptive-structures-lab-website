"""Make self-contained copies of the built pages (CSS, fonts, images inlined) for quick previewing.
Run after:  python3 build.py --preview
Usage:      python3 tools/inline_preview.py   -> writes _preview/<page>.html
"""
import base64, mimetypes, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '_site'); OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, '_preview')
os.makedirs(OUT, exist_ok=True)

def data(path, limit=4_000_000):
    if not os.path.exists(path) or os.path.getsize(path) > limit: return None
    mt = mimetypes.guess_type(path)[0] or ('font/woff2' if path.endswith('.woff2') else 'application/octet-stream')
    return 'data:%s;base64,%s' % (mt, base64.b64encode(open(path, 'rb').read()).decode())

for root, _, files in os.walk(SITE):
    for fn in files:
        if fn != 'index.html': continue
        p = os.path.join(root, fn); base = os.path.dirname(p)
        s = open(p, encoding='utf-8').read()
        def css(m):
            cp = os.path.normpath(os.path.join(base, m.group(1))); c = open(cp, encoding='utf-8').read()
            c = re.sub(r'url\(([^)]+)\)', lambda u: 'url(%s)' % (data(os.path.normpath(os.path.join(os.path.dirname(cp), u.group(1)))) or u.group(1)), c)
            return '<style>%s</style>' % c
        s = re.sub(r'<link rel="stylesheet" href="([^"]+)">', css, s)
        def attr(m):
            u = m.group(2)
            if u.startswith(('http', 'data:', 'mailto')) or u.endswith('/') or u.endswith('.html'): return m.group(0)
            d = data(os.path.normpath(os.path.join(base, u)), 2_500_000 if u.endswith(('.mp4', '.webm')) else 4_000_000)
            return '%s"%s"' % (m.group(1), d) if d else m.group(0)
        s = re.sub(r'((?:src|poster)=)"([^"]+)"', attr, s)
        s = re.sub(r'url\(([^)"]+)\)', lambda u: 'url(%s)' % (data(os.path.normpath(os.path.join(base, u.group(1)))) or u.group(1)), s)
        name = (os.path.relpath(root, SITE).replace(os.sep, '_') if root != SITE else 'home') + '.html'
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(s)
        print(name, os.path.getsize(os.path.join(OUT, name)) // 1024, 'KB')
