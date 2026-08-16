#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Шрифты: скачать у Google, урезать до нужных символов, положить к себе.

Полные файлы Unbounded и Manrope весят около полумегабайта, а сайту нужны
кириллица, латиница и десяток типографских знаков. Подрезанные лежат в
assets/fonts и раздаются с нашего домена — браузер не ходит на чужие
серверы и не ждёт цепочку «html → css гугла → файл шрифта».

    python3 scripts/build_fonts.py

Перезаписывает assets/fonts/*.woff2 и css/fonts.css.

Про узбекские oʻ и gʻ: официально это U+02BB, но в Manrope такого глифа
просто нет — ни в полном файле, ни тем более в подрезанном. Поэтому в
текстах стоит U+2018 «‘», который в обоих шрифтах есть и рисуется той же
запятой. Менять charset осторожно: убрать символ легко, заметить пропажу —
нет.
"""

from pathlib import Path
from urllib.request import urlopen, Request
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"
CACHE = ROOT / ".fonts-src"          # скачанные ttf, в git не нужны

FAMILIES = [("Unbounded", [400, 800, 900]), ("Manrope", [400, 600, 700, 800])]

# Формат шрифта Google выбирает по User-Agent. Современному браузеру он
# пришлёт woff2, старому MSIE — eot, и только такому вот андроиду достаётся
# обычный ttf, с которым умеет работать pyftsubset.
OLD_UA = ("Mozilla/5.0 (Linux; U; Android 4.0.3; en-us) AppleWebKit/534.30 "
          "(KHTML, like Gecko) Version/4.0 Mobile Safari/534.30")

CHARS = (
    "".join(chr(c) for c in range(0x20, 0x7F)) +      # латиница, цифры, знаки
    "".join(chr(c) for c in range(0x400, 0x460)) +    # кириллица
    "–—…«»„“”‘’·•★→−°№"
)


def fetch_ttfs():
    CACHE.mkdir(exist_ok=True)
    got = {}
    for family, weights in FAMILIES:
        for w in weights:
            # по старому UA Google присылает ровно одно начертание на запрос,
            # поэтому просим их по одному, а не списком через ;
            url = "https://fonts.googleapis.com/css2?family=%s:wght@%d" % (family, w)
            css = urlopen(Request(url, headers={"User-Agent": OLD_UA}), timeout=30).read().decode()

            # адрес приходит без расширения (/l/font?kit=…), но по старому UA
            # за ним лежит именно ttf
            m = re.search(r"url\((https://[^)]+)\)", css)
            if not m:
                sys.exit("не нашёл ttf для %s %d — Google изменил формат ответа" % (family, w))
            src = m.group(1)

            dst = CACHE / ("%s-%d.ttf" % (family.lower(), w))
            if not dst.exists():
                dst.write_bytes(urlopen(Request(src, headers={"User-Agent": OLD_UA}), timeout=60).read())
            got[(family, w)] = dst
    return got


def subset(src, dst):
    subprocess.run([
        sys.executable, "-m", "fontTools.subset", str(src),
        "--text=%s" % CHARS,
        "--layout-features=kern,liga,calt",
        "--flavor=woff2",
        "--output-file=%s" % dst,
    ], check=True)


CSS_HEAD = """/* =====================================================
   Шрифты лежат у нас, а не на серверах Google.

   Файл собирается скриптом — правки руками пропадут:

       python3 scripts/build_fonts.py

   Каждое начертание урезано до символов, которые реально встречаются на
   сайте: кириллица, латиница с узбекскими oʻ и gʻ, цифры и типографика.

   Unbounded и Manrope — SIL Open Font License 1.1.
   ===================================================== */
"""

FACE = """
@font-face {
  font-family: '%s';
  font-style: normal;
  font-weight: %d;
  font-display: swap;
  src: url('/assets/fonts/%s') format('woff2');
}
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ttfs = fetch_ttfs()

    css = [CSS_HEAD]
    total = 0
    for family, weights in FAMILIES:
        for w in weights:
            name = "%s-%d.woff2" % (family.lower(), w)
            subset(ttfs[(family, w)], OUT / name)
            size = (OUT / name).stat().st_size
            total += size
            print("  %-22s %5.1f КБ" % (name, size / 1024))
            css.append(FACE % (family, w, name))

    (ROOT / "css" / "fonts.css").write_text("".join(css), encoding="utf-8")
    print("итого %.1f КБ, css/fonts.css перезаписан" % (total / 1024))


if __name__ == "__main__":
    main()
