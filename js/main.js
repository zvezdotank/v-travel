/* =====================================================
   V-travel — интерактив
   Ничего не отправляем на сервер: все заявки уходят
   в Telegram или через звонок.
   ===================================================== */
(function () {
  'use strict';

  var TG_USER = 'vtour_travel';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Telegram deep-link ---------- */
  function tgLink(text) {
    return 'https://t.me/' + TG_USER + (text ? '?text=' + encodeURIComponent(text) : '');
  }

  /* ---------- шапка: фон при скролле ---------- */
  var header = document.getElementById('header');
  var fab = document.getElementById('fab');
  var actionbar = document.getElementById('actionbar');
  var footer = document.querySelector('.footer');

  function onScroll() {
    var y = window.scrollY;
    header.classList.toggle('is-stuck', y > 20);

    // плавающие кнопки появляются после первого экрана
    // и прячутся, когда виден футер с теми же контактами
    var footerTop = footer.getBoundingClientRect().top;
    var show = y > 480 && footerTop > window.innerHeight * 0.9;
    fab.classList.toggle('is-visible', show);
    actionbar.classList.toggle('is-visible', show);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- мобильное меню ---------- */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');

  function closeNav() {
    nav.classList.remove('is-open');
    burger.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
  }

  burger.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    burger.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
  });

  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) closeNav();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeNav();
  });

  /* ---------- появление блоков при скролле ---------- */
  var revealables = document.querySelectorAll('.reveal');

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---------- счётчики в цифрах героя ---------- */
  var counters = document.querySelectorAll('.num[data-count]');

  function runCounter(el) {
    var target = parseInt(el.dataset.count, 10);
    if (reduceMotion) { el.textContent = format(target); return; }

    var start = performance.now();
    var dur = 1400;
    function tick(now) {
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = format(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function format(n) {
    return n >= 1000 ? n.toLocaleString('ru-RU').replace(/,/g, ' ') : String(n);
  }

  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { runCounter(entry.target); cio.unobserve(entry.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(runCounter);
  }

  /* ---------- активный пункт меню ---------- */
  var sections = ['hot', 'dest', 'how', 'reviews', 'pick']
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav__link'));

  if ('IntersectionObserver' in window && sections.length) {
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (l) {
          l.classList.toggle('is-active', l.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { threshold: 0.25, rootMargin: '-30% 0px -55% 0px' });
    sections.forEach(function (s) { sio.observe(s); });
  }

  /* ---------- кнопки «Забронировать» и карточки направлений ---------- */
  document.querySelectorAll('.js-book').forEach(function (el) {
    var tour = el.dataset.tour || '';
    el.setAttribute('target', '_blank');
    el.setAttribute('rel', 'noopener');
    el.href = tgLink('Здравствуйте! Пишу с сайта V-travel. ' + tour + '. Подскажите, пожалуйста, детали.');
  });

  /* ---------- форма подбора → Telegram ---------- */
  var form = document.getElementById('pickForm');
  var hint = document.getElementById('pickHint');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var dest = form.dest.value.trim() || 'Ещё не решили';
      var date = form.date.value.trim() || 'даты гибкие';

      var msg = [
        'Здравствуйте! Заявка на подбор тура с сайта V-travel.',
        '',
        'Направление: ' + dest,
        'Даты: ' + date,
        'Длительность: ' + form.nights.value,
        'Состав: ' + form.people.value,
        'Бюджет на человека: ' + form.budget.value,
        '',
        'Жду варианты 🙂'
      ].join('\n');

      var win = window.open(tgLink(msg), '_blank', 'noopener');

      if (hint) {
        hint.textContent = win
          ? 'Открыли Telegram — заявка уже вписана, нажмите «Отправить».'
          : 'Не удалось открыть Telegram. Напишите @vtour_travel или позвоните +998 90 317-22-88.';
        hint.style.color = win ? 'var(--cyan)' : 'var(--gold)';
      }
    });
  }

  /* ---------- плавный скролл с учётом высоты шапки ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = link.getAttribute('href');
      if (id === '#' || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;

      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 70;
      window.scrollTo({ top: top, behavior: reduceMotion ? 'auto' : 'smooth' });
      history.replaceState(null, '', id);
    });
  });

  /* ---------- год в подвале ---------- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
