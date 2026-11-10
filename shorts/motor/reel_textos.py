"""Motor visual de "reel de textos": un clip vertical 1080x1920 por escena.

Cada escena muestra: fondo degradé animado con manchas de luz, barra de progreso
tipo historias, etiqueta superior, emoji grande, la frase en pantalla apareciendo
palabra por palabra con UNA palabra resaltada y, opcional, un número gigante que
cuenta ("dato"). Los subtítulos de la voz los agrega MoneyPrinterTurbo abajo.

Uso como módulo: render_clips(guion, duraciones, carpeta) -> [rutas mp4]
"""
import math
import os
import random
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

# Paletas: dos colores de fondo, color de acento (palabra resaltada) y color de manchas de luz.
TEMAS = {
    "oceano":  {"a": (6, 40, 77),   "b": (2, 12, 30),   "acento": (0, 229, 255),  "luz": (40, 140, 255)},
    "noche":   {"a": (40, 16, 82),  "b": (8, 4, 24),    "acento": (255, 79, 216), "luz": (120, 70, 255)},
    "fuego":   {"a": (110, 20, 10), "b": (25, 4, 6),    "acento": (255, 196, 0),  "luz": (255, 90, 30)},
    "selva":   {"a": (8, 70, 45),   "b": (2, 18, 12),   "acento": (170, 255, 60), "luz": (40, 200, 120)},
    "espacio": {"a": (14, 18, 48),  "b": (0, 0, 6),     "acento": (255, 212, 0),  "luz": (90, 110, 255)},
    "dulce":   {"a": (255, 120, 160), "b": (120, 40, 140), "acento": (255, 240, 120), "luz": (255, 200, 230)},
}


def _fuente(tam):
    for f in FUENTES:
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


_cache_emoji = {}


def _emoji_img(ch, tam):
    """Renderiza un emoji a color (Noto, tamaño nativo 109) y lo escala."""
    key = (ch, tam)
    if key in _cache_emoji:
        return _cache_emoji[key]
    img = None
    if ch and os.path.exists(EMOJI):
        try:
            f = ImageFont.truetype(EMOJI, 109)
            tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
            bbox = tmp.getbbox()
            if bbox:
                img = tmp.crop(bbox).resize((tam, int(tam * (bbox[3] - bbox[1]) / (bbox[2] - bbox[0]))), Image.LANCZOS)
        except Exception:
            img = None
    _cache_emoji[key] = img
    return img


def _ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def _ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


class Fondo:
    """Degradé + manchas de luz renderizadas a baja resolución y escaladas (se ven difuminadas)."""

    def __init__(self, tema, semilla=3):
        self.t = TEMAS.get(tema, TEMAS["oceano"])
        rnd = random.Random(semilla)
        self.manchas = [(rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0.18, 0.35), rnd.uniform(0.2, 0.6), rnd.uniform(0, 6.28)) for _ in range(5)]
        self.particulas = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 6), rnd.uniform(20, 70)) for _ in range(60)]
        w, h = 108, 192
        yy = np.linspace(0, 1, h)[:, None]
        xx = np.linspace(0, 1, w)[None, :]
        self.xx, self.yy = xx, yy

    def frame(self, t):
        a, b, luz = (np.array(self.t[k], np.float32) for k in ("a", "b", "luz"))
        ang = 0.6 + 0.25 * math.sin(t * 0.3)
        g = np.clip(self.xx * math.sin(ang) * 0.5 + self.yy * math.cos(ang), 0, 1)[..., None]
        img = a * (1 - g) + b * g
        for (mx, my, r, vel, fase) in self.manchas:
            cx = mx + 0.18 * math.sin(t * vel + fase)
            cy = my + 0.12 * math.cos(t * vel * 0.8 + fase)
            d2 = ((self.xx - cx) ** 2 + ((self.yy - cy) * 0.56) ** 2) / (r * r * 0.25)
            img = img + luz * 0.35 * np.exp(-d2)[..., None]
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        d = ImageDraw.Draw(im, "RGBA")
        for (px, py, r, v) in self.particulas:
            y = (py - v * t) % H
            d.ellipse([px - r, y - r, px + r, y + r], fill=(255, 255, 255, 50))
        return im, d


def _partir_lineas(d, palabras, fuente, maxw):
    lineas, cur = [], []
    for p in palabras:
        prueba = " ".join(cur + [p])
        if cur and d.textlength(prueba, font=fuente) > maxw:
            lineas.append(cur)
            cur = [p]
        else:
            cur.append(p)
    if cur:
        lineas.append(cur)
    return lineas


def _norm(s):
    return re.sub(r"[^\wáéíóúüñ]", "", s.lower())


def _texto_animado(d, im, texto, destacar, lt, acento, y_centro):
    """Frase grande centrada; aparece palabra por palabra con rebote; 'destacar' va con marcador de color."""
    palabras = texto.split()
    tam = 104 if len(texto) < 28 else (90 if len(texto) < 48 else 76)
    f = _fuente(tam)
    lineas = _partir_lineas(d, palabras, f, 940)
    lh = int(tam * 1.22)
    y0 = y_centro - len(lineas) * lh / 2
    objetivo = {_norm(x) for x in (destacar or "").split()}
    k = 0
    for li, linea in enumerate(lineas):
        ancho = d.textlength(" ".join(linea), font=f)
        x = (W - ancho) / 2
        y = y0 + li * lh
        for p in linea:
            ap = _ease_out_back((lt - 0.08 * k) / 0.35)
            k += 1
            pw = d.textlength(p, font=f)
            if ap <= 0:
                x += pw + d.textlength(" ", font=f)
                continue
            dy = (1 - min(ap, 1)) * 60
            es_dest = _norm(p) in objetivo and objetivo
            if es_dest:
                m = _ease((lt - 0.08 * k - 0.15) / 0.3)
                d.rounded_rectangle([x - 14, y + 6, x - 14 + (pw + 28) * m, y + lh - 8], 16, fill=acento + (255,))
                col = (15, 15, 25)
                d.text((x, y + dy), p, font=f, fill=col)
            else:
                d.text((x, y + dy), p, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
            x += pw + d.textlength(" ", font=f)


def _escena(fondo, esc, idx, total, lt, gt, dur, etiqueta, acento):
    im, d = fondo.frame(gt)
    # barra de progreso segmentada (estilo historias)
    gap, x0 = 10, 40
    seg = (W - 2 * x0 - gap * (total - 1)) / total
    for i in range(total):
        xa = x0 + i * (seg + gap)
        d.rounded_rectangle([xa, 60, xa + seg, 70], 5, fill=(255, 255, 255, 70))
        lleno = 1 if i < idx else (min(1, lt / dur) if i == idx else 0)
        if lleno > 0:
            d.rounded_rectangle([xa, 60, xa + seg * lleno, 70], 5, fill=(255, 255, 255, 235))
    # etiqueta
    if etiqueta:
        fe = _fuente(40)
        tw = d.textlength(etiqueta, font=fe)
        d.rounded_rectangle([(W - tw) / 2 - 28, 120, (W + tw) / 2 + 28, 190], 35, fill=acento + (255,))
        d.text((W / 2, 155), etiqueta, font=fe, fill=(15, 15, 25), anchor="mm")
    # emoji grande flotando
    em = _emoji_img(esc.get("emoji", ""), 260)
    if em is not None:
        s = _ease_out_back(lt / 0.5)
        if s > 0.02:
            e2 = em.resize((max(1, int(em.width * s)), max(1, int(em.height * s))), Image.LANCZOS)
            y = 470 + 18 * math.sin(gt * 2.2) - e2.height / 2
            rot = 6 * math.sin(gt * 1.7)
            e2 = e2.rotate(rot, resample=Image.BICUBIC, expand=True)
            im.paste(e2, (int(W / 2 - e2.width / 2), int(y)), e2)
    # dato gigante (número que cuenta)
    y_texto = 960
    dato = esc.get("dato")
    if dato:
        m = re.match(r"^([^\d]*)([\d.,]+)(.*)$", dato)
        txt = dato
        if m:
            pre, num, suf = m.groups()
            dec = len(num.split(",")[1]) if "," in num else 0
            val = float(num.replace(".", "").replace(",", "."))
            cur = val * _ease((lt - 0.2) / 1.2)
            s = f"{cur:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            txt = f"{pre}{s}{suf}"
        fd = _fuente(150)
        d.text((W / 2, 800), txt, font=fd, fill=acento, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
        y_texto = 1060
    _texto_animado(d, im, esc["pantalla"], esc.get("destacar", ""), lt - 0.15, acento, y_texto)
    # flash suave de entrada
    if lt < 0.15 and idx > 0:
        d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(110 * (1 - lt / 0.15))))
    return im


def render_clips(guion, duraciones, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    tema = TEMAS.get(guion.get("tema", "oceano"), TEMAS["oceano"])
    acento = tema["acento"]
    fondo = Fondo(guion.get("tema", "oceano"))
    etiqueta = guion.get("etiqueta", "¿SABÍAS QUÉ?")
    escenas = guion["escenas"]
    rutas, gt0 = [], 0.0
    for i, esc in enumerate(escenas):
        ruta = os.path.join(carpeta, f"escena_{i:02d}.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                               "-crf", "20", "-pix_fmt", "yuv420p", ruta], stdin=subprocess.PIPE)
        n = max(1, round(duraciones[i] * FPS))
        for fr in range(n):
            lt = fr / FPS
            im = _escena(fondo, esc, i, len(escenas), lt, gt0 + lt, duraciones[i], etiqueta, acento)
            ff.stdin.write(im.convert("RGB").tobytes())
        ff.stdin.close()
        ff.wait()
        gt0 += n / FPS
        rutas.append(ruta)
        print(f"  escena {i + 1}/{len(escenas)} lista ({duraciones[i]:.2f} s)", flush=True)
    return rutas
