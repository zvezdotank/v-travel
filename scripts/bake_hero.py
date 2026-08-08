#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Впекаем грейд героя прямо в файл.

Раньше дуотон делался в браузере слоем с mix-blend-mode поверх фотографии.
Пока фон был статичным, это стоило один пересчёт. Но любое движение фона
заставляло браузер пересчитывать смешивание каждый кадр — на этом рендер
и ложился. Считаем то же самое один раз здесь.

Повторяем ровно то, что делал CSS:
    filter: saturate(1.45) contrast(1.1) brightness(.92)
    + linear-gradient(190deg, #0b5c94, #0a3a63 45%, #072742)
      с mix-blend-mode: color и opacity .62

    python3 scripts/bake_hero.py
"""

import colorsys
import numpy as np
from pathlib import Path
from PIL import Image

SRC = Path("assets/img/new/Gemini_Generated_Image_5321jh5321jh5321.png")
OUT = Path("assets/img/hero-water.webp")
WIDTH = 2000
CROP_RIGHT = 0.12          # тот же срез маркера Gemini, что и при первой обработке

SATURATE, CONTRAST, BRIGHTNESS = 1.45, 1.10, 0.92
GRADIENT = [(0.00, (0x0b, 0x5c, 0x94)),
            (0.45, (0x0a, 0x3a, 0x63)),
            (1.00, (0x07, 0x27, 0x42))]
GRADIENT_ANGLE = 190       # градусы, как в CSS
OPACITY = 0.62


def css_filters(a):
    """saturate → contrast → brightness, в том же порядке, что и в CSS."""
    lum = (a * np.array([0.2126, 0.7152, 0.0722])).sum(axis=2, keepdims=True)
    a = lum + (a - lum) * SATURATE
    a = (a - 0.5) * CONTRAST + 0.5
    return np.clip(a * BRIGHTNESS, 0, 1)


def gradient_layer(h, w):
    """Линейный градиент под углом, как его считает CSS."""
    rad = np.deg2rad(GRADIENT_ANGLE - 90)
    dx, dy = np.cos(rad), np.sin(rad)
    xs = (np.arange(w) - w / 2)[None, :]
    ys = (np.arange(h) - h / 2)[:, None]
    t = xs * dx + ys * dy
    t = (t - t.min()) / (t.max() - t.min())

    stops = np.array([s for s, _ in GRADIENT])
    cols = np.array([c for _, c in GRADIENT], dtype=float) / 255
    out = np.empty((h, w, 3))
    for i in range(3):
        out[..., i] = np.interp(t, stops, cols[:, i])
    return out


def blend_color(base, top):
    """Режим «color»: тон и насыщенность сверху, светлота снизу."""
    def to_hls(a):
        flat = a.reshape(-1, 3)
        return np.array([colorsys.rgb_to_hls(*px) for px in flat]).reshape(a.shape)

    b, t = to_hls(base), to_hls(top)
    mixed = np.stack([t[..., 0], b[..., 1], t[..., 2]], axis=-1)   # H top, L base, S top
    flat = mixed.reshape(-1, 3)
    rgb = np.array([colorsys.hls_to_rgb(*px) for px in flat]).reshape(base.shape)
    return np.clip(rgb, 0, 1)


def main():
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    im = im.crop((0, 0, int(w * (1 - CROP_RIGHT)), h))
    cw, ch = im.size
    im = im.resize((WIDTH, round(ch * WIDTH / cw)), Image.LANCZOS)

    a = np.asarray(im, dtype=float) / 255
    a = css_filters(a)

    h, w, _ = a.shape
    g = gradient_layer(h, w)
    a = a * (1 - OPACITY) + blend_color(a, g) * OPACITY

    Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8")).save(
        OUT, "WEBP", quality=82, method=6)
    print("%s  %dx%d  %d КБ" % (OUT, w, h, OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
