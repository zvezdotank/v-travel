#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обложки для превью ссылок в мессенджерах и соцсетях.

Telegram и остальные показывают над картинкой заголовок и описание,
поэтому дублировать их текстом на самой обложке незачем — получится шум.
Картинка должна добавлять то, чего в тексте нет: мгновенное узнавание
категории и брендовую метку, которая переживёт пересылку скриншотом.

Отсюда состав: кадр, тёмная подложка внизу для читаемости, логотип
слева и телефон справа.

    python3 scripts/make_covers.py

Шрифты берутся из scratchpad; если их там нет, скрипт скажет, откуда
скачать. Результат — assets/img/og-*.jpg.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONTS = Path("/private/tmp/claude-501/-Users-zvezdotank-Claude"
             "/21b5c055-979b-4120-a627-f8cda6873879/scratchpad/fonts")

VER = "-v2"   # менять при обновлении обложек: сбрасывает кэш мессенджеров
W, H = 1200, 630
PHONE = "+998 90 317-22-88"

# кадр → имя обложки. Для главной берём вид с крылом: в ленте он за долю
# секунды читается как «перелёт», а абстрактная вода не говорит ничего.
JOBS = [
    ("porthole-source", "og-cover%s.jpg" % VER),
    ("dest-turkey.webp", "og-turciya%s.jpg" % VER),
    ("dest-egypt.webp", "og-egipet%s.jpg" % VER),
    ("dest-thailand.webp", "og-tailand%s.jpg" % VER),
    ("dest-vietnam.webp", "og-vietnam%s.jpg" % VER),
]
WING_SRC = Path.home() / "Downloads" / "Gemini_Generated_Image_8wmj2j8wmj2j8wmj.png"


def cover_crop(im, focus=0.5, right_limit=None):
    """Кадрируем под 1200×630, беря полосу вокруг заданной высоты."""
    w, h = im.size
    if right_limit:
        im = im.crop((0, 0, right_limit, h)); w = right_limit
    nh = int(w / (W / H))
    if nh > h:                       # кадр слишком «плоский» — режем по ширине
        nw = int(h * (W / H))
        left = max(0, min(int(w * focus) - nw // 2, w - nw))
        im = im.crop((left, 0, left + nw, h))
    else:
        top = max(0, min(int(h * focus) - nh // 2, h - nh))
        im = im.crop((0, top, w, top + nh))
    return im.resize((W, H), Image.LANCZOS)


def add_plate(im):
    """Подложка снизу, логотип и телефон."""
    im = im.convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")

    # мягкое затемнение снизу, иначе текст утонет в светлых кадрах
    band = 190
    for i in range(band):
        a = int(215 * (i / band) ** 1.7)
        d.rectangle([(0, H - band + i), (W, H - band + i + 1)], fill=(4, 16, 28, a))

    try:
        f_logo = ImageFont.truetype(str(FONTS / "unbounded-800.ttf"), 46)
        f_phone = ImageFont.truetype(str(FONTS / "manrope-700.ttf"), 36)
    except OSError:
        sys.exit("Нет шрифтов в %s — скачайте Unbounded 800 и Manrope 700 в ttf." % FONTS)

    pad = 54
    baseline = H - 62

    # логотип: квадратная метка с галочкой плюс название
    box = 54
    bx, by = pad, baseline - box + 6
    d.rounded_rectangle([(bx, by), (bx + box, by + box)], radius=15, fill=(56, 208, 255, 255))
    d.line([(bx + 15, by + 17), (bx + 27, by + 39), (bx + 39, by + 17)],
           fill=(4, 18, 31, 255), width=7, joint="curve")
    d.text((bx + box + 18, baseline), "V-travel", font=f_logo, fill=(242, 248, 252, 255), anchor="ls")

    # телефон справа
    d.text((W - pad, baseline - 4), PHONE, font=f_phone, fill=(234, 246, 251, 235), anchor="rs")
    return im


def main():
    for src, out in JOBS:
        if src == "porthole-source":
            if not WING_SRC.exists():
                print("пропуск %s: нет исходника %s" % (out, WING_SRC)); continue
            im = cover_crop(Image.open(WING_SRC), focus=0.56, right_limit=1520)
        else:
            im = cover_crop(Image.open(IMG / src), focus=0.5)
        add_plate(im).save(IMG / out, "JPEG", quality=86, optimize=True)
        print("  %-16s %d КБ" % (out, (IMG / out).stat().st_size / 1024))


if __name__ == "__main__":
    main()
