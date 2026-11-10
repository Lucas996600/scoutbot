"""Biblioteca de dibujo 2D vectorial (Skia) para escenas ilustradas de los shorts.

Todo se dibuja con antialiasing, degradés, sombras y brillos. Coordenadas en píxeles
de un lienzo 1080x1920. Cada función recibe el canvas `c` de Skia.

Bloques listos: cielo, sol, luna, estrellas, nubes, montañas, colinas, pinos, agua,
olas, burbujas, partículas, lluvia, nieve, onda de sonido, flecha, etiqueta (callout),
contador, lupa/zoom circular, emoji como sprite, texto, cámara y viñeta.
"""
import math
import os
import random
from contextlib import contextmanager

import skia

W, H = 1080, 1920

# ---------------------------------------------------------------- utilidades


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(x):
    """ease-in-out suave"""
    x = clamp(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def aparece(lt, inicio, dur=0.4):
    """0→1 a partir del segundo `inicio` de la escena."""
    return ease_out((lt - inicio) / dur)


def col(c, a=255):
    """'#RRGGBB' o (r,g,b) o (r,g,b,a) o un color skia ya armado (int) -> color skia"""
    if isinstance(c, int):
        return c
    if isinstance(c, str):
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        return skia.Color(r, g, b, a)
    if len(c) == 4:
        return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(c[3] * a / 255))
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(a))


def mezcla(c1, c2, t):
    def rgb(c):
        if isinstance(c, str):
            c = c.lstrip("#")
            if len(c) == 3:
                c = "".join(ch * 2 for ch in c)
            return [int(c[i:i + 2], 16) for i in (0, 2, 4)]
        return list(c[:3])
    a, b = rgb(c1), rgb(c2)
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))


def pintura(color="#ffffff", a=255, trazo=None, blur=None, shader=None, cap_round=True):
    p = skia.Paint(AntiAlias=True)
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a / 255)
    else:
        p.setColor(col(color, a))
    if trazo:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(trazo)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def grad_lineal(x0, y0, x1, y1, colores, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [col(c) for c in colores], pos)


def grad_radial(x, y, r, colores, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), max(1, r), [col(c) if not isinstance(c, int) else c for c in colores], pos)


def camino(puntos, cerrado=True, suave=False, tension=0.5):
    """Path de Skia desde una lista de puntos. suave=True usa curvas Catmull-Rom."""
    p = skia.Path()
    if not puntos:
        return p
    if not suave or len(puntos) < 3:
        p.moveTo(*puntos[0])
        for q in puntos[1:]:
            p.lineTo(*q)
    else:
        pts = list(puntos)
        n = len(pts)
        p.moveTo(*pts[0])
        rango = range(n) if cerrado else range(n - 1)
        for i in rango:
            p0 = pts[(i - 1) % n] if (cerrado or i > 0) else pts[i]
            p1, p2 = pts[i], pts[(i + 1) % n]
            p3 = pts[(i + 2) % n] if (cerrado or i + 2 < n) else p2
            c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
            c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
            p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if cerrado:
        p.close()
    return p


# Modo "tinta" (cómic/caricatura plana con contorno grueso). Se activa con activar_tinta() o "estilo": "tinta" en el guion.
TINTA = None


def activar_tinta(color="#1B0F3A", ancho=7, plano=True):
    global TINTA
    TINTA = dict(color=color, ancho=ancho, plano=plano)


def _tinta_aplica(area, a, blur, trazo, ancho=0):
    return TINTA is not None and not blur and not trazo and a >= 150 and area < W * H * 0.35 and ancho < W * 0.85


def _relleno(color, a, shader, area, blur, trazo, ancho=0):
    if _tinta_aplica(area, a, blur, trazo, ancho) and TINTA["plano"] and shader is not None:
        shader = None
    return pintura(color, a, shader=shader, blur=blur, trazo=trazo)


def _borde(c, dibujar, area, a, blur, trazo, ancho=0):
    if _tinta_aplica(area, a, blur, trazo, ancho) and area > 120:
        dibujar(pintura(TINTA["color"], a, trazo=TINTA["ancho"]))


def figura(c, puntos, color, a=255, suave=True, sombra=0, trazo=None, borde=None, shader=None):
    """Polígono/forma (suave por defecto) con sombra opcional y borde opcional."""
    pth = camino(puntos, True, suave)
    if sombra:
        c.save()
        c.translate(0, sombra * 0.5)
        c.drawPath(pth, pintura("#000000", 70, blur=sombra))
        c.restore()
    b = pth.computeTightBounds()
    area = b.width() * b.height()
    c.drawPath(pth, _relleno(color, a, shader, area, None, trazo, b.width()) if not trazo else pintura(color, a, trazo=trazo))
    _borde(c, lambda p: c.drawPath(pth, p), area, a, None, trazo, b.width())
    if borde:
        c.drawPath(pth, pintura(borde[0], borde[2] if len(borde) > 2 else 255, trazo=borde[1]))
    return pth


def circulo(c, x, y, r, color, a=255, blur=None, trazo=None, shader=None):
    area = 4 * r * r
    c.drawCircle(x, y, r, _relleno(color, a, shader, area, blur, trazo))
    _borde(c, lambda p: c.drawCircle(x, y, r, p), area, a, blur, trazo)


def elipse(c, x, y, rx, ry, color, a=255, blur=None, trazo=None, shader=None):
    rr = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
    area = 4 * rx * ry
    c.drawOval(rr, _relleno(color, a, shader, area, blur, trazo, 2 * rx))
    _borde(c, lambda p: c.drawOval(rr, p), area, a, blur, trazo, 2 * rx)


def rect(c, x0, y0, x1, y1, color, a=255, radio=0, shader=None, blur=None, trazo=None):
    r = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    area = abs((x1 - x0) * (y1 - y0))
    an = abs(x1 - x0)
    p = _relleno(color, a, shader, area, blur, trazo, an)
    if radio:
        c.drawRoundRect(r, radio, radio, p)
        _borde(c, lambda q: c.drawRoundRect(r, radio, radio, q), area, a, blur, trazo, an)
    else:
        c.drawRect(r, p)
        _borde(c, lambda q: c.drawRect(r, q), area, a, blur, trazo, an)


def destellos(c, t, n=14, semilla=8, colores=("#E9FF8A", "#9FFFE0", "#FFFFFF"), y_max=None):
    """Estrellitas de 4 puntas que titilan (look de caricatura retro)."""
    import random as _r
    rnd = _r.Random(semilla)
    for k in range(n):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(60, y_max or H * 0.6)
        tam = rnd.uniform(14, 34) * (0.7 + 0.3 * math.sin(t * rnd.uniform(2, 4) + k))
        colr = colores[k % len(colores)]
        pth = camino([(x, y - tam), (x + tam * 0.22, y - tam * 0.22), (x + tam, y), (x + tam * 0.22, y + tam * 0.22),
                      (x, y + tam), (x - tam * 0.22, y + tam * 0.22), (x - tam, y), (x - tam * 0.22, y - tam * 0.22)], True, False)
        c.drawPath(pth, pintura(colr))


def linea(c, x0, y0, x1, y1, color, ancho=6, a=255):
    c.drawLine(x0, y0, x1, y1, pintura(color, a, trazo=ancho))


def brillo(c, x, y, r, color, a=180):
    """Halo de luz radial (glow)."""
    c.drawCircle(x, y, r, pintura(shader=grad_radial(x, y, r, [col(color, a), col(color, 0)]), a=255))


@contextmanager
def camara(c, zoom=1.0, cx=W / 2, cy=H / 2, dx=0, dy=0, rot=0):
    """Zoom/paneo/rotación alrededor de (cx, cy)."""
    c.save()
    c.translate(cx + dx, cy + dy)
    c.rotate(rot)
    c.scale(zoom, zoom)
    c.translate(-cx, -cy)
    try:
        yield
    finally:
        c.restore()


# ---------------------------------------------------------------- texto y emoji

_FUENTES = {
    "titulo": ["/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf",
               "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "bold": ["/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}
_tf_cache = {}


def tipografia(tipo="bold"):
    if tipo not in _tf_cache:
        for f in _FUENTES.get(tipo, _FUENTES["bold"]):
            if os.path.exists(f):
                _tf_cache[tipo] = skia.Typeface.MakeFromFile(f)
                break
        else:
            _tf_cache[tipo] = skia.Typeface("sans-serif", skia.FontStyle.Bold())
    return _tf_cache[tipo]


def ancho_texto(txt, tam, tipo="bold"):
    return skia.Font(tipografia(tipo), tam).measureText(txt)


def texto(c, txt, x, y, tam=60, color="#ffffff", alinear="centro", tipo="bold", contorno=0, color_contorno="#000000", a=255, sombra=True):
    """Texto en (x, y) = línea base. alinear: izquierda | centro | derecha."""
    f = skia.Font(tipografia(tipo), tam)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    w = f.measureText(txt)
    x0 = x - w / 2 if alinear == "centro" else (x - w if alinear == "derecha" else x)
    blob = skia.TextBlob.MakeFromString(txt, f)
    if sombra:
        c.drawTextBlob(blob, x0, y + tam * 0.06, pintura("#000000", int(a * 0.55), blur=tam * 0.08))
    if contorno:
        c.drawTextBlob(blob, x0, y, pintura(color_contorno, a, trazo=contorno))
    c.drawTextBlob(blob, x0, y, pintura(color, a))
    return w


def partir(txt, tam, maxw, tipo="titulo"):
    lineas, cur = [], ""
    for p in txt.split():
        prueba = (cur + " " + p).strip()
        if cur and ancho_texto(prueba, tam, tipo) > maxw:
            lineas.append(cur)
            cur = p
        else:
            cur = prueba
    if cur:
        lineas.append(cur)
    return lineas


_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
_emoji_tf = None


def emoji(c, ch, x, y, tam=200, a=255, rot=0):
    """Dibuja un emoji a color centrado en (x, y). Útil para objetos difíciles de dibujar."""
    global _emoji_tf
    if _emoji_tf is None and os.path.exists(_EMOJI):
        _emoji_tf = skia.Typeface.MakeFromFile(_EMOJI)
    if _emoji_tf is None:
        return
    f = skia.Font(_emoji_tf, 109)
    w = f.measureText(ch)
    s = tam / 109.0
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a / 255)
    c.drawString(ch, -w / 2, 109 * 0.36, f, p)
    c.restore()


# ---------------------------------------------------------------- escenografía


def cielo(c, arriba="#1e3c72", abajo="#7fb3e6", y0=0, y1=H):
    rect(c, 0, y0, W, y1, "#000", shader=grad_lineal(0, y0, 0, y1, [arriba, abajo]))


def fondo(c, arriba, abajo):
    cielo(c, arriba, abajo)


def sol(c, x, y, r, t=0.0, color="#FFD54A", rayos=True):
    brillo(c, x, y, r * 4, color, 110)
    if rayos:
        c.save()
        c.translate(x, y)
        c.rotate(t * 8)
        for k in range(12):
            c.rotate(30)
            linea(c, r * 1.25, 0, r * 1.7 + 10 * math.sin(t * 3 + k), 0, color, ancho=r * 0.12, a=180)
        c.restore()
    circulo(c, x, y, r, color, shader=grad_radial(x - r * 0.3, y - r * 0.3, r * 1.4, ["#FFF6C8", color]))


def luna(c, x, y, r, color_fondo="#0b1530"):
    brillo(c, x, y, r * 3, "#dfe8ff", 70)
    circulo(c, x, y, r, "#F4F1DE")
    circulo(c, x + r * 0.45, y - r * 0.2, r * 0.9, color_fondo)


def estrellas(c, t=0.0, n=90, semilla=1, y_max=H * 0.6):
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y, r, f = rnd.uniform(0, W), rnd.uniform(0, y_max), rnd.uniform(1.2, 3.6), rnd.uniform(0, 6.28)
        a = int(140 + 115 * math.sin(t * 2 + f))
        circulo(c, x, y, r, "#ffffff", a=max(30, a))


def nube(c, x, y, s=1.0, a=235, color="#ffffff"):
    partes = [(-70, 10, 55), (-20, -25, 70), (40, -10, 60), (85, 15, 45), (0, 25, 70), (-60, 30, 45), (60, 32, 50)]
    elipse(c, x, y + 55 * s, 140 * s, 22 * s, "#000000", a=35, blur=14 * s)
    for dx, dy, r in partes:
        circulo(c, x + dx * s, y + dy * s, r * s, color, a=a)
    for dx, dy, r in partes[:3]:
        circulo(c, x + dx * s - 8 * s, y + dy * s - 10 * s, r * 0.55 * s, "#ffffff", a=int(a * 0.35))


def nubes(c, t, filas=((350, 0.9, 25), (620, 0.6, 15)), semilla=4, a=230):
    rnd = random.Random(semilla)
    for (y, s, vel) in filas:
        for k in range(3):
            x0 = rnd.uniform(0, W)
            x = (x0 + vel * t) % (W + 500) - 250
            nube(c, x, y + rnd.uniform(-60, 60), s * rnd.uniform(0.8, 1.2), a)


def _cresta(semilla, x, rugosidad=1.0):
    rnd = random.Random(semilla)
    fs = [(rnd.uniform(0.002, 0.004), rnd.uniform(0, 6), 1.0), (rnd.uniform(0.006, 0.01), rnd.uniform(0, 6), 0.45 * rugosidad),
          (rnd.uniform(0.018, 0.03), rnd.uniform(0, 6), 0.15 * rugosidad)]
    return sum(a * math.sin(x * f + ph) for f, ph, a in fs) / 1.6


def montanas(c, base_y, alto, semilla=1, color="#4b5d7a", nieve=True, desplazar=0.0, picos=None, sombra_lado=True, color_nieve="#F4F8FF"):
    """Cordillera procedural. `picos` = lista de (x, altura_relativa) para picos marcados."""
    pts = []
    for x in range(-40, W + 60, 20):
        xx = x + desplazar
        h = alto * (0.55 + 0.45 * _cresta(semilla, xx))
        if picos:
            for (px, ph) in picos:
                h = max(h, alto * ph * max(0, 1 - abs(x - px) / (alto * 0.9)))
        pts.append((x, base_y - h))
    pts += [(W + 60, H + 10), (-40, H + 10)]
    pth = camino(pts, True, False)
    c.drawPath(pth, pintura(shader=grad_lineal(0, base_y - alto, 0, base_y, [mezcla(color, "#ffffff", 0.15), color])))
    if nieve:
        linea_nieve = base_y - alto * 0.72
        c.save()
        c.clipPath(pth, doAntiAlias=True)
        nv = []
        for x in range(-40, W + 60, 20):
            nv.append((x, linea_nieve + 25 * math.sin(x * 0.05 + semilla) + 12 * math.sin(x * 0.13)))
        nv += [(W + 60, -10), (-40, -10)]
        c.drawPath(camino(nv, True, False), pintura(color_nieve, 245))
        c.restore()
    if sombra_lado:
        c.save()
        c.clipPath(pth, doAntiAlias=True)
        rect(c, 0, base_y - alto, W, base_y, "#000", shader=grad_lineal(0, 0, W, 0, [col("#000000", 0), col("#000000", 60)]))
        c.restore()
    return pth


def colinas(c, base_y, alto, color="#3f8f4f", semilla=7, desplazar=0.0):
    pts = [(x, base_y - alto * (0.6 + 0.4 * math.sin((x + desplazar) * 0.004 + semilla))) for x in range(-40, W + 60, 30)]
    pts += [(W + 60, H + 10), (-40, H + 10)]
    c.drawPath(camino(pts, True, True), pintura(shader=grad_lineal(0, base_y - alto, 0, base_y + 200, [mezcla(color, "#ffffff", 0.1), mezcla(color, "#000000", 0.25)])))


def pino(c, x, y, h, color="#1f5e3b", nieve=False):
    rect(c, x - h * 0.04, y - h * 0.15, x + h * 0.04, y, "#5b3a22")
    for k in range(3):
        yy = y - h * 0.12 - k * h * 0.25
        ww = h * (0.32 - k * 0.07)
        figura(c, [(x - ww, yy), (x, yy - h * 0.42), (x + ww, yy)], mezcla(color, "#000000", 0.1 * k), suave=False)
        if nieve:
            figura(c, [(x - ww * 0.35, yy - h * 0.28), (x, yy - h * 0.42), (x + ww * 0.35, yy - h * 0.28)], "#ffffff", suave=False)


def agua(c, y, t, arriba="#1b8fd1", abajo="#062a4d", olas=True):
    rect(c, 0, y, W, H, "#000", shader=grad_lineal(0, y, 0, H, [arriba, abajo]))
    if olas:
        pts = [(x, y + 12 * math.sin(x / 60 + t * 3) + 6 * math.sin(x / 23 - t * 2)) for x in range(-20, W + 40, 20)]
        c.drawPath(camino(pts, False, True), pintura("#ffffff", 200, trazo=7))


def rayos_luz(c, t, n=6, a=22):
    for i in range(n):
        x0 = 100 + i * 180 + 60 * math.sin(t * 0.6 + i)
        figura(c, [(x0, 0), (x0 + 70, 0), (x0 + 260, H), (x0 + 120, H)], "#bfe9ff", a=a, suave=False)


def burbujas(c, t, n=40, semilla=2, y_min=0):
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y0, r, v = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(5, 20), rnd.uniform(60, 160)
        y = (y0 - v * t) % (H + 60) - 30
        if y < y_min:
            continue
        circulo(c, x + 8 * math.sin(t * 2 + y0), y, r, "#d8f4ff", a=140, trazo=3)
        circulo(c, x - r * 0.3 + 8 * math.sin(t * 2 + y0), y - r * 0.3, r * 0.25, "#ffffff", a=160)


def particulas(c, t, n=50, color="#ffffff", semilla=3, a=90, vel=(15, 50), tam=(2, 5)):
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y0, r, v, f = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(*tam), rnd.uniform(*vel), rnd.uniform(0, 6)
        y = (y0 - v * t) % H
        circulo(c, x + 10 * math.sin(t + f), y, r, color, a=a)


def lluvia(c, t, n=120, semilla=5, a=120):
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y0, v = rnd.uniform(0, W + 200), rnd.uniform(0, H), rnd.uniform(1400, 2000)
        y = (y0 + v * t) % (H + 100) - 50
        linea(c, x - y * 0.12, y, x - y * 0.12 - 8, y + 40, "#cfe3ff", ancho=3, a=a)


def nieve(c, t, n=120, semilla=6):
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y0, r, v, f = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 8), rnd.uniform(60, 140), rnd.uniform(0, 6)
        y = (y0 + v * t) % (H + 40) - 20
        circulo(c, x + 30 * math.sin(t * 0.8 + f), y, r, "#ffffff", a=220)


# ---------------------------------------------------------------- recursos didácticos


def onda_sonido(c, x, y, t, color="#ffffff", n=3, r0=40, paso=45, angulo=0, apertura=70, ancho=8):
    """Arcos de sonido/vibración que salen de (x, y) hacia `angulo` (grados, 0 = derecha)."""
    for k in range(n):
        fase = (t * 1.6 + k / n) % 1
        r = r0 + fase * paso * n
        a = int(255 * (1 - fase))
        rr = skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r)
        c.drawArc(rr, angulo - apertura / 2, apertura, False, pintura(color, a, trazo=ancho))


def anillos(c, x, y, t, color="#FFD400", n=3, rmax=130, ancho=7):
    for k in range(n):
        f = (t * 0.9 + k / n) % 1
        circulo(c, x, y, 20 + f * rmax, color, a=int(255 * (1 - f)), trazo=ancho)


def flecha(c, x0, y0, x1, y1, color="#FFD400", ancho=12, progreso=1.0, punta=34):
    p = clamp(progreso)
    if p <= 0:
        return
    xe, ye = lerp(x0, x1, p), lerp(y0, y1, p)
    linea(c, x0, y0, xe, ye, color, ancho)
    ang = math.atan2(ye - y0, xe - x0)
    pts = [(xe + math.cos(ang) * punta * 0.4, ye + math.sin(ang) * punta * 0.4),
           (xe + math.cos(ang + 2.5) * punta, ye + math.sin(ang + 2.5) * punta),
           (xe + math.cos(ang - 2.5) * punta, ye + math.sin(ang - 2.5) * punta)]
    figura(c, pts, color, suave=False)


def etiqueta(c, txt, x, y, px=None, py=None, color="#FFD400", texto_color="#111111", tam=44, a=1.0):
    """Cartel redondeado con texto centrado en (x, y) y una línea hacia el punto (px, py)."""
    if a <= 0:
        return
    al = int(255 * clamp(a))
    w = ancho_texto(txt, tam) + tam * 1.0
    h = tam * 1.55
    if px is not None:
        linea(c, x, y, px, py, color, ancho=5, a=al)
        circulo(c, px, py, 11, color, a=al)
    s = ease_out_back(a)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rect(c, -w / 2, -h / 2 + 6, w / 2, h / 2 + 6, "#000000", a=int(al * 0.35), radio=h / 2, blur=10)
    rect(c, -w / 2, -h / 2, w / 2, h / 2, color, a=al, radio=h / 2)
    texto(c, txt, 0, tam * 0.36, tam, texto_color, tipo="bold", sombra=False, a=al)
    c.restore()


def contador(c, valor, x, y, tam=170, sufijo="", decimales=0, color="#FFD400", caja=True):
    s = f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".") + sufijo
    w = ancho_texto(s, tam, "titulo")
    if caja:
        rect(c, x - w / 2 - 40, y - tam * 0.95, x + w / 2 + 40, y + tam * 0.3, "#000000", a=150, radio=40)
    texto(c, s, x, y, tam, color, tipo="titulo", contorno=0)


def lupa(c, x, y, r, dibujar_dentro, color_borde="#ffffff"):
    """Círculo de 'zoom' con contenido propio: dibujar_dentro(c) se dibuja recortado al círculo."""
    circulo(c, x, y + 10, r + 8, "#000000", a=90, blur=20)
    c.save()
    pth = skia.Path()
    pth.addCircle(x, y, r)
    c.clipPath(pth, doAntiAlias=True)
    dibujar_dentro(c)
    c.restore()
    circulo(c, x, y, r, color_borde, trazo=12)


def vineta(c, fuerza=150):
    c.drawRect(skia.Rect.MakeWH(W, H), pintura(shader=grad_radial(W / 2, H / 2, H * 0.75, [col("#000000", 0), col("#000000", 0), col("#000000", fuerza)], [0, 0.55, 1.0])))
