/* =====================================================
   V-travel — интерактив
   Ничего не отправляем на сервер: все заявки уходят
   в Telegram или через звонок.
   ===================================================== */
(function () {
  'use strict';

  var TG_USER = 'vtour_travel';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- язык страницы ----------
     Тексты заявок уходят человеку в Telegram, поэтому они должны быть на том
     языке, на котором он читал сайт. Язык берём из <html lang>, который
     проставляет сборщик, — отдельного переключателя в скрипте нет. */
  var STR = {
    ru: {
      book: function (tour) {
        return 'Здравствуйте! Пишу с сайта V-travel. ' + tour +
               '. Подскажите, пожалуйста, детали.';
      },
      budget: function (sum) {
        return 'Здравствуйте! Планирую около ' + sum + ' на человека. Что можно подобрать?';
      },
      from: function (sum) { return 'от ' + sum; },
      nothingFits: 'В эту сумму пока не попадает ни одно направление — позвоните, поищем горящее',
      dests: [
        { name: 'Турция',  price: 520, url: '/turciya/' },
        { name: 'Египет',  price: 590, url: '/egipet/' },
        { name: 'Вьетнам', price: 720, url: '/vietnam/' },
        { name: 'Таиланд', price: 790, url: '/tailand/' }
      ],
      bands: [[600, 'до $600'], [1000, '$600–1000'], [1500, '$1000–1500'], [Infinity, 'от $1500']],
      anyDest: 'Ещё не решили',
      anyDate: 'даты гибкие',
      form: ['Здравствуйте! Заявка на подбор тура с сайта V-travel.', 'Направление: ',
             'Даты: ', 'Длительность: ', 'Состав: ', 'Бюджет на человека: ', 'Жду варианты 🙂'],
      sent: 'Открыли Telegram — заявка уже вписана, нажмите «Отправить».',
      failed: 'Не удалось открыть Telegram. Напишите @vtour_travel или позвоните +998 90 317-22-88.'
    },
    uz: {
      book: function (tour) {
        return 'Assalomu alaykum! V-travel saytidan yozyapman. ' + tour +
               '. Iltimos, tafsilotlarni ayting.';
      },
      budget: function (sum) {
        return 'Assalomu alaykum! Kishi boshiga taxminan ' + sum +
               ' rejalashtiryapman. Nima taklif qila olasiz?';
      },
      from: function (sum) { return sum + ' dan'; },
      nothingFits: 'Bu summaga hozircha birorta yo‘nalish tushmayapti — qo‘ng‘iroq qiling, ' +
                   'yonayotgan tur qidiramiz',
      dests: [
        { name: 'Turkiya', price: 520, url: '/uz/turkiya/' },
        { name: 'Misr',    price: 590, url: '/uz/misr/' },
        { name: 'Vyetnam', price: 720, url: '/uz/vetnam/' },
        { name: 'Tailand', price: 790, url: '/uz/tailand/' }
      ],
      bands: [[600, '$600 gacha'], [1000, '$600–1000'], [1500, '$1000–1500'], [Infinity, '$1500 dan']],
      anyDest: 'Hali hal qilmadik',
      anyDate: 'sanalar moslashuvchan',
      form: ['Assalomu alaykum! V-travel saytidan tur tanlash uchun ariza.', 'Yo‘nalish: ',
             'Sanalar: ', 'Davomiyligi: ', 'Kimlar bilan: ', 'Kishi boshiga byudjet: ',
             'Variantlarni kutaman 🙂'],
      sent: 'Telegram ochildi — ariza yozilgan, «Yuborish» tugmasini bosing.',
      failed: 'Telegramni ochib bo‘lmadi. @vtour_travel ga yozing yoki ' +
              '+998 90 317-22-88 raqamiga qo‘ng‘iroq qiling.'
    }
  }[document.documentElement.lang === 'uz' ? 'uz' : 'ru'];

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
    el.href = tgLink(STR.book(tour));
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

  /* ---------- бюджет поездки ----------
     Один бегунок: человек называет сумму и сразу видит, какие направления
     в неё попадают. Цены берём те же, что стоят на карточках направлений,
     чтобы на сайте нигде не было двух разных чисел про одно и то же. */
  var planRange = document.getElementById('planRange');

  if (planRange) {
    var DESTS = STR.dests;
    var money = function (n) { return '$' + n.toLocaleString('ru-RU').replace(/,/g, ' '); };
    var planOut = document.getElementById('planOut');
    var fitsList = document.getElementById('fitsList');
    var budgetTg = document.getElementById('budgetTg');

    var renderBudget = function () {
      var plan = +planRange.value;
      planOut.textContent = money(plan);

      var fits = DESTS.filter(function (d) { return d.price <= plan; });
      fitsList.innerHTML = fits.length
        ? fits.map(function (d) {
            return '<li><a href="' + d.url + '">' + d.name +
                   '<b>' + STR.from(money(d.price)) + '</b></a></li>';
          }).join('')
        : '<li><span>' + STR.nothingFits + '</span></li>';

      budgetTg.href = tgLink(STR.budget(money(plan)));

      // подставляем бюджет в форму подбора ниже по странице
      var budgetSelect = document.getElementById('f-budget');
      if (budgetSelect) {
        var bands = STR.bands;
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
    renderBudget();
  }

  /* ---------- форма подбора → Telegram ---------- */
  var form = document.getElementById('pickForm');
  var hint = document.getElementById('pickHint');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var dest = form.dest.value.trim() || STR.anyDest;
      var date = form.date.value.trim() || STR.anyDate;
      var f = STR.form;

      var msg = [
        f[0],
        '',
        f[1] + dest,
        f[2] + date,
        f[3] + form.nights.value,
        f[4] + form.people.value,
        f[5] + form.budget.value,
        '',
        f[6]
      ].join('\n');

      var win = window.open(tgLink(msg), '_blank', 'noopener');

      if (hint) {
        hint.textContent = win ? STR.sent : STR.failed;
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
