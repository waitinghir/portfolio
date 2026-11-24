"""Build the static site from src/.

    python3 tools/build.py

Writes index.html and projects/**/index.html. The generated HTML is committed,
so GitHub Pages serves it with no build step. Edit src/ (article bodies in
src/content/, everything else in src/site.json or the templates below), then
run this script and commit both.

Design: direction 10 (kana particle hero, Unbounded + Manrope, electric blue)
with Japanese accents from direction 3 (seal, vertical section labels).
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
site = json.load(open(os.path.join(SRC, 'site.json'), encoding='utf-8'))

JP = 'nihongo-quiz-king'
JP_NAME = {'en': 'Nihongo Quiz King', 'zh': '日文知識王'}
JP_DESC = {'en': 'A 1v1 Japanese vocabulary game I built solo with AI. Four write-ups on testing AI-written content, scaling it, and finding out why new players leave.',
           'zh': '一款我一個人和 AI 一起做的 1v1 日文單字對戰遊戲。四篇文章，寫怎麼檢驗 AI 產出的內容、讓它規模化，以及找出新玩家為什麼離開。'}
JP_ORDER = ['jpquiz-v1', 'jpquiz-v4', 'jpquiz-v5', 'jpquiz-v6']
JP_BADGE = {'jpquiz-v4': {'en': 'Start here', 'zh': '從這篇開始'}, 'jpquiz-v6': {'en': 'In progress', 'zh': '持續更新'}}
DECK = ['jobmonitor', 'cny', 'flight', 'i18n']
DECK_VIS = {
    'cny': '<img src="{pre}cny-cover.png" alt="" loading="lazy">',
    'flight': '<img src="{pre}images/flight-title.jpg" alt="" loading="lazy">',
}
EMAIL = 'waitinghir@gmail.com'
LINKS = [('LinkedIn', 'https://www.linkedin.com/in/weitim/'), ('GitHub', 'https://github.com/waitinghir')]
FONTS = ('https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;800&family=Manrope:wght@400;500;600;700;800'
         '&family=Shippori+Mincho+B1:wght@700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap')


def esc(s):
    return html.escape(s, quote=True)


def bi(p, tag='span'):
    """Bilingual inline text from a {'en','zh'} pair."""
    if p['en'] == p['zh']:
        return esc(p['en'])
    return f'<{tag} class="lang-en">{esc(p["en"])}</{tag}><{tag} class="lang-zh">{esc(p["zh"])}</{tag}>'


def T(en, zh):
    return bi({'en': en, 'zh': zh})


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


def vlab(jp, en, zh=None):
    return f'<div class="vlab" aria-hidden="true">{jp}<small>{en}</small></div>'


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
    flinks = ''.join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + f'<a href="mailto:{EMAIL}">Email</a>'
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
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{pre}assets/site.css">
<script src="{pre}assets/site.js"></script>
</head>
<body>
<div class="w">
<header class="top">
  <a class="seal" href="{pre}" aria-label="Home">ティ<br>ム</a>
  <a class="brand" href="{pre}">Tim<b>.</b></a>
  <a class="n" href="{pre}#work">{T("Work", "作品")}</a>
  <a class="n" href="{pre}#about">{T("About", "關於")}</a>
  <button class="lang" id="lang-toggle" type="button"><span class="lang-en">中文</span><span class="lang-zh">EN</span></button>
</header>
{crumb_html}
{main}
<footer id="contact"><span>© 2026 Tim Ho</span><span class="flinks">{flinks}</span></footer>
</div>
</body>
</html>
'''


def write(d, content):
    path = os.path.join(ROOT, d, 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)
    return path


def arts_list(d):
    out = []
    for v in site['jpquiz']['versions']:
        out.append(f'<a href="{rel(d, page_dir(v["id"]))}"><span><span class="v">{esc(v["tag"])}</span><span class="t">{bi(v["title"])}</span></span><span class="go" aria-hidden="true">→</span></a>')
    return ''.join(out)


def build_home():
    d = ''
    cards = {c['id']: c for c in site['cards']}
    stats = site['about']['stats']
    chips = ''.join(f'<span><b>{esc(s["value"])}</b>{bi(s["label"])}</span>' for s in stats)
    shots = lambda l: ''.join(f'<img src="images/jpquiz-{n}-{l}.jpg" alt="" loading="lazy">' for n in ('home', 'today', 'result'))
    deck = []
    for i, aid in enumerate(DECK):
        a, c = site['articles'][aid], cards[aid]
        cat = a['category'].split('—', 1)[-1].strip()
        vis = f'\n      <div class="vis" aria-hidden="true">{DECK_VIS[aid].format(pre="")}</div>' if aid in DECK_VIS else ''
        deck.append(f'''<a class="cardx c{i}{"" if vis else " novis"}" href="{page_dir(aid).replace(os.sep, "/")}/" style="--i:{i}">
      <div><span class="k">{esc(cat)}</span><h3>{bi(a["title"])}</h3><p>{bi(c["desc"])}</p><span class="cta">{T("Read", "閱讀")} →</span></div>{vis}
    </a>''')
    facts = ''.join(f'<div><b>{esc(s["value"])}</b><span>{bi(s["label"])}</span></div>' for s in stats)
    links = ''.join(f'<a href="{u}" target="_blank" rel="noopener">{n} ↗</a>' for n, u in LINKS)
    main = f'''<div class="stage" id="stage" data-words="Product.|Growth.|AI.|Tim." aria-hidden="true"><canvas></canvas><span class="hint">{T("move here · tap to change", "滑過這裡 · 點一下換字")}</span></div>
<section class="intro">
  <div><h1 class="disp"><span class="lang-en">Product and growth, <span class="hl">built with AI.</span></span><span class="lang-zh">產品與成長，<span class="hl">用 AI 實作。</span></span></h1>
  <div class="chips">{chips}</div></div>
  <p>{bi(site["hero"]["subtitle"])}</p>
  <div class="vtag" aria-hidden="true">AIで、つくる。</div>
</section>
<section class="sec" id="work">{vlab("作品", "WORK")}<div>
  <h2 class="h2">{T("Selected work", "精選作品")}</h2>
  <article class="feat">
    <a href="projects/{JP}/" aria-label="{esc(JP_NAME["en"])}"><div class="tilt lang-en">{shots("en")}</div><div class="tilt lang-zh">{shots("zh")}</div></a>
    <div><span class="kick">{T("Live on the App Store · 4 articles", "已上架 App Store · 4 篇文章")}</span>
      <h3><a href="projects/{JP}/">{bi(JP_NAME)}</a></h3><p>{bi(JP_DESC)}</p>
      <a class="more" href="projects/{JP}/">{T("Project page, with the data", "專案頁與數據")} →</a>
      <div class="arts">{arts_list(d)}</div></div>
  </article>
</div></section>
<section class="sec">{vlab("記録", "NOTES")}<div>
  <h2 class="h2">{T("More projects", "其他專案")}</h2>
  <div class="deck">{"".join(deck)}</div>
</div></section>
<section class="sec" id="about">{vlab("略歴", "ABOUT")}<div class="about">
  <div class="txt"><h2 class="h2">{T("About", "關於我")}</h2><div class="lang-en">{site["about"]["en"]}</div><div class="lang-zh">{site["about"]["zh"]}</div></div>
  <div><div class="facts">{facts}</div><a class="mag" href="mailto:{EMAIL}">{EMAIL} →</a><div class="links">{links}</div></div>
</div></section>'''
    return write(d, layout(d, 'Tim Ho — Product & Growth × AI', 'Product and growth leader building and shipping products with AI, and writing up the judgment calls behind them.', None, main))


def chart_bars(data, mx, unit, lang):
    W, H, bw = 300, 170, 64
    gap = (W - len(data) * bw) / (len(data) + 1)
    out = [f'<svg viewBox="0 0 {W} {H + 34}" role="img"><line x1="0" x2="{W}" y1="{H}" y2="{H}" stroke="#0d0f1a"/>']
    for i, (lab, v, base) in enumerate(data):
        h = v / mx * H * .85
        x = gap + i * (bw + gap)
        fill = '#2f5bff' if i == len(data) - 1 else ('#d9dde8' if base else '#b9c6f5')
        out.append(f'<rect class="bar" style="animation-delay:{i * .15}s" x="{x:.1f}" y="{H - h:.1f}" width="{bw}" height="{h:.1f}" rx="8" fill="{fill}"/>'
                   f'<text class="val" x="{x + bw / 2:.1f}" y="{H - h - 8:.1f}" text-anchor="middle">{v:g}{unit}</text>'
                   f'<text x="{x + bw / 2:.1f}" y="{H + 20}" text-anchor="middle">{esc(lab[lang])}</text>')
    out.append('</svg>')
    return ''.join(out)


def chart_speed(lang):
    rows = [({'en': 'answers in 3 seconds', 'zh': '每題 3 秒作答'}, 64, '#2f5bff'), ({'en': 'answers in 7 seconds', 'zh': '每題 7 秒作答'}, 25, '#ff6b4a')]
    out = ['<svg viewBox="0 0 300 150" role="img">']
    for i, (lab, v, col) in enumerate(rows):
        out.append(f'<text x="0" y="{26 + i * 62}">{esc(lab[lang])}</text><rect class="hbar" style="animation-delay:{i * .15}s" x="0" y="{34 + i * 62}" width="{v / 100 * 240:.1f}" height="22" rx="6" fill="{col}"/>'
                   f'<text class="val" x="{v / 100 * 240 + 8:.1f}" y="{51 + i * 62}">{v}%</text>')
    out.append('</svg>')
    return ''.join(out)


def bil_svg(fn):
    return f'<div class="lang-en">{fn("en")}</div><div class="lang-zh">{fn("zh")}</div>'


def build_jp_project():
    d = os.path.join('projects', JP)
    B, A, BASE = {'en': 'before', 'zh': '之前'}, {'en': 'after', 'zh': '之後'}, {'en': 'baseline', 'zh': '基準'}
    charts = [
        ({'en': 'ACQUISITION', 'zh': '獲取'}, {'en': 'Organic first downloads, 4 weeks', 'zh': '自然首次下載（四週）'},
         bil_svg(lambda l: chart_bars([(B, 11, 0), (A, 24, 0)], 26, '', l)),
         {'en': 'App Store Connect. After the kana and N5 levels and a new store page. No paid ads.', 'zh': 'App Store Connect。加入假名和 N5、換了商店頁之後。沒有付費推廣。'}),
        ({'en': 'CONVERSION', 'zh': '轉換'}, {'en': 'Store page → download', 'zh': '商店頁 → 下載'},
         bil_svg(lambda l: chart_bars([(B, 11.0, 0), (BASE, 14.2, 1), (A, 19.5, 0)], 21, '%', l)),
         {'en': 'App Store Connect, 4 weeks before vs after.', 'zh': 'App Store Connect，前後各四週。'}),
        ({'en': 'RETENTION', 'zh': '留存'}, {'en': 'First-match win rate, player at 50% accuracy', 'zh': '正確率 50% 的玩家，第一場勝率'},
         bil_svg(chart_speed),
         {'en': 'Simulation. Speed matters about as much as accuracy.', 'zh': '模擬結果。速度的影響和正確率差不多大。'}),
    ]
    ch = ''.join(f'<div class="ch"><span class="k">{bi(k)}</span><h3>{bi(t)}</h3>{svg}<div class="src">{bi(s)}</div></div>' for k, t, svg, s in charts)
    rows = []
    for v in site['jpquiz']['versions']:
        badge = f'<span class="badge">{bi(JP_BADGE[v["id"]])}</span>' if v['id'] in JP_BADGE else '<span></span>'
        rows.append(f'<a href="{rel(d, page_dir(v["id"]))}"><span class="v">{esc(v["tag"])}</span><div><h3>{bi(v["title"])}</h3><p>{bi(v["desc"])}</p></div>{badge}<span class="go" aria-hidden="true">→</span></a>')
    main = f'''<section class="phead">
  <div><span class="jp">日文知識王</span><h1 class="disp">{bi(JP_NAME)}</h1><p>{bi(JP_DESC)}</p>
  <div class="btns"><a class="btn f" href="https://apps.apple.com/app/id6759833560" target="_blank" rel="noopener">App Store</a><a class="btn" href="https://github.com/waitinghir/jp-knowledge-king" target="_blank" rel="noopener">GitHub</a><span class="btn" style="background:transparent;padding-inline:4px">{T("Currently v1.8.0", "目前 v1.8.0")}</span></div></div>
  <div class="vtag" aria-hidden="true">一人で、AIと。</div>
</section>
<section class="sec">{vlab("成果", "RESULTS")}<div>
  <div class="charts">{ch}</div>
  <p class="note">{T("Small numbers from a solo app: a handful of new players each week. They come from my own weekly data review, after removing my devices and App Store review devices.", "一人開發的小規模數據：每週只有幾位新玩家。來自我每週的數據檢查，已排除我自己和 App Store 審查員的裝置。")}</p>
</div></section>
<section class="sec">{vlab("記事", "ARTICLES")}<div class="rows">{"".join(rows)}</div></section>
<section class="sec">{vlab("画面", "SCREENS")}<div class="screens">{transform(site["jpquiz"]["gallery"], d)}</div></section>'''
    crumbs = [(T('Home', '首頁'), ''), (bi(JP_NAME), d)]
    return write(d, layout(d, 'Nihongo Quiz King — Tim Ho', 'A 1v1 Japanese vocabulary game built solo with AI and live on the App Store, with results and four write-ups.', crumbs, main))


def head_links(links):
    out = []
    for i, l in enumerate(links):
        lab = {'en': clean_label(l['label']['en']), 'zh': clean_label(l['label']['zh'])}
        out.append(f'<a class="btn{" f" if i == 0 else ""}" href="{esc(l["href"])}" target="_blank" rel="noopener">{bi(lab)}</a>')
    return f'<div class="btns">{"".join(out)}</div>' if out else ''


def build_article(aid):
    a = site['articles'][aid]
    d = page_dir(aid)
    home = (T('Home', '首頁'), '')
    if a['project'] == JP:
        crumbs = [home, (bi(JP_NAME), os.path.join('projects', JP)), (bi(a['title']), d)]
        kick = f'<span class="ver">{esc(a["category"].split("—", 1)[-1].strip())}</span>'
    else:
        crumbs = [home, (bi(a['title']), d)]
        kick = f'<span class="ver">{esc(a["category"].split("—", 1)[-1].strip())}</span>'
    meta = kick + (f'<span>{bi(a["read"])}</span>' if a.get('read') else '')
    nav = ''
    if a['project'] == JP:
        i = JP_ORDER.index(aid)
        parts = []
        if i > 0:
            pv = JP_ORDER[i - 1]
            parts.append(f'<a href="{rel(d, page_dir(pv))}"><small>{T("Previous", "上一篇")}</small>{bi(site["articles"][pv]["title"])}</a>')
        if i < len(JP_ORDER) - 1:
            nx = JP_ORDER[i + 1]
            parts.append(f'<a class="to-next" href="{rel(d, page_dir(nx))}"><small>{T("Next", "下一篇")}</small>{bi(site["articles"][nx]["title"])}</a>')
        nav = f'<nav class="next" aria-label="More articles">{"".join(parts)}</nav>'
    body = transform(open(os.path.join(SRC, 'content', f'{aid}.html'), encoding='utf-8').read(), d)
    main = f'''<div class="art">{vlab("記事", "ARTICLE")}<article>
  <div class="ahead"><div class="meta">{meta}</div><h1 class="disp">{bi(a["title"])}</h1>{head_links(a["links"])}</div>
  <div class="article-body">
{body}
  </div>
  {nav}
</article></div>'''
    title = f'{a["title"]["en"]} — Tim Ho'
    desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body.split('</p>', 2)[1] if body.count('</p>') > 1 else body))[:200].strip()
    return write(d, layout(d, title, desc, crumbs, main))


if __name__ == '__main__':
    paths = [build_home(), build_jp_project()] + [build_article(aid) for aid in site['articles']]
    for p in paths:
        print(os.path.relpath(p, ROOT))
