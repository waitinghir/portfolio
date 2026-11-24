// Shared by every page: language toggle (same storage key as before), and on the home page
// the kana particle hero, the 3D tilt on screenshots and the magnetic contact button.
(function () {
  var root = document.documentElement, lang = 'en';
  try { lang = localStorage.getItem('lang') || 'en'; } catch (e) {}
  if (lang !== 'en' && lang !== 'zh') lang = 'en';
  function apply() { root.setAttribute('data-lang', lang); root.setAttribute('lang', lang === 'zh' ? 'zh-Hant' : 'en'); }
  apply();
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('lang-toggle');
    if (btn) btn.addEventListener('click', function () {
      lang = lang === 'en' ? 'zh' : 'en'; apply();
      try { localStorage.setItem('lang', lang); } catch (e) {}
    });
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    particles(reduce); tilt(reduce); magnet(reduce);
  });

  function particles(reduce) {
    var stage = document.getElementById('stage'); if (!stage) return;
    var cv = stage.querySelector('canvas'), ctx = cv.getContext('2d');
    var KANA = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノ';
    var COLS = ['#2f5bff', '#2f5bff', '#2f5bff', '#0d0f1a', '#ff6b4a', '#12b98f'];
    var WORDS = (stage.getAttribute('data-words') || 'Product.|Growth.|AI.|Tim.').split('|');
    var W = 0, H = 0, parts = [], wi = 0, mouse = { x: -9999, y: -9999 }, timer;
    function sample(word) {
      var off = document.createElement('canvas'); off.width = W; off.height = H; var o = off.getContext('2d');
      var fs = Math.min(H * .78, W / (word.length * .62)); o.font = '800 ' + fs + 'px Unbounded, sans-serif';
      while (o.measureText(word).width > W * .94 && fs > 20) { fs -= 4; o.font = '800 ' + fs + 'px Unbounded, sans-serif'; }
      o.textAlign = 'center'; o.textBaseline = 'middle'; o.fillText(word, W / 2, H / 2 + fs * .04);
      var d = o.getImageData(0, 0, W, H).data, pts = [], gap = W < 600 ? 4 : 8;
      for (var y = 0; y < H; y += gap) for (var x = 0; x < W; x += gap) if (d[(y * W + x) * 4 + 3] > 128) pts.push([x, y]);
      for (var i = pts.length - 1; i > 0; i--) { var j = Math.random() * (i + 1) | 0, t = pts[i]; pts[i] = pts[j]; pts[j] = t; }
      return pts.slice(0, 1500);
    }
    function setWord() {
      var pts = sample(WORDS[wi % WORDS.length]);
      while (parts.length < pts.length) parts.push({ x: Math.random() * W, y: Math.random() * H, vx: 0, vy: 0, c: KANA[Math.random() * KANA.length | 0], col: COLS[Math.random() * COLS.length | 0], a: 0 });
      parts.forEach(function (q, i) {
        if (i < pts.length) { q.tx = pts[i][0]; q.ty = pts[i][1]; q.on = 1; } else { q.tx = Math.random() * W; q.ty = H + 40; q.on = 0; }
        if (!reduce) { q.vx += (Math.random() - .5) * 18; q.vy += (Math.random() - .5) * 18; }
      });
      if (reduce) { parts.forEach(function (q) { q.x = q.tx; q.y = q.ty; q.a = q.on; }); draw(); }
    }
    function resize() {
      var dpr = Math.min(2, window.devicePixelRatio || 1), r = stage.getBoundingClientRect();
      W = Math.round(r.width); H = Math.round(r.height); cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); setWord();
    }
    function draw() {
      ctx.clearRect(0, 0, W, H); var fs = W < 600 ? 6.5 : 10;
      ctx.font = '600 ' + fs + 'px Manrope, "Hiragino Sans", "Noto Sans JP", sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      for (var i = 0; i < parts.length; i++) { var q = parts[i]; if (q.a < .02) continue; ctx.globalAlpha = q.a; ctx.fillStyle = q.col; ctx.fillText(q.c, q.x, q.y); }
      ctx.globalAlpha = 1;
    }
    function step() {
      var R = W < 600 ? 60 : 110;
      for (var i = 0; i < parts.length; i++) {
        var q = parts[i], dx = q.x - mouse.x, dy = q.y - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < R * R) { var d = Math.sqrt(d2) || 1, f = (R - d) / R * 6; q.vx += dx / d * f; q.vy += dy / d * f; }
        q.vx += (q.tx - q.x) * .045; q.vy += (q.ty - q.y) * .045; q.vx *= .82; q.vy *= .82; q.x += q.vx; q.y += q.vy;
        q.a += ((q.on ? 1 : 0) - q.a) * .08;
      }
      draw(); requestAnimationFrame(step);
    }
    function next() { wi++; setWord(); }
    stage.addEventListener('pointermove', function (e) { var r = stage.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
    stage.addEventListener('pointerleave', function () { mouse.x = mouse.y = -9999; });
    stage.addEventListener('click', function () { next(); clearInterval(timer); if (!reduce) timer = setInterval(next, 3600); });
    function go() { resize(); if (!reduce) { requestAnimationFrame(step); timer = setInterval(next, 3600); } }
    var fontReady = document.fonts && document.fonts.load ? Promise.race([document.fonts.load('800 100px Unbounded'), new Promise(function (r) { setTimeout(r, 1500); })]) : Promise.resolve();
    fontReady.then(go);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(resize, 150); });
  }

  function tilt(reduce) {
    if (reduce) return;
    [].forEach.call(document.querySelectorAll('.tilt'), function (t) {
    t.addEventListener('pointermove', function (e) {
      var r = t.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      [].forEach.call(t.children, function (im, i) { im.style.transform = 'rotateY(' + x * 24 + 'deg) rotateX(' + (-y * 18) + 'deg) translateZ(' + (i === 1 ? 40 : 10) + 'px)'; });
    });
    t.addEventListener('pointerleave', function () { [].forEach.call(t.children, function (im) { im.style.transform = ''; }); });
    });
  }

  function magnet(reduce) {
    if (reduce) return;
    [].forEach.call(document.querySelectorAll('.mag'), function (m) {
      m.addEventListener('pointermove', function (e) { var r = m.getBoundingClientRect(); m.style.transform = 'translate(' + (e.clientX - r.left - r.width / 2) * .18 + 'px,' + (e.clientY - r.top - r.height / 2) * .3 + 'px)'; });
      m.addEventListener('pointerleave', function () { m.style.transform = ''; });
    });
  }
})();
