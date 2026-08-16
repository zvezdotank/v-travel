#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Узбекская версия сайта — из готовой русской.

Вёрстка у двух языков одна и та же, разный только текст. Держать две копии
html значило бы чинить каждую правку дважды и однажды забыть; поэтому
узбекские страницы собираются из русских подстановкой по словарю.

    python3 scripts/build_uz.py            собрать /uz/
    python3 scripts/build_uz.py --report   показать непереведённые строки

Словарь лежит в scripts/lang_uz.py. Сборка падает, если в результате
осталась хоть одна кириллическая буква, — это и есть проверка полноты
перевода, забыть фразу нельзя.

Порядок такой: сначала python3 scripts/build_pages.py (русские страницы
направлений), потом этот скрипт.
"""

from pathlib import Path
from urllib.parse import quote, unquote
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lang_uz import PHRASES, REGEXES, SLUGS          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://v-travel.uz"

# русская страница → узбекская. Слаги разные: узбекскому читателю нужен
# /uz/turkiya/, а не транслит русского названия.
PAGES = [("index.html", "uz/index.html")] + [
    ("%s/index.html" % ru, "uz/%s/index.html" % uz) for ru, uz in SLUGS.items()
]

CYR = re.compile(r"[А-Яа-яЁё]")


# ─────────────────────────── перевод текста ───────────────────────────

def compile_table():
    """Длинные фразы идут первыми, иначе короткая съест кусок длинной.

    Пробелы в html переносятся как попало, поэтому между словами
    разрешаем любой пропуск — так словарь не зависит от вёрстки.
    """
    items = sorted(PHRASES.items(), key=lambda kv: -len(kv[0]))
    out = []
    for ru, uz in items:
        pattern = r"\s+".join(re.escape(w) for w in ru.split())
        # без границ слова короткое «от» нашлось бы внутри «отель»
        if ru[0].isalnum():
            pattern = r"\b" + pattern
        if ru[-1].isalnum():
            pattern += r"\b"
        out.append((re.compile(pattern), uz))
    return out


TABLE = compile_table()
SPANNING = [(re.compile(p), uz) for p, uz in REGEXES]


def translate(text):
    # сначала фразы, разорванные разметкой: после них половинки заголовков
    # до словаря уже не доходят
    for pattern, uz in SPANNING:
        text = pattern.sub(uz, text)
    for pattern, uz in TABLE:
        text = pattern.sub(lambda m: uz, text)
    return text


def translate_tg_links(html):
    """Текст заявки внутри ссылки на Telegram закодирован процентами."""
    def repl(m):
        return "?text=" + quote(translate(unquote(m.group(1))))
    return re.sub(r"\?text=([^\"'&]+)", repl, html)


# ─────────────────────────── ссылки и мета ───────────────────────────

def relink(html):
    """Внутренние адреса переводим на узбекскую ветку сайта."""
    for ru, uz in SLUGS.items():
        html = html.replace('href="/%s/"' % ru, 'href="/uz/%s/"' % uz)
        html = html.replace('"%s/%s/"' % (SITE, ru), '"%s/uz/%s/"' % (SITE, uz))
        html = html.replace("'%s/%s/'" % (SITE, ru), "'%s/uz/%s/'" % (SITE, uz))
    # главная и якоря на ней
    html = re.sub(r'href="/(#[a-z]+)"', r'href="/uz/\1"', html)
    html = re.sub(r'href="/"', 'href="/uz/"', html)
    html = html.replace('"%s/"' % SITE, '"%s/uz/"' % SITE)
    # адреса в микроразметке и canonical для страниц направлений
    for ru, uz in SLUGS.items():
        html = html.replace("%s/%s/" % (SITE, ru), "%s/uz/%s/" % (SITE, uz))
    return html


def retag(html, ru_url, uz_url):
    html = html.replace('<html lang="ru">', '<html lang="uz">', 1)
    html = html.replace('content="ru_RU"', 'content="uz_UZ"', 1)
    html = html.replace('<link rel="canonical" href="%s">' % ru_url,
                        '<link rel="canonical" href="%s">' % uz_url, 1)
    html = html.replace('<meta property="og:url" content="%s">' % ru_url,
                        '<meta property="og:url" content="%s">' % uz_url, 1)
    return html


def alternates(ru_url, uz_url):
    """Поисковику надо сказать, что это одна страница на двух языках."""
    return ('<link rel="alternate" hreflang="ru" href="%s">\n'
            '<link rel="alternate" hreflang="uz" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">' % (ru_url, uz_url, ru_url))


def switcher(ru_url, uz_url, active):
    """Переключатель языков. Текущий язык — не ссылка, а состояние."""
    def item(code, label, url, on):
        if on:
            return ('        <span class="langswitch__item is-active" '
                    'aria-current="true">%s</span>' % label)
        return ('        <a class="langswitch__item" href="%s" hreflang="%s" lang="%s">%s</a>'
                % (url, code, code, label))

    return ('      <div class="langswitch" role="group" aria-label="%s">\n%s\n%s\n      </div>'
            % ("Til" if active == "uz" else "Язык",
               item("ru", "RU", ru_url, active == "ru"),
               item("uz", "UZ", uz_url, active == "uz")))


SWITCH_RE = re.compile(r' *<div class="langswitch".*?</div>', re.S)
# прошлая сборка уже вписала hreflang в русские страницы. Если их не срезать
# перед новой вставкой, они накопятся, а relink ещё и перепишет адрес русской
# версии на узбекский — получится пара ссылок, ведущих в одно и то же место.
ALTERNATE_RE = re.compile(r'<link rel="alternate"[^>]*>\n')


# ─────────────────────────── отчёт ───────────────────────────

ATTRS = re.compile(r'\b(?:alt|title|placeholder|aria-label|content|data-tour|label)="([^"]*)"')


def cyrillic_fragments(html):
    """Куски текста, которые ещё не переведены."""
    found = []
    for m in ATTRS.finditer(html):
        found.append(m.group(1))
    # текст заявки в ссылке на Telegram закодирован процентами, и непереведённая
    # кириллица в нём выглядит как %D0%97 — глазами и обычным поиском её не
    # видно, поэтому раскодируем и проверяем наравне с остальным
    for m in re.finditer(r"\?text=([^\"'&]+)", html):
        found.append(unquote(m.group(1)))
    # комментарии сюда не попадают: split съедает их целиком как один «тег».
    # Так и задумано — это заметки разработчику, а не текст страницы, и
    # переводить их незачем. Но кириллицы в них тоже быть не должно, иначе
    # непонятно, забыли строку или это комментарий, — поэтому в index.html
    # все метки блоков латиницей.
    for chunk in re.split(r"<[^>]*>", html):
        # микроразметка — это один большой текстовый узел; разбираем её на
        # отдельные значения, иначе отчёт покажет весь json одной строкой
        if chunk.lstrip().startswith("{"):
            found.extend(re.findall(r'"([^"]*)"', chunk))
        else:
            found.append(chunk)

    out = []
    for f in found:
        f = " ".join(f.split())
        if f and CYR.search(f) and f not in out:
            out.append(f)
    return out


def report():
    rows = []
    for src, _ in PAGES:
        html = ALTERNATE_RE.sub("", (ROOT / src).read_text(encoding="utf-8"))
        # переключатель в сборке заменяется целиком, его русский ярлык не в счёт
        html = SWITCH_RE.sub("", html)
        html = translate_tg_links(html)
        html = translate(html)
        for f in cyrillic_fragments(html):
            if f not in rows:
                rows.append(f)

    if not rows:
        print("непереведённых строк нет")
        return
    print("# осталось перевести (%d):" % len(rows))
    for f in sorted(rows, key=len, reverse=True):
        print('    %r: "",' % f)


# ─────────────────────────── сборка ───────────────────────────

def build():
    problems = []
    for src, dst in PAGES:
        ru_url = SITE + "/" + src.replace("index.html", "")
        uz_url = SITE + "/" + dst.replace("index.html", "")

        html = ALTERNATE_RE.sub("", (ROOT / src).read_text(encoding="utf-8"))
        html = translate_tg_links(html)
        html = translate(html)
        html = relink(html)
        html = retag(html, ru_url, uz_url)
        html = html.replace('<link rel="canonical"',
                            alternates(ru_url, uz_url) + '\n<link rel="canonical"', 1)
        html = SWITCH_RE.sub(switcher(ru_url, uz_url, "uz"), html)

        left = cyrillic_fragments(html)
        if left:
            problems.append((dst, left))

        out = ROOT / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("собрано: /%s" % dst.replace("index.html", ""))

    # русские страницы тоже должны знать про узбекские
    for src, dst in PAGES:
        ru_url = SITE + "/" + src.replace("index.html", "")
        uz_url = SITE + "/" + dst.replace("index.html", "")
        html = ALTERNATE_RE.sub("", (ROOT / src).read_text(encoding="utf-8"))
        html = html.replace('<link rel="canonical"',
                            alternates(ru_url, uz_url) + '\n<link rel="canonical"', 1)
        html = SWITCH_RE.sub(switcher(ru_url, uz_url, "ru"), html)
        (ROOT / src).write_text(html, encoding="utf-8")

    build_sitemap()

    if problems:
        print("\nперевод неполный:")
        for dst, left in problems:
            print("  %s" % dst)
            for f in left[:12]:
                print("    %s" % f)
        sys.exit("запустите --report и допишите словарь в scripts/lang_uz.py")


def build_sitemap():
    from datetime import date
    today = date.today().isoformat()
    rows = []
    for src, dst in PAGES:
        ru_url = SITE + "/" + src.replace("index.html", "")
        uz_url = SITE + "/" + dst.replace("index.html", "")
        prio = "1.0" if src == "index.html" else "0.8"
        for loc in (ru_url, uz_url):
            rows.append(
                "  <url>\n    <loc>%s</loc>\n"
                '    <xhtml:link rel="alternate" hreflang="ru" href="%s"/>\n'
                '    <xhtml:link rel="alternate" hreflang="uz" href="%s"/>\n'
                "    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n"
                "    <priority>%s</priority>\n  </url>" % (loc, ru_url, uz_url, today, prio))

    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    print("собрано: sitemap.xml (%d адресов)" % len(rows))


if __name__ == "__main__":
    report() if "--report" in sys.argv else build()
