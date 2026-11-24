"""Render tools/og.html to assets/og.png (1200x630), the image shown when a page is shared.

Run: python3 tools/og.py   (needs Node + Playwright; only rerun when the card design changes)
"""
import os, subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js = f"""
const {{chromium}} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{viewport: {{width: 1200, height: 630}}, deviceScaleFactor: 1}});
  await p.goto('file://{root}/tools/og.html');
  await p.waitForSelector('body[data-ready]', {{timeout: 15000}});
  await p.screenshot({{path: '{root}/assets/og.png'}});
  await b.close();
}})();
"""
subprocess.run(['node', '-e', js], check=True)
print('wrote assets/og.png')
