# Portfolio Site — Project Memory

> 給接手開發的 Claude 讀的專案脈絡文件。

---

## 專案概述

Tim 的個人 AI 專案作品集網站，部署在 GitHub Pages。
- **Live URL:** https://waitinghir.github.io/portfolio/
- **Repo:** https://github.com/waitinghir/portfolio
- **Tech:** 單一 HTML 檔案 + 一張圖片，零框架、零建置流程

---

## 檔案結構

```
~/portfolio/
├── index.html      # 整個網站（所有頁面、文章、CSS、JS 都在這一個檔案裡）
├── cny-cover.png   # 新春大作戰的封面截圖
├── README.md       # Repo 說明
└── MEMORY.md       # 本文件
```

---

## 網站架構

### 頁面導航
- 單頁應用（SPA），用 JS `showArticle(id)` / `showHome()` 切換顯示
- 首頁（home-page）：Hero → Projects Grid → About → Footer
- 文章頁用 `<div id="article-{id}" class="article-page">` 結構，`.active` 控制顯示

### 專案列表（5 個）

| # | ID | 中文名 | 英文名 | 狀態 |
|---|-----|--------|--------|------|
| 01 | cny | 新春大作戰 | Lunar New Year Challenge | ✅ 文章完成 |
| 02 | jpquiz | 日文知識王 | Japanese Knowledge King | ✅ 有版本索引頁 |
| 02a | jpquiz-v1 | — | From Zero to the App Store | ✅ v1.0→v1.1 文章完成 |
| 02b | jpquiz-v2 | — | Cloud Architecture and N3 Expansion | ✅ v1.2→v1.3 文章完成 |
| 03 | jobgame | 求職遊戲化 | Gamified Job Search | ⬜ Placeholder，文章未寫 |
| 04 | flight | 飛行的回憶 | Memories of Flight | ✅ 文章完成 |
| 05 | i18n | 用 AI 把這個網站雙語化 | Bilingual-izing This Site with AI | ✅ 文章完成 |

### 日文知識王特殊結構
- 卡片點進去是**版本索引頁**（article-jpquiz），列出各版本文章
- 每篇版本文章是獨立的 article-page（article-jpquiz-v1, article-jpquiz-v2）
- Coming Soon 的 v1.4.0+ 卡片用 `opacity:0.4; pointer-events:none` 灰顯

---

## 雙語系統

### 機制
- `<html lang="en">` 屬性控制顯示語言
- CSS: `[lang="en"] .lang-zh { display: none !important; }` 及反向
- 所有可翻譯文字都用 `<span class="lang-en">` / `<span class="lang-zh">` 包裹
- 長篇文章內容：整個 body 包在兩個並列 span 裡（一個 lang-en、一個 lang-zh）
- JS toggle 函式切換 lang 屬性，偏好存 localStorage

### 字型
- 英文: Outfit（display）、JetBrains Mono（mono）
- 中文: Noto Sans TC（透過 font-family fallback）

### 語言切換按鈕
- 在 nav-links 裡，class="lang-toggle"
- 英文模式顯示「中文」，中文模式顯示「EN」

---

## 視覺設計

- 深色科技主題
- 主要配色：cyan (#00e5ff)、magenta (#ff006e)、violet (#8b5cf6)、emerald (#10b981)
- 每個專案卡片有對應的 accent color（data-accent 屬性）
- 背景：grid pattern + 三顆模糊光球（orb）+ noise overlay
- 動畫：scroll fade-in（IntersectionObserver）、hover 效果、pulse dot

---

## 外部連結

| 專案 | 產品連結 | GitHub |
|------|---------|--------|
| 新春大作戰 | https://waitinghir.github.io/Lunar-New-Year-game/ | https://github.com/waitinghir/Lunar-New-Year-game |
| 日文知識王 | https://apps.apple.com/app/id6759833560 | https://github.com/waitinghir/jp-knowledge-king |
| 飛行的回憶 | https://waitinghir.github.io/flight-of-memories/ | https://github.com/waitinghir/flight-of-memories |

---

## 開發注意事項

1. **單檔結構**：所有 CSS、HTML、JS 都在 index.html 裡，目前約 1,400+ 行
2. **編輯策略**：不要一次重寫整個檔案，用 str_replace 分段編輯。一次改完會因為體量太大而失敗（這個教訓已經寫成文章了）
3. **部署**：`git push` 到 main branch，GitHub Pages 自動部署，通常 1-2 分鐘生效
4. **快取問題**：更新後需 Cmd+Shift+R 強制刷新才能看到變化
5. **圖片**：目前只有 cny-cover.png，其他專案未放截圖。圖片和 index.html 要在同一目錄
6. **Tim 的偏好**：
   - 與 Tim 用中文對話時，一律使用正體中文（繁體中文）
   - 文章英文為主，中文為翻譯版
   - 專案名稱保留原始中文名

---

## 待辦事項

- [ ] 求職遊戲化（jobgame）文章——等 Tim 提供摘要
- [ ] 各專案補截圖（目前只有新春大作戰有封面圖）
- [ ] 日文知識王後續版本文章（v1.4.0+）
- [ ] 校正中文翻譯品質（Tim 尚未校稿）
- [ ] nav 裡的 Contact email 和 footer 的 LinkedIn/GitHub 連結待填入真實網址
