"""Estilo "garabato" para episodios con diálogos: personajes blancos y pelados de ojos grandes con párpado caído,
colores pastel apagados y líneas finas violeta. Coordenadas de la franja: 1920x1080 (ver reel_dialogo.py)."""
import math

import dibujo as d

BW, BH = 1920, 1080
TINTA = "#3B2F63"
PIEL = "#F3F4FA"
CIELO, CIELO2 = "#DCEFF2", "#BFE0E8"
PASTO, PASTO2 = "#9CC3CF", "#DDEED9"
LAVANDA = "#A9A2D6"


def fondo_parque(c, t, noche=0.0, hielo=0.0):
    cielo = d.mezcla(CIELO, "#1D2347", noche)
    d.rect(c, 0, 0, BW, BH, "#000000", shader=d.grad_lineal(0, 0, 0, BH, [cielo, d.mezcla(CIELO2, "#141833", noche)]))
    for (x, y, s) in ((380, 150, 1.0), (1150, 110, 0.8), (1650, 200, 0.7)):  # nubes crema
        for (dx, dy, r) in ((-70, 10, 55), (0, -15, 70), (75, 10, 55)):
            d.circulo(c, x + dx * s + 10 * math.sin(t * 0.3), y + dy * s, r * s, d.mezcla("#FFF6D6", "#3A3F66", noche))
    # ciudad dibujada solo con líneas
    for k, (x, w, h) in enumerate(((60, 220, 220), (300, 160, 300), (480, 260, 180), (1150, 240, 260), (1420, 200, 200), (1640, 260, 320))):
        d.rect(c, x, 560 - h, x + w, 560, d.mezcla("#E7EEF5", "#262B4F", noche), trazo=None)
        for j in range(3):
            d.rect(c, x + 25 + j * 60, 560 - h + 40, x + 55 + j * 60, 560 - h + 90, d.mezcla(LAVANDA, "#3B3F6E", noche))
    d.rect(c, 0, 540, BW, 820, d.mezcla(PASTO, "#1E2A44", noche))
    d.rect(c, 0, 800, BW, BH, d.mezcla(PASTO2, "#26304A", noche))
    if hielo > 0:
        d.rect(c, 0, 540, BW, BH, "#EAF6FF", a=int(170 * hielo))
    for k in range(14):  # pastitos
        gx, gy = 80 + k * 137, 600 + (k * 53) % 180
        c.drawPath(d.camino([(gx - 10, gy), (gx - 4, gy - 22), (gx, gy), (gx + 6, gy - 26), (gx + 12, gy)], False, False),
                   d.pintura(TINTA, trazo=4))


def arbol(c, x, y, s=1.0, noche=0.0, hielo=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    tronco = d.mezcla("#8C86C9", "#3B3F6E", noche)
    c.drawPath(d.camino([(-30, 0), (-20, -150), (-60, -260), (0, -200), (40, -300), (20, -150), (30, 0)], True, True),
               d.pintura(tronco))
    copa = d.mezcla("#8FB6D6", "#2E3A63", noche)
    copa = d.mezcla(copa, "#F4FBFF", hielo)
    for (dx, dy, r) in ((-120, -300, 110), (0, -360, 140), (120, -300, 110), (-60, -250, 100), (70, -250, 100)):
        d.circulo(c, dx, dy, r, copa)
    c.restore()


def banco(c, x, y, s=1.0, color="#8C86C9"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for yy in (-210, -160):
        d.rect(c, -230, yy, 230, yy + 32, color, radio=8)
    d.rect(c, -240, -110, 240, -80, color, radio=8)
    for sx in (-1, 1):
        d.rect(c, sx * 200 - 14, -80, sx * 200 + 14, 0, "#5E5896", radio=6)
    c.restore()


def persona(c, x, y, s=1.0, t=0.0, tipo="joven", boca=0.0, mira=0.0, ojos="normal", pose="parado",
            brazos="abajo", bufanda=None, tiembla=0.0, solo_ojos=False, gorra="#E9EAF2"):
    """Personaje garabato. (x, y) = pies (parado) o asiento (sentado). s=1 -> ~560 px de alto."""
    c.save()
    c.translate(x + tiembla * 5 * math.sin(t * 45), y)
    c.scale(s, s)
    cab_y = -470 if pose == "parado" else -330
    if not solo_ojos:
        if pose == "parado":
            for sx in (-1, 1):
                d.rect(c, sx * 34 - 26, -190, sx * 34 + 26, -20, PIEL, radio=24)
                d.elipse(c, sx * 40, -14, 46, 20, PIEL)
            torso = (-70, -370, 70, -170)
        else:
            for sx in (-1, 1):
                d.rect(c, sx * 34 - 26, -70, sx * 34 + 26 + 130, -20, PIEL, radio=24)
                d.rect(c, sx * 34 + 110, -60, sx * 34 + 160, 110, PIEL, radio=22)
                d.elipse(c, sx * 34 + 150, 115, 44, 18, PIEL)
            torso = (-70, -240, 70, -40)
        d.rect(c, *torso, PIEL, radio=50)
        # brazos
        hx, hy = 0, torso[1] + 30
        for sx in (-1, 1):
            if brazos == "adelante":
                pts = [(sx * 60, hy), (sx * 120, hy + 30), (sx * 190, hy + 20)]
            elif brazos == "abrazo":
                pts = [(sx * 60, hy), (sx * 70, hy + 90), (-sx * 30, hy + 110)]
            elif brazos == "cabeza" and sx == 1:
                pts = [(sx * 60, hy), (sx * 120, hy - 80), (sx * 70, cab_y - 30)]
            else:
                pts = [(sx * 64, hy), (sx * 85, hy + 100), (sx * 85, hy + 190)]
            c.drawPath(d.camino(pts, False, True), d.pintura(TINTA, trazo=46))
            c.drawPath(d.camino(pts, False, True), d.pintura(PIEL, trazo=36))
            d.circulo(c, pts[-1][0], pts[-1][1] + 6, 26, PIEL)
        if bufanda:
            d.rect(c, -60, torso[1] - 18, 60, torso[1] + 22, bufanda, radio=16)
            d.rect(c, 20, torso[1], 55, torso[1] + 90, bufanda, radio=12)
        # cabeza
        d.rect(c, -22, cab_y + 50, 22, cab_y + 100, PIEL)
        d.elipse(c, 0, cab_y, 78, 92, PIEL)
        if tipo == "abuelo":  # gorra y arrugas
            d.figura(c, [(-82, cab_y - 30), (-70, cab_y - 85), (0, cab_y - 100), (70, cab_y - 85), (82, cab_y - 30)], gorra)
            d.linea(c, -82, cab_y - 30, 82, cab_y - 30, TINTA, ancho=5)
            for k in range(2):
                c.drawPath(d.camino([(-60, cab_y + 55 + k * 14), (-40, cab_y + 50 + k * 14)], False, True), d.pintura(TINTA, trazo=3))
        else:  # pelito parado
            c.drawPath(d.camino([(-10, cab_y - 88), (0, cab_y - 120), (8, cab_y - 92), (22, cab_y - 115), (24, cab_y - 86)], False, False),
                       d.pintura(TINTA, trazo=5))
        for sx in (-1, 1):  # orejas
            d.elipse(c, sx * 80, cab_y + 5, 16, 24, PIEL)
    # ojos grandes con párpado caído
    for sx in (-1, 1):
        ex, ey = sx * 34, cab_y - 5
        if solo_ojos:
            d.elipse(c, ex, ey, 34, 30, "#FFFFFF")
            d.circulo(c, ex + mira * 12, ey + 6, 10, "#1B1530")
            continue
        if ojos == "cerrados":
            d.linea(c, ex - 24, ey + 4, ex + 24, ey + 4, TINTA, ancho=5)
            continue
        abierto = 36 if ojos == "susto" else 32
        d.elipse(c, ex, ey, 34, abierto, "#FFFFFF")
        d.circulo(c, ex + mira * 12, ey + 8, 10 if ojos != "susto" else 7, "#2A2340")
        if ojos != "susto":  # párpado pesado (solo una línea curva, sin relleno oscuro)
            c.drawPath(d.camino([(ex - 33, ey - 4), (ex, ey - 12), (ex + 33, ey - 4)], False, True), d.pintura(TINTA, trazo=5))
        if ojos == "enojado":
            d.linea(c, ex - sx * 30, ey - 40, ex + sx * 24, ey - 28, TINTA, ancho=6)
    if not solo_ojos:
        my = cab_y + 52
        if boca > 0.05:
            d.elipse(c, 4, my, 14 + 6 * boca, 6 + 16 * boca, "#4A2F5E")
        else:
            d.linea(c, -12, my, 16, my - 2, TINTA, ancho=5)
        if tipo == "abuelo":
            c.drawPath(d.camino([(-26, my - 10), (0, my + 4), (30, my - 12)], False, True), d.pintura(TINTA, trazo=3))
    c.restore()


def murcielago(c, x, y, s, t, boca=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    al = math.sin(t * 16)
    for sx in (-1, 1):
        d.figura(c, [(sx * 30, 0), (sx * 150, -60 - 50 * al), (sx * 180, 20 - 20 * al), (sx * 120, 10), (sx * 90, 40), (sx * 50, 20)], "#6F64B0")
    d.elipse(c, 0, 0, 48, 52, "#7F74C2")
    for sx in (-1, 1):
        d.figura(c, [(sx * 14, -40), (sx * 34, -90), (sx * 44, -30)], "#7F74C2", suave=False)
        d.elipse(c, sx * 16, -8, 14, 13, "#FFFFFF")
        d.circulo(c, sx * 16 + 3, -6, 7, "#1B1530")
    d.elipse(c, 0, 22, 8 + 6 * boca, 3 + 10 * boca, "#3A2350")
    c.restore()
