/* ============================================================
   AEONIC — shared interactions + tweak application
   Loaded synchronously in <head> so tweaks apply before paint.
   ============================================================ */
(function () {
  var STORE = 'aeonic-tweaks-v3';
  var root = document.documentElement;

  // page tones that render on a light ground (nav text must flip dark when scrolled)
  var LIGHT_THEMES = ['cream','linen','oat','sand','greige','blush','white','slate','fog','mist','sage-light'];
  function __aeIsLight(hex){
    var h = String(hex).replace('#','');
    if (h.length === 3) h = h.replace(/./g, function(c){ return c + c; });
    var n = parseInt(h.slice(0,6), 16);
    if (isNaN(n)) return true;
    var r = (n>>16)&255, g = (n>>8)&255, b = n&255;
    return (r*299 + g*587 + b*114) > 148000;
  }
  // on light tones, flip the top-state nav text dark when there's no dark hero behind it
  function updateNavLight(){
    if (!document.body) return;
    var light = root.classList.contains('is-lighttheme');
    root.classList.toggle('is-navlight', light && !document.querySelector('.hero.has-bg'));
  }
  window.__aeUpdateNavLight = updateNavLight;

  // Dynamically load a Google font family on demand (so theme/font tests work on every page).
  var GF_QS = ':ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap';
  window.aeonicLoadFont = function (family) {
    if (!family || /Helvetica|system-ui|-apple/.test(family)) return;
    var id = 'gf-' + family.replace(/[^A-Za-z0-9]+/g, '');
    if (document.getElementById(id)) return;
    var l = document.createElement('link');
    l.id = id; l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=' + encodeURIComponent(family).replace(/%20/g, '+') + GF_QS;
    document.head.appendChild(l);
  };
  function familyName(stack) {
    if (!stack) return '';
    var m = String(stack).match(/'([^']+)'|^([^,]+)/);
    return (m && (m[1] || m[2]) || '').trim();
  }
  // logo wordmark is always Spectral — ensure it's loaded on every page
  window.aeonicLoadFont('Spectral');

  // Apply a tweak value-set to :root (CSS vars + data-attrs).
  window.applyAeonicTweaks = function (v) {
    if (!v) return;
    if (v.accent)  root.setAttribute('data-accent', v.accent);
    if (v.theme)   root.setAttribute('data-theme', v.theme);
    if (v.hero)    root.setAttribute('data-hero', v.hero);
    if (v.eyebrow) root.setAttribute('data-eyebrow', v.eyebrow);
    if (v.radius)  root.setAttribute('data-radius', v.radius);
    if (v.density) root.setAttribute('data-density', v.density);
    if (v.emph)    root.setAttribute('data-emph', v.emph);
    root.setAttribute('data-texture', v.texture === false ? 'off' : 'on');
    if (v.texstyle) root.setAttribute('data-texstyle', v.texstyle);
    if (v.divider)   root.setAttribute('data-divider', v.divider);
    if (v.btnstyle)  root.setAttribute('data-btnstyle', v.btnstyle);
    if (v.cardstyle) root.setAttribute('data-cardstyle', v.cardstyle);
    if (v.imgtreat)  root.setAttribute('data-imgtreat', v.imgtreat);
    if (v.motion)    root.setAttribute('data-motion', v.motion);
    if (v.rhythm)    root.setAttribute('data-rhythm', v.rhythm);
    if (v.heroDark != null) root.style.setProperty('--hero-dark', String(v.heroDark));
    if (v.serif) { root.style.setProperty('--serif', v.serif); window.aeonicLoadFont(familyName(v.serif)); }
    if (v.serif2) { root.style.setProperty('--serif-2', v.serif2); window.aeonicLoadFont(familyName(v.serif2)); }
    if (v.sans)  { root.style.setProperty('--sans',  v.sans);  window.aeonicLoadFont(familyName(v.sans)); }
    // light/dark page-tone class from the chosen theme (may be overridden by custom bg below)
    root.classList.toggle('is-lighttheme', LIGHT_THEMES.indexOf(v.theme) !== -1);
    // full custom background — paints every section surface from one picked color
    var bgCustom = v.bg && v.bg !== 'auto';
    if (bgCustom) {
      var bl = __aeIsLight(v.bg);
      root.style.setProperty('--bg', v.bg);
      root.style.setProperty('--bg-deep', 'color-mix(in srgb, ' + v.bg + ' 92%, #000)');
      root.style.setProperty('--panel',   'color-mix(in srgb, ' + v.bg + ' 94%, #fff)');
      root.style.setProperty('--panel-2', 'color-mix(in srgb, ' + v.bg + ' 88%, #fff)');
      root.style.setProperty('--card',    'color-mix(in srgb, ' + v.bg + ' 95%, #fff)');
      root.style.setProperty('--line',   bl ? 'rgba(20,16,8,.10)' : 'rgba(234,227,214,.10)');
      root.style.setProperty('--line-2', bl ? 'rgba(20,16,8,.18)' : 'rgba(234,227,214,.17)');
      root.style.setProperty('--wm', bl ? 'color-mix(in srgb, ' + v.bg + ' 88%, #000)' : 'color-mix(in srgb, ' + v.bg + ' 82%, #fff)');
      root.classList.toggle('is-lighttheme', bl);
    } else {
      ['--bg','--bg-deep','--panel','--panel-2','--card','--line','--line-2','--wm'].forEach(function (p) { root.style.removeProperty(p); });
    }
    // text (ink) color override + derived muted tones
    if (v.fg && v.fg !== 'auto') {
      root.style.setProperty('--fg',   v.fg);
      root.style.setProperty('--fg-2', 'color-mix(in srgb, ' + v.fg + ' 62%, var(--bg))');
      root.style.setProperty('--fg-3', 'color-mix(in srgb, ' + v.fg + ' 40%, var(--bg))');
    } else if (bgCustom) {
      // auto-contrast ink so a custom background stays legible
      var ink = __aeIsLight(v.bg) ? '#1c1710' : '#ece6da';
      root.style.setProperty('--fg',   ink);
      root.style.setProperty('--fg-2', 'color-mix(in srgb, ' + ink + ' 62%, var(--bg))');
      root.style.setProperty('--fg-3', 'color-mix(in srgb, ' + ink + ' 40%, var(--bg))');
    } else {
      root.style.removeProperty('--fg'); root.style.removeProperty('--fg-2'); root.style.removeProperty('--fg-3');
    }
    // button color override (filled / outline / soft all key off --btn-bg)
    if (v.btn && v.btn !== 'auto') {
      root.style.setProperty('--btn-bg',    v.btn);
      root.style.setProperty('--btn-hover', 'color-mix(in srgb, ' + v.btn + ' 84%, #000)');
      root.style.setProperty('--btn-fg',    __aeIsLight(v.btn) ? '#1a140a' : '#ffffff');
    } else {
      root.style.removeProperty('--btn-bg'); root.style.removeProperty('--btn-hover'); root.style.removeProperty('--btn-fg');
    }
    // hero CTA color overrides (primary fill + text, secondary border+text)
    if (v.heroBtnBg) root.style.setProperty('--hero-btn-bg', v.heroBtnBg); else root.style.removeProperty('--hero-btn-bg');
    if (v.heroBtnFg) root.style.setProperty('--hero-btn-fg', v.heroBtnFg); else root.style.removeProperty('--hero-btn-fg');
    if (v.heroBtn2)  root.style.setProperty('--hero-btn2',   v.heroBtn2);  else root.style.removeProperty('--hero-btn2');
    // nav legibility class: custom bg wins (set above), else follows theme
    if (!bgCustom) root.classList.toggle('is-lighttheme', LIGHT_THEMES.indexOf(v.theme) !== -1);
    updateNavLight();
  };

  // Read persisted tweaks and apply immediately (pre-paint).
  // When nothing is saved, fall back to the locked brand defaults.
  var DEFAULTS = {
    theme: 'graphite', accent: 'greige-accent', radius: 'round', density: 'normal',
    emph: 'upright', hero: 'editorial', eyebrow: 'line', texture: true, texstyle: 'glow',
    divider: 'line', btnstyle: 'soft', cardstyle: 'glass', imgtreat: 'full-color',
    motion: 'lively', rhythm: 'subtle', heroDark: 0.5,
    serif:  "'Helvetica Neue', Helvetica, Arial, sans-serif",
    serif2: "'Helvetica Neue', Helvetica, Arial, sans-serif",
    sans:   "'Mona Sans', system-ui, sans-serif",
    heroBtnBg: '#9a604c',
    heroBtnFg: '#ffffff',
    heroBtn2: '#ffffff'
  };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    window.applyAeonicTweaks(saved || DEFAULTS);
  } catch (e) { window.applyAeonicTweaks(DEFAULTS); }

  // Expose for the React panel to mirror cross-page.
  window.AEONIC_STORE = STORE;

  // reset page-transition fade if restored from bfcache (back/forward)
  window.addEventListener('pageshow', function () { document.body.classList.remove('pt-leaving'); });

  // ---- interactions ----
  document.addEventListener('DOMContentLoaded', function () {
    updateNavLight();

    // hero video bed — fade in once it can actually play (kills the poster flash)
    document.querySelectorAll('.hero__video').forEach(function (v) {
      var show = function () { v.classList.add('is-ready'); };
      if (v.readyState >= 3) show();
      else { v.addEventListener('canplay', show); v.addEventListener('playing', show); v.addEventListener('loadeddata', show); }
      var p = v.play && v.play(); if (p && p.catch) p.catch(function(){});
    });

    // guarantee the header logo always links home (System)
    document.querySelectorAll('.nav .brand').forEach(function (a) {
      a.setAttribute('href', 'aeonic-systems.html');
      a.addEventListener('click', function (e) { e.preventDefault(); window.location.href = 'aeonic-systems.html'; });
    });

    // generic card sliders: <div data-cardslider> with .cslider__track + [data-slider-prev]/[data-slider-next]
    document.querySelectorAll('[data-cardslider]').forEach(function (root) {
      var track = root.querySelector('.cslider__track');
      var prev = root.querySelector('[data-slider-prev]');
      var next = root.querySelector('[data-slider-next]');
      if (!track) return;
      var step = function () {
        var card = track.querySelector('.fcard, .whocard, :scope > *');
        var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || '14') || 14;
        return card ? card.getBoundingClientRect().width + gap : 300;
      };
      var sync = function () {
        var max = track.scrollWidth - track.clientWidth - 2;
        if (prev) prev.disabled = track.scrollLeft <= 2;
        if (next) next.disabled = track.scrollLeft >= max;
      };
      if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: 'smooth' }); });
      if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: 'smooth' }); });
      track.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);
      sync();
    });

    // in-page section nav: scroll-spy + smooth offset
    (function () {
      var secnav = document.querySelector('.secnav');
      if (!secnav) return;
      var links = [].slice.call(secnav.querySelectorAll('a[href^="#"]'));
      if (!links.length) return;
      var targets = links.map(function (a) {
        var el = document.getElementById(a.getAttribute('href').slice(1));
        return el ? { a: a, el: el } : null;
      }).filter(Boolean);
      function spy() {
        var y = window.scrollY + secnav.getBoundingClientRect().height + 120;
        var cur = targets[0];
        for (var i = 0; i < targets.length; i++) {
          if (targets[i].el.offsetTop <= y) cur = targets[i];
        }
        links.forEach(function (a) { a.classList.toggle('is-active', cur && a === cur.a); });
      }
      window.addEventListener('scroll', spy, { passive: true });
      spy();
      // offset smooth-scroll so the sticky bar doesn't cover the heading
      targets.forEach(function (t) {
        t.a.addEventListener('click', function (e) {
          e.preventDefault();
          var top = t.el.getBoundingClientRect().top + window.scrollY - secnav.getBoundingClientRect().height - 12;
          window.scrollTo({ top: top, behavior: 'smooth' });
        });
      });
    })();
    // property-aware home link: clicking the header logo returns you to the
    // home of whichever property you're in (Systems / Health / Connect).
    (function () {
      var PROP_HOME = {
        systems: 'aeonic-systems.html',
        health:  'aeonic-health.html',
        connect: 'aeonic-connect.html'
      };
      var prop = (document.body.getAttribute('data-prop') || 'systems');
      var home = PROP_HOME[prop] || 'aeonic-systems.html';
      var brand = document.querySelector('.nav .brand');
      if (brand) brand.setAttribute('href', home);

      // The Systems home was historically linked as the (non-existent) index.html.
      // Repoint every such link — the property switch, footer, breadcrumbs, About
      // links — to the real Systems homepage, preserving any #hash.
      [].slice.call(document.querySelectorAll('a[href^="index.html"]')).forEach(function (a) {
        var href = a.getAttribute('href') || '';
        a.setAttribute('href', href.replace(/^index\.html/, 'aeonic-systems.html'));
      });
    })();

    // sticky nav shadow + fade-in on load
    var nav = document.querySelector('.nav');
    if (nav) {
      var onScroll = function () { nav.classList.toggle('is-stuck', window.scrollY > 8); };
      onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
      requestAnimationFrame(function () { nav.classList.add('nav--in'); });
      // safety: ensure the header is visible even if the transition clock stalls
      setTimeout(function () { nav.classList.add('nav--in'); nav.style.opacity = '1'; nav.style.transform = 'none'; }, 1300);
    }

    // mobile sheet
    var burger = document.querySelector('.burger');
    var sheet = document.querySelector('.sheet');
    // ---- unified mobile menu — one persistent accordion, identical on every page ----
    if (sheet) {
      var MENU = [
        { key:'system', label:'System', href:'aeonic-systems.html' },
        { key:'programs', label:'Program', href:'aeonic-health.html' },
        { key:'platform', label:'Platform', href:'aeonic-connect.html' },
        { key:'aura', label:'Aeva', href:'aeva.html' },
        { key:'pricing', label:'Plans', href:'pricing.html' },
        { key:'catalog', label:'Catalog', href:'aeonic-store.html' },
        { key:'about', label:'About', href:'our-story.html' }
      ];
      var here = (location.pathname.split('/').pop() || 'aeonic-systems.html');
      var prop = document.body.getAttribute('data-prop') || '';
      var propKey = { systems:'system', health:'programs', connect:'platform' }[prop] || '';
      var currentKey = null;
      MENU.forEach(function (sec) {
        if (sec.items && sec.items.some(function (it) { return Array.isArray(it) && it[0].split('#')[0] === here; })) currentKey = sec.key;
      });
      var openKey = currentKey || propKey || 'system';
      var h = '<div class="msheet">';
      h += '<div class="msheet__top"><a class="brand" href="aeonic-systems.html"><span class="brand__mark"></span><span class="brand__word">Aeonic</span></a><button class="msheet__close" type="button" aria-label="Close menu">\u2715</button></div>';
      MENU.forEach(function (sec) {
        if (sec.href) {
          var lc = sec.href.split('#')[0] === here ? ' aria-current="page"' : '';
          h += '<a class="msheet__parent msheet__parent--link" href="' + sec.href + '"' + lc + '>' + sec.label + '<span class="msheet__go">\u2192</span></a>';
          return;
        }
        var on = sec.key === openKey;
        h += '<button class="msheet__parent' + (on ? ' open' : '') + '" type="button" aria-expanded="' + (on ? 'true' : 'false') + '">' + sec.label + '<span class="msheet__chev"></span></button>';
        h += '<div class="msheet__panel' + (on ? ' open' : '') + '">';
        sec.items.forEach(function (it) {
          if (Array.isArray(it)) {
            var cur = it[0].split('#')[0] === here ? ' aria-current="page"' : '';
            h += '<a href="' + it[0] + '"' + cur + '>' + it[1] + '</a>';
          } else if (it.sub) {
            h += '<span class="msheet__sub">' + it.sub + '</span>';
          }
        });
        h += '</div>';
      });
      h += '<div class="msheet__actions"><a class="btn btn--primary" href="connect-inquiry.html">Get started <span class="arw">\u2192</span></a><a class="btn btn--ghost" href="aeonic-systems-login.html">Log in</a></div><a class="msheet__dtc" href="https://wellness.aeonic.com" target="_blank" rel="noopener"><span class="brand"><span class="brand__mark"></span><span class="brand__word">Aeonic</span><span class="brand__tag">Health</span></span></a>';
      h += '</div>';
      sheet.innerHTML = h;
      sheet.querySelectorAll('button.msheet__parent').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var willOpen = !btn.classList.contains('open');
          sheet.querySelectorAll('button.msheet__parent').forEach(function (b) {
            b.classList.remove('open'); b.setAttribute('aria-expanded', 'false');
            if (b.nextElementSibling) b.nextElementSibling.classList.remove('open');
          });
          if (willOpen) { btn.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); btn.nextElementSibling.classList.add('open'); }
        });
      });
      var scrim = document.createElement('div');
      scrim.className = 'sheet-scrim';
      document.body.appendChild(scrim);
      scrim.addEventListener('click', function () { sheet.classList.remove('open'); scrim.classList.remove('show'); document.body.style.overflow = ''; });
      sheet._scrim = scrim;
      var closeBtn = sheet.querySelector('.msheet__close');
      if (closeBtn) closeBtn.addEventListener('click', function () { sheet.classList.remove('open'); scrim.classList.remove('show'); document.body.style.overflow = ''; });
    }
    if (burger && sheet) {
      burger.addEventListener('click', function () {
        var open = sheet.classList.toggle('open');
        document.body.style.overflow = open ? 'hidden' : '';
        if (sheet._scrim) sheet._scrim.classList.toggle('show', open);
      });
      sheet.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { sheet.classList.remove('open'); if (sheet._scrim) sheet._scrim.classList.remove('show'); document.body.style.overflow = ''; });
      });
    }

    // dropdown nav — hover works via CSS; this adds click/touch toggle + outside-close
    var ddItems = [].slice.call(document.querySelectorAll('.nav__item'));
    ddItems.forEach(function (item) {
      var trig = item.querySelector('.nav__trigger');
      if (!trig) return;
      trig.addEventListener('click', function (e) {
        e.preventDefault();
        var wasOpen = item.classList.contains('open');
        ddItems.forEach(function (i) { i.classList.remove('open'); });
        if (!wasOpen) item.classList.add('open');
      });
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.nav__item')) ddItems.forEach(function (i) { i.classList.remove('open'); });
    });

    // scroll-spy: bold the nav item whose section is in view
    var spyMap = [];
    [].slice.call(document.querySelectorAll('.nav__links > .nav__item')).forEach(function (item) {
      var ids = [].slice.call(item.querySelectorAll('a[href^="#"]')).map(function (a) { return a.getAttribute('href').slice(1); });
      if (ids.length) spyMap.push({ el: item, ids: ids });
    });
    [].slice.call(document.querySelectorAll('.nav__links > a[href^="#"]')).forEach(function (a) {
      spyMap.push({ el: a, ids: [a.getAttribute('href').slice(1)] });
    });
    if (spyMap.length) {
      var spyTick = false;
      var spy = function () {
        spyTick = false;
        var pos = window.scrollY + 130, current = null, best = -Infinity;
        spyMap.forEach(function (m) {
          m.ids.forEach(function (id) {
            var s = document.getElementById(id); if (!s) return;
            var top = s.getBoundingClientRect().top + window.scrollY;
            if (top <= pos && top > best) { best = top; current = m; }
          });
        });
        spyMap.forEach(function (m) { m.el.classList.toggle('is-active', m === current); });
      };
      window.addEventListener('scroll', function () { if (!spyTick) { spyTick = true; requestAnimationFrame(spy); } }, { passive: true });
      spy();
    }

    // accordion
    document.querySelectorAll('.acc__item, .dd-acc__item').forEach(function (item) {
      var q = item.querySelector('.acc__q, .dd-acc__q');
      var a = item.querySelector('.acc__a, .dd-acc__a');
      if (!q || !a) return;
      q.addEventListener('click', function () {
        var open = item.classList.contains('open');
        if (!open) { item.classList.add('open'); a.style.maxHeight = a.scrollHeight + 'px'; }
        else { item.classList.remove('open'); a.style.maxHeight = '0px'; }
      });
    });

    // inline tabs
    document.querySelectorAll('[data-tabs]').forEach(function (group) {
      var btns = [].slice.call(group.querySelectorAll('.tabs__btn'));
      var panels = [].slice.call(group.querySelectorAll('.tabs__panel'));
      btns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var key = btn.getAttribute('data-tab');
          btns.forEach(function (b) { b.classList.toggle('on', b === btn); });
          panels.forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-panel') === key); });
        });
      });
    });

    // page transition — fast fade-IN on load only (no fade-out intercept, which
    // caused a double-flash: fade-out → reload → fade-in). Links navigate instantly;
    // the new page fades in via the .pt-fade CSS animation.
    document.body.classList.add('pt-fade');

    // auth form (prototype) — redirect into the portal app if data-go is set
    document.querySelectorAll('.auth-form').forEach(function (form) {
      var go = form.getAttribute('data-go');
      if (go) {
        // any input + Enter (or empty) should sign in — no validation blocking
        form.noValidate = true;
        form.addEventListener('keydown', function (e) {
          if (e.key === 'Enter') { e.preventDefault(); window.location.href = go; }
        });
      }
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var btn = form.querySelector('button[type="submit"]');
        if (go) {
          if (btn) { btn.textContent = 'Signing in…'; btn.disabled = true; }
          window.location.href = go;
          return;
        }
        var note = form.querySelector('.auth__note');
        if (btn) { btn.textContent = 'Signing in…'; }
        setTimeout(function () {
          if (note) { note.classList.add('show'); }
          if (btn) { btn.textContent = form.getAttribute('data-cta') || 'Log in'; }
        }, 650);
      });
    });

    // scroll reveal — IntersectionObserver (async, no layout thrash = smooth)
    var reveals = [].slice.call(document.querySelectorAll('.reveal'));
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 });
      reveals.forEach(function (el) { io.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add('in'); });
    }
    // safety net: force-show reveals currently in view if the clock is frozen
    // (some capture iframes) — off-screen sections still animate in on scroll.
    function rescueVisible() {
      var vh = window.innerHeight || document.documentElement.clientHeight;
      document.querySelectorAll('.reveal:not(.in)').forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < vh * 0.95 && r.bottom > 0) el.classList.add('in');
      });
      document.querySelectorAll('.reveal.in').forEach(function (el) {
        if (getComputedStyle(el).opacity !== '1') el.classList.add('force-in');
      });
    }
    setTimeout(rescueVisible, 1200);

    // ---- global Aura chat widget (context-aware per page) ----
    (function () {
      return; // Ask Aura tab disabled for now — remove this line to restore
      if (document.querySelector('.aura-fab')) return;
      var prop = (document.body.getAttribute('data-prop') || 'systems');
      var h1 = document.querySelector('h1');
      var section = (h1 ? h1.textContent.trim() : document.title).replace(/\s+/g, ' ').slice(0, 60);
      var ctx = {
        systems: { name: 'Aeonic', sugg: ['What is Aeonic Health Systems?', 'How do the three engines work?', 'Who is Dr. Lacey?'] },
        health:  { name: 'Aeonic Continuum', sugg: ['What treatments do you offer?', 'How does a protocol work?', 'How do I get started?'] },
        connect: { name: 'Aeonic Connect', sugg: ['How does Connect work for my practice?', 'What does the platform include?', 'What are the pricing tiers?'] }
      }[prop] || { name: 'Aeonic', sugg: ['Tell me more about this page.'] };

      var fab = document.createElement('button');
      fab.className = 'aura-fab';
      fab.innerHTML = '<svg class="ax" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l1.4 5.6c.2.7.7 1.2 1.4 1.4L20 10l-5.2 1c-.7.2-1.2.7-1.4 1.4L12 18l-1.4-5.6c-.2-.7-.7-1.2-1.4-1.4L4 10l5.2-1c.7-.2 1.2-.7 1.4-1.4z"/></svg> Ask Aura';

      var chat = document.createElement('div');
      chat.className = 'aura-chat';
      chat.innerHTML =
        '<div class="aura-head"><span class="ah-mark"><img src="assets/aeonic-mark.png" alt="" style="width:22px;height:22px;display:block"></span>' +
        '<div><div class="ah-t">Aeva</div><div class="ah-s">Aeonic Intelligence</div></div>' +
        '<button class="ah-x" aria-label="Close">\u2715</button></div>' +
        '<div class="aura-msgs"></div>' +
        '<div class="aura-sugg"></div>' +
        '<form class="aura-form"><input type="text" placeholder="Ask about ' + (section || 'this page') + '\u2026" autocomplete="off"><button type="submit" aria-label="Send"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg></button></form>' +
        '<div class="aura-note">Aeva is intelligence woven through Aeonic \u2014 informational, not medical advice.</div>';

      document.body.appendChild(fab);
      document.body.appendChild(chat);
      var msgs = chat.querySelector('.aura-msgs');
      var suggWrap = chat.querySelector('.aura-sugg');
      var form = chat.querySelector('.aura-form');
      var input = form.querySelector('input');

      function add(text, who) {
        var m = document.createElement('div');
        m.className = 'aura-m ' + (who || 'bot');
        m.textContent = text;
        msgs.appendChild(m);
        msgs.scrollTop = msgs.scrollHeight;
        return m;
      }
      function renderSugg() {
        suggWrap.innerHTML = '';
        ctx.sugg.forEach(function (q) {
          var b = document.createElement('button');
          b.textContent = q;
          b.addEventListener('click', function () { ask(q); });
          suggWrap.appendChild(b);
        });
      }
      function answer(q) {
        var c = ctx.name;
        var canned = {
          systems: 'Aeonic Health Systems is the clinical infrastructure behind modern longevity medicine \u2014 20+ years of protocols, prescribing, pharmacy, and compliance, built into one system that powers both our own patient care and partner practices. What would you like to explore?',
          health:  'Aeonic Continuum delivers physician-guided, lab-based longevity care \u2014 weight, hormones, peptides, recovery and more \u2014 as an ongoing protocol built around your biomarkers and delivered to your door. Want help finding the right starting point?',
          connect: 'Aeonic Connect gives your practice the full clinical backend \u2014 protocols, prescribing, pharmacy, compliance, and a white-labeled portal \u2014 so you can run longevity medicine under your own brand. Want a walkthrough of the platform or pricing?'
        };
        var base = canned[prop] || 'Here to help with anything on this page.';
        return 'On ' + (section || c) + ': ' + base;
      }
      function ask(q) {
        add(q, 'me');
        input.value = '';
        var thinking = add('\u2026', 'bot');
        setTimeout(function () { thinking.textContent = answer(q); }, 450);
      }
      form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value.trim(); if (v) ask(v); });
      fab.addEventListener('click', function () { chat.classList.add('open'); fab.classList.add('hide'); if (!msgs.children.length) { add('Hi, I\u2019m Aeva \u2014 ask me anything about ' + (section || ctx.name) + '.', 'bot'); } input.focus(); });
      chat.querySelector('.ah-x').addEventListener('click', function () { chat.classList.remove('open'); fab.classList.remove('hide'); });
      renderSugg();
    })();
  });
})();
