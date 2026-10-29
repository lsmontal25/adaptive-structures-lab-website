#!/usr/bin/env python3
"""Builds the Adaptive Structures Lab website.

    python3 build.py            -> writes the finished site to _site/
    python3 build.py --preview  -> same, but links also work when opening files directly on your computer

All text lives in content/. Photos/videos live in assets/. You normally never need to edit this file.
"""
import datetime, html, os, re, shutil, sys
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(ROOT, '_site')
PREVIEW = '--preview' in sys.argv
ME = 'L. Stein-Montalvo'


def load(p):
    with open(os.path.join(ROOT, 'content', p), encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


SITE = load('site.yaml')
TEAM = load('team.yaml')
PUBS = load('publications.yaml')
RES = load('research.yaml')
PROJECTS = {}
for fn in sorted(os.listdir(os.path.join(ROOT, 'content', 'projects'))):
    if fn.endswith('.yaml') and not fn.startswith('_'):
        PROJECTS[fn[:-5]] = load('projects/' + fn)


# ---------------------------------------------------------------- helpers
class Page:
    def __init__(self, path):
        self.path = path.strip('/')

    @property
    def pre(self):
        return '' if not self.path else '../' * (self.path.count('/') + 1)

    def url(self, u):
        """'/team/' (a page) or 'img/x.jpg' (a file in assets/) -> link that works from this page."""
        if not u:
            return ''
        if re.match(r'^(https?:|mailto:|#|tel:)', u):
            return u
        if u.startswith('/'):
            u = u.strip('/')
            target = (u + '/') if u else ''
            if PREVIEW:
                return self.pre + target + 'index.html'
            return (self.pre + target) or './'
        if u.startswith('assets/'):
            return self.pre + u
        return self.pre + 'assets/' + u


def esc(s):
    return html.escape(str(s), quote=False)


def inline(s, pg, bold_me=False):
    """*italic*, **bold**, [text](url)."""
    s = esc(s or '')

    def lnk(m):
        u = m.group(2)
        ext = '' if u.startswith(('/', 'mailto:')) else ' target="_blank" rel="noopener"'
        return '<a class="ul" href="%s"%s>%s</a>' % (html.escape(pg.url(u)), ext, m.group(1))

    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lnk, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    if bold_me:
        s = s.replace(ME, '<b>%s</b>' % ME)
    return s


def paras(s, pg, bold_me=False):
    if not s:
        return ''
    parts = [p.strip() for p in re.split(r'\n\s*\n', str(s).strip()) if p.strip()]
    return ''.join('<p>%s</p>' % inline(p, pg, bold_me) for p in parts)


def lines(s):
    return '<br>'.join(esc(l) for l in str(s).strip('\n').split('\n'))


def plain(s, n=155):
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(s or ''))
    return re.sub(r'\s+', ' ', s.replace('*', '')).strip()[:n]


ICON = {
    'email': ('Email', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6 8.5 7 8.5-7"/></svg>'),
    'website': ('Website', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.7 2.8 2.7 15.2 0 18M12 3c-2.7 2.8-2.7 15.2 0 18"/></svg>'),
    'github': ('GitHub', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/></svg>'),
    'linkedin': ('LinkedIn', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/></svg>'),
    'scholar': ('Google Scholar', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M2 9.5 12 4l10 5.5L12 15z"/><path d="M6 11.7V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.3"/></svg>'),
    'researchgate': ('ResearchGate', '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.7"/><text x="12" y="16" text-anchor="middle" font-size="9" font-weight="700" fill="currentColor" font-family="Arial">RG</text></svg>'),
    'orcid': ('ORCID', '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.7"/><text x="12" y="15.5" text-anchor="middle" font-size="9" font-weight="700" fill="currentColor" font-family="Arial">iD</text></svg>'),
}
SOC = {
    'instagram': ('Instagram', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>'),
    'bluesky': ('Bluesky', '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5.2 3.6C7.8 5.5 10.6 9.4 12 11.3c1.4-1.9 4.2-5.8 6.8-7.7 1.9-1.4 4.9-2.4 4.9 1 0 .7-.4 5.7-.6 6.5-.8 2.8-3.6 3.5-6.1 3.1 4.4.7 5.5 3.2 3.1 5.7-4.6 4.7-6.6-1.2-7.1-2.7l-.1-.3-.1.3c-.5 1.5-2.5 7.4-7.1 2.7-2.4-2.5-1.3-5 3.1-5.7-2.5.4-5.3-.3-6.1-3.1C2.5 10.3 2.1 5.3 2.1 4.6c0-3.4 3-2.4 4.9-1z" transform="translate(-.9 0)"/></svg>'),
    'linkedin': ICON['linkedin'],
}


def link_icons(links):
    out = []
    for k, v in (links or {}).items():
        if not v or k not in ICON:
            continue
        href = 'mailto:' + v if k == 'email' else v
        out.append('<a href="%s" title="%s" aria-label="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(href), ICON[k][0], ICON[k][0], ICON[k][1]))
    return ''.join(out)


def media(m, pg):
    src = m['src']
    cap = '<figcaption>%s</figcaption>' % inline(m['caption'], pg) if m.get('caption') else ''
    st = ' style="max-width:%s;margin:0 auto"' % m['width'] if m.get('width') else ''
    if src.lower().endswith(('.mp4', '.webm', '.mov')):
        poster = os.path.splitext(src)[0] + '-poster.jpg'
        pa = ' poster="%s"' % pg.url(poster) if os.path.exists(os.path.join(ROOT, 'assets', poster)) else ''
        el = '<video src="%s"%s autoplay muted loop playsinline controls preload="metadata"></video>' % (pg.url(src), pa)
    else:
        el = '<img src="%s" alt="%s" loading="lazy">' % (pg.url(src), esc(m.get('alt', '')))
    return '<figure%s>%s%s</figure>' % (st, el, cap)


def cite_tags(c):
    t = []
    if c.get('doi'):
        t.append('<a href="https://doi.org/%s" target="_blank" rel="noopener">doi: %s</a>' % (c['doi'], esc(c['doi'])))
    else:
        t.append('<span class="prep">In preparation</span>')
    for n, u in (c.get('links') or {}).items():
        t.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(u), esc(n)))
    if c.get('cover'):
        t.append('<span class="cov">Front cover</span>')
    return ''.join(t)


def cite(c, pg):
    return '<div class="cite">%s<div class="tags">%s</div></div>' % (inline(c['text'], pg, True), cite_tags(c))


# ---------------------------------------------------------------- shell
def nav(pg, active):
    items = ''.join('<li%s><a href="%s">%s</a></li>' % (' class="on"' if m['label'] == active else '', pg.url(m['url']), esc(m['label'])) for m in SITE['menu'])
    return ('<nav><a href="%s" style="display:flex" aria-label="Home"><img src="%s" alt="%s"></a>'
            '<button class="menu-btn" aria-expanded="false" onclick="var u=this.nextElementSibling;u.classList.toggle(\'open\');'
            'this.setAttribute(\'aria-expanded\',u.classList.contains(\'open\'))">Menu</button><ul>%s</ul></nav>') % (
        pg.url('/'), pg.url('img/misc/logo-white.png'), esc(SITE['lab_name']), items)


def footer(pg):
    f = SITE['footer']
    soc = ''.join('<a href="%s" aria-label="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(f[k]), SOC[k][0], SOC[k][1]) for k in ('instagram', 'bluesky', 'linkedin') if f.get(k))
    links = ''.join('<a href="%s">%s</a>' % (pg.url(m['url']), esc(m['label'])) for m in SITE['menu'] if m['url'] != '/')
    return ('<footer><div class="fwrap"><div class="ftop"><div><img src="%s" alt="%s"></div>'
            '<div class="col"><h5>Address</h5>%s</div>'
            '<div class="col"><h5>Contact</h5><a class="mail" href="mailto:%s">%s</a><div class="soc">%s</div></div></div>'
            '<div class="fbot"><nav>%s</nav><span>%s © %d. All Rights Reserved.</span></div></div></footer>') % (
        pg.url('img/misc/logo-white.png'), esc(SITE['lab_name']), lines(f['address']), f['email'], f['email'], soc, links,
        esc(SITE['lab_name']), datetime.date.today().year)


def shell(pg, title, css, body, desc=''):
    t = esc('%s | %s' % (title, SITE['lab_name']) if title else SITE['lab_name'])
    d = esc(desc or plain(SITE['home']['about']))
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title><meta name="description" content="%s">\n'
            '<link rel="icon" href="%s" sizes="32x32"><link rel="apple-touch-icon" href="%s">\n'
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s">\n'
            '<link rel="stylesheet" href="%s"><link rel="stylesheet" href="%s">\n'
            '</head><body class="fC">\n%s\n</body></html>\n') % (
        t, d, pg.url('img/misc/icon-32.png'), pg.url('img/misc/icon-180.png'), t, d,
        pg.url('css/common.css'), pg.url('css/%s.css' % css), body)


def write(pg, s):
    d = os.path.join(OUT, pg.path)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(s)


# ---------------------------------------------------------------- pages
def home():
    pg = Page('')
    h = SITE['home']
    btns = ''.join('<a class="go" href="%s">%s</a>' % (pg.url(m['url']), esc(m['label'])) for m in SITE['menu'] if m['url'] != '/')
    poster = os.path.splitext(h['video_mp4'])[0] + '-poster.jpg'
    body = ('<section class="hero"><video autoplay muted loop playsinline poster="%s"><source src="%s" type="video/mp4"><source src="%s" type="video/webm"></video>\n'
            '%s\n<div class="cap"><h1>%s</h1><h2>%s</h2></div></section>\n'
            '<section class="about"><div class="eyebrow">%s</div>%s<div class="rule"></div><div class="gos">%s</div></section>\n%s') % (
        pg.url(poster), pg.url(h['video_mp4']), pg.url(h['video_webm']), nav(pg, 'Home'), esc(SITE['lab_name']),
        inline(SITE['tagline'], pg), esc(h['about_title']), paras(h['about'], pg), btns, footer(pg))
    write(pg, shell(pg, '', 'home', body))


def research():
    pg = Page('research')
    halves = []
    for gi, g in enumerate(RES['groups']):
        bub = ''.join('<button class="bub" data-t="%s">%s</button>' % (k, esc(RES['tags'][k])) for k in g['bubbles'])
        cards = []
        for slug in g['projects']:
            p = PROJECTS[slug]
            c = p.get('card', {})
            credit = ' title="%s"' % esc(c['image_credit']) if c.get('image_credit') else ''
            img = ('<div class="img" style="background-image:url(%s)"%s></div>' % (pg.url('img/cards/' + c['image']), credit)) if c.get('image') else '<div class="img"></div>'
            inner = '%s<div><h3 class="hd">%s</h3><p>%s</p>' % (img, esc(p['title']), inline(c.get('summary', ''), pg))
            t = ' '.join(p.get('tags', []))
            if p.get('coming_soon'):
                cards.append('<div class="proj soon" data-t="%s">%s<div class="tags"><span class="soonpill">Coming soon</span></div></div></div>' % (t, inner))
            else:
                refs = '<div class="tags">%s</div>' % inline(c['refs'], pg) if c.get('refs') else ''
                cards.append('<a class="proj" data-t="%s" href="%s">%s%s</div></a>' % (t, pg.url('/' + slug + '/'), inner, refs))
        halves.append('<div class="half%s"><div class="head"><h2 class="hd">%s</h2><p class="desc">%s</p><div class="bubbles">%s</div></div>%s</div>' % (
            ' r' if gi else '', esc(g['title']), inline(g['description'], pg), bub, ''.join(cards)))
    title = inline(RES['title'], pg).replace(' for ', '<br>for ', 1)
    script = ('<script>const split=document.getElementById("split");'
              'document.querySelectorAll(".bub").forEach(b=>b.onclick=()=>{const on=b.classList.contains("on");'
              'document.querySelectorAll(".bub").forEach(x=>x.classList.remove("on"));'
              'document.querySelectorAll(".proj").forEach(p=>p.classList.remove("hit"));'
              'if(on){split.classList.remove("dim");return}b.classList.add("on");split.classList.add("dim");'
              'document.querySelectorAll(".proj").forEach(p=>{if(p.dataset.t.split(" ").includes(b.dataset.t))p.classList.add("hit")})});</script>')
    body = '%s\n<section class="intro"><div class="eyebrow">%s</div><h1 class="hd">%s</h1>%s</section>\n<section class="split" id="split">%s</section>\n%s\n%s' % (
        nav(pg, 'Research'), esc(RES['label']), title, paras(RES['intro'], pg), ''.join(halves), footer(pg), script)
    write(pg, shell(pg, 'Research', 'research', body, plain(RES['intro'])))


def project(slug, p):
    pg = Page(slug)
    group = next((g['title'] for g in RES['groups'] if slug in g['projects']), 'Research')
    tags = ''.join('<span>%s</span>' % esc(RES['tags'][k]) for k in p.get('tags', []))
    body = '%s\n<section class="intro"><a class="back" href="%s">← Research · %s</a><h1 class="hd">%s</h1>%s<div class="ptags">%s</div></section>' % (
        nav(pg, 'Research'), pg.url('/research/'), esc(group), esc(p['title']), paras(p.get('intro'), pg), tags)
    if p.get('hero'):
        body += '<div class="hero">%s</div>' % media(p['hero'], pg)
    body += '<div class="wrap">'
    for s in p.get('sections') or []:
        figs = ''.join(media(m, pg) for m in s.get('media') or [])
        txt = paras(s.get('text'), pg) + ''.join(cite(c, pg) for c in s.get('citations') or [])
        h2 = '<h2 class="hd">%s</h2>' % esc(s['heading']) if s.get('heading') else ''
        if figs and not txt:
            body += '<section class="sec">%s<div class="gal">%s</div></section>' % (h2, figs)
        else:
            body += '<section class="sec">%s<div class="sgrid%s"><div class="txt">%s</div>%s</div></section>' % (
                h2, '' if figs else ' solo', txt, '<div class="figs">%s</div>' % figs if figs else '')
    body += '</div><div class="foot-nav"><a href="%s">← Back to Research</a></div>%s' % (pg.url('/research/'), footer(pg))
    write(pg, shell(pg, p['title'], 'project', body, plain(p.get('intro'))))


def team():
    pg = Page('team')
    pi, cur, alum, bios = '', [], [], []
    for i, p in enumerate(TEAM['people']):
        if p.get('photo'):
            img = '<div class="ph" style="background-image:url(%s)"></div>' % pg.url('img/team/' + p['photo'])
        else:
            img = '<div class="ph ph0"><img src="%s" alt=""></div>' % pg.url('img/misc/icon-180.png')
        if p.get('pi'):
            pi = '<div class="pi">%s<div><h2 class="hd">%s</h2><div class="t">%s</div>%s<div class="links">%s</div></div></div>' % (
                img, esc(p['name']), esc(p['title']), paras(p.get('bio'), pg), link_icons(p.get('links')))
            continue
        if p.get('bio'):
            bios.append('<template id="bio%d"><div class="bimg">%s</div><div><h3 class="hd">%s</h3><div class="bt">%s</div><div class="bb">%s</div><div class="links">%s</div></div></template>' % (
                i, img, esc(p['name']), esc(p['title']), paras(p['bio'], pg), link_icons(p.get('links'))))
            photo = '<button class="open" data-bio="bio%d" aria-label="Read bio of %s">%s</button>' % (i, esc(p['name']), img)
        else:
            photo = img
        card = '<div class="card%s">%s<h3 class="hd">%s</h3><div class="t">%s</div><div class="links">%s</div></div>' % (
            ' has' if p.get('bio') else '', photo, esc(p['name']), esc(p['title']), link_icons(p.get('links')))
        (alum if p.get('alum') else cur).append(card)
    alum_html = '<h2 class="hd gh">Alumni</h2><div class="grid">%s</div>' % ''.join(alum) if alum else ''
    script = ('<script>const D=document.getElementById("bio");document.querySelectorAll(".open").forEach(b=>b.onclick=()=>{'
              'D.querySelector(".bwrap").innerHTML=document.getElementById(b.dataset.bio).innerHTML;D.showModal()});'
              'D.querySelector(".x").onclick=()=>D.close();D.onclick=e=>{if(e.target===D)D.close()};</script>')
    body = ('%s\n<section class="intro"><div class="eyebrow">%s</div><h1 class="hd">%s</h1>%s</section>\n'
            '<main class="team">%s<h2 class="hd gh">Group members</h2><div class="grid">%s</div>%s</main>\n'
            '<dialog id="bio"><button class="x" aria-label="Close">×</button><div class="bwrap"></div></dialog>%s\n%s\n%s') % (
        nav(pg, 'Team'), esc(TEAM['intro_label']), inline(TEAM['intro_title'], pg), paras(TEAM['intro_text'], pg),
        pi, ''.join(cur), alum_html, ''.join(bios), footer(pg), script)
    write(pg, shell(pg, 'Team', 'team', body))


def publications():
    pg = Page('publications')
    years = []
    for p in PUBS['papers']:
        if p['year'] not in years:
            years.append(p['year'])
    rows = []
    for y in years:
        items = []
        for p in [q for q in PUBS['papers'] if q['year'] == y]:
            items.append('<div class="p"><div class="ti">%s</div><div class="au">%s</div><div class="jo">%s</div><div class="tags">%s</div></div>' % (
                inline(p['title'], pg), inline(p['authors'], pg, True), inline(p['journal'], pg), cite_tags(p)))
        rows.append('<div class="yr"><div class="y">%s</div><div>%s</div></div>' % (y, ''.join(items)))
    covers = ''.join('<a href="%s" target="_blank" rel="noopener"><img src="%s" alt="%s" loading="lazy"></a>' % (
        html.escape(c['url']), pg.url(c['image']), esc(c.get('alt', ''))) for c in PUBS.get('featured_covers') or [])
    body = ('%s\n<section class="intro"><h1 class="hd">Publications</h1>%s</section>\n'
            '<section class="pubs"><div>%s</div><aside><h2 class="hd">Featured covers</h2><div class="cv">%s</div></aside></section>\n%s') % (
        nav(pg, 'Publications'), paras(PUBS['intro'], pg), ''.join(rows), covers, footer(pg))
    write(pg, shell(pg, 'Publications', 'publications', body))


def contact():
    pg = Page('contact')
    c = SITE['contact']
    cols = ''.join('<div class="col"><h3 class="hd">%s</h3>%s</div>' % (esc(j['title']), paras(j['text'], pg)) for j in c['join'])
    body = ('%s\n<section class="intro"><h1 class="hd">Contact</h1></section>\n'
            '<div class="wrap"><section class="gen"><div><h2 class="hd">%s</h2><div class="addr">%s</div>'
            '<div class="kv"><b>Office</b><span>%s</span><b>Email</b><span><a class="ul" href="mailto:%s">%s</a></span><b>Lab</b><span>%s</span></div></div>'
            '<img src="%s" alt="Northwestern University lakefront campus"></section>'
            '<section class="join"><h2 class="hd">%s</h2><p class="note">%s</p><div class="cols">%s</div></section></div>\n'
            '<section class="map"><iframe loading="lazy" title="Map" src="%s"></iframe></section>\n%s') % (
        nav(pg, 'Contact'), esc(c['heading']), lines(c['address']), esc(c['office']), c['email'], c['email'], esc(c['lab']),
        pg.url(c['photo']), esc(c['join_title']), inline(c['join_note'], pg), cols, html.escape(c['map']), footer(pg))
    write(pg, shell(pg, 'Contact', 'contact', body))


def redirect(path, to):
    pg = Page(path)
    u = pg.url(to)
    write(pg, '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=%s"><link rel="canonical" href="%s"><a href="%s">Continue</a>' % (u, u, u))


def check():
    """Warn about missing files referenced from content."""
    missing = []
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn.endswith('.html'):
                s = open(os.path.join(root, fn), encoding='utf-8').read()
                for u in re.findall(r'(?:src|href|poster)="([^"#:]+?)"|url\(([^)]+)\)', s):
                    u = u[0] or u[1]
                    if not u or u.startswith(('http', 'mailto', 'data:', '/')):
                        continue
                    p = os.path.normpath(os.path.join(root, u.split('?')[0]))
                    if u.endswith('/') or u in ('./',):
                        p = os.path.join(p, 'index.html')
                    if not os.path.exists(p):
                        missing.append('%s -> %s' % (os.path.relpath(os.path.join(root, fn), OUT), u))
    for m in sorted(set(missing)):
        print('  MISSING:', m)
    return not missing


if __name__ == '__main__':
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    home(); research(); team(); publications(); contact()
    for slug, p in PROJECTS.items():
        if not p.get('coming_soon'):
            project(slug, p)
    redirect('news-events', '/')  # old WordPress address
    if os.path.exists(os.path.join(ROOT, 'CNAME')):
        shutil.copy(os.path.join(ROOT, 'CNAME'), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    with open(os.path.join(OUT, '404.html'), 'w') as f:
        f.write('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/"><a href="/">Adaptive Structures Lab</a>')
    ok = check()
    print('Built %s%s%s' % (OUT, ' (preview links)' if PREVIEW else '', '' if ok else '  -- with missing files, see above'))
