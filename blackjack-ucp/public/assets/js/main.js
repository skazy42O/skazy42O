(function () {
  'use strict';

  // Mobilni meni
  var nav = document.querySelector('.nav');
  var tog = document.querySelector('.nav-toggle');
  if (tog && nav) {
    tog.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      tog.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('open'); });
    });
  }

  // Kopiraj IP
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var txt = b.getAttribute('data-copy');
      var done = function () {
        var s = b.querySelector('span');
        b.classList.add('ok');
        if (s) s.textContent = 'Kopirano!';
        setTimeout(function () { b.classList.remove('ok'); if (s) s.textContent = 'Kopiraj'; }, 1800);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(txt).then(done);
      } else {
        var t = document.createElement('textarea');
        t.value = txt; document.body.appendChild(t); t.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        t.remove();
      }
    });
  });

  // Prikazi / sakrij lozinku
  document.querySelectorAll('.eye').forEach(function (b) {
    b.addEventListener('click', function () {
      var i = b.parentNode.querySelector('input');
      i.type = i.type === 'password' ? 'text' : 'password';
    });
  });

  // Jacina lozinke
  document.querySelectorAll('[data-strength]').forEach(function (inp) {
    var form = inp.closest('form');
    var bar = form && form.querySelector('.strength');
    if (!bar) return;
    inp.addEventListener('input', function () {
      var v = inp.value, lvl = 0;
      if (v.length >= 6) lvl++;
      if (v.length >= 10) lvl++;
      if (/[A-Z]/.test(v) && /[a-z]/.test(v)) lvl++;
      if (/\d/.test(v) && /[^A-Za-z0-9]/.test(v)) lvl++;
      if (!v) lvl = 0;
      bar.setAttribute('data-lvl', String(Math.max(v ? 1 : 0, lvl)));
    });
  });

  // Provera RP imena uzivo
  var hint = document.querySelector('[data-name-hint]');
  if (hint) {
    var ni = hint.parentNode.querySelector('input');
    var base = hint.textContent;
    var re = /^[A-Z][a-zA-Z]{1,15}_[A-Z][a-zA-Z]{1,15}$/;
    ni.addEventListener('input', function () {
      var v = ni.value.trim(), box = ni.parentNode;
      box.classList.remove('bad', 'good'); hint.classList.remove('bad', 'good');
      if (!v) { hint.textContent = base; return; }
      if (re.test(v)) {
        box.classList.add('good'); hint.classList.add('good'); hint.textContent = 'Ime je u ispravnom formatu ✓';
      } else {
        box.classList.add('bad'); hint.classList.add('bad');
        hint.textContent = v.indexOf('_') < 0 ? 'Fali donja crta: Ime_Prezime' : 'Samo slova, oba dela sa velikim početnim slovom.';
      }
    });
  }

  // Lightbox galerija
  var lb = document.querySelector('.lightbox');
  if (lb) {
    var img = lb.querySelector('img'), cap = lb.querySelector('p');
    document.querySelectorAll('a.lb').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        ev.preventDefault();
        img.src = a.href; img.alt = a.dataset.cap || ''; cap.textContent = a.dataset.cap || '';
        lb.hidden = false;
      });
    });
    var close = function () { lb.hidden = true; img.src = ''; };
    lb.addEventListener('click', function (ev) { if (ev.target !== img) close(); });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !lb.hidden) close(); });
  }

  // Live online brojac
  if (window.BJ_STATUS_URL) {
    var p = document.getElementById('st-players');
    var m = document.getElementById('st-max');
    var st = document.getElementById('st-state');
    var refresh = function () {
      fetch(window.BJ_STATUS_URL, { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
        if (!p) return;
        p.textContent = d.online ? d.players : '—';
        m.textContent = d.online ? '/ ' + d.max : '';
        st.textContent = d.online ? 'Server je online' : 'Server je offline';
        document.querySelectorAll('.eyebrow .dot').forEach(function (dot) { dot.classList.toggle('live', !!d.online); });
      }).catch(function () {});
    };
    setInterval(refresh, 30000);
  }
})();
