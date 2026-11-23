"""One-off: pull content out of the old single-page index.html into src/.
Kept for reference; the new site is built from src/ by tools/build.py."""
import json, re, sys
from bs4 import BeautifulSoup
s = open(sys.argv[1], encoding='utf-8').read()
soup = BeautifulSoup(s, 'html.parser')

SLUG = {  # old article id -> (project, page slug or None for project root)
  'jpquiz-v1': ('nihongo-quiz-king', 'five-decisions'),
  'jpquiz-v4': ('nihongo-quiz-king', 'test-the-reviewer'),
  'jpquiz-v5': ('nihongo-quiz-king', 'scale-needs-a-process'),
  'jpquiz-v6': ('nihongo-quiz-king', 'it-was-the-clock'),
  'jobmonitor': ('job-monitor', None),
  'cny': ('game-feel', None),
  'flight': ('memories-of-flight', None),
  'i18n': ('how-this-portfolio-gets-written', None),
}
def inner(el): return ''.join(str(c) for c in el.contents).strip('\n')
def pair(el):
    en = el.select_one('.lang-en'); zh = el.select_one('.lang-zh')
    if en and zh: return {'en': en.get_text(' ', strip=True), 'zh': zh.get_text(' ', strip=True)}
    t = el.get_text(' ', strip=True); return {'en': t, 'zh': t}

site = {'articles': {}, 'cards': [], 'about': {}, 'hero': {}, 'jpquiz': {}}
for a in soup.select('.article-page'):
    aid = a['id'][len('article-'):]
    body = a.select_one('.article-body')
    if aid == 'jpquiz':
        site['jpquiz']['intro'] = inner(body.find('p', recursive=False)) if body.find('p', recursive=False) else ''
        site['jpquiz']['gallery'] = ''.join(str(d) for d in body.find_all('div', recursive=False) if 'version-list' not in (d.get('class') or []))
        site['jpquiz']['versions'] = []
        for v in a.select('.version-card'):
            oc = v.get('onclick') or ''
            m = re.search(r"showArticle\('([\w-]+)'\)", oc)
            site['jpquiz']['versions'].append({'id': m.group(1) if m else None, 'tag': v.select_one('.version-tag').get_text(strip=True),
                'title': pair(v.select_one('.version-title')), 'desc': pair(v.select_one('.version-desc'))})
        site['jpquiz']['meta_version'] = pair(a.select('.article-meta span')[-1]) if a.select('.article-meta span') else None
        continue
    proj, page = SLUG[aid]
    meta = [x for x in a.select('.article-meta > span')]
    site['articles'][aid] = {
        'project': proj, 'slug': page,
        'category': a.select_one('.article-category').get_text(strip=True),
        'title': pair(a.select_one('.article-h1')),
        'read': pair(meta[-1]) if meta else None,
        'links': [{'href': x.get('href'), 'label': pair(x)} for x in a.select('.article-links a')],
    }
    open(f'src/content/{aid}.html', 'w', encoding='utf-8').write(inner(body).strip() + '\n')

for c in soup.select('.project-card'):
    m = re.search(r"showArticle\('([\w-]+)'\)", c.get('onclick', ''))
    site['cards'].append({'id': m.group(1), 'title': pair(c.select_one('.project-title')),
        'subtitle': pair(c.select_one('.project-subtitle')), 'desc': pair(c.select_one('.project-desc')),
        'tags': [pair(t) for t in c.select('.tag') if not t.find_parent(class_='tag') or True if t.parent.get('class') == ['project-tags']]})
hero = soup.select_one('.hero')
site['hero'] = {'tag': hero.select_one('.hero-tag').get_text(strip=True), 'title': pair(hero.select_one('.hero-title')), 'subtitle': pair(hero.select_one('.hero-subtitle'))}
about = soup.select_one('#about')
site['about'] = {'en': inner(about.select_one('.about-text > .lang-en')).strip(), 'zh': inner(about.select_one('.about-text > .lang-zh')).strip(),
    'stats': [{'value': s.select_one('.stat-value').get_text(strip=True), 'label': pair(s.select_one('.stat-label'))} for s in about.select('.stat-card')]}
json.dump(site, open('src/site.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('articles', list(site['articles']), 'cards', [c['id'] for c in site['cards']], 'versions', [v['id'] for v in site['jpquiz']['versions']])
