"""Dibujos compartidos por la serie del apagón mundial (partes 1 y 2)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import skia  # noqa: E402
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

AMARILLO, ROJO, CIAN, VERDE, NARANJA = "#FFD400", "#E04848", "#7FE3FF", "#46E08A", "#FF9A3C"
VENTANA = "#FFD27A"


# ------------------------------------------------------------------ planeta de noche

_CONT = [  # continentes aproximados en coordenadas de la esfera (x, y en -1..1)
    [(-0.75, -0.55), (-0.45, -0.7), (-0.2, -0.5), (-0.3, -0.2), (-0.45, 0.0), (-0.6, -0.15), (-0.8, -0.35)],
    [(-0.42, 0.05), (-0.22, 0.1), (-0.15, 0.35), (-0.3, 0.75), (-0.42, 0.45)],
    [(0.05, -0.6), (0.4, -0.65), (0.75, -0.45), (0.7, -0.15), (0.45, -0.05), (0.2, -0.2), (0.05, -0.35)],
    [(0.05, -0.1), (0.3, -0.05), (0.35, 0.3), (0.2, 0.6), (0.08, 0.3)],
    [(0.55, 0.35), (0.8, 0.3), (0.8, 0.55), (0.6, 0.6)],
]


def _dentro(px, py, pol):
    n, ok = len(pol), False
    for k in range(n):
        x1, y1 = pol[k]
        x2, y2 = pol[(k + 1) % n]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1:
            ok = not ok
    return ok


_rnd = random.Random(11)
_LUCES = []
while len(_LUCES) < 520:
    x, y = _rnd.uniform(-1, 1), _rnd.uniform(-1, 1)
    if x * x + y * y < 0.95 and any(_dentro(x, y, p) for p in _CONT):
        _LUCES.append((x, y, _rnd.uniform(1.5, 4.5), _rnd.random()))


def planeta(c, cx, cy, r, t, apagado=0.0, rot=0.0):
    """Tierra de noche vista desde el espacio. apagado 0..1 = ola de oscuridad que barre de este a oeste."""
    d.brillo(c, cx, cy, r * 1.25, "#3D7BFF", 70)
    d.circulo(c, cx, cy, r, "#0A1A3A", shader=d.grad_radial(cx - r * 0.3, cy - r * 0.3, r * 1.3, ["#173A6E", "#06102A"]))
    c.save()
    pth = skia.Path()
    pth.addCircle(cx, cy, r)
    c.clipPath(pth, doAntiAlias=True)
    for pol in _CONT:
        pts = [(cx + (x + rot) * r, cy + y * r) for x, y in pol]
        d.figura(c, pts, "#15294A", suave=True)
    for (x, y, tam, fase) in _LUCES:
        frente = 1.15 - 2.3 * apagado  # la ola avanza de derecha (x=1) a izquierda
        if x > frente:
            continue
        borde = d.clamp((frente - x) / 0.12)
        tw = 0.75 + 0.25 * math.sin(t * 3 + fase * 20)
        px, py = cx + (x + rot) * r, cy + y * r
        d.circulo(c, px, py, tam * 2.2, VENTANA, a=int(60 * borde * tw))
        d.circulo(c, px, py, tam * 0.9, "#FFF1C4", a=int(240 * borde * tw))
    c.restore()
    d.circulo(c, cx, cy, r, "#6FA8FF", a=120, trazo=8)


def espacio(c, t):
    d.fondo(c, "#02040C", "#060B1E")
    d.estrellas(c, t, n=120, semilla=7, y_max=H)


# ------------------------------------------------------------------ ciudad con ventanas

_rc = random.Random(5)
EDIFICIOS = []
x = -20
while x < W + 20:
    w = _rc.randint(110, 190)
    h = _rc.randint(380, 900)
    EDIFICIOS.append((x, w, h, _rc.choice(["#1B2238", "#20283F", "#171D30", "#242C45"])))
    x += w + _rc.randint(6, 18)
VENTANAS = []
for (bx, bw, bh, _) in EDIFICIOS:
    for fy in range(int(bh / 55) - 1):
        for fx in range(int((bw - 20) / 34)):
            VENTANAS.append((bx + 16 + fx * 34, fy * 55, _rc.random(), _rc.random() < 0.72))


def cielo_noche(c, t, estrellas=0.0, via_lactea=0.0):
    d.fondo(c, d.mezcla("#14203F", "#05070F", estrellas), d.mezcla("#3B3F6E", "#0B1022", estrellas))
    if estrellas > 0:
        rnd = random.Random(3)
        for k in range(int(260 * estrellas)):
            sx, sy, r = rnd.uniform(0, W), rnd.uniform(0, 1300), rnd.uniform(1, 3.2)
            tw = 0.6 + 0.4 * math.sin(t * rnd.uniform(1, 4) + k)
            d.circulo(c, sx, sy, r, "#FFFFFF", a=int(230 * tw * estrellas))
    if via_lactea > 0:
        c.save()
        c.translate(540, 700)
        c.rotate(-35)
        d.elipse(c, 0, 0, 900, 150, "#BFAEFF", a=int(70 * via_lactea), blur=60)
        d.elipse(c, 0, 0, 700, 60, "#FFE7C9", a=int(70 * via_lactea), blur=30)
        rnd = random.Random(9)
        for k in range(int(500 * via_lactea)):
            gx = rnd.gauss(0, 380)
            gy = rnd.gauss(0, 55)
            d.circulo(c, gx, gy, rnd.uniform(0.8, 2.4), "#FFFFFF", a=int(200 * via_lactea * rnd.random()))
        c.restore()


def ciudad(c, t, suelo=1520, apagado=0.0, parpadeo=0.0, escala=1.0):
    """Skyline con ventanas. apagado 0..1 apaga ventanas en orden aleatorio; parpadeo hace temblar las luces."""
    tiembla = parpadeo > 0 and (t * 9) % 1 < 0.35 * parpadeo
    for (bx, bw, bh, color) in EDIFICIOS:
        h = bh * escala
        d.rect(c, bx, suelo - h, bx + bw, suelo, color)
        d.rect(c, bx, suelo - h, bx + 6, suelo, "#000000", a=60)
    for (wx, wy, orden, prendida) in VENTANAS:
        b = next(e for e in EDIFICIOS if e[0] <= wx < e[0] + e[1])
        h = b[2] * escala
        yy = suelo - h + 30 + wy
        if yy > suelo - 40:
            continue
        on = prendida and orden > apagado * 1.05 and not (tiembla and orden < 0.5)
        if on:
            d.rect(c, wx, yy, wx + 20, yy + 30, VENTANA, radio=3)
            d.rect(c, wx - 4, yy - 4, wx + 24, yy + 34, VENTANA, a=40, radio=6)
        else:
            d.rect(c, wx, yy, wx + 20, yy + 30, "#0D111E", radio=3)
    d.rect(c, 0, suelo, W, H, "#000000", shader=d.grad_lineal(0, suelo, 0, H, ["#1A1A24", "#09090E"]))


# ------------------------------------------------------------------ objetos

def semaforo(c, x, y, s=1.0, luz=None):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -14, 0, 14, 420, "#2A2E38")
    d.rect(c, -60, -260, 60, 10, "#1C1F27", radio=24)
    for k, colr in enumerate(("#FF3B30", "#FFCC00", "#34C759")):
        cy = -200 + k * 85
        if luz == k:
            d.brillo(c, 0, cy, 90, colr, 160)
            d.circulo(c, 0, cy, 34, colr)
        else:
            d.circulo(c, 0, cy, 34, "#0E1015")
            d.circulo(c, -8, cy - 8, 8, "#FFFFFF", a=30)
    c.restore()


def auto(c, x, y, s=1.0, color="#D9534F", luces=True, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if luces:
        c.drawPath(d.camino([(130, -40), (520, -110), (520, 40)], True, False), d.pintura(shader=d.grad_lineal(130, 0, 520, 0, [d.col("#FFF6C8", 150), d.col("#FFF6C8", 0)])))
    d.rect(c, -140, -70, 140, 0, color, radio=26)
    d.figura(c, [(-80, -70), (-50, -120), (60, -120), (95, -70)], color, suave=False)
    d.figura(c, [(-65, -72), (-42, -110), (5, -110), (5, -72)], "#9FD3FF", suave=False)
    d.figura(c, [(15, -72), (15, -110), (55, -110), (82, -72)], "#9FD3FF", suave=False)
    for wx in (-85, 85):
        d.circulo(c, wx, 0, 30, "#151515")
        d.circulo(c, wx, 0, 12, "#888888")
    d.rect(c, 120, -55, 142, -35, "#FFF6C8", radio=4)
    d.rect(c, -142, -55, -124, -35, "#FF3B30", radio=4)
    c.restore()


def persona(c, x, y, s=1.0, ropa="#3D6FB6", piel="#E8B48A", pelo="#2B1B12", linterna=False, t=0.0, mira=0.0):
    """Persona de frente (cuerpo superior). (x, y) = cintura."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.figura(c, [(-90, 40), (-100, -120), (-60, -200), (60, -200), (100, -120), (90, 40)], ropa)
    d.rect(c, -22, -235, 22, -195, piel, radio=10)
    d.circulo(c, 0, -290, 72, piel)
    d.figura(c, [(-76, -280), (-70, -340), (-20, -372), (40, -368), (78, -330), (76, -280), (40, -320), (-30, -322)], pelo)
    for sx in (-1, 1):
        d.circulo(c, sx * 26 + mira * 8, -290, 9, "#1A1A1A")
    c.drawPath(d.camino([(-18, -250), (0, -258), (18, -250)], False, True), d.pintura("#7A3A2A", trazo=5))
    if linterna:
        d.rect(c, 40, -150, 110, -100, ropa, radio=20)
        d.rect(c, 100, -175, 130, -115, "#1B1F2A", radio=6)
        c.drawPath(d.camino([(118, -175), (40, -700), (300, -700)], True, False),
                   d.pintura(shader=d.grad_lineal(118, -175, 160, -700, [d.col("#FFFBE0", 170), d.col("#FFFBE0", 0)])))
    c.restore()


def celular_grande(c, x, y, s, bateria, barras, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -170, -330, 170, 330, "#000000", a=110, radio=50, blur=24)
    d.rect(c, -170, -330, 170, 330, "#1B1F2A", radio=50)
    d.rect(c, -150, -305, 150, 305, "#000000", radio=36, shader=d.grad_lineal(0, -305, 0, 305, ["#1E3A6E", "#0E1A33"]))
    d.rect(c, -50, -296, 50, -276, "#000000", radio=10)
    # señal
    for k in range(4):
        h = 18 + k * 14
        d.rect(c, -120 + k * 24, -230 - h, -104 + k * 24, -230, "#FFFFFF", a=255 if k < barras else 60, radio=4)
    if barras == 0:
        d.linea(c, -130, -290, -20, -215, ROJO, ancho=8)
    # batería
    colb = VERDE if bateria > 0.3 else ROJO
    d.rect(c, 40, -275, 130, -235, "#FFFFFF", radio=8, trazo=5)
    d.rect(c, 130, -263, 138, -247, "#FFFFFF", radio=3)
    d.rect(c, 48, -267, 48 + 74 * d.clamp(bateria), -243, colb, radio=5)
    d.texto(c, f"{int(100 * bateria)}%", 0, 30, 110, "#FFFFFF", tipo="titulo")
    d.texto(c, "SIN SEÑAL" if barras == 0 else "Buscando red…" if barras < 2 else "Conectado", 0, 110, 44,
            ROJO if barras == 0 else "#FFFFFF", tipo="bold")
    c.restore()


def calendario(c, x, y, s, numero, voltea=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -170, -150, 170, 190, "#000000", a=90, radio=26, blur=16)
    d.rect(c, -170, -150, 170, 190, "#FFFFFF", radio=26)
    d.rect(c, -170, -150, 170, -60, ROJO, radio=26)
    d.rect(c, -170, -90, 170, -60, ROJO)
    d.texto(c, "DÍA", 0, -85, 48, "#FFFFFF", tipo="titulo", sombra=False)
    d.texto(c, str(numero), 0, 140, 190, "#1B1F2A", tipo="titulo", sombra=False)
    if voltea > 0:
        h = 250 * (1 - voltea)
        d.rect(c, -170, -60, 170, -60 + h, "#F2F2F2")
        if h > 60:
            d.texto(c, str(numero - 1), 0, -60 + h * 0.8, int(190 * (1 - voltea) + 1), "#1B1F2A", tipo="titulo", sombra=False)
    for sx in (-90, 90):
        d.rect(c, sx - 10, -175, sx + 10, -125, "#555555", radio=8)
    c.restore()
