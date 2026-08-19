# -*- coding: utf-8 -*-
"""
Узбекский перевод сайта.

Ключ — русская фраза ровно так, как она стоит в html; значение — узбекская.
Сборщик (scripts/build_uz.py) подставляет их в готовые русские страницы и
падает, если хоть одна кириллическая буква осталась непереведённой. Поэтому
добавили текст на сайт — добавьте строку сюда, иначе сборка не пройдёт.

    python3 scripts/build_uz.py --report   покажет, чего не хватает

Про апострофы: в oʻzbekcha официально стоит U+02BB, но в Manrope такого
глифа нет. Здесь везде U+2018 «‘» — он выглядит той же запятой и есть в
обоих шрифтах. Для гортанного смычного (taʼtil) по той же причине U+2019.
"""

import re

# Узбекскому читателю нужен свой адрес, а не транслит русского названия.
SLUGS = {
    "turciya": "turkiya",
    "egipet": "misr",
    "tailand": "tailand",
    "vietnam": "vetnam",
}


# ─────────────────────────────────────────────────────────────────────
#  Фразы, разорванные вёрсткой.
#
#  В заголовках строка ломается через <br>, и половинки в двух языках не
#  совпадают: где по-русски «Три шага / до вылета», по-узбекски порядок
#  обратный. Переводить половинки по отдельности значило бы писать в
#  словаре неправду, поэтому такие места заменяются целиком, вместе с
#  разметкой, и делается это до основного словаря.
# ─────────────────────────────────────────────────────────────────────

REGEXES = [
    # Дословное «Dengiz o‘ylaganingizdan yaqinroq» не помещается: слово в
    # 16 букв на телефоне шире экрана, а переносить его посреди заголовка
    # нельзя. Берём равноценное по смыслу и короткое: «шаг до моря».
    (r'Море ближе,(<br>\s*<span class="hero__title-out">)чем кажется',
     r'Dengizga\1bir qadam'),
    (r'Цены, которые<br>\s*сгорают за сутки',
     'Bir kunda<br>yonib ketadigan narxlar'),
    (r'Куда летят<br>\s*наши туристы',
     'Turistlarimiz<br>qayerga uchadi'),
    (r'Авиабилеты<br>\s*из Ташкента',
     'Toshkentdan<br>aviachiptalar'),
    (r'Работаем так,<br>\s*чтобы вы вернулись',
     'Siz yana qaytishingiz<br>uchun ishlaymiz'),
    (r'Три шага<br>\s*до вылета',
     'Uchishgacha<br>uch qadam'),
    (r'Куда именно<br>\s*лететь',
     'Aynan qayerga<br>uchish kerak'),
    (r'О чём спрашивают<br>\s*перед поездкой',
     'Sayohatdan oldin<br>nima so‘rashadi'),
    (r'О чём спрашивают<br>\s*про горящие туры',
     'Yonayotgan turlar haqida<br>nima so‘rashadi'),

    # заголовок страницы направления: «Туры в Турцию / из Ташкента»
    (r'<h1>Туры в Турцию<br>\s*из Ташкента</h1>', '<h1>Toshkentdan<br>Turkiyaga turlar</h1>'),
    (r'<h1>Туры в Египет<br>\s*из Ташкента</h1>', '<h1>Toshkentdan<br>Misrga turlar</h1>'),
    (r'<h1>Туры в Таиланд<br>\s*из Ташкента</h1>', '<h1>Toshkentdan<br>Tailandga turlar</h1>'),
    (r'<h1>Туры во Вьетнам<br>\s*из Ташкента</h1>', '<h1>Toshkentdan<br>Vyetnamga turlar</h1>'),

    # «от $520 за человека» — в узбекском послелог идёт после суммы
    (r'<p class="phero__price">от <strong>\$(\d+)</strong> за человека</p>',
     r'<p class="phero__price"><strong>$\1</strong> dan, kishi boshiga</p>'),

    # Заявка про авторскую программу: название и состав подставляются, поэтому
    # берём их как есть — словарь переведёт их следующим проходом.
    (r'Здравствуйте! Интересует авторская программа (.+?)\. '
     r'Рассчитайте, пожалуйста, на мои даты\.',
     r'Assalomu alaykum! \1 mualliflik dasturi qiziqtiryapti. '
     r'Iltimos, mening sanalarimga hisoblang.'),
]


# Тексты заявок, которые уходят в Telegram прямо в ссылке. Они собираются по
# шаблону в scripts/build_pages.py, и переводить их по кускам нельзя: в
# узбекском название страны срастается с окончанием (Turkiya + ga), а
# сказуемое уезжает в конец предложения. Поэтому шаблон целиком.
_TG_MSG = [
    ("Здравствуйте! Интересуют туры %s из Ташкента.",
     "Assalomu alaykum! Toshkentdan %sga turlar qiziqtiryapti."),
    ("Здравствуйте! Интересуют туры %s.",
     "Assalomu alaykum! %sga turlar qiziqtiryapti."),
    ("Здравствуйте! Помогите выбрать курорт %s. Лечу ",
     "Assalomu alaykum! %sda kurort tanlashga yordam bering. Kim bilan uchaman: "),
    ("Здравствуйте! Хочу %s. Мои даты: ",
     "Assalomu alaykum! %sga bormoqchiman. Sanalarim: "),
]
_COUNTRIES = [("в Турцию", "Turkiya"), ("в Египет", "Misr"),
              ("в Таиланд", "Tailand"), ("во Вьетнам", "Vyetnam")]

REGEXES += [(re.escape(ru_tpl % ru_c), uz_tpl % uz_c)
            for ru_tpl, uz_tpl in _TG_MSG
            for ru_c, uz_c in _COUNTRIES]


# ─────────────────────────────────────────────────────────────────────
#  Словарь. Порядок в файле — по смыслу, при подстановке сборщик всё
#  равно сортирует длинные фразы вперёд.
# ─────────────────────────────────────────────────────────────────────

PHRASES = {

# ─── шапка, подвал, общая навигация ───────────────────────────────────
'К основному содержимому': 'Asosiy mazmunga o‘tish',
'V-travel, на главную': 'V-travel, bosh sahifaga',
'Основная навигация': 'Asosiy navigatsiya',
'Разделы сайта': 'Sayt bo‘limlari',
'Хлебные крошки': 'Sahifalar zanjiri',
'Главная': 'Bosh sahifa',
'Меню': 'Menyu',
'Горящие туры': 'Yonayotgan turlar',
'Направления': 'Yo‘nalishlar',
'Авиабилеты': 'Aviachiptalar',
'Как работаем': 'Qanday ishlaymiz',
'Отзывы': 'Sharhlar',
'Подбор тура': 'Tur tanlash',
'Бюджет поездки': 'Sayohat byudjeti',
'Другие направления': 'Boshqa yo‘nalishlar',
'Ещё варианты': 'Yana variantlar',
'Написать в Telegram': 'Telegramga yozish',
'Спросить в Telegram': 'Telegramda so‘rash',
'Позвонить': 'Qo‘ng‘iroq qilish',
'Позвоните: +998 90 317-22-88': 'Qo‘ng‘iroq qiling: +998 90 317-22-88',
'Ежедневно 09:00–21:00': 'Har kuni 09:00–21:00',
'Канал с горящими турами:': 'Yonayotgan turlar kanali:',
'Туристическое агентство. Подбор и оформление туров под ключ. Вылеты из Ташкента.':
    'Sayyohlik agentligi. Turlarni tanlash va to‘liq rasmiylashtirish. Toshkentdan uchishlar.',
'Цены указаны за человека при двухместном размещении и зависят от даты вылета.':
    'Narxlar ikki kishilik joylashuvda kishi boshiga ko‘rsatilgan va uchish sanasiga bog‘liq.',

# ─── микроразметка ────────────────────────────────────────────────────
'Турагентство в Ташкенте: подбор и оформление туров под ключ, горящие туры, перелёт, отель, виза и страховка.':
    'Toshkentdagi turagentlik: turlarni tanlash va to‘liq rasmiylashtirish, yonayotgan turlar, '
    'parvoz, mehmonxona, viza va sug‘urta.',
'Услуги V-travel': 'V-travel xizmatlari',
'Подбор и оформление туров под ключ': 'Turlarni tanlash va to‘liq rasmiylashtirish',
'Оформление виз и страховок': 'Viza va sug‘urta rasmiylashtirish',
'Узбекистан': 'O‘zbekiston',
'Ташкент': 'Toshkent',

# ─── первый экран ─────────────────────────────────────────────────────
'Горящие туры из Ташкента — турагентство V-travel':
    'Toshkentdan yonayotgan turlar — V-travel turagentligi',
'Турагентство V-travel в Ташкенте: горящие туры от $590, авиабилеты, подбор за 15 минут, '
'виза и страховка под ключ. Звоните +998 90 317-22-88.':
    'Toshkentdagi V-travel turagentligi: $590 dan yonayotgan turlar, aviachiptalar, '
    '15 daqiqada tanlash, viza va sug‘urta — hammasi biz zimmamizda. '
    'Qo‘ng‘iroq qiling +998 90 317-22-88.',
'Горящие туры из Ташкента': 'Toshkentdan yonayotgan turlar',
'Горящие туры от $590. Подбор за 15 минут, оформление под ключ. Звоните или пишите в Telegram.':
    '$590 dan yonayotgan turlar. 15 daqiqada tanlash, to‘liq rasmiylashtirish. '
    'Qo‘ng‘iroq qiling yoki Telegramga yozing.',
'Вид из иллюминатора на побережье — V-travel, туры из Ташкента':
    'Illuminatordan sohil manzarasi — V-travel, Toshkentdan turlar',
'Турагентство в Ташкенте · На связи прямо сейчас':
    'Toshkentdagi turagentlik · Hozir aloqadamiz',
'Подберём тур под ваш бюджет за 15 минут и возьмём на себя всё: перелёт, отель, '
'страховку и визу. Вам останется собрать чемодан.':
    '15 daqiqada byudjetingizga mos tur tanlaymiz va hammasini o‘z zimmamizga olamiz: '
    'parvoz, mehmonxona, sug‘urta va viza. Sizga faqat chamadon yig‘ish qoladi.',
'Отвечаем за 5 минут · Ежедневно 09:00–21:00 · Подбор бесплатный':
    '5 daqiqada javob beramiz · Har kuni 09:00–21:00 · Tanlash bepul',
'лет на рынке': 'yil bozorda',
'туристов отправили': 'turistni jo‘natdik',
'направлений': 'yo‘nalish',
'средняя оценка': 'o‘rtacha baho',

# ─── горящие туры ─────────────────────────────────────────────────────
'Места ограничены — как правило, остаётся 2–4 номера. Нажмите «Забронировать», '
'и мы проверим наличие прямо сейчас.':
    'Joylar cheklangan — odatda 2–4 ta xona qoladi. «Bron qilish» tugmasini bosing, '
    'mavjudligini hoziroq tekshiramiz.',
'Не нашли подходящий вариант? Позвоните — у нас есть предложения, которых нет на сайте.':
    'Mos variant topilmadimi? Qo‘ng‘iroq qiling — bizda saytda yo‘q takliflar ham bor.',
'Забронировать': 'Bron qilish',
'Осталось 2 места': '2 ta joy qoldi',
'Новинка': 'Yangi',
'Хит': 'Xit',
'7 ночей · всё включено': '7 kecha · hammasi kiritilgan',
'8 ночей · всё включено': '8 kecha · hammasi kiritilgan',
'6 ночей · завтраки': '6 kecha · nonushta bilan',
'10 ночей · завтраки': '10 kecha · nonushta bilan',
'Отель 5★ · 1-я линия': '5★ mehmonxona · birinchi qator',
'Отель 5★ · аквапарк': '5★ mehmonxona · akvapark',
'Отель 4★ · центр города': '4★ mehmonxona · shahar markazi',
'Отель 4★ · 5 мин до пляжа': '4★ mehmonxona · plyajgacha 5 daqiqa',
'Даты — по запросу': 'Sanalar — so‘rov bo‘yicha',
'за человека': 'kishi boshiga',
'Египет, Шарм-эль-Шейх — 7 ночей, 5★ всё включено, $590':
    'Misr, Sharm-ash-Shayx — 7 kecha, 5★ hammasi kiritilgan, $590',
'Турция, Анталия — 8 ночей, 5★ всё включено, $650':
    'Turkiya, Antalya — 8 kecha, 5★ hammasi kiritilgan, $650',
'ОАЭ, Дубай — 6 ночей, 4★ завтраки, $720':
    'BAA, Dubay — 6 kecha, 4★ nonushta bilan, $720',
'Таиланд, Пхукет — 10 ночей, 4★ завтраки, $790':
    'Tailand, Phuket — 10 kecha, 4★ nonushta bilan, $790',

# ─── направления ──────────────────────────────────────────────────────
'Собрали направления с прямыми и удобными стыковочными рейсами из Ташкента.':
    'Toshkentdan to‘g‘ridan-to‘g‘ri va qulay ulanishli reyslar bor yo‘nalishlarni to‘pladik.',
'А ещё: Мальдивы, Шри-Ланка, Грузия, Малайзия, Индонезия и ещё 30 направлений':
    'Yana: Maldiv orollari, Shri-Lanka, Gruziya, Malayziya, Indoneziya va yana 30 ta yo‘nalish',
'Скажите, куда хочется — подберём даже то, чего нет в списке.':
    'Qayerga borishni xohlayotganingizni ayting — ro‘yxatda yo‘q joyni ham topamiz.',
'Подробнее →': 'Batafsil →',
'Анталия · Кемер · Бодрум · Стамбул': 'Antalya · Kemer · Bodrum · Istanbul',
'Шарм-эль-Шейх · Хургада': 'Sharm-ash-Shayx · Xurgada',
'Пхукет · Паттайя · Самуи': 'Phuket · Pattayya · Samui',
'Нячанг · Фукуок · Дананг': 'Nyachang · Fukuok · Danang',
'Туры в Турцию из Ташкента — Голубая лагуна Олюдениз с высоты':
    'Toshkentdan Turkiyaga turlar — O‘lyudeniz Ko‘k lagunasi tepadan',
'Туры в Египет — коралловый риф Красного моря с высоты':
    'Misrga turlar — Qizil dengiz marjon rifi tepadan',
'Туры в Таиланд — известняковые скалы островов Пхи-Пхи':
    'Tailandga turlar — Phi-Phi orollarining ohaktosh qoyalari',
'Туры во Вьетнам — острова бухты Халонг в утренней дымке':
    'Vyetnamga turlar — tonggi tumandagi Halong qo‘ltig‘i orollari',

# ─── авиабилеты ───────────────────────────────────────────────────────
'Продаём билеты отдельно от туров — на любые направления и любые даты. '
'Смотрим все доступные тарифы и стыковки, а не первую строчку в агрегаторе.':
    'Chiptalarni turlardan alohida sotamiz — istalgan yo‘nalish va istalgan sanaga. '
    'Agregatordagi birinchi qatorni emas, mavjud barcha tariflar va ulanishlarni ko‘rib chiqamiz.',
'Подберём дешёвую дату вылета, если поездка не привязана к числу':
    'Sayohat aniq sanaga bog‘liq bo‘lmasa, arzon uchish kunini topamiz',
'Разберёмся с багажом, местами и питанием до оплаты, а не после':
    'Bagaj, o‘rindiq va ovqatni to‘lovdan keyin emas, oldin hal qilamiz',
'Поможем с возвратом и обменом, если планы изменятся':
    'Rejalar o‘zgarsa, qaytarish va almashtirishga yordam beramiz',
'Детские и семейные тарифы, групповые перелёты':
    'Bolalar va oilaviy tariflar, guruh parvozlari',
'Запросить билет в Telegram': 'Telegramda chipta so‘rash',
'Нужен авиабилет': 'Aviachipta kerak',
'Чаще всего берут': 'Ko‘p tanlanadigan yo‘nalishlar',
'Цена зависит от даты и глубины бронирования — назовите направление, '
'и мы посчитаем на ваши числа.':
    'Narx sanaga va qancha oldin bron qilinganiga bog‘liq — yo‘nalishni ayting, '
    'sizning kunlaringizga hisoblab beramiz.',
'Стамбул': 'Istanbul',
'Дубай': 'Dubay',
'ОАЭ': 'BAA',
'Москва': 'Moskva',
'Бангкок': 'Bangkok',
'Сеул': 'Seul',
'Джидда': 'Jidda',
'Куала-Лумпур': 'Kuala-Lumpur',
'Франкфурт': 'Frankfurt',

# ─── почему мы ────────────────────────────────────────────────────────
'Почему V-travel': 'Nega V-travel',
'Ответ за 5 минут': '5 daqiqada javob',
'Пишете в Telegram — получаете 3 варианта с ценами, фото отеля и честными отзывами. '
'Без «перезвоним завтра».':
    'Telegramga yozasiz — narxlari, mehmonxona suratlari va halol sharhlari bilan 3 ta '
    'variant olasiz. «Ertaga qo‘ng‘iroq qilamiz»siz.',
'Цена без сюрпризов': 'Kutilmagan to‘lovsiz narx',
'В стоимости уже перелёт, отель, трансфер и страховка. Комиссию берём с туроператора, а не с вас.':
    'Narxga parvoz, mehmonxona, transfer va sug‘urta allaqachon kiritilgan. '
    'Komissiyani sizdan emas, turoperatordan olamiz.',
# «mehmonxonalar» на 8px шире колонки карточки, поэтому здесь единственное число
'Только проверенные отели': 'Har bir mehmonxona tekshirilgan',
'Рекомендуем то, где были сами или куда отправляли туристов. '
'Знаем, у какого отеля «первая линия» на самом деле вторая.':
    'O‘zimiz bo‘lgan yoki turistlarni jo‘natgan joylarni tavsiya qilamiz. '
    'Qaysi mehmonxonaning «birinchi qatori» aslida ikkinchi ekanini bilamiz.',
'На связи всю поездку': 'Butun sayohat davomida aloqadamiz',
'Задержали рейс, вопрос на ресепшене, нужен врач — пишите в любое время. '
'Решаем, пока вы отдыхаете.':
    'Reys kechikdimi, resepshenda savol tug‘ildimi, shifokor kerakmi — istalgan vaqtda yozing. '
    'Siz dam olayotganingizda hal qilamiz.',

# ─── три шага ─────────────────────────────────────────────────────────
'Звонок или сообщение': 'Qo‘ng‘iroq yoki xabar',
'Рассказываете, куда, когда и на какой бюджет рассчитываете. 3 минуты разговора.':
    'Qayerga, qachon va qanday byudjetga mo‘ljallayotganingizni aytasiz. 3 daqiqalik suhbat.',
'Подборка за 15 минут': '15 daqiqada tanlov',
'Присылаем варианты с ценами и разбором плюсов и минусов каждого отеля.':
    'Narxlari va har bir mehmonxonaning ortiqcha-kamchiliklari tahlili bilan variantlar yuboramiz.',
'Бронь и документы': 'Bron va hujjatlar',
'Оформляем бронь, страховку и визу. Билеты и ваучеры приходят вам в Telegram.':
    'Bron, sug‘urta va vizani rasmiylashtiramiz. Chiptalar va vaucherlar Telegramingizga keladi.',

# ─── бюджет ───────────────────────────────────────────────────────────
'Сколько закладывать': 'Qancha pul rejalashtirish kerak',
'Подвиньте бегунок — покажем, какие направления попадают в эту сумму и из чего обычно '
'набегает разница сверх плана.':
    'Slayderni suring — qaysi yo‘nalishlar shu summaga sig‘ishini va rejadan ortiq xarajat '
    'odatda nimadan yig‘ilishini ko‘rsatamiz.',
'Планирую на человека': 'Kishi boshiga rejalashtiryapman',
'Что попадает в эту сумму': 'Bu summaga nima sig‘adi',
'Почему выходит дороже, чем закладывали': 'Nega rejalashtirganingizdan qimmatga tushadi',
'Трансфер из аэропорта и багаж сверх нормы': 'Aeroportdan transfer va me’yordan ortiq bagaj',
'Страховка и оформление документов': 'Sug‘urta va hujjatlarni rasmiylashtirish',
'Экскурсии, которые покупают уже на месте': 'Joyiga borgach sotib olinadigan ekskursiyalar',
'Курортный сбор и доплаты в отеле': 'Kurort yig‘imi va mehmonxonadagi qo‘shimcha to‘lovlar',
'Еда и напитки вне «всё включено»': '«Hammasi kiritilgan»dan tashqari taom va ichimliklar',
'Мы считаем всё это сразу, до брони — чтобы на месте не оказалось, '
'что половина за отдельные деньги.':
    'Biz bularning hammasini bron qilishdan oldin hisoblaymiz — joyiga borib, '
    'yarmi alohida pul ekanini bilib qolmang.',
'Посчитать мой бюджет': 'Byudjetimni hisoblash',

# ─── форма подбора ────────────────────────────────────────────────────
'Ответьте на 4 вопроса —': '4 ta savolga javob bering —',
'пришлём варианты': 'variantlarni yuboramiz',
'Форма не отправляет данные на сервер: она собирает готовое сообщение и открывает '
'ваш Telegram. Вам останется нажать «Отправить».':
    'Shakl ma’lumotlarni serverga yubormaydi: u tayyor xabarni yig‘adi va Telegramingizni '
    'ochadi. Sizga faqat «Yuborish» tugmasini bosish qoladi.',
'Не пользуетесь Telegram?': 'Telegramdan foydalanmaysizmi?',
'Куда хотите полететь': 'Qayerga uchmoqchisiz',
'Например, Турция или ещё не решили': 'Masalan, Turkiya yoki hali hal qilmadik',
'Ещё не решили': 'Hali hal qilmadik',
'Мальдивы': 'Maldiv orollari',
'Шри-Ланка': 'Shri-Lanka',
'Грузия': 'Gruziya',
'Конец августа': 'Avgust oxiri',
'На сколько ночей': 'Necha kechaga',
'5–7 ночей': '5–7 kecha',
'8–10 ночей': '8–10 kecha',
'11–14 ночей': '11–14 kecha',
'Больше двух недель': 'Ikki haftadan ko‘p',
'Сколько человек': 'Necha kishi',
'1 взрослый': '1 katta odam',
'2 взрослых + ребёнок': '2 katta + 1 bola',
'2 взрослых + 2 детей': '2 katta + 2 bola',
'2 взрослых': '2 katta odam',
'Компания от 5 человек': '5 kishidan iborat davra',
'Бюджет на человека': 'Kishi boshiga byudjet',
'до $600': '$600 gacha',
'от $1500': '$1500 dan',
'Пока не определился': 'Hali hal qilmadim',
'Получить подборку в Telegram': 'Telegramda variantlarni olish',
'Нажимая кнопку, вы откроете чат с менеджером — заявка уже будет вписана.':
    'Tugmani bosganingizda menejer bilan chat ochiladi — ariza allaqachon yozilgan bo‘ladi.',

# ─── отзывы ───────────────────────────────────────────────────────────
'4,9 из 5': '5 dan 4,9',
'по 380 отзывам': '380 ta sharh bo‘yicha',
'Оценка 5 из 5': 'Baho: 5 dan 5',
'Летели в Шарм вдвоём. Подобрали отель за вечер, цена вышла на $180 дешевле, '
'чем в другом агентстве. В аэропорту встретили с табличкой — мелочь, а приятно.':
    'Sharmga ikkovlon uchdik. Mehmonxonani bir kechada tanlab berishdi, narx boshqa '
    'agentlikdagidan $180 arzonroq chiqdi. Aeroportda ismimiz yozilgan lavha bilan '
    'kutib olishdi — arzimas narsa, lekin yoqimli.',
'Первый раз летели с ребёнком, переживали. Подсказали отель с нормальным детским меню '
'и мелким входом в море. Всю поездку были на связи в Telegram, отвечали даже ночью.':
    'Birinchi marta bola bilan uchdik, xavotirda edik. Bolalar menyusi yaxshi va dengizga '
    'kirish sayoz bo‘lgan mehmonxonani maslahat berishdi. Butun sayohat davomida Telegramda '
    'aloqada bo‘lishdi, hatto kechasi ham javob berishdi.',
'Горящий тур в Дубай нашли за два дня до вылета. Визу оформили за сутки, '
'я только паспорт скинул. Улетел, как и хотел.':
    'Dubayga yonayotgan turni uchishdan ikki kun oldin topib berishdi. Vizani bir kunda '
    'rasmiylashtirishdi, men faqat passportni tashladim. Xohlaganimdek uchib ketdim.',
'Дилноза А.': 'Dilnoza A.',
'Семья Ким': 'Kim oilasi',
'Тимур Р.': 'Timur R.',
'Египет, июль': 'Misr, iyul',
'Турция, июнь': 'Turkiya, iyun',
'ОАЭ, май': 'BAA, may',

# ─── вопросы на главной ───────────────────────────────────────────────
'Что такое горящий тур и почему он дешевле обычного?':
    'Yonayotgan tur nima va nega u oddiysidan arzon?',
'Туроператор выкупает места в самолёте и номера в отеле заранее. Если ближе к вылету '
'часть осталась непроданной, её отдают со скидкой: везти пустое кресло дороже, чем '
'продать его вполцены. Отель и рейс при этом те же самые, что и по полной цене.':
    'Turoperator samolyotdagi o‘rinlar va mehmonxona xonalarini oldindan sotib oladi. '
    'Uchishga yaqin ularning bir qismi sotilmay qolsa, chegirma bilan beriladi: bo‘sh '
    'o‘rindiqni olib uchish uni yarim narxda sotgandan qimmatroq. Mehmonxona ham, reys '
    'ham to‘liq narxdagi bilan bir xil bo‘ladi.',

'За сколько дней до вылета появляются горящие туры?':
    'Yonayotgan turlar uchishdan necha kun oldin paydo bo‘ladi?',
'Обычно за 3–14 дней. Иногда предложение живёт несколько часов — как только места '
'выкупают, цена возвращается к обычной. Поэтому мы проверяем наличие в момент '
'обращения, а не показываем вчерашние цены.':
    'Odatda 3–14 kun oldin. Ba’zan taklif bir necha soat yashaydi — o‘rinlar sotilishi '
    'bilan narx odatdagiga qaytadi. Shuning uchun biz kechagi narxlarni ko‘rsatmay, siz '
    'murojaat qilgan paytda mavjudligini tekshiramiz.',

'Горящий тур — это обязательно плохой отель?':
    'Yonayotgan tur — bu albatta yomon mehmonxonami?',
'Нет. Скидка зависит от того, что осталось непроданным, а не от качества: она бывает и '
'на пятизвёздочные отели первой линии. Ограничен не уровень, а выбор — берёте из того, '
'что есть на эти даты.':
    'Yo‘q. Chegirma sifatga emas, nima sotilmay qolganiga bog‘liq: u birinchi qatordagi '
    'besh yulduzli mehmonxonalarda ham bo‘ladi. Cheklangan narsa daraja emas, tanlov — '
    'shu sanalarda nima bor bo‘lsa, shundan olasiz.',

'Можно ли выбрать конкретный отель и конкретные даты?':
    'Aniq mehmonxona va aniq sanalarni tanlash mumkinmi?',
'В горящем туре — только из оставшегося. Если даты отпуска жёсткие или нужен '
'определённый отель, выгоднее бронировать заранее: это всё равно дешевле, чем покупать '
'тот же тур за неделю до вылета по обычной цене. Скажите, что важнее — цена или '
'даты, и мы будем искать под это.':
    'Yonayotgan turda — faqat qolganidan. Ta’til sanalari qat’iy bo‘lsa yoki muayyan '
    'mehmonxona kerak bo‘lsa, oldindan bron qilgan foydaliroq: bu baribir o‘sha turni '
    'uchishdan bir hafta oldin oddiy narxda olishdan arzon. Nima muhimroq — narxmi yoki '
    'sanalarmi, ayting, shunga qarab qidiramiz.',

'Успею ли я оформить документы, если вылет через неделю?':
    'Uchish bir haftadan keyin bo‘lsa, hujjatlarni rasmiylashtirishga ulguramanmi?',
'Чаще всего да. Правила въезда меняются, поэтому мы проверяем их на вашу дату вылета '
'ещё до брони и сразу говорим, какие документы понадобятся и сколько времени займёт '
'оформление.':
    'Ko‘pincha ha. Kirish qoidalari o‘zgarib turadi, shuning uchun biz ularni bron '
    'qilishdan oldin sizning uchish sanangizga tekshiramiz va qanday hujjatlar '
    'kerakligini hamda rasmiylashtirish qancha vaqt olishini darrov aytamiz.',

'Как узнать о горящем туре первым?':
    'Yonayotgan tur haqida birinchi bo‘lib qanday bilish mumkin?',
'Предложения появляются без предупреждения, поэтому лучший способ — сказать нам '
'направление и бюджет заранее: как только появится подходящее, мы напишем. Ещё есть '
'канал, куда они попадают по мере поступления.':
    'Takliflar ogohlantirishsiz paydo bo‘ladi, shuning uchun eng yaxshi yo‘l — yo‘nalish '
    'va byudjetingizni bizga oldindan aytish: mos variant chiqishi bilan yozamiz. Bundan '
    'tashqari, ular tushib turadigan kanal ham bor.',

# ─── финальный экран ──────────────────────────────────────────────────
'Позвоните — и через 15 минут у вас будут варианты':
    'Qo‘ng‘iroq qiling — 15 daqiqadan so‘ng variantlar tayyor',
'Ежедневно с 09:00 до 21:00. Подбор бесплатный, ни к чему не обязывает.':
    'Har kuni 09:00 dan 21:00 gacha. Tanlash bepul va hech narsaga majbur qilmaydi.',
'ваш рейс': 'sizning reysingiz',

# ─── страницы направлений: общее ──────────────────────────────────────
'Курорты': 'Kurortlar',
'Курорты внутри одной страны отличаются сильнее, чем кажется по каталогу. '
'Коротко о том, кому какой подходит.':
    'Bir mamlakat ichidagi kurortlar katalogda ko‘ringanidan ko‘ra ko‘proq farq qiladi. '
    'Qaysi biri kimga mosligi haqida qisqacha.',
'Не знаете, какой курорт ваш?': 'Qaysi kurort sizniki ekanini bilmayapsizmi?',
'Назовите бюджет и с кем летите — подскажем за пять минут, без каталогов и уговоров.':
    'Byudjetingizni va kim bilan uchayotganingizni ayting — besh daqiqada aytamiz, '
    'kataloglarsiz va ko‘ndirishlarsiz.',
'Сезонность': 'Mavsumiylik',
'Когда лететь': 'Qachon uchish kerak',
'Разница между «дорого и жарко» и «дёшево и приятно» — часто две недели в календаре.':
    '«Qimmat va jazirama» bilan «arzon va yoqimli» orasidagi farq — ko‘pincha taqvimdagi ikki hafta.',
'Период': 'Davr',
'Воздух и вода': 'Havo va suv',
'Что это значит': 'Bu nimani anglatadi',
'Скажите свои даты — посчитаем': 'Sanalaringizni ayting — hisoblaymiz',
'Проверим, что попадает на ваш отпуск, и предложим варианты в этих числах.':
    'Ta’tilingizga nima to‘g‘ri kelishini tekshiramiz va shu kunlarga variantlar taklif qilamiz.',
'Авторская программа': 'Mualliflik dasturi',
'Маршрут подстраивается под вас': 'Marshrut sizga moslashadi',
'Можно добавить дни на море, поменять города местами или убрать переезды — скажите, '
'что важно, и пересоберём. Стоимость зависит от дат и класса отелей, поэтому считаем '
'под конкретные числа.':
    'Dengizda kunlarni qo‘shish, shaharlarni almashtirish yoki uzoq yo‘llarni olib tashlash '
    'mumkin — nima muhimligini ayting, marshrutni qayta yig‘amiz. Narx sanalarga va '
    'mehmonxona darajasiga bog‘liq, shuning uchun aniq kunlarga hisoblaymiz.',
'Рассчитать в Telegram': 'Telegramda hisoblash',
'Вопросы': 'Savollar',
'Подбор бесплатный, ответим за 5 минут.': 'Tanlash bepul, 5 daqiqada javob beramiz.',

# ─── Турция ───────────────────────────────────────────────────────────
'Туры в Турцию из Ташкента — цены и авторские программы':
    'Toshkentdan Turkiyaga turlar — narxlar va mualliflik dasturlari',
'Туры в Турцию из Ташкента от $520: какой курорт кому подходит, когда лететь, '
'авторская программа по дням. Подбор за 15 минут, звоните +998 90 317-22-88.':
    'Toshkentdan Turkiyaga turlar $520 dan: qaysi kurort kimga mos, qachon uchish kerak, '
    'kunlar bo‘yicha mualliflik dasturi. 15 daqiqada tanlaymiz, '
    'qo‘ng‘iroq qiling +998 90 317-22-88.',
'Туры в Турцию из Ташкента': 'Toshkentdan Turkiyaga turlar',
'Туры в Турцию': 'Turkiyaga turlar',
'Турция': 'Turkiya',
'Прямой рейс Ташкент — Анталия занимает около 5,5 часов.':
    'Toshkent — Antalya to‘g‘ri reysi taxminan 5,5 soat davom etadi.',
'Самое простое первое море: прямые рейсы, «всё включено» как норма, отели под любой '
'бюджет. Сюда летят и с детьми, и вдвоём, и компанией.':
    'Birinchi dengiz uchun eng oson variant: to‘g‘ridan-to‘g‘ri reyslar, «hammasi kiritilgan» '
    '— odatiy hol, har qanday byudjetga mehmonxona. Bu yerga bolalar bilan ham, ikkovlon ham, '
    'davra bo‘lib ham uchishadi.',
'Анталия': 'Antalya',
'Самый большой выбор отелей и вся инфраструктура под рукой: аквапарки, рынки, экскурсии. '
'Городские пляжи галечные. Берите, если хотите, чтобы вокруг что-то происходило.':
    'Mehmonxonalar tanlovi eng katta, butun infratuzilma qo‘l ostida: akvaparklar, bozorlar, '
    'ekskursiyalar. Shahar plyajlari shag‘alli. Atrofda hayot qaynashini istasangiz — '
    'shu yerni oling.',
'Кемер': 'Kemer',
'Горы подходят вплотную к морю, вода прозрачнее, чем на равнине, вечером заметно '
'прохладнее. Пляжи галечные. Для тех, кому важен вид из окна.':
    'Tog‘lar dengizga tegib turadi, suv tekislikdagidan tiniqroq, kechqurun sezilarli salqin '
    'bo‘ladi. Plyajlar shag‘alli. Deraza oldidagi manzara muhim bo‘lganlar uchun.',
'Белек': 'Belek',
'Сосновые леса, песок, поля для гольфа и самые дорогие отели побережья. '
'Сюда едут семьи, готовые доплатить за территорию и сервис.':
    'Qarag‘ayzorlar, qum, golf maydonlari va sohildagi eng qimmat mehmonxonalar. '
    'Bu yerga hudud va xizmat uchun qo‘shimcha to‘lashga tayyor oilalar keladi.',
'Сиде': 'Side',
'Песчаные пляжи и античные руины прямо в черте города. '
'Разумный компромисс между ценой и качеством пляжа.':
    'Qumli plyajlar va shahar ichidagi antik xarobalar. '
    'Narx bilan plyaj sifati o‘rtasidagi oqilona muvozanat.',
'Бодрум': 'Bodrum',
'Эгейское побережье: вода прохладнее, публика взрослее, ночная жизнь серьёзнее. '
'Не для отдыха с малышами.':
    'Egey sohili: suv salqinroq, mehmonlar kattaroq yoshda, tungi hayot jiddiyroq. '
    'Kichkintoylar bilan dam olish uchun emas.',
'Народу мало, цены низкие, но море ещё бодрит': 'Odam kam, narxlar past, lekin dengiz hali salqin',
'Оптимально: тепло, но ещё не пекло': 'Eng maqbuli: issiq, lekin hali jazirama emas',
'Пик сезона. Самые высокие цены и самая сильная жара':
    'Mavsum cho‘qqisi. Eng yuqori narxlar va eng kuchli jazirama',
'Лучший месяц. Вода прогрета, жара спала, школьники уехали':
    'Eng yaxshi oy. Suv isigan, jazirama qaytgan, o‘quvchilar ketgan',
'Купаться ещё можно, цены падают заметно': 'Hali cho‘milsa bo‘ladi, narxlar sezilarli tushadi',
'Средиземноморское побережье: бирюзовые бухты и сосновые склоны, спускающиеся прямо к воде':
    'O‘rta yer dengizi sohili: firuza qo‘ltiqlar va to‘g‘ridan-to‘g‘ri suvga tushadigan '
    'qarag‘ayli yonbag‘irlar',
'Рассвет над Каппадокией — четвёртый день программы':
    'Kappadokiya uzra tong — dasturning to‘rtinchi kuni',
'Босфор на закате: паром идёт мимо силуэтов минаретов':
    'Quyosh botayotgan Bosfor: parom minoralar siluetlari yonidan o‘tadi',
'Стамбул и Каппадокия': 'Istanbul va Kappadokiya',
'7 дней · Стамбул → Каппадокия → Памуккале или Анталия':
    '7 kun · Istanbul → Kappadokiya → Pamukkale yoki Antalya',
'Прилёт и размещение. Обзорная экскурсия: Голубая мечеть, собор Святой Софии, '
'дворец Топкапы и прогулка по Босфору.':
    'Yetib borish va joylashish. Tanishuv ekskursiyasi: Ko‘k masjid, Ayasofya, '
    'Topqopi saroyi va Bosfor bo‘ylab sayr.',
'Перелёт в Каппадокию': 'Kappadokiyaga parvoz',
'Утренний перелёт в Невшехир или Кайсери, размещение в пещерном отеле в Гёреме, '
'музей под открытым небом.':
    'Nevshehir yoki Kayseriga ertalabki parvoz, Go‘remedagi g‘or mehmonxonasiga joylashish, '
    'ochiq osmon ostidagi muzey.',
'Каппадокия': 'Kappadokiya',
'Ранний подъём и полёт на воздушном шаре. Подземные города и долина Пашабаг.':
    'Erta turish va havo sharida parvoz. Yer osti shaharlari va Pashabag vodiysi.',
'Памуккале или Анталия': 'Pamukkale yoki Antalya',
'На выбор: белоснежные травертины Памуккале или отдых на средиземноморском побережье.':
    'Tanlov: Pamukkalening oppoq travertinlari yoki O‘rta yer dengizi sohilida dam olish.',
'Стамбул и вылет': 'Istanbul va uchish',
'Возвращение в Стамбул, сувениры на Гранд-базаре, трансфер в аэропорт.':
    'Istanbulga qaytish, Grand bozorda sovg‘alar, aeroportga transfer.',
'Нужна ли виза гражданам Узбекистана?': 'O‘zbekiston fuqarolariga viza kerakmi?',
'Правила въезда меняются, поэтому мы всегда проверяем их на конкретную дату вылета '
'перед бронированием. Напишите или позвоните — уточним актуальные условия и, '
'если нужны документы, поможем их собрать.':
    'Kirish qoidalari o‘zgarib turadi, shuning uchun biz ularni har safar aniq uchish sanasiga, '
    'bron qilishdan oldin tekshiramiz. Yozing yoki qo‘ng‘iroq qiling — amaldagi shartlarni '
    'aniqlaymiz va hujjatlar kerak bo‘lsa, yig‘ishga yordam beramiz.',
'Когда дешевле всего лететь?': 'Qachon uchish eng arzon?',
'В мае и октябре. Цены на те же отели ниже пиковых, а море уже или ещё пригодно для '
'купания. Если даты не привязаны к отпуску, разница бывает существенной.':
    'May va oktabrda. O‘sha mehmonxonalarning narxi eng yuqori davrdagidan past, dengizda esa '
    'cho‘milsa bo‘ladi. Sanalar ta’tilga bog‘liq bo‘lmasa, farq sezilarli bo‘ladi.',
'Что на самом деле входит в «всё включено»?': '«Hammasi kiritilgan»ga aslida nima kiradi?',
'У разных отелей это разные вещи: где-то местный алкоголь и три приёма пищи, где-то ещё и '
'снеки, мороженое, а-ля карт рестораны. Мы разбираем состав до бронирования, чтобы на месте '
'не оказалось, что половина — за отдельные деньги.':
    'Har bir mehmonxonada bu boshqacha: birida mahalliy ichimliklar va uch mahal ovqat, '
    'boshqasida yana gazaklar, muzqaymoq, a la carte restoranlar. Biz tarkibni bron qilishdan '
    'oldin ochib beramiz — joyiga borib, yarmi alohida pul ekanini bilib qolmang.',
'Галька или песок?': 'Shag‘almi yoki qummi?',
'В Кемере и большей части Анталии — галька, в Сиде и Белеке — песок. Если едете с маленьким '
'ребёнком, это принципиально: скажите, и мы подберём отель с песчаным входом.':
    'Kemerda va Antalyaning ko‘p qismida — shag‘al, Side va Belekda — qum. Kichkina bola bilan '
    'borsangiz, bu muhim: ayting, qumli kirishga ega mehmonxona tanlab beramiz.',

# ─── Египет ───────────────────────────────────────────────────────────
'Туры в Египет из Ташкента — цены и авторские программы':
    'Toshkentdan Misrga turlar — narxlar va mualliflik dasturlari',
'Туры в Египет из Ташкента от $590: какой курорт кому подходит, когда лететь, '
'авторская программа по дням. Подбор за 15 минут, звоните +998 90 317-22-88.':
    'Toshkentdan Misrga turlar $590 dan: qaysi kurort kimga mos, qachon uchish kerak, '
    'kunlar bo‘yicha mualliflik dasturi. 15 daqiqada tanlaymiz, '
    'qo‘ng‘iroq qiling +998 90 317-22-88.',
'Туры в Египет из Ташкента': 'Toshkentdan Misrga turlar',
'Туры в Египет': 'Misrga turlar',
'Египет': 'Misr',
'Перелёт из Ташкента занимает около 6 часов прямым рейсом или с одной стыковкой.':
    'Toshkentdan parvoz to‘g‘ridan-to‘g‘ri reys yoki bitta ulanish bilan taxminan '
    '6 soat davom etadi.',
'Круглогодичное море и лучший в регионе подводный мир. Риф здесь начинается в нескольких '
'метрах от берега — маску стоит взять, даже если вы не ныряли.':
    'Yil bo‘yi cho‘miladigan dengiz va mintaqadagi eng yaxshi suv osti olami. Rif bu yerda '
    'qirg‘oqdan bir necha metr narida boshlanadi — hech qachon sho‘ng‘imagan bo‘lsangiz ham, '
    'niqob oling.',
'Шарм-эль-Шейх': 'Sharm-ash-Shayx',
'Коралловый риф прямо у берега, лучший снорклинг. Вход в воду часто с понтона — '
'учитывайте, если едете с малышами.':
    'Marjon rifi to‘g‘ridan-to‘g‘ri qirg‘oq yonida, snorkling uchun eng yaxshi joy. Suvga '
    'kirish ko‘pincha pontondan — kichkintoylar bilan borsangiz, buni hisobga oling.',
'Хургада': 'Xurgada',
'Песчаный пологий вход, спокойнее для детей. Ветрено — поэтому здесь же центр '
'виндсёрфинга и кайта.':
    'Qumli, sayoz kirish — bolalar uchun xavfsizroq. Shamol kuchli, shu bois bu yer '
    'vindsyorfing va kayt markazi ham.',
'Макади и Сахл-Хашиш': 'Makadi va Sahl-Hashish',
'Новые отели, тихие бухты, почти нет городской суеты. Для тех, кто едет отдыхать от людей, '
'а не к людям.':
    'Yangi mehmonxonalar, tinch qo‘ltiqlar, shahar shovqini deyarli yo‘q. Odamlarga emas, '
    'odamlardan dam olishga boradiganlar uchun.',
'Дахаб': 'Dahab',
'Бюджетно, неформально, отличный дайвинг. Культуры «всё включено» тут почти нет — '
'едят в кафе на набережной.':
    'Arzon, erkin muhit, ajoyib dayving. «Hammasi kiritilgan» madaniyati bu yerda deyarli '
    'yo‘q — qirg‘oq bo‘yidagi kafelarda ovqatlanishadi.',
'Купаться можно, но вечером прохладно': 'Cho‘milsa bo‘ladi, lekin kechqurun salqin',
'Один из двух лучших периодов': 'Eng yaxshi ikki davrdan biri',
'Очень жарко. Едут те, кому важна цена': 'Juda issiq. Narx muhim bo‘lganlar boradi',
'Лучшее время: море максимально тёплое, жара спадает':
    'Eng yaxshi vaqt: dengiz eng iliq, jazirama qaytadi',
'Красное море: риф начинается в нескольких метрах от берега':
    'Qizil dengiz: rif qirg‘oqdan bir necha metr narida boshlanadi',
'Пирамиды Гизы — третий день программы': 'Giza piramidalari — dasturning uchinchi kuni',
'Карнакский храм в Луксоре — пятый день программы':
    'Luxordagi Karnak ibodatxonasi — dasturning beshinchi kuni',
'Море, пирамиды и риф': 'Dengiz, piramidalar va rif',
'6 дней · Шарм-эль-Шейх или Хургада с выездом в Каир':
    '6 kun · Sharm-ash-Shayx yoki Xurgada, Qohiraga chiqish bilan',
'Прилёт': 'Yetib borish',
'Прилёт в Шарм-эль-Шейх или Каир, трансфер в отель, размещение и первый выход к морю.':
    'Sharm-ash-Shayx yoki Qohiraga yetib borish, mehmonxonaga transfer, joylashish va '
    'dengizga birinchi chiqish.',
'Пляж': 'Plyaj',
'Свободный день: море, знакомство с территорией отеля, вечерняя прогулка.':
    'Erkin kun: dengiz, mehmonxona hududi bilan tanishuv, kechki sayr.',
'Каир': 'Qohira',
'Экскурсия в Каир автобусом или самолётом: пирамиды Гизы, Сфинкс и Каирский музей.':
    'Qohiraga avtobus yoki samolyotda ekskursiya: Giza piramidalari, Sfinks va Qohira muzeyi.',
'Риф': 'Rif',
'День на курорте: дайвинг или снорклинг в коралловых заповедниках, в том числе '
'в Рас-Мохаммеде.':
    'Kurortda bir kun: marjon qo‘riqxonalarida, jumladan Ras-Muhammadda dayving yoki snorkling.',
'Луксор или яхта': 'Luxor yoki yaxta',
'Из Хургады — Луксор и Карнакский храм. Из Шарм-эль-Шейха — морская прогулка на яхте '
'с выходом в открытое море.':
    'Xurgadadan — Luxor va Karnak ibodatxonasi. Sharm-ash-Shayxdan — ochiq dengizga chiqadigan '
    'yaxtada sayr.',
'Свободный день': 'Erkin kun',
'Сувениры, спа или поездка на квадроциклах по пустыне.':
    'Sovg‘alar, spa yoki cho‘l bo‘ylab kvadrotsikllarda sayohat.',
'Обязательны ли специальные тапочки для моря?': 'Dengiz uchun maxsus shippak shartmi?',
'В Шарм-эль-Шейхе — да, риф острый, без обуви легко порезаться. В Хургаде на песчаных '
'пляжах можно обойтись. Мы предупреждаем об этом заранее, а не когда вы уже на месте.':
    'Sharm-ash-Shayxda — ha, rif o‘tkir, oyoq kiyimsiz oson kesiladi. Xurgadada qumli '
    'plyajlarda usiz ham bo‘ladi. Biz bu haqda oldindan ogohlantiramiz, siz joyga '
    'borganingizda emas.',
'Можно ли пить воду из-под крана?': 'Jo‘mrakdagi suvni ichsa bo‘ladimi?',
'Нет, только бутилированную. В отелях она обычно есть в номере и в барах.':
    'Yo‘q, faqat shishadagisini. Mehmonxonalarda u odatda xonada va barlarda bo‘ladi.',
'Когда ехать, если важно тёплое море?': 'Iliq dengiz muhim bo‘lsa, qachon borish kerak?',
'Сентябрь и октябрь — вода около +27 при уже терпимом воздухе. Зимой купаться можно, '
'но вода около +22 и ветер.':
    'Sentabr va oktabr — suv taxminan +27, havo esa allaqachon chidasa bo‘ladigan darajada. '
    'Qishda ham cho‘milsa bo‘ladi, lekin suv +22 atrofida va shamol bo‘ladi.',
'Что с визой?': 'Viza qanday?',
'Условия въезда меняются, мы проверяем их на дату вашего вылета. Позвоните или напишите — '
'скажем точно и поможем с оформлением, если оно потребуется.':
    'Kirish shartlari o‘zgarib turadi, biz ularni sizning uchish sanangizga tekshiramiz. '
    'Qo‘ng‘iroq qiling yoki yozing — aniq aytamiz va kerak bo‘lsa, rasmiylashtirishga '
    'yordam beramiz.',

# ─── Таиланд ──────────────────────────────────────────────────────────
'Туры в Таиланд из Ташкента — цены и авторские программы':
    'Toshkentdan Tailandga turlar — narxlar va mualliflik dasturlari',
'Туры в Таиланд из Ташкента от $790: какой курорт кому подходит, когда лететь, '
'авторская программа по дням. Подбор за 15 минут, звоните +998 90 317-22-88.':
    'Toshkentdan Tailandga turlar $790 dan: qaysi kurort kimga mos, qachon uchish kerak, '
    'kunlar bo‘yicha mualliflik dasturi. 15 daqiqada tanlaymiz, '
    'qo‘ng‘iroq qiling +998 90 317-22-88.',
'Туры в Таиланд из Ташкента': 'Toshkentdan Tailandga turlar',
'Туры в Таиланд': 'Tailandga turlar',
'Таиланд': 'Tailand',
'Перелёт с одной стыковкой занимает от 9 до 12 часов в зависимости от маршрута.':
    'Bitta ulanishli parvoz marshrutga qarab 9 soatdan 12 soatgacha davom etadi.',
'Море, острова и еда, ради которой стоит лететь отдельно. Летят на подольше — '
'перелёт длинный, и на неделю ехать обидно.':
    'Dengiz, orollar va alohida uchishga arziydigan taomlar. Uzoqroq muddatga uchishadi — '
    'parvoz uzoq, bir haftaga borish esa achinarli.',
'Пхукет': 'Phuket',
'Главный курорт с максимальной инфраструктурой. Патонг шумный и ночной, Ката и Карон '
'заметно спокойнее, Най Харн — почти для своих.':
    'Infratuzilmasi eng to‘liq bo‘lgan asosiy kurort. Patong shovqinli va tungi, Kata bilan '
    'Karon ancha tinch, Nay Xarn esa deyarli o‘zimiznikilar uchun.',
'Краби и Ао Нанг': 'Krabi va Ao Nang',
'Известняковые скалы, лодки до островов, тише и дешевле Пхукета. Для тех, кому важнее '
'природа, чем сервис.':
    'Ohaktosh qoyalar, orollarga qayiqlar, Phuketdan tinchroq va arzonroq. Xizmatdan ko‘ra '
    'tabiat muhimroq bo‘lganlar uchun.',
'Самуи': 'Samui',
'Отдельный остров со своим ритмом и своим сезоном — он не совпадает с Пхукетом, '
'это важно при выборе дат.':
    'O‘z ritmi va o‘z mavsumiga ega alohida orol — u Phuket bilan mos kelmaydi, sanalarni '
    'tanlashda bu muhim.',
'Паттайя': 'Pattayya',
'Ближе всего к Бангкоку и дешевле остальных. Море заметно хуже — берут ради цены '
'и городской жизни.':
    'Bangkokka eng yaqin va boshqalardan arzon. Dengizi sezilarli yomonroq — narx va shahar '
    'hayoti uchun tanlashadi.',
'Сухой сезон на Андаманском побережье. Лучшее время':
    'Andaman sohilida quruq mavsum. Eng yaxshi vaqt',
'Дожди начинаются, но ещё короткие. Цены ниже':
    'Yomg‘irlar boshlanadi, lekin hali qisqa. Narxlar past',
'Сезон дождей на Пхукете и Краби. На Самуи в это время суше':
    'Phuket va Krabida yomg‘irlar mavsumi. Samuida bu paytda quruqroq',
'Бухта Майя Бэй на островах Пхи-Пхи — пятый день программы':
    'Phi-Phi orollaridagi Mayya Bey qo‘ltig‘i — dasturning beshinchi kuni',
'Большой королевский дворец в Бангкоке — второй день программы':
    'Bangkokdagi Katta qirollik saroyi — dasturning ikkinchi kuni',
'Чаопхрая вечером: огни города на воде': 'Kechki Chaopxraya: suvdagi shahar chiroqlari',
'Бангкок и море': 'Bangkok va dengiz',
'9 дней · Бангкок → Пхукет или Паттайя': '9 kun · Bangkok → Phuket yoki Pattayya',
'Прилёт в Бангкок': 'Bangkokka yetib borish',
'Трансфер в отель, отдых после перелёта, вечерняя прогулка по реке Чаопхрая.':
    'Mehmonxonaga transfer, parvozdan keyin dam olish, Chaopxraya daryosi bo‘ylab kechki sayr.',
'Королевский Бангкок': 'Qirollik Bangkoki',
'Большой королевский дворец, храм Изумрудного Будды и Ват Пхо с лежащим Буддой.':
    'Katta qirollik saroyi, Zumrad Budda ibodatxonasi va yotgan Budda joylashgan Vat Pho.',
'Город сверху': 'Shahar tepadan',
'Смотровая площадка небоскрёба Mahanakhon, шопинг в Siam Paragon или MBK.':
    'Mahanakhon osmono‘par binosidagi kuzatuv maydonchasi, Siam Paragon yoki MBKda xarid.',
'Переезд на море': 'Dengizga ko‘chish',
'Перелёт или переезд на курорт, заселение в отель у моря, первый вечер на пляже.':
    'Kurortga parvoz yoki ko‘chish, dengiz bo‘yidagi mehmonxonaga joylashish, '
    'plyajdagi birinchi kech.',
'Пхи-Пхи': 'Phi-Phi',
'Морская экскурсия на скоростном катере к островам Пхи-Пхи и в бухту Майя Бэй.':
    'Tezyurar kater bilan Phi-Phi orollariga va Mayya Bey qo‘ltig‘iga dengiz ekskursiyasi.',
'Отдых': 'Dam olish',
'Свободный день на пляже — Патонг, Карон или Ката. Тайский массаж и вечернее шоу.':
    'Plyajda erkin kun — Patong, Karon yoki Kata. Tay massaji va kechki shou.',
'Слоны или Будда': 'Fillar yoki Budda',
'Экскурсия в заповедник слонов или поездка к Большому Будде.':
    'Fillar qo‘riqxonasiga ekskursiya yoki Katta Buddaga sayohat.',
'Свой темп': 'O‘z sur’atingizda',
'Пляж, аренда байка, поездка на соседние уединённые пляжи.':
    'Plyaj, mototsikl ijarasi, qo‘shni xilvat plyajlarga sayohat.',
'Прощание': 'Xayrlashuv',
'Сувениры и фрукты, прощальный ужин с морепродуктами.':
    'Sovg‘alar va mevalar, dengiz mahsulotlari bilan xayrlashuv kechki ovqati.',
'На сколько дней имеет смысл лететь?': 'Necha kunga uchish ma’qul?',
'От десяти ночей. Перелёт длинный, плюс два-три дня уходит на смену часового пояса — '
'на неделе вы толком не успеете отдохнуть.':
    'Kamida o‘n kecha. Parvoz uzoq, ustiga vaqt mintaqasiga ko‘nikishga ikki-uch kun ketadi — '
    'bir haftada dam olishga ulgurmaysiz.',
'Когда сезон дождей и стоит ли его бояться?':
    'Yomg‘irlar mavsumi qachon va undan qo‘rqish kerakmi?',
'С мая по октябрь на Пхукете и в Краби. Дождь обычно короткий и сильный, а не весь день, '
'и цены в это время заметно ниже. Если поездка не первая — вариант рабочий.':
    'Maydan oktabrgacha Phuketda va Krabida. Yomg‘ir odatda kun bo‘yi emas, qisqa va kuchli '
    'yog‘adi, narxlar esa bu paytda sezilarli past. Agar sayohat birinchi bo‘lmasa — '
    'bu ishlaydigan variant.',
'Чем Самуи отличается по датам?': 'Samui sanalar bo‘yicha nimasi bilan farq qiladi?',
'У него противоположный сезон: когда на Пхукете дожди, на Самуи чаще сухо. '
'Это спасает, если отпуск выпадает на лето.':
    'Uning mavsumi teskari: Phuketda yomg‘ir yog‘ayotganda Samuida ko‘pincha quruq bo‘ladi. '
    'Ta’til yozga to‘g‘ri kelsa, bu qutqaradi.',
'Что с визой и документами?': 'Viza va hujjatlar qanday?',
'Правила въезда для граждан Узбекистана меняются, мы уточняем их на дату вылета. '
'Напишите — проверим и подскажем, что понадобится.':
    'O‘zbekiston fuqarolari uchun kirish qoidalari o‘zgarib turadi, biz ularni uchish sanasiga '
    'aniqlaymiz. Yozing — tekshiramiz va nima kerakligini aytamiz.',

# ─── Вьетнам ──────────────────────────────────────────────────────────
'Туры во Вьетнам из Ташкента — цены и авторские программы':
    'Toshkentdan Vyetnamga turlar — narxlar va mualliflik dasturlari',
'Туры во Вьетнам из Ташкента от $720: какой курорт кому подходит, когда лететь, '
'авторская программа по дням. Подбор за 15 минут, звоните +998 90 317-22-88.':
    'Toshkentdan Vyetnamga turlar $720 dan: qaysi kurort kimga mos, qachon uchish kerak, '
    'kunlar bo‘yicha mualliflik dasturi. 15 daqiqada tanlaymiz, '
    'qo‘ng‘iroq qiling +998 90 317-22-88.',
'Туры во Вьетнам из Ташкента': 'Toshkentdan Vyetnamga turlar',
'Туры во Вьетнам': 'Vyetnamga turlar',
'Вьетнам': 'Vyetnam',
'Перелёт с одной стыковкой занимает от 9 до 11 часов.':
    'Bitta ulanishli parvoz 9 soatdan 11 soatgacha davom etadi.',
'Дешевле Таиланда при сопоставимом море, а еда и природа — отдельная причина лететь. '
'Здесь проще выйти за пределы отеля и увидеть страну.':
    'Dengiz Tailanddagiga o‘xshash, narx esa arzonroq, taomlar va tabiat esa uchish uchun '
    'alohida sabab. Bu yerda mehmonxonadan chiqib, mamlakatni ko‘rish osonroq.',
'Нячанг': 'Nyachang',
'Длинный городской пляж, много русскоязычной среды, кафе и экскурсий. '
'Проще всего для первой поездки.':
    'Uzun shahar plyaji, ko‘p rusiyzabon muhit, kafelar va ekskursiyalar. '
    'Birinchi sayohat uchun eng oson variant.',
'Фукуок': 'Fukuok',
'Остров с самыми чистыми пляжами страны и спокойным морем. Дороже материка, '
'но и уровень другой.':
    'Mamlakatdagi eng toza plyajlar va tinch dengizga ega orol. Materikdan qimmat, '
    'lekin darajasi ham boshqacha.',
'Дананг и Хойан': 'Danang va Xoyan',
'Пляж рядом со старым городом, внесённым в список ЮНЕСКО. Для тех, кому мало лежать на песке.':
    'YUNESKO ro‘yxatiga kiritilgan eski shahar yonidagi plyaj. Qumda yotishning o‘zi kamlik '
    'qiladiganlar uchun.',
'Муйне': 'Muyne',
'Ветер и кайтсёрфинг, дюны, минимум суеты. Едут ради спорта и тишины.':
    'Shamol va kaytsyorfing, qumtepalar, shovqin minimal. Sport va sokinlik uchun kelishadi.',
'Сухо и солнечно в Нячанге. Основной сезон': 'Nyachangda quruq va quyoshli. Asosiy mavsum',
'Дожди в Нячанге, но на Фукуоке становится лучше':
    'Nyachangda yomg‘irlar, Fukuokda esa yaxshilanadi',
'Сухой сезон на Фукуоке. Лучшее время для острова':
    'Fukuokda quruq mavsum. Orol uchun eng yaxshi vaqt',
'Бухта Халонг: джонка среди известняковых скал — третий день программы':
    'Halong qo‘ltig‘i: ohaktosh qoyalar orasidagi jonka — dasturning uchinchi kuni',
'Золотой мост в Бана Хиллс — четвёртый день программы':
    'Bana Hillsdagi Oltin ko‘prik — dasturning to‘rtinchi kuni',
'Хойан вечером, когда зажигают шёлковые фонарики': 'Ipak chiroqlar yoqilgan kechki Xoyan',
'Гранд-тур по Вьетнаму': 'Vyetnam bo‘ylab grand-tur',
'10 дней · Ханой → Халонг → Дананг → море → Хошимин':
    '10 kun · Hanoy → Halong → Danang → dengiz → Xoshimin',
'Ханой': 'Hanoy',
'Прилёт в столицу, прогулка по Старому кварталу, озеро Возвращённого меча и храм '
'Нгок Шон на островке.':
    'Poytaxtga yetib borish, Eski mahalla bo‘ylab sayr, Qaytarilgan qilich ko‘li va '
    'oroldagi Ngok Shon ibodatxonasi.',
'Бухта Халонг': 'Halong qo‘ltig‘i',
'Круиз среди тысяч известняковых скал в изумрудной воде. Ночёвка на боте или '
'возвращение в Ханой.':
    'Zumrad suvdagi minglab ohaktosh qoyalar orasida kruiz. Kemada tunash yoki Hanoyga qaytish.',
'Перелёт в центральную часть страны, Золотой мост на руке гиганта в Бана Хиллс, '
'вечерний Хойан с фонариками.':
    'Mamlakatning markaziy qismiga parvoz, Bana Hillsdagi ulkan qo‘llar ustidagi Oltin '
    'ko‘prik, chiroqlar yoqilgan kechki Xoyan.',
'Море': 'Dengiz',
'Переезд на курорт — Нячанг или Фукуок. Пляжный отдых и парк развлечений Винперл.':
    'Kurortga ko‘chish — Nyachang yoki Fukuok. Plyajda dam olish va Vinperl ko‘ngilochar parki.',
'Хошимин': 'Xoshimin',
'Переезд на юг, экскурсия по Сайгону, тоннели Кути. Трансфер в аэропорт.':
    'Janubga ko‘chish, Saygon bo‘ylab ekskursiya, Kuti tunnellari. Aeroportga transfer.',
'Чем Вьетнам лучше Таиланда?': 'Vyetnam Tailanddan nimasi bilan yaxshi?',
'В среднем дешевле при сопоставимом море, и заметно интереснее с точки зрения еды и '
'поездок вглубь страны. Хуже — с сервисом в отелях среднего уровня и с прозрачностью '
'цен на месте.':
    'O‘rtacha arzonroq, dengiz esa taqqoslasa bo‘ladigan darajada, taomlar va mamlakat '
    'ichkarisiga sayohatlar jihatidan ancha qiziqroq. Yomonroq tomoni — o‘rta darajadagi '
    'mehmonxonalar xizmati va joydagi narxlarning shaffofligi.',
'Куда лучше с детьми?': 'Bolalar bilan qayerga borgan yaxshi?',
'На Фукуок: море спокойнее, пляжи чище, меньше городского движения. Нячанг — это всё-таки '
'большой город с оживлённой набережной.':
    'Fukuokka: dengiz tinchroq, plyajlar tozaroq, shahar harakati kamroq. Nyachang esa '
    'baribir gavjum qirg‘oq bo‘yiga ega katta shahar.',
'Когда ехать?': 'Qachon borish kerak?',
'В Нячанг — с февраля по август. На Фукуок — с ноября по апрель. Это разные сезоны, '
'и выбор курорта часто определяется именно датами отпуска.':
    'Nyachangga — fevraldan avgustgacha. Fukuokka — noyabrdan aprelgacha. Bu turli mavsumlar, '
    'va kurort tanlovi ko‘pincha aynan ta’til sanalariga qarab hal bo‘ladi.',
'Нужна ли виза?': 'Viza kerakmi?',
'Условия въезда меняются, мы проверяем их на конкретную дату. Позвоните или напишите — '
'уточним и поможем с оформлением.':
    'Kirish shartlari o‘zgarib turadi, biz ularni aniq sanaga tekshiramiz. Qo‘ng‘iroq qiling '
    'yoki yozing — aniqlaymiz va rasmiylashtirishga yordam beramiz.',

# ─── месяцы и периоды ─────────────────────────────────────────────────
'Май — июнь': 'May — iyun',
'Март — май': 'Mart — may',
'Июль — август': 'Iyul — avgust',
'Июнь — август': 'Iyun — avgust',
'Июль — октябрь': 'Iyul — oktabr',
'Февраль — август': 'Fevral — avgust',
'Сентябрь — ноябрь': 'Sentabr — noyabr',
'Сентябрь — декабрь': 'Sentabr — dekabr',
'Ноябрь — апрель': 'Noyabr — aprel',
'Декабрь — февраль': 'Dekabr — fevral',
'Сентябрь': 'Sentabr',
'Октябрь': 'Oktabr',
'Июнь': 'Iyun',
'Май': 'May',
'Когда': 'Qachon',
'+26 воздух, +21 море': 'havo +26, dengiz +21',
'+24 воздух, +22 море': 'havo +24, dengiz +22',
'+31 воздух, +28 море': 'havo +31, dengiz +28',
'+32 воздух, +29 море': 'havo +32, dengiz +29',

# ─── цены на карточках ────────────────────────────────────────────────
'от $520': '$520 dan',
'от $590': '$590 dan',
'от $720': '$720 dan',
'от $790': '$790 dan',
}
