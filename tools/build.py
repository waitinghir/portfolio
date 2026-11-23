"""Build the static site from src/.

    python3 tools/build.py

Writes index.html and projects/**/index.html. The generated HTML is committed,
so GitHub Pages serves it with no build step. Edit src/ (article bodies in
src/content/, everything else in src/site.json or the templates below), then
run this script and commit both.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
site = json.load(open(os.path.join(SRC, 'site.json'), encoding='utf-8'))

JP = 'nihongo-quiz-king'
JP_NAME = {'en': 'Nihongo Quiz King', 'zh': '日文知識王'}
JP_ORDER = ['jpquiz-v1', 'jpquiz-v4', 'jpquiz-v5', 'jpquiz-v6']
JP_BADGE = {'jpquiz-v4': {'en': 'Start here', 'zh': '從這篇開始'}, 'jpquiz-v6': {'en': 'In progress', 'zh': '持續更新'}}
HOME_ORDER = ['jpquiz', 'jobmonitor', 'cny', 'flight', 'i18n']
CONTACT = [('LinkedIn', 'https://www.linkedin.com/in/weitim/'), ('GitHub', 'https://github.com/waitinghir'), ('Email', 'mailto:waitinghir@gmail.com')]
HERO_TITLE = {'en': 'Product and growth, built with AI', 'zh': '產品與成長，用 AI 實作'}
TOTAL = len(JP_ORDER)


def esc(s):
    return html.escape(s, quote=True)


def bi(p, tag='span'):
    """Bilingual inline text from a {'en','zh'} pair."""
    if p['en'] == p['zh']:
        return esc(p['en'])
    return f'<{tag} class="lang-en">{esc(p["en"])}</{tag}><{tag} class="lang-zh">{esc(p["zh"])}</{tag}>'


def page_dir(aid):
    a = site['articles'][aid]
    return os.path.join('projects', a['project'], a['slug']) if a['slug'] else os.path.join('projects', a['project'])


def rel(from_dir, to_dir):
    r = os.path.relpath(to_dir or '.', from_dir or '.')
    return '' if r == '.' else r.replace(os.sep, '/') + '/'


def prefix(d):
    return rel(d, '')


def clean_label(t):
    return re.sub(r'^[^\w぀-鿿]+', '', t).strip()


def transform(body, d):
    """Adapt old single-page content to a page living in directory d."""
    def link(m):
        return f'<a href="{rel(d, page_dir(m.group(1)))}">'
    body = re.sub(r'<a onclick="showArticle\(\'([\w-]+)\'\)"[^>]*>', link, body)
    body = re.sub(r'<p style="font-family:var\(--font-mono\)[^"]*">', '<p class="codeblock">', body)
    body = re.sub(r'(<span class="lang-(?:en|zh)">\s*)<p><em>', r'\1<p class="note"><em>', body)
    pre = prefix(d)
    body = re.sub(r'src="(images/[^"]+|cny-cover\.png)"', lambda m: f'src="{pre}{m.group(1)}"', body)
    return body


def layout(d, title, desc, crumbs, main):
    pre = prefix(d)
    crumb_html = ''
    if crumbs:
        items = []
        for i, (label, target) in enumerate(crumbs):
            if i == len(crumbs) - 1:
                items.append(f'<li><span aria-current="page">{label}</span></li>')
            else:
                items.append(f'<li><a href="{rel(d, target)}">{label}</a></li>')
        crumb_html = f'<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(items)}</ol></nav>'
    ext = ' target="_blank" rel="noopener"'
    contact = ''.join('<a href="%s"%s>%s</a>' % (u, ext if u.startswith('http') else '', n) for n, u in CONTACT)
    return f'''<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,400;8..144,500;8..144,600&family=Roboto:wght@400;500&family=Roboto+Mono:wght@500&family=Noto+Sans+TC:wght@400;500&display=swap">
<link rel="stylesheet" href="{pre}assets/site.css">
<script src="{pre}assets/site.js"></script>
</head>
<body>
<header class="appbar"><div class="wrap">
  <a class="brand" href="{pre}">Tim</a>
  <nav class="nav" aria-label="Main">
    <a href="{pre}#projects"><span class="lang-en">Projects</span><span class="lang-zh">專案</span></a>
    <a href="{pre}#about"><span class="lang-en">About</span><span class="lang-zh">關於</span></a>
    <a href="#contact"><span class="lang-en">Contact</span><span class="lang-zh">聯絡</span></a>
  </nav>
  <button class="chipbtn" id="lang-toggle" type="button"><span class="lang-en">中文</span><span class="lang-zh">EN</span></button>
</div></header>
<main class="wrap">
{crumb_html}
{main}
</main>
<footer id="contact"><div class="wrap">
  <span>© 2026 Tim</span>
  <span class="footer-links">{contact}</span>
</div></footer>
</body>
</html>
'''


def write(d, content):
    path = os.path.join(ROOT, d, 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)
    return path


def card_title(c):
    if c['id'] == 'jpquiz':
        return JP_NAME
    t = c['title']
    if t['en'] == t['zh'] and c['subtitle']['en'] != t['en']:
        return {'en': t['en'], 'zh': c['subtitle']['zh']}
    return t


def build_home():
    cards = {c['id']: c for c in site['cards']}
    out = []
    for cid in HOME_ORDER:
        c = cards[cid]
        if cid == 'jpquiz':
            href, kicker, cls = f'projects/{JP}/', {'en': f'App Store · {TOTAL} articles', 'zh': f'App Store · {TOTAL} 篇文章'}, 'card feature'
        else:
            a = site['articles'][cid]
            href = page_dir(cid).replace(os.sep, '/') + '/'
            cat = a['category'].split('—', 1)[-1].strip()
            kicker, cls = {'en': cat, 'zh': cat}, 'card'
        t = card_title(c)
        sub = ''
        if cid not in ('jpquiz',) and site['articles'][cid]['title']['en'] != c['title']['en']:
            sub = f'<span class="sub">{bi(site["articles"][cid]["title"])}</span>'
        tags = ''.join(f'<span class="tag">{bi(x)}</span>' for x in c['tags'])
        out.append(f'''<a class="{cls}" href="{href}">
      <span class="kicker">{bi(kicker)}</span>
      <h3>{bi(t)}</h3>{sub}
      <p>{bi(c["desc"])}</p>
      <div class="tags">{tags}</div>
    </a>''')
    facts = ''.join(f'<span class="fact"><b>{esc(s["value"])}</b> {bi(s["label"])}</span>' for s in site['about']['stats'])
    about = site['about']
    main = f'''<section class="hero">
    <h1>{bi(HERO_TITLE)}</h1>
    <p>{bi(site["hero"]["subtitle"])}</p>
    <div class="facts">{facts}</div>
  </section>
  <section id="projects">
    <div class="section-head"><h2><span class="lang-en">Projects</span><span class="lang-zh">專案</span></h2></div>
    <div class="grid">
    {"".join(out)}
    </div>
  </section>
  <section id="about">
    <div class="section-head"><h2><span class="lang-en">About</span><span class="lang-zh">關於我</span></h2></div>
    <div class="about"><div class="lang-en">{about["en"]}</div><div class="lang-zh">{about["zh"]}</div></div>
  </section>'''
    return write('', layout('', 'Tim — Product & Growth × AI', 'Product and growth leader building and shipping products with AI, and writing up the judgment calls behind them.', None, main))


def head_links(links):
    out = []
    for i, l in enumerate(links):
        lab = {'en': clean_label(l['label']['en']), 'zh': clean_label(l['label']['zh'])}
        cls = 'btn filled' if i == 0 else 'btn tonal'
        out.append(f'<a class="{cls}" href="{esc(l["href"])}" target="_blank" rel="noopener">{bi(lab)}</a>')
    return f'<div class="btnrow">{"".join(out)}</div>' if out else ''


def build_jp_project():
    d = os.path.join('projects', JP)
    rows = []
    for v in site['jpquiz']['versions']:
        badge = f'<span class="badge">{bi(JP_BADGE[v["id"]])}</span>' if v['id'] in JP_BADGE else '<span></span>'
        rows.append(f'''<a class="row" href="{rel(d, page_dir(v["id"]))}"><span class="ver">{esc(v["tag"])}</span><div><h3>{bi(v["title"])}</h3><p>{bi(v["desc"])}</p></div>{badge}</a>''')
    links = [{'href': 'https://apps.apple.com/app/id6759833560', 'label': {'en': 'App Store', 'zh': 'App Store'}},
             {'href': 'https://github.com/waitinghir/jp-knowledge-king', 'label': {'en': 'GitHub', 'zh': 'GitHub'}}]
    main = f'''<div class="page-head">
    <h1>{bi(JP_NAME)}</h1>
    <p class="lead">{site["jpquiz"]["intro"]}</p>
    <div class="meta"><span><span class="lang-en">Currently v1.8.0</span><span class="lang-zh">目前 v1.8.0</span></span></div>
    {head_links(links)}
  </div>
  <div class="list">{"".join(rows)}</div>
  <div class="gallery">{transform(site["jpquiz"]["gallery"], d)}</div>'''
    crumbs = [('<span class="lang-en">Home</span><span class="lang-zh">首頁</span>', ''), (bi(JP_NAME), d)]
    return write(d, layout(d, 'Nihongo Quiz King — Tim', 'A 1v1 Japanese vocabulary game built solo with AI and live on the App Store, and what building it taught me.', crumbs, main))


def build_article(aid):
    a = site['articles'][aid]
    d = page_dir(aid)
    home = ('<span class="lang-en">Home</span><span class="lang-zh">首頁</span>', '')
    if a['project'] == JP:
        crumbs = [home, (bi(JP_NAME), os.path.join('projects', JP)), (bi(a['title']), d)]
        ver = a['category'].split('—', 1)[-1].strip()
        meta = f'<span>{esc(ver)}</span>'
    else:
        crumbs = [home, (bi(a['title']), d)]
        meta = ''
    if a.get('read'):
        meta += f'<span>{bi(a["read"])}</span>'
    nav = ''
    if a['project'] == JP:
        i = JP_ORDER.index(aid)
        prev_ = JP_ORDER[i - 1] if i > 0 else None
        next_ = JP_ORDER[i + 1] if i < len(JP_ORDER) - 1 else None
        parts = []
        if prev_:
            parts.append(f'<a href="{rel(d, page_dir(prev_))}"><small><span class="lang-en">Previous</span><span class="lang-zh">上一篇</span></small>{bi(site["articles"][prev_]["title"])}</a>')
        if next_:
            parts.append(f'<a class="to-next" href="{rel(d, page_dir(next_))}"><small><span class="lang-en">Next</span><span class="lang-zh">下一篇</span></small>{bi(site["articles"][next_]["title"])}</a>')
        nav = f'<nav class="next" aria-label="More articles">{"".join(parts)}</nav>'
    body = transform(open(os.path.join(SRC, 'content', f'{aid}.html'), encoding='utf-8').read(), d)
    main = f'''<article class="article">
    <div class="page-head">
      <h1>{bi(a["title"])}</h1>
      <div class="meta">{meta}</div>
      {head_links(a["links"])}
    </div>
    <div class="article-body">
{body}
    </div>
    {nav}
  </article>'''
    title = f'{a["title"]["en"]} — Tim'
    desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body.split('</p>', 2)[1] if body.count('</p>') > 1 else body))[:200].strip()
    return write(d, layout(d, title, desc, crumbs, main))


if __name__ == '__main__':
    paths = [build_home(), build_jp_project()] + [build_article(aid) for aid in site['articles']]
    for p in paths:
        print(os.path.relpath(p, ROOT))
