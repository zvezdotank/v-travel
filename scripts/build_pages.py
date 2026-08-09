#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка страниц направлений из данных.

Четыре страницы отличаются только содержимым, поэтому шапка, подвал и
разметка описаны здесь один раз. Правка контактов или меню — правка этого
файла и один запуск, а не пять html подряд.

    python3 scripts/build_pages.py

Пересобирает /turciya/, /egipet/, /tailand/, /vietnam/ и sitemap.xml.
"""

from pathlib import Path
import html
import json
import re
from datetime import date
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://v-travel.uz"
PHONE = "+998903172288"
PHONE_HUMAN = "+998 90 317-22-88"
TG = "vtour_travel"
TG_DEALS = "vtour_deals"

# ════════════════════════════════════════════════════════════════════
#  Авторские программы — присланы агентством, это реальный продукт.
#  Цены намеренно не проставлены: они зависят от дат и класса отеля,
#  поэтому вместо числа стоит расчёт по запросу.
#  Курорты, сезонность и вопросы — общая проверяемая справка.
# ════════════════════════════════════════════════════════════════════

DESTS = [
{
 "slug": "turciya",
 "name": "Турция",
 "to": "в Турцию",
 "image": "dest-turkey.webp",
 "price": "520",
 "flight": "Прямой рейс Ташкент — Анталия занимает около 5,5 часов.",
 "lead": "Самое простое первое море: прямые рейсы, «всё включено» как норма, "
         "отели под любой бюджет. Сюда летят и с детьми, и вдвоём, и компанией.",
 "resorts": [
   ("Анталия", "Самый большой выбор отелей и вся инфраструктура под рукой: аквапарки, "
               "рынки, экскурсии. Городские пляжи галечные. Берите, если хотите, чтобы вокруг что-то происходило."),
   ("Кемер", "Горы подходят вплотную к морю, вода прозрачнее, чем на равнине, вечером "
             "заметно прохладнее. Пляжи галечные. Для тех, кому важен вид из окна."),
   ("Белек", "Сосновые леса, песок, поля для гольфа и самые дорогие отели побережья. "
             "Сюда едут семьи, готовые доплатить за территорию и сервис."),
   ("Сиде", "Песчаные пляжи и античные руины прямо в черте города. Разумный компромисс "
            "между ценой и качеством пляжа."),
   ("Бодрум", "Эгейское побережье: вода прохладнее, публика взрослее, ночная жизнь "
              "серьёзнее. Не для отдыха с малышами."),
 ],
 "seasons": [
   ("Май", "+26 воздух, +21 море", "Народу мало, цены низкие, но море ещё бодрит"),
   ("Июнь", "+30 / +24", "Оптимально: тепло, но ещё не пекло"),
   ("Июль — август", "+34 / +28", "Пик сезона. Самые высокие цены и самая сильная жара"),
   ("Сентябрь", "+31 / +27", "Лучший месяц. Вода прогрета, жара спала, школьники уехали"),
   ("Октябрь", "+26 / +24", "Купаться ещё можно, цены падают заметно"),
 ],
 "photos": {
   "after_resorts": ("turciya-buhta.webp", "Средиземноморское побережье: бирюзовые бухты и сосновые склоны, спускающиеся прямо к воде"),
   "in_program": ("turciya-kappadokiya.webp", "Рассвет над Каппадокией — четвёртый день программы"),
   "in_faq": ("turciya-stambul.webp", "Босфор на закате: паром идёт мимо силуэтов минаретов"),
 },
 "program": {
   "title": "Стамбул и Каппадокия",
   "sub": "7 дней · Стамбул → Каппадокия → Памуккале или Анталия",
   "days": [
     ("1–2", "Стамбул", "Прилёт и размещение. Обзорная экскурсия: Голубая мечеть, собор Святой Софии, дворец Топкапы и прогулка по Босфору."),
     ("3", "Перелёт в Каппадокию", "Утренний перелёт в Невшехир или Кайсери, размещение в пещерном отеле в Гёреме, музей под открытым небом."),
     ("4", "Каппадокия", "Ранний подъём и полёт на воздушном шаре. Подземные города и долина Пашабаг."),
     ("5–6", "Памуккале или Анталия", "На выбор: белоснежные травертины Памуккале или отдых на средиземноморском побережье."),
     ("7", "Стамбул и вылет", "Возвращение в Стамбул, сувениры на Гранд-базаре, трансфер в аэропорт."),
   ],
 },
 "faq": [
   ("Нужна ли виза гражданам Узбекистана?",
    "Правила въезда меняются, поэтому мы всегда проверяем их на конкретную дату вылета "
    "перед бронированием. Напишите или позвоните — уточним актуальные условия и, если "
    "нужны документы, поможем их собрать."),
   ("Когда дешевле всего лететь?",
    "В мае и октябре. Цены на те же отели ниже пиковых, а море уже или ещё пригодно для "
    "купания. Если даты не привязаны к отпуску, разница бывает существенной."),
   ("Что на самом деле входит в «всё включено»?",
    "У разных отелей это разные вещи: где-то местный алкоголь и три приёма пищи, где-то "
    "ещё и снеки, мороженое, а-ля карт рестораны. Мы разбираем состав до бронирования, "
    "чтобы на месте не оказалось, что половина — за отдельные деньги."),
   ("Галька или песок?",
    "В Кемере и большей части Анталии — галька, в Сиде и Белеке — песок. Если едете с "
    "маленьким ребёнком, это принципиально: скажите, и мы подберём отель с песчаным входом."),
 ],
},
{
 "slug": "egipet",
 "name": "Египет",
 "to": "в Египет",
 "image": "dest-egypt.webp",
 "price": "590",
 "flight": "Перелёт из Ташкента занимает около 6 часов прямым рейсом или с одной стыковкой.",
 "lead": "Круглогодичное море и лучший в регионе подводный мир. Риф здесь начинается "
         "в нескольких метрах от берега — маску стоит взять, даже если вы не ныряли.",
 "resorts": [
   ("Шарм-эль-Шейх", "Коралловый риф прямо у берега, лучший снорклинг. Вход в воду часто "
                     "с понтона — учитывайте, если едете с малышами."),
   ("Хургада", "Песчаный пологий вход, спокойнее для детей. Ветрено — поэтому здесь же "
               "центр виндсёрфинга и кайта."),
   ("Макади и Сахл-Хашиш", "Новые отели, тихие бухты, почти нет городской суеты. "
                           "Для тех, кто едет отдыхать от людей, а не к людям."),
   ("Дахаб", "Бюджетно, неформально, отличный дайвинг. Культуры «всё включено» тут почти "
             "нет — едят в кафе на набережной."),
 ],
 "seasons": [
   ("Декабрь — февраль", "+24 воздух, +22 море", "Купаться можно, но вечером прохладно"),
   ("Март — май", "+30 / +24", "Один из двух лучших периодов"),
   ("Июнь — август", "+40 / +29", "Очень жарко. Едут те, кому важна цена"),
   ("Сентябрь — ноябрь", "+33 / +27", "Лучшее время: море максимально тёплое, жара спадает"),
 ],
 "photos": {
   "after_resorts": ("egipet-rif.webp", "Красное море: риф начинается в нескольких метрах от берега"),
   "in_program": ("egipet-piramidy.webp", "Пирамиды Гизы — третий день программы"),
   "in_faq": ("egipet-karnak.webp", "Карнакский храм в Луксоре — пятый день программы"),
 },
 "program": {
   "title": "Море, пирамиды и риф",
   "sub": "6 дней · Шарм-эль-Шейх или Хургада с выездом в Каир",
   "days": [
     ("1", "Прилёт", "Прилёт в Шарм-эль-Шейх или Каир, трансфер в отель, размещение и первый выход к морю."),
     ("2", "Пляж", "Свободный день: море, знакомство с территорией отеля, вечерняя прогулка."),
     ("3", "Каир", "Экскурсия в Каир автобусом или самолётом: пирамиды Гизы, Сфинкс и Каирский музей."),
     ("4", "Риф", "День на курорте: дайвинг или снорклинг в коралловых заповедниках, в том числе в Рас-Мохаммеде."),
     ("5", "Луксор или яхта", "Из Хургады — Луксор и Карнакский храм. Из Шарм-эль-Шейха — морская прогулка на яхте с выходом в открытое море."),
     ("6", "Свободный день", "Сувениры, спа или поездка на квадроциклах по пустыне."),
   ],
 },
 "faq": [
   ("Обязательны ли специальные тапочки для моря?",
    "В Шарм-эль-Шейхе — да, риф острый, без обуви легко порезаться. В Хургаде на песчаных "
    "пляжах можно обойтись. Мы предупреждаем об этом заранее, а не когда вы уже на месте."),
   ("Можно ли пить воду из-под крана?",
    "Нет, только бутилированную. В отелях она обычно есть в номере и в барах."),
   ("Когда ехать, если важно тёплое море?",
    "Сентябрь и октябрь — вода около +27 при уже терпимом воздухе. Зимой купаться можно, "
    "но вода около +22 и ветер."),
   ("Что с визой?",
    "Условия въезда меняются, мы проверяем их на дату вашего вылета. Позвоните или "
    "напишите — скажем точно и поможем с оформлением, если оно потребуется."),
 ],
},
{
 "slug": "tailand",
 "name": "Таиланд",
 "to": "в Таиланд",
 "image": "dest-thailand.webp",
 "price": "790",
 "flight": "Перелёт с одной стыковкой занимает от 9 до 12 часов в зависимости от маршрута.",
 "lead": "Море, острова и еда, ради которой стоит лететь отдельно. Летят на подольше — "
         "перелёт длинный, и на неделю ехать обидно.",
 "resorts": [
   ("Пхукет", "Главный курорт с максимальной инфраструктурой. Патонг шумный и ночной, "
              "Ката и Карон заметно спокойнее, Най Харн — почти для своих."),
   ("Краби и Ао Нанг", "Известняковые скалы, лодки до островов, тише и дешевле Пхукета. "
                       "Для тех, кому важнее природа, чем сервис."),
   ("Самуи", "Отдельный остров со своим ритмом и своим сезоном — он не совпадает с "
             "Пхукетом, это важно при выборе дат."),
   ("Паттайя", "Ближе всего к Бангкоку и дешевле остальных. Море заметно хуже — берут "
               "ради цены и городской жизни."),
 ],
 "seasons": [
   ("Ноябрь — апрель", "+32 воздух, +29 море", "Сухой сезон на Андаманском побережье. Лучшее время"),
   ("Май — июнь", "+32 / +29", "Дожди начинаются, но ещё короткие. Цены ниже"),
   ("Июль — октябрь", "+31 / +29", "Сезон дождей на Пхукете и Краби. На Самуи в это время суше"),
 ],
 "photos": {
   "after_resorts": ("tailand-mayya.webp", "Бухта Майя Бэй на островах Пхи-Пхи — пятый день программы"),
   "in_program": ("tailand-dvorec.webp", "Большой королевский дворец в Бангкоке — второй день программы"),
   "in_faq": ("tailand-reka.webp", "Чаопхрая вечером: огни города на воде"),
 },
 "program": {
   "title": "Бангкок и море",
   "sub": "9 дней · Бангкок → Пхукет или Паттайя",
   "days": [
     ("1", "Прилёт в Бангкок", "Трансфер в отель, отдых после перелёта, вечерняя прогулка по реке Чаопхрая."),
     ("2", "Королевский Бангкок", "Большой королевский дворец, храм Изумрудного Будды и Ват Пхо с лежащим Буддой."),
     ("3", "Город сверху", "Смотровая площадка небоскрёба Mahanakhon, шопинг в Siam Paragon или MBK."),
     ("4", "Переезд на море", "Перелёт или переезд на курорт, заселение в отель у моря, первый вечер на пляже."),
     ("5", "Пхи-Пхи", "Морская экскурсия на скоростном катере к островам Пхи-Пхи и в бухту Майя Бэй."),
     ("6", "Отдых", "Свободный день на пляже — Патонг, Карон или Ката. Тайский массаж и вечернее шоу."),
     ("7", "Слоны или Будда", "Экскурсия в заповедник слонов или поездка к Большому Будде."),
     ("8", "Свой темп", "Пляж, аренда байка, поездка на соседние уединённые пляжи."),
     ("9", "Прощание", "Сувениры и фрукты, прощальный ужин с морепродуктами."),
   ],
 },
 "faq": [
   ("На сколько дней имеет смысл лететь?",
    "От десяти ночей. Перелёт длинный, плюс два-три дня уходит на смену часового пояса — "
    "на неделе вы толком не успеете отдохнуть."),
   ("Когда сезон дождей и стоит ли его бояться?",
    "С мая по октябрь на Пхукете и в Краби. Дождь обычно короткий и сильный, а не весь "
    "день, и цены в это время заметно ниже. Если поездка не первая — вариант рабочий."),
   ("Чем Самуи отличается по датам?",
    "У него противоположный сезон: когда на Пхукете дожди, на Самуи чаще сухо. Это "
    "спасает, если отпуск выпадает на лето."),
   ("Что с визой и документами?",
    "Правила въезда для граждан Узбекистана меняются, мы уточняем их на дату вылета. "
    "Напишите — проверим и подскажем, что понадобится."),
 ],
},
{
 "slug": "vietnam",
 "name": "Вьетнам",
 "to": "во Вьетнам",
 "image": "dest-vietnam.webp",
 "price": "720",
 "flight": "Перелёт с одной стыковкой занимает от 9 до 11 часов.",
 "lead": "Дешевле Таиланда при сопоставимом море, а еда и природа — отдельная причина "
         "лететь. Здесь проще выйти за пределы отеля и увидеть страну.",
 "resorts": [
   ("Нячанг", "Длинный городской пляж, много русскоязычной среды, кафе и экскурсий. "
              "Проще всего для первой поездки."),
   ("Фукуок", "Остров с самыми чистыми пляжами страны и спокойным морем. Дороже "
              "материка, но и уровень другой."),
   ("Дананг и Хойан", "Пляж рядом со старым городом, внесённым в список ЮНЕСКО. "
                      "Для тех, кому мало лежать на песке."),
   ("Муйне", "Ветер и кайтсёрфинг, дюны, минимум суеты. Едут ради спорта и тишины."),
 ],
 "seasons": [
   ("Февраль — август", "+31 воздух, +28 море", "Сухо и солнечно в Нячанге. Основной сезон"),
   ("Сентябрь — декабрь", "+28 / +27", "Дожди в Нячанге, но на Фукуоке становится лучше"),
   ("Ноябрь — апрель", "+30 / +28", "Сухой сезон на Фукуоке. Лучшее время для острова"),
 ],
 "photos": {
   "after_resorts": ("vietnam-halong.webp", "Бухта Халонг: джонка среди известняковых скал — третий день программы"),
   "in_program": ("vietnam-most.webp", "Золотой мост в Бана Хиллс — четвёртый день программы"),
   "in_faq": ("vietnam-hoyan.webp", "Хойан вечером, когда зажигают шёлковые фонарики"),
 },
 "program": {
   "title": "Гранд-тур по Вьетнаму",
   "sub": "10 дней · Ханой → Халонг → Дананг → море → Хошимин",
   "days": [
     ("1–2", "Ханой", "Прилёт в столицу, прогулка по Старому кварталу, озеро Возвращённого меча и храм Нгок Шон на островке."),
     ("3", "Бухта Халонг", "Круиз среди тысяч известняковых скал в изумрудной воде. Ночёвка на боте или возвращение в Ханой."),
     ("4–5", "Дананг и Хойан", "Перелёт в центральную часть страны, Золотой мост на руке гиганта в Бана Хиллс, вечерний Хойан с фонариками."),
     ("6–8", "Море", "Переезд на курорт — Нячанг или Фукуок. Пляжный отдых и парк развлечений Винперл."),
     ("9–10", "Хошимин", "Переезд на юг, экскурсия по Сайгону, тоннели Кути. Трансфер в аэропорт."),
   ],
 },
 "faq": [
   ("Чем Вьетнам лучше Таиланда?",
    "В среднем дешевле при сопоставимом море, и заметно интереснее с точки зрения еды и "
    "поездок вглубь страны. Хуже — с сервисом в отелях среднего уровня и с прозрачностью "
    "цен на месте."),
   ("Куда лучше с детьми?",
    "На Фукуок: море спокойнее, пляжи чище, меньше городского движения. Нячанг — это "
    "всё-таки большой город с оживлённой набережной."),
   ("Когда ехать?",
    "В Нячанг — с февраля по август. На Фукуок — с ноября по апрель. Это разные сезоны, "
    "и выбор курорта часто определяется именно датами отпуска."),
   ("Нужна ли виза?",
    "Условия въезда меняются, мы проверяем их на конкретную дату. Позвоните или напишите "
    "— уточним и поможем с оформлением."),
 ],
},
]


# ─────────────────────────── помощники ───────────────────────────

def tg_link(text):
    return "https://t.me/%s?text=%s" % (TG, quote(text))


def e(s):
    return html.escape(s, quote=True)


ICON_PHONE = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
              'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6 19.8 19.8 0 '
              '01-3.1-8.7A2 2 0 014.1 2h3a2 2 0 012 1.7c.1 1 .3 2 .7 2.9a2 2 0 01-.4 2.1L8 10.1a16 16 0 '
              '006 6l1.4-1.4a2 2 0 012.1-.4c.9.4 1.9.6 2.9.7a2 2 0 011.7 2"/></svg>')

ICON_TG = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">'
           '<path d="M21.9 4.3L18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1L18 '
           '6.4c.4-.4-.1-.6-.6-.2L7.2 12.7l-4.9-1.5c-1.1-.3-1.1-1 .2-1.5l19.1-7.4c.9-.3 1.7.2 1.4 2z"/></svg>')


def header_html():
    return f'''<header class="header" id="header">
  <div class="shell header__inner">
    <a href="/" class="logo" aria-label="V-travel, на главную">
      <span class="logo__mark" aria-hidden="true">
        <svg viewBox="0 0 32 32" width="20" height="20"><path d="M6 9l10 16L26 9" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </span>
      <span class="logo__text">V<span>-travel</span></span>
    </a>

    <nav class="nav" id="nav" aria-label="Основная навигация">
      <a href="/#hot" class="nav__link">Горящие туры</a>
      <a href="/#dest" class="nav__link">Направления</a>
      <a href="/#tickets" class="nav__link">Авиабилеты</a>
      <a href="/#how" class="nav__link">Как работаем</a>
      <a href="/#reviews" class="nav__link">Отзывы</a>
      <a href="/#pick" class="nav__link">Подбор тура</a>
      <div class="nav__mobile-actions">
        <a href="tel:{PHONE}" class="btn btn--ghost btn--block">+998 90 317-22-88</a>
        <a href="https://t.me/{TG}" target="_blank" rel="noopener" class="btn btn--tg btn--block">Написать в Telegram</a>
      </div>
    </nav>

    <div class="header__actions">
      <a href="tel:{PHONE}" class="header__phone" data-goal="call">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6 19.8 19.8 0 01-3.1-8.7A2 2 0 014.1 2h3a2 2 0 012 1.7c.1 1 .3 2 .7 2.9a2 2 0 01-.4 2.1L8 10.1a16 16 0 006 6l1.4-1.4a2 2 0 012.1-.4c.9.4 1.9.6 2.9.7a2 2 0 011.7 2"/></svg>
        <span>{PHONE_HUMAN}</span>
      </a>
      <a href="https://t.me/{TG}" target="_blank" rel="noopener" class="btn btn--tg btn--sm" data-goal="telegram">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3L18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1L18 6.4c.4-.4-.1-.6-.6-.2L7.2 12.7l-4.9-1.5c-1.1-.3-1.1-1 .2-1.5l19.1-7.4c.9-.3 1.7.2 1.4 2z"/></svg>
        Telegram
      </a>
      <button class="burger" id="burger" aria-label="Меню" aria-expanded="false" aria-controls="nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>'''


def footer_html(others):
    links = "\n".join(
        '      <a href="/%s/">Туры %s</a>' % (d["slug"], d["to"]) for d in others)
    return f'''<footer class="footer">
  <div class="shell footer__inner">
    <div class="footer__brand">
      <a href="/" class="logo logo--sm">
        <span class="logo__mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="18" height="18"><path d="M6 9l10 16L26 9" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="logo__text">V<span>-travel</span></span>
      </a>
      <p>Туристическое агентство. Подбор и оформление туров под ключ. Вылеты из Ташкента.</p>
    </div>

    <nav class="footer__nav" aria-label="Направления">
{links}
      <a href="/#tickets">Авиабилеты</a>
    </nav>

    <div class="footer__contacts">
      <a href="tel:{PHONE}" class="footer__phone" data-goal="call">{PHONE_HUMAN}</a>
      <a href="https://t.me/{TG}" target="_blank" rel="noopener" data-goal="telegram">Telegram: @{TG}</a>
      <span>Ежедневно 09:00–21:00</span>
    </div>
  </div>
  <div class="shell footer__bottom">
    <span>© <span id="year">{date.today().year}</span> V-travel</span>
    <span>Цены указаны за человека при двухместном размещении и зависят от даты вылета.</span>
  </div>
</footer>

<div class="actionbar" id="actionbar">
  <a href="tel:{PHONE}" class="actionbar__btn actionbar__btn--call" data-goal="call">{ICON_PHONE}Позвонить</a>
  <a href="https://t.me/{TG}" target="_blank" rel="noopener" class="actionbar__btn actionbar__btn--tg" data-goal="telegram">{ICON_TG}Telegram</a>
</div>

<a href="https://t.me/{TG}" target="_blank" rel="noopener" class="fab" id="fab" aria-label="Написать в Telegram" data-goal="telegram">
  {ICON_TG}
  <span class="fab__label">Написать в Telegram</span>
</a>

<script src="/js/main.js"></script>'''


def photoband(d, slot):
    """Широкая фотополоса. Слот может отсутствовать — тогда ничего не рисуем."""
    item = d.get("photos", {}).get(slot)
    if not item:
        return ""
    src, caption = item
    return f'''      <figure class="photoband reveal">
        <img src="/assets/img/{src}" alt="{e(caption)}" width="1600" height="900" loading="lazy">
        <figcaption>{e(caption)}</figcaption>
      </figure>'''


def cta_strip(title, text, tg_text):
    """Конверсионная врезка внутри контента, а не баннер сбоку."""
    return f'''      <div class="inline-cta reveal">
        <div>
          <p class="inline-cta__title">{e(title)}</p>
          <p class="inline-cta__text">{e(text)}</p>
        </div>
        <div class="inline-cta__actions">
          <a href="tel:{PHONE}" class="btn btn--primary" data-goal="call">{ICON_PHONE}+998 90 317-22-88</a>
          <a href="{e(tg_link(tg_text))}" target="_blank" rel="noopener" class="btn btn--tg" data-goal="telegram">{ICON_TG}Telegram</a>
        </div>
      </div>'''


def build_page(d, all_dests):
    others = [x for x in all_dests if x["slug"] != d["slug"]]
    name, to = d["name"], d["to"]
    url = "%s/%s/" % (SITE, d["slug"])
    img = "/assets/img/%s" % d["image"]

    title = "Туры %s из Ташкента — цены, курорты и авторские программы | V-travel" % to
    desc = ("Туры %s из Ташкента от $%s: какие курорты кому подходят, когда лучше лететь, "
            "авторские программы. Подберём за 15 минут — позвоните %s или напишите в Telegram."
            % (to, d["price"], PHONE_HUMAN))

    # ─ курорты
    resorts = "\n".join(
        f'''        <article class="resort reveal">
          <h3>{e(n)}</h3>
          <p>{e(t)}</p>
        </article>''' for n, t in d["resorts"])

    # ─ сезоны
    seasons = "\n".join(
        f'''          <tr>
            <th scope="row">{e(m)}</th>
            <td class="season__temp">{e(t)}</td>
            <td>{e(v)}</td>
          </tr>''' for m, t, v in d["seasons"])

    # ─ авторская программа по дням
    prog = d["program"]
    days_html = "\n".join(
        f'''        <li class="pday reveal">
          <div class="pday__mark"><span>{e(num)}</span></div>
          <div class="pday__body">
            <h3>{e(place)}</h3>
            <p>{e(text)}</p>
          </div>
        </li>''' for num, place, text in prog["days"])
    prog_msg = ("Здравствуйте! Интересует авторская программа «%s» (%s). "
                "Рассчитайте, пожалуйста, на мои даты." % (prog["title"], prog["sub"]))

    # ─ вопросы
    faq = "\n".join(
        f'''        <details class="faq__item reveal" name="faq">
          <summary>{e(q)}</summary>
          <p>{e(a)}</p>
        </details>''' for q, a in d["faq"])

    # ─ другие направления
    other_links = "\n".join(
        f'''        <a class="otherdest" href="/{o["slug"]}/">
          <img src="/assets/img/{o["image"]}" alt="Туры {e(o["to"])} из Ташкента" width="1500" height="952" loading="lazy">
          <span>{e(o["name"])}<em>от ${e(o["price"])}</em></span>
        </a>''' for o in others)

    # ─ микроразметка
    ld = {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "BreadcrumbList",
          "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Туры " + to, "item": url},
          ],
        },
        {
          "@type": "FAQPage",
          "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in d["faq"]
          ],
        },
      ],
    }

    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#04121f">
<link rel="canonical" href="{url}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="V-travel">
<meta property="og:locale" content="ru_RU">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}{img}">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23061c2e'/%3E%3Cpath d='M16 20l16 26 16-26' fill='none' stroke='%2338d0ff' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<link rel="preload" href="/assets/fonts/unbounded-900.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{img}" as="image" fetchpriority="high">
<link rel="stylesheet" href="/css/fonts.css">
<link rel="stylesheet" href="/css/styles.css">
<link rel="stylesheet" href="/css/pages.css">
<script>document.documentElement.classList.add('js');</script>

<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>

<a class="skip-link" href="#main">К основному содержимому</a>

{header_html()}

<main id="main">

  <section class="phero">
    <div class="phero__media" aria-hidden="true">
      <img src="{img}" alt="" width="1500" height="952" fetchpriority="high">
      <div class="phero__scrim"></div>
    </div>
    <div class="shell phero__inner">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="/">Главная</a><span aria-hidden="true">→</span><span>Туры {e(to)}</span>
      </nav>
      <h1>Туры {e(to)}<br>из Ташкента</h1>
      <p class="phero__lead">{e(d["lead"])}</p>
      <p class="phero__price">от <strong>${e(d["price"])}</strong> за человека</p>
      <div class="phero__cta">
        <a href="tel:{PHONE}" class="btn btn--primary btn--lg" data-goal="call">{ICON_PHONE}+998 90 317-22-88</a>
        <a href="{e(tg_link("Здравствуйте! Интересуют туры %s из Ташкента." % to))}" target="_blank" rel="noopener" class="btn btn--tg btn--lg" data-goal="telegram">{ICON_TG}Написать в Telegram</a>
      </div>
      <p class="phero__note">{e(d["flight"])} Подбор бесплатный, ответим за 5 минут.</p>
    </div>
  </section>

  <section class="section section--resorts">
    <div class="shell">
      <header class="sec-head reveal">
        <p class="sec-kicker">Курорты</p>
        <h2 class="sec-title">Куда именно<br>лететь</h2>
        <p class="sec-lead">Курорты внутри одной страны отличаются сильнее, чем кажется по каталогу. Коротко о том, кому какой подходит.</p>
      </header>
      <div class="resorts">
{resorts}
      </div>
{photoband(d, "after_resorts")}
{cta_strip("Не знаете, какой курорт ваш?",
           "Назовите бюджет и с кем летите — подскажем за пять минут, без каталогов и уговоров.",
           "Здравствуйте! Помогите выбрать курорт %s. Лечу " % to)}
    </div>
  </section>

  <section class="section section--seasons">
    <div class="shell">
      <header class="sec-head reveal">
        <p class="sec-kicker">Сезонность</p>
        <h2 class="sec-title">Когда лететь</h2>
        <p class="sec-lead">Разница между «дорого и жарко» и «дёшево и приятно» — часто две недели в календаре.</p>
      </header>
      <div class="season reveal">
        <table>
          <thead>
            <tr><th scope="col">Период</th><th scope="col">Воздух и вода</th><th scope="col">Что это значит</th></tr>
          </thead>
          <tbody>
{seasons}
          </tbody>
        </table>
      </div>
{cta_strip("Скажите свои даты — посчитаем",
           "Проверим, что попадает на ваш отпуск, и предложим варианты в этих числах.",
           "Здравствуйте! Хочу %s. Мои даты: " % to)}
    </div>
  </section>

  <section class="section section--tours" id="program">
    <div class="shell">
      <header class="sec-head reveal">
        <p class="sec-kicker">Авторская программа</p>
        <h2 class="sec-title">{e(prog["title"])}</h2>
        <p class="sec-lead">{e(prog["sub"])}</p>
      </header>
{photoband(d, "in_program")}
      <ol class="program">
{days_html}
      </ol>
      <div class="inline-cta inline-cta--wide reveal">
        <div>
          <p class="inline-cta__title">Маршрут подстраивается под вас</p>
          <p class="inline-cta__text">Можно добавить дни на море, поменять города местами или убрать переезды — скажите, что важно, и пересоберём. Стоимость зависит от дат и класса отелей, поэтому считаем под конкретные числа.</p>
        </div>
        <div class="inline-cta__actions">
          <a href="tel:{PHONE}" class="btn btn--primary" data-goal="call">{ICON_PHONE}+998 90 317-22-88</a>
          <a href="{e(tg_link(prog_msg))}" target="_blank" rel="noopener" class="btn btn--tg" data-goal="telegram">{ICON_TG}Рассчитать в Telegram</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--faq">
    <div class="shell">
      <header class="sec-head reveal">
        <p class="sec-kicker">Вопросы</p>
        <h2 class="sec-title">О чём спрашивают<br>перед поездкой</h2>
      </header>
{photoband(d, "in_faq")}
      <div class="faq">
{faq}
      </div>
    </div>
  </section>

  <section class="section section--other">
    <div class="shell">
      <header class="sec-head reveal">
        <p class="sec-kicker">Другие направления</p>
        <h2 class="sec-title">Ещё варианты</h2>
      </header>
      <div class="otherdests">
{other_links}
      </div>
    </div>
  </section>

  <section class="cta" id="contacts">
    <div class="cta__media" aria-hidden="true"><div class="cta__caustics"></div></div>
    <div class="shell cta__inner">
      <figure class="porthole reveal" aria-hidden="true">
        <span class="porthole__frame">
          <span class="porthole__glass">
            <img src="/assets/img/porthole-view.webp" alt="" width="820" height="1138" loading="lazy">
            <span class="porthole__glare"></span>
          </span>
        </span>
        <figcaption class="porthole__hud">
          <span>TAS</span>
          <span class="porthole__hud-line"></span>
          <span>ваш рейс</span>
        </figcaption>
      </figure>

      <div class="cta__text">
      <h2 class="cta__title reveal">Позвоните — и через 15 минут у вас будут варианты</h2>
      <p class="cta__lead reveal">Ежедневно с 09:00 до 21:00. Подбор бесплатный, ни к чему не обязывает.</p>
      <a href="tel:{PHONE}" class="cta__phone reveal" data-goal="call">{PHONE_HUMAN}</a>
      <div class="cta__buttons reveal">
        <a href="tel:{PHONE}" class="btn btn--primary btn--lg" data-goal="call">Позвонить</a>
        <a href="{e(tg_link("Здравствуйте! Интересуют туры %s." % to))}" target="_blank" rel="noopener" class="btn btn--tg btn--lg" data-goal="telegram">{ICON_TG}Написать в Telegram</a>
      </div>
      <p class="cta__extra reveal">Канал с горящими турами: <a href="https://t.me/{TG_DEALS}" target="_blank" rel="noopener">@{TG_DEALS}</a></p>
      </div>
    </div>
  </section>

</main>

{footer_html(others)}
</body>
</html>
'''


def build_sitemap():
    today = date.today().isoformat()
    urls = [(SITE + "/", "1.0")] + [("%s/%s/" % (SITE, d["slug"]), "0.8") for d in DESTS]
    body = "\n".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n    <priority>%s</priority>\n  </url>"
        % (u, today, p) for u, p in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + "\n</urlset>\n")


def main():
    for d in DESTS:
        out = ROOT / d["slug"]
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(build_page(d, DESTS), encoding="utf-8")
        print("собрано: /%s/" % d["slug"])
    (ROOT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    print("собрано: sitemap.xml (%d адресов)" % (len(DESTS) + 1))


if __name__ == "__main__":
    main()
