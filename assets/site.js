// Language toggle shared by every page. Same storage key as the old single-page site.
(function () {
  var root = document.documentElement;
  var lang = 'en';
  try { lang = localStorage.getItem('lang') || 'en'; } catch (e) {}
  if (lang !== 'en' && lang !== 'zh') lang = 'en';
  root.setAttribute('lang', lang === 'zh' ? 'zh-Hant' : 'en');
  root.setAttribute('data-lang', lang);
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('lang-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      lang = root.getAttribute('data-lang') === 'en' ? 'zh' : 'en';
      root.setAttribute('data-lang', lang);
      root.setAttribute('lang', lang === 'zh' ? 'zh-Hant' : 'en');
      try { localStorage.setItem('lang', lang); } catch (e) {}
    });
  });
})();
