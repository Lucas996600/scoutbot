"""Fotos (por ej. generadas con Higgsfield) animadas con zoom/paneo tipo Ken Burns, para usar en escenas."""
import os

import skia

import dibujo as d
from dibujo import W, H

_cache = {}


def cargar(ruta):
    if ruta not in _cache:
        _cache[ruta] = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(ruta))
    return _cache[ruta]


def foto(c, ruta, p=0.0, zoom=(1.0, 1.12), centro=(0.5, 0.5), mover=(0.0, 0.0), brillo=1.0):
    """Dibuja la foto cubriendo la pantalla. p (0..1) avanza el zoom de zoom[0] a zoom[1];
    centro = punto (0..1) hacia el que se acerca; mover = paneo total en fracción de pantalla."""
    img = cargar(ruta)
    z = d.lerp(zoom[0], zoom[1], d.ease(p))
    iw, ih = img.width(), img.height()
    esc = max(W / iw, H / ih) * z
    w, h = iw * esc, ih * esc
    cx = centro[0] * w + mover[0] * W * d.ease(p)
    cy = centro[1] * h + mover[1] * H * d.ease(p)
    x0 = min(0, max(W - w, W / 2 - cx))
    y0 = min(0, max(H - h, H / 2 - cy))
    c.drawImageRect(img, skia.Rect.MakeXYWH(x0, y0, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    if brillo < 1:
        d.rect(c, 0, 0, W, H, "#000000", a=int(255 * (1 - brillo)))
    elif brillo > 1:
        d.rect(c, 0, 0, W, H, "#FFFFFF", a=int(255 * min(1, brillo - 1)))


def ruta_fotos(nombre):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fotos", nombre)
