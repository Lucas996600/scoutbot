"""Escenas ilustradas: ¿Cómo duermen los tiburones?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

GRIS, GRIS_OSC, PANZA = "#6F8FA8", "#46627A", "#EEF3F6"
NODRIZA, NODRIZA_OSC = "#B08A5A", "#7C5E38"
CIAN, AMARILLO = "#7FE3FF", "#FFD400"


# ------------------------------------------------------------------ el tiburón

def tiburon(c, x, y, s=1.0, rot=0.0, t=0.0, ojos="abiertos", boca=0.0, color=GRIS, oscuro=GRIS_OSC, nado=1.0, sonrisa=True, barbillas=False):
    """Tiburón de perfil mirando a la derecha, centrado en (x, y). s=1 -> ~900 px de largo."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    w = 34 * math.sin(t * 4) * nado
    # cola (heterocerca)
    d.figura(c, [(-330, -10), (-470, -190 + w), (-430, -10 + w * 0.5), (-460, 110 + w), (-330, 20)], oscuro)
    # aletas
    d.figura(c, [(-40, -100), (30, -260), (110, -95)], oscuro)
    d.figura(c, [(-250, -50), (-225, -110), (-190, -55)], oscuro)
    d.figura(c, [(-200, 50), (-180, 95), (-150, 55)], oscuro)
    # cuerpo
    cuerpo = [(420, 10), (380, -55), (250, -105), (60, -125), (-150, -95), (-300, -40), (-345, 0),
              (-300, 32), (-150, 80), (60, 110), (250, 95), (380, 55)]
    d.figura(c, cuerpo, color, shader=d.grad_lineal(0, -125, 0, 110, [d.mezcla(color, "#000000", 0.15), color, PANZA], [0, 0.5, 0.78]))
    # aleta pectoral
    d.figura(c, [(120, 60), (40, 200 + 10 * math.sin(t * 2)), (10, 190), (60, 70)], oscuro)
    # branquias
    for k in range(5):
        gx = 230 - k * 26
        c.drawPath(d.camino([(gx, -40), (gx - 10, 0), (gx, 40)], False, True), d.pintura(oscuro, trazo=6))
    # boca
    if boca > 0:
        d.figura(c, [(395, 30), (300, 45), (340, 55 + 60 * boca), (400, 50)], "#5A2A34", suave=True)
        for k in range(4):
            tx = 380 - k * 22
            d.figura(c, [(tx - 7, 38), (tx + 7, 38), (tx, 52)], "#FFFFFF", suave=False)
    elif sonrisa:
        c.drawPath(d.camino([(395, 38), (350, 55), (305, 48)], False, True), d.pintura("#3A2A2A", trazo=7))
    if barbillas:
        d.linea(c, 405, 25, 420, 70, oscuro, ancho=6)
    # ojo
    ex, ey = 320, -25
    if ojos == "cerrados":
        c.drawPath(d.camino([(ex - 22, ey), (ex, ey + 12), (ex + 22, ey)], False, True), d.pintura("#1A1A1A", trazo=7))
    elif ojos == "sueño":
        d.circulo(c, ex, ey, 20, "#FFFFFF")
        d.circulo(c, ex + 3, ey + 4, 11, "#111111")
        tapa = [(ex + 23 * math.cos(math.radians(a)), ey + 4 - 23 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
        d.figura(c, tapa, d.mezcla(color, "#000000", 0.1), suave=False)
        c.drawPath(d.camino([(ex - 23, ey + 4), (ex, ey + 9), (ex + 23, ey + 4)], False, True), d.pintura("#1A1A1A", trazo=5))
    else:
        d.circulo(c, ex, ey, 20, "#FFFFFF")
        d.circulo(c, ex + 4, ey, 12, "#111111")
        d.circulo(c, ex - 2, ey - 6, 4, "#FFFFFF")
    c.restore()


def zzz(c, x, y, t, color="#FFFFFF", tam=60):
    for k in range(3):
        f = (t * 0.45 + k / 3) % 1
        d.texto(c, "z" if k % 2 else "Z", x + 50 * f + 20 * math.sin(f * 6), y - 220 * f, int(tam * (0.6 + 0.6 * f)), color, tipo="titulo",
                a=int(255 * math.sin(math.pi * f)))


def oceano(c, t, arriba="#1E78B4", abajo="#06233F", fondo_y=None):
    d.fondo(c, arriba, abajo)
    d.rayos_luz(c, t, n=6, a=18)
    d.particulas(c, t, 40, "#CFEFFF", a=60)
    if fondo_y:
        d.rect(c, 0, fondo_y, W, H, "#000000", shader=d.grad_lineal(0, fondo_y, 0, H, ["#C9B27E", "#7E6A44"]))
        for k in range(6):
            bx = 80 + k * 190
            c.drawPath(d.camino([(bx, fondo_y + 10), (bx + 18 * math.sin(t * 1.4 + k), fondo_y - 110), (bx - 12, fondo_y - 210 + (k % 3) * 40)], False, True),
                       d.pintura("#2E8A5A", trazo=14))
    d.burbujas(c, t, n=18, y_min=480)


def corriente(c, t, n=16, a=90, vel=500):
    for k in range(n):
        y = 560 + (k * 97) % 1000
        x = W - ((t * vel + k * 211) % (W + 400))
        d.linea(c, x, y, x + 140, y, "#FFFFFF", ancho=4, a=a)


def flujo(c, x0, y0, x1, y1, t, color=CIAN, n=4):
    for k in range(n):
        f = (t * 0.9 + k / n) % 1
        x, y = d.lerp(x0, x1, f), d.lerp(y0, y1, f)
        d.circulo(c, x, y, 12, color, a=int(255 * math.sin(math.pi * f)))


def barra(c, x, y, w, h, nivel, color, etiqueta_txt):
    d.rect(c, x, y, x + w, y + h, "#0B1A2A", a=200, radio=h / 2)
    d.rect(c, x + 8, y + 8, x + 8 + (w - 16) * d.clamp(nivel), y + h - 8, color, radio=(h - 16) / 2)
    d.texto(c, etiqueta_txt, x + w / 2, y + h * 0.68, int(h * 0.5), "#FFFFFF", tipo="titulo", sombra=True)


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # duermen nadando
        oceano(c, gt)
        x = d.lerp(380, 700, p)
        y = 1080 + 20 * math.sin(gt * 1.2)
        tiburon(c, x, y, 0.95, 2 * math.sin(gt), gt, ojos="sueño", nado=0.6)
        zzz(c, x + 330, y - 120, gt)
        d.etiqueta(c, "NADA Y DESCANSA", 540, 640, color=CIAN, tam=48, a=d.aparece(lt, 0.8))
    elif i == 1:  # agua por la boca y branquias; si para, falta oxígeno
        oceano(c, gt)
        para = d.ease((p - 0.55) / 0.25)
        x, y = 470, 1080
        tiburon(c, x, y, 0.95, 0, gt, ojos="abiertos" if para < 0.5 else "sueño", boca=0.5, nado=1 - 0.85 * para)
        if para < 0.9:
            mx, my = x + 395 * 0.95, y + 45 * 0.95
            flujo(c, mx + 220, my, mx - 30, my, gt, n=4)
            flujo(c, x + 200 * 0.95, y, x + 120 * 0.95, y + 160, gt + 0.3, n=3)
        if para < 0.3:
            corriente(c, gt, n=12, a=70)
        d.etiqueta(c, "BRANQUIAS", 330, 1330, x + 180 * 0.95, y + 10, color=CIAN, tam=42, a=d.aparece(lt, 0.6))
        barra(c, 240, 640, 600, 90, 1 - 0.7 * para, "#46E08A" if para < 0.5 else "#E04848", "OXÍGENO")
    elif i == 2:  # blanco filmado durmiendo en 2016
        oceano(c, gt, "#164E7A", "#041A30")
        corriente(c, gt, n=18, a=80, vel=420)
        tiburon(c, 520, 1080, 1.0, -2, gt, ojos="sueño", boca=0.7, nado=0.35)
        # cámara
        d.rect(c, 40, 560, 1040, 1500, "#FFFFFF", a=180, radio=30, trazo=6)
        if (gt % 1) < 0.6:
            d.circulo(c, 110, 630, 18, "#E04848")
        d.texto(c, "REC", 190, 645, 44, "#FFFFFF", tipo="titulo")
        d.etiqueta(c, "2016", 900, 630, color=AMARILLO, tam=48, a=d.aparece(lt, 0.4))
        d.etiqueta(c, "BOCA ABIERTA", 760, 1390, color="#FFFFFF", tam=40, a=d.aparece(lt, dur * 0.5))
    elif i == 3:  # médula = piloto automático
        oceano(c, gt, "#123A5E", "#030F1E")
        x, y, s = 470, 1080, 0.95
        tiburon(c, x, y, s, 0, gt, ojos="cerrados", nado=0.8, color="#557089", oscuro="#33495C")
        # cerebro que descansa
        bx, by = x + 280 * s, y - 50 * s
        d.brillo(c, bx, by, 80, "#9FB8FF", 120)
        d.elipse(c, bx, by, 38, 26, "#C9B8FF")
        zzz(c, bx + 20, by - 40, gt, "#C9B8FF", 44)
        # médula con pulsos
        pts = [(x + (250 - k * 60) * s, y + (-50 + 10 * math.sin(gt * 4 + k * 0.7)) * s) for k in range(10)]
        c.drawPath(d.camino(pts, False, True), d.pintura(AMARILLO, 120, trazo=20, blur=8))
        c.drawPath(d.camino(pts, False, True), d.pintura(AMARILLO, trazo=8))
        for k in range(3):
            f = (gt * 0.8 + k / 3) % 1
            j = f * (len(pts) - 1)
            a, b = pts[int(j)], pts[min(int(j) + 1, len(pts) - 1)]
            d.brillo(c, d.lerp(a[0], b[0], j % 1), d.lerp(a[1], b[1], j % 1), 30, "#FFFFFF", 230)
        d.etiqueta(c, "CEREBRO: DESCANSA", 650, 700, bx, by - 30, color="#C9B8FF", tam=40, a=d.aparece(lt, 0.4))
        d.etiqueta(c, "MÉDULA: NADA", 330, 1350, x - 60 * s, y - 40 * s, color=AMARILLO, tam=40, a=d.aparece(lt, 1.2))
        d.etiqueta(c, "TEORÍA", 880, 1480, color="#FFFFFF", tam=34, a=d.aparece(lt, 2.0))
    elif i == 4:  # nodrizas en el fondo / cueva
        oceano(c, gt, "#1A6E8C", "#06283A", fondo_y=1420)
        # cueva
        d.figura(c, [(-60, 1500), (-40, 820), (200, 640), (620, 600), (980, 700), (1140, 900), (1140, 1500)], "#3E4A52")
        d.figura(c, [(60, 1460), (90, 960), (300, 820), (640, 790), (900, 880), (1020, 1060), (1030, 1460)], "#000000", a=255,
                 shader=d.grad_radial(540, 1200, 600, ["#1B3A48", "#081820"]))
        d.rect(c, 60, 1400, 1030, 1470, "#000000", shader=d.grad_lineal(0, 1400, 0, 1470, ["#8E7A50", "#5E4E30"]))
        for k, (bx, by, s, rr) in enumerate(((380, 1340, 0.62, -3), (700, 1300, 0.55, 4), (520, 1220, 0.5, -2))):
            bomba = 0.2 + 0.3 * (0.5 + 0.5 * math.sin(gt * 2.4 + k))
            tiburon(c, bx, by, s, rr, gt, ojos="cerrados", boca=bomba, color=NODRIZA, oscuro=NODRIZA_OSC, nado=0.05, barbillas=True)
            mx, my = bx + 400 * s, by + 40 * s
            flujo(c, mx + 120, my - 30, mx - 10, my, gt + k * 0.4, n=3)
        zzz(c, 820, 1100, gt)
        d.etiqueta(c, "TIBURÓN NODRIZA", 540, 690, color=AMARILLO, tam=46, a=d.aparece(lt, 0.4))
    elif i == 5:  # ojos abiertos, poca energía
        oceano(c, gt, "#0E2E52", "#020A16", fondo_y=1380)
        d.luna(c, 860, 640, 60, "#0E2E52")
        d.brillo(c, 860, 640, 260, "#BFD8FF", 60)
        tiburon(c, 520, 1330, 0.9, 0, gt, ojos="abiertos", nado=0.03, color="#7A8C6A", oscuro="#55664A", sonrisa=True)
        d.anillos(c, 520 + 320 * 0.9, 1330 - 25 * 0.9, gt, "#FFFFFF", n=2, rmax=70, ancho=4)
        zzz(c, 360, 1200, gt)
        barra(c, 200, 800, 520, 80, 1 - 0.55 * d.ease(p / 0.6), "#FFD400", "ENERGÍA")
        d.etiqueta(c, "OJOS ABIERTOS", 730, 1180, 520 + 320 * 0.9, 1330 - 25 * 0.9, color="#FFFFFF", tam=40, a=d.aparece(lt, dur * 0.45))
    else:  # cierre
        oceano(c, gt)
        x = 470 + 40 * math.sin(gt * 0.8)
        tiburon(c, x, 1100, 0.95, 4 * math.sin(gt * 1.3), gt, ojos="abiertos")
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > 0.6:
            d.emoji(c, "💬", 860, 720, int(160 * s))
