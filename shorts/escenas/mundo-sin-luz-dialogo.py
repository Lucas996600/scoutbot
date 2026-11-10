"""Episodio con diálogos: ¿Cómo sería el mundo sin LUZ? (estilo garabato, escena en franja 1920x1080)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
import doodle as G  # noqa: E402
import ruleta  # noqa: E402

BW, BH = G.BW, G.BH


def living(c, prendida=True):
    d.rect(c, 0, 0, BW, BH, "#C9C4EA" if prendida else "#1A1A2E")
    d.rect(c, 0, 760, BW, BH, "#A9A2D6" if prendida else "#141426")
    # ventana, cuadro y lámpara
    d.rect(c, 1300, 160, 1640, 470, "#DCEFF2" if prendida else "#0D1022", radio=10)
    d.linea(c, 1470, 160, 1470, 470, G.TINTA, ancho=6)
    d.rect(c, 300, 180, 520, 340, "#FFE7B0", radio=6)
    d.linea(c, 820, 0, 820, 140, G.TINTA, ancho=5)
    d.figura(c, [(760, 210), (880, 210), (850, 140), (790, 140)], "#FFF2B0" if prendida else "#2A2A40", suave=False)
    if prendida:
        d.brillo(c, 820, 230, 260, "#FFF2B0", 90)
    # sillón y tele
    d.rect(c, 350, 560, 1050, 780, "#8C86C9", radio=40)
    d.rect(c, 330, 680, 1070, 860, "#7A74B8", radio=40)
    d.rect(c, 1350, 560, 1720, 800, "#3B2F63", radio=14)
    d.rect(c, 1370, 580, 1700, 760, "#9FE6FF" if prendida else "#0B0B14", radio=8)
    d.rect(c, 1480, 800, 1590, 860, "#3B2F63")


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    habla = esc.get("_habla", {})
    if i == 0:
        ruleta.dibujar(c, lt, dur, "luz", gt)
    elif i == 1:  # living: se corta TODA la luz
        prendida = lt < 0.7
        living(c, prendida)
        G.persona(c, 560, 690, 1.12, gt, "joven", boca=habla.get("tito", 0), pose="sentado", mira=0.5)
        G.persona(c, 1150, 1030, 1.12, gt, "abuelo", boca=habla.get("abuelo", 0), mira=-0.6)
        if not prendida:
            d.rect(c, 0, 0, BW, BH, "#05040C", a=248)
            parpadeo = (gt % 2.7) > 2.55
            if not parpadeo:  # solo se ven los ojos
                G.persona(c, 560, 690, 1.12, gt, pose="sentado", solo_ojos=True, mira=math.sin(gt * 2))
                G.persona(c, 1150, 1030, 1.12, gt, solo_ojos=True, mira=-0.8)
    elif i == 2:  # parque de noche: Tito choca un árbol, el murciélago la tiene clara
        G.fondo_parque(c, gt, noche=0.92)
        G.arbol(c, 620, 900, 1.2, noche=0.92)
        choque = lt < 1.2
        tx = 470 if choque else 470 - 40 * math.sin(gt * 1.5)
        G.persona(c, tx, 1040, 1.12, gt, "joven", boca=habla.get("tito", 0), brazos="adelante",
                  ojos="cerrados" if choque and lt > 0.25 else "susto", mira=0.4)
        if 0.2 < lt < 1.4:  # estrellitas del golpe
            for k in range(4):
                ang = gt * 6 + k * 1.57
                d.circulo(c, tx + 110 * math.cos(ang), 520 + 30 * math.sin(ang), 12, "#FFE14D")
        bx = 1950 - (lt / dur) * 1500
        by = 330 + 50 * math.sin(gt * 3)
        for k in range(3):
            d.anillos(c, bx - 60, by, gt + k * 0.25, "#7FE3FF", n=2, rmax=220, ancho=6)
        G.murcielago(c, bx, by, 1.2, gt, boca=habla.get("murcielago", 0))
    elif i == 3:  # la huerta del abuelo
        G.fondo_parque(c, gt, noche=0.85)
        marchita = d.ease(d.clamp(p / 0.8))
        verde = d.mezcla("#7BC47F", "#8A7A5A", marchita)
        mx, my = 960, 900
        d.figura(c, [(mx - 110, my), (mx + 110, my), (mx + 80, my + 140), (mx - 80, my + 140)], "#C98A5E", suave=False)
        c.drawPath(d.camino([(mx, my), (mx + 40 * marchita, my - 200 + 60 * marchita), (mx + 150 * marchita, my - 300 + 200 * marchita)], False, True),
                   d.pintura(verde, trazo=16))
        for k in range(3):
            lx, ly = mx + 30 * marchita + (k - 1) * 70, my - 150 - k * 40 + 120 * marchita
            d.elipse(c, lx, ly, 46, 22, verde)
            d.circulo(c, lx + 20, ly + 50 + 40 * marchita, 30, d.mezcla("#E8574F", "#7A5A4A", marchita))
        G.persona(c, 520, 1040, 1.12, gt, "abuelo", boca=habla.get("abuelo", 0), mira=0.8, ojos="normal")
        G.persona(c, 1420, 1040, 1.12, gt, "joven", boca=habla.get("tito", 0), mira=-0.8,
                  brazos="cabeza" if habla.get("tito", 0) and p > 0.5 else "abajo")
    elif i == 4:  # frío: el abuelo termina congelado
        hielo = d.ease(d.clamp(p / 0.6))
        G.fondo_parque(c, gt, noche=0.8, hielo=hielo)
        G.arbol(c, 250, 860, 1.0, noche=0.8, hielo=hielo)
        d.nieve(c, gt, n=int(40 + 80 * hielo))
        G.banco(c, 960, 960, 1.4)
        G.persona(c, 780, 820, 1.12, gt, "joven", boca=habla.get("tito", 0), pose="sentado", brazos="abrazo",
                  bufanda="#E8574F", tiembla=hielo, mira=0.7 if p > 0.7 else 0)
        G.persona(c, 1150, 820, 1.12, gt, "abuelo", pose="sentado", ojos="susto" if hielo > 0.8 else "normal", tiembla=hielo * (1 - hielo))
        if hielo > 0.5:  # bloque de hielo sobre el abuelo
            a = int(170 * d.clamp((hielo - 0.5) * 2))
            d.rect(c, 1010, 380, 1330, 980, "#BFE8FF", a=a, radio=24)
            d.rect(c, 1010, 380, 1330, 980, "#EAF8FF", trazo=8, a=a)
            d.linea(c, 1050, 420, 1120, 520, "#FFFFFF", ancho=6, a=a)
        if p > 0.82:
            d.texto(c, "...", 1330, 380, 90, "#FFFFFF", tipo="titulo")
    else:  # el gusano de la fuente hidrotermal sigue de fiesta
        d.rect(c, 0, 0, BW, BH, "#000000", shader=d.grad_lineal(0, 0, 0, BH, ["#16294A", "#060B18"]))
        d.rect(c, 0, 900, BW, BH, "#3A3048")
        d.figura(c, [(820, 910), (870, 600), (900, 540), (1020, 540), (1050, 600), (1100, 910)], "#5A4E6A")
        d.brillo(c, 960, 560, 260, "#FF9A5A", 170)
        for k in range(5):
            f = (gt * 0.5 + k / 5) % 1
            d.circulo(c, 960 + 30 * math.sin(f * 7 + k), 520 - f * 420, 40 + f * 70, "#6A5A78", a=int(150 * (1 - f)))
        for k, bx in enumerate((300, 420, 1500, 1620)):  # gusanos bailando
            ond = 35 * math.sin(gt * 4 + k)
            c.drawPath(d.camino([(bx, 910), (bx + ond * 0.5, 760), (bx + ond, 620)], False, True), d.pintura(G.TINTA, trazo=48))
            c.drawPath(d.camino([(bx, 910), (bx + ond * 0.5, 760), (bx + ond, 620)], False, True), d.pintura("#F3F4FA", trazo=38))
            d.circulo(c, bx + ond, 600, 42, "#E8574F")
        # el gusano que habla, con ojos de la serie
        gx = 660
        bo = habla.get("gusano", 0)
        c.drawPath(d.camino([(gx, 910), (gx + 10 * math.sin(gt * 3), 700), (gx, 520)], False, True), d.pintura(G.TINTA, trazo=78))
        c.drawPath(d.camino([(gx, 910), (gx + 10 * math.sin(gt * 3), 700), (gx, 520)], False, True), d.pintura("#F3F4FA", trazo=66))
        d.circulo(c, gx, 470, 70, "#E8574F")
        for sx in (-1, 1):
            d.elipse(c, gx + sx * 28, 560, 22, 20, "#FFFFFF")
            d.circulo(c, gx + sx * 28 + 6, 565, 10, "#1B1530")
        d.elipse(c, gx + 4, 615, 12 + 6 * bo, 4 + 14 * bo, "#4A2F5E")
        for k in range(3):  # notitas de la fiesta
            f = (gt * 0.6 + k / 3) % 1
            d.texto(c, "♪", 1300 + k * 120, 500 - f * 300, 80, "#FFE14D", tipo="titulo", a=int(255 * (1 - f)))
        ruleta.globi(c, 1550, 260 + 20 * math.sin(gt * 2), 0.9, gt, expresion="susto" if p < 0.5 else "feliz")
