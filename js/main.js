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
  var sections = ['hot', 'dest', 'tickets', 'how', 'reviews', 'pick']
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

  /* ---------- вопросы: открыт только один ----------
     Современные браузеры делают это сами по общему атрибуту name у
     <details>. Здесь подстраховка для тех, где его ещё нет. */
  if (!('name' in document.createElement('details'))) {
    var faq = document.querySelectorAll('details[name="faq"]');
    faq.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (!d.open) return;
        faq.forEach(function (other) {
          if (other !== d) other.open = false;
        });
      });
    });
  }

  /* ---------- бюджет: план и факт ----------
     Считаем только то, что человек ввёл сам. Никаких «средних по рынку»:
     сравнивать не с кем — ответы никуда не отправляются и нигде не копятся. */
  var planRange = document.getElementById('planRange');
  var factRange = document.getElementById('factRange');

  if (planRange && factRange) {
    var MAX = parseInt(planRange.max, 10);
    var money = function (n) { return '$' + n.toLocaleString('ru-RU').replace(/,/g, ' '); };

    var els = {
      planOut: document.getElementById('planOut'),
      factOut: document.getElementById('factOut'),
      planBar: document.getElementById('planBar'),
      factBar: document.getElementById('factBar'),
      planNum: document.getElementById('planNum'),
      factNum: document.getElementById('factNum'),
      delta: document.getElementById('delta'),
      tg: document.getElementById('budgetTg')
    };

    var renderBudget = function () {
      var plan = +planRange.value;
      var fact = +factRange.value;

      els.planOut.textContent = els.planNum.textContent = money(plan);
      els.factOut.textContent = els.factNum.textContent = money(fact);
      els.planBar.style.width = (plan / MAX * 100) + '%';
      els.factBar.style.width = (fact / MAX * 100) + '%';

      var diff = fact - plan;
      var pct = plan ? Math.round(Math.abs(diff) / plan * 100) : 0;
      if (diff > 0) {
        els.delta.innerHTML = 'Прошлая поездка вышла дороже плана на <b>' + money(diff) +
          '</b> — это ' + pct + '% сверху.';
      } else if (diff < 0) {
        els.delta.innerHTML = 'В прошлый раз уложились дешевле плана на <b>' + money(-diff) + '</b>.';
      } else {
        els.delta.innerHTML = 'План и факт совпали — так бывает редко.';
      }

      els.tg.href = tgLink('Здравствуйте! Планирую около ' + money(plan) +
        ' на человека, прошлая поездка обошлась примерно в ' + money(fact) +
        '. Что можно подобрать?');

      // бюджет из бегунка подставляем в форму подбора ниже по странице
      var budgetSelect = document.getElementById('f-budget');
      if (budgetSelect) {
        var bands = [[600, 'до $600'], [1000, '$600–1000'], [1500, '$1000–1500'], [Infinity, 'от $1500']];
        for (var i = 0; i < bands.length; i++) {
          if (plan <= bands[i][0]) {
            for (var j = 0; j < budgetSelect.options.length; j++) {
              if (budgetSelect.options[j].text === bands[i][1]) budgetSelect.selectedIndex = j;
            }
            break;
          }
        }
      }
    };

    planRange.addEventListener('input', renderBudget);
    factRange.addEventListener('input', renderBudget);
    renderBudget();
  }

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
