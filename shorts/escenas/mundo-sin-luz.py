"""¿Cómo sería el mundo sin... LUZ?  — Episodio 1 de la serie (ruleta + caricatura con volumen)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import cartoon3d as C  # noqa: E402
import ruleta  # noqa: E402

CIAN, AMARILLO = "#7FE3FF", "#FFD400"
GENTE = [  # (x, ropa, piel, pelo)
    (230, "#E2574C", "#F2C28B", "#3A2418"),
    (540, "#3D9BFF", "#C68C5E", "#1B1B1B"),
    (850, "#9BE34A", "#F6D2B0", "#C9862E"),
]


def ciudad_atardecer(c, t, ventanas=0.0, escarcha=0.0, noche=False):
    if noche:
        d.fondo(c, "#0A0E24", "#141A3A")
    else:
        d.fondo(c, "#FF8A5A", "#FFD08A")
        d.elipse(c, 540, 900, 700, 300, "#FF5FA2", a=50, blur=120)
    C.edificio(c, 40, 1500, 250, 760, "#5B7BD6", ventanas=ventanas, escarcha=escarcha, semilla=1)
    C.edificio(c, 360, 1500, 300, 600, "#E07A5F", ventanas=ventanas, escarcha=escarcha, semilla=4)
    C.edificio(c, 720, 1500, 260, 820, "#8E5BFF", ventanas=ventanas, escarcha=escarcha, semilla=7)
    d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#6E7A8A" if not noche else "#22283A", "#3A414E" if not noche else "#0E1120"]))
    if escarcha > 0:
        d.rect(c, 0, 1500, W, 1540, "#F4FBFF", a=int(230 * escarcha))


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # la ruleta oficial del canal
        ruleta.dibujar(c, lt, dur, "luz", gt)
    elif i == 1:  # todo se apaga
        corte = dur * 0.32
        shake = 14 * math.exp(-max(0, lt - corte) * 6) * math.sin(lt * 60) if lt > corte else 0
        with d.camara(c, zoom=1.0 + 0.04 * p, dx=shake):
            ciudad_atardecer(c, gt, ventanas=0.85)
            C.sol_cara(c, 540, 640, 120, gt, prendido=1.0 if lt < corte else 0.0)
            for k, (x, ropa, piel, pelo) in enumerate(GENTE):
                C.personaje(c, x, 1600, 0.85, gt + k, ropa, piel, pelo, expresion="feliz" if lt < corte else "susto", camina=1.0 if lt < corte else 0)
        if lt >= corte:
            d.rect(c, 0, 0, W, H, "#02030A", a=250)
            with d.camara(c, zoom=1.0 + 0.04 * p, dx=shake):
                for k, (x, ropa, piel, pelo) in enumerate(GENTE):  # solo se ven los ojos
                    C.personaje(c, x, 1600, 0.85, gt + k, ropa, piel, pelo, solo_ojos=True, mira=math.sin(gt * 3 + k))
    elif i == 2:  # nadie ve; murciélagos y delfines son los reyes
        ciudad_atardecer(c, gt, ventanas=0.0, noche=True)
        d.rect(c, 0, 0, W, H, "#02030A", a=150)
        for k, (x, ropa, piel, pelo) in enumerate(GENTE):
            C.personaje(c, x + 25 * math.sin(gt * 1.5 + k * 2), 1620, 0.8, gt + k, ropa, piel, pelo,
                        expresion="susto", brazos="adelante", mira=math.sin(gt * 4 + k))
        bx = 120 + (lt / dur) * 820
        by = 950 + 60 * math.sin(gt * 2)
        for k in range(3):
            d.anillos(c, bx, by, gt + k * 0.3, CIAN, n=2, rmax=260, ancho=6)
        C.murcielago(c, bx, by, 0.9, gt)
        a = d.aparece(lt, dur * 0.45, 0.5)
        if a > 0:  # delfín en una burbuja-ventana del mar
            def dentro(cv):
                d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(800, 640, 260, ["#0E3A66", "#03101F"]))
                d.anillos(cv, 860, 640, gt, CIAN, n=3, rmax=200, ancho=5)
                C.delfin(cv, 760, 650, 0.5, gt)
            d.lupa(c, 800, 640, 190 * d.ease_out_back(a), dentro, color_borde=CIAN)
        if p > 0.7:
            d.emoji(c, "👑", bx, by - 130, 90)
    elif i == 3:  # plantas sin fotosíntesis
        d.fondo(c, "#0E1730", "#1A2A40")
        d.rect(c, 0, 1450, W, H, "#000000", shader=d.grad_lineal(0, 1450, 0, H, ["#3A2E20", "#1A140C"]))
        marchita = d.ease(d.clamp(p / 0.85))
        verde = d.mezcla("#4CC36A", "#8A6A3A", marchita)
        for k, bx in enumerate((150, 330, 760, 930)):  # plantitas
            alto = 220 - 120 * marchita
            c.drawPath(d.camino([(bx, 1460), (bx + 30 * marchita, 1460 - alto * 0.6), (bx + 70 * marchita, 1460 - alto)], False, True), d.pintura(verde, trazo=14))
            for sx in (-1, 1):
                d.elipse(c, bx + sx * 40 + 40 * marchita, 1460 - alto * 0.6 + 40 * marchita, 40, 18, verde)
        # girasol personaje
        cab = (540 + 160 * marchita, 820 + 420 * marchita)
        c.drawPath(d.camino([(540, 1460), (530, 1150), (540 + 60 * marchita, 1000 + 150 * marchita), cab], False, True), d.pintura(verde, trazo=26))
        for k in range(14):
            ang = math.radians(k * 360 / 14)
            d.elipse(c, cab[0] + 130 * math.cos(ang), cab[1] + 130 * math.sin(ang), 70, 30,
                     d.mezcla("#FFC93C", "#8A6A3A", marchita))
        C.esfera(c, cab[0], cab[1], 95, d.mezcla("#7A4A1A", "#4A2E14", marchita), contorno=None)
        for sx in (-1, 1):
            d.elipse(c, cab[0] + sx * 32, cab[1] - 10, 16, 20, "#FFFFFF")
            d.circulo(c, cab[0] + sx * 32, cab[1] - 4, 8, "#1B1B1B")
        c.drawPath(d.camino([(cab[0] - 30, cab[1] + 45), (cab[0], cab[1] + 30), (cab[0] + 30, cab[1] + 45)], False, True), d.pintura("#1B1B1B", trazo=6))
        # oruguita preocupada
        for k in range(5):
            C.esfera(c, 200 + k * 34, 1440 - 6 * math.sin(gt * 5 + k), 26, "#9BE34A", contorno=None)
        d.elipse(c, 345, 1428, 8, 10, "#FFFFFF")
        d.circulo(c, 346, 1430, 4, "#111111")
        d.etiqueta(c, "SIN FOTOSÍNTESIS", 540, 620, color="#9BE34A", texto_color="#10230F", tam=42, a=d.aparece(lt, dur * 0.4))
    elif i == 4:  # el frío
        frio = d.ease(d.clamp(p / 0.8))
        ciudad_atardecer(c, gt, ventanas=0.0, escarcha=frio, noche=True)
        d.rect(c, 0, 0, W, H, "#7FC4FF", a=int(40 * frio))
        d.nieve(c, gt, n=int(60 + 60 * frio))
        for k, (x, ropa, piel, pelo) in enumerate(GENTE[:2]):
            C.personaje(c, x + 60, 1620, 0.8, gt + k, ropa, piel, pelo, expresion="frio", brazos="abrazo",
                        bufanda=("#E8413C", "#FFC93C")[k], aliento=True, tiembla=frio)
        C.termometro(c, 900, 1420, 0.85, 0.85 - 0.75 * frio, gt)
        d.etiqueta(c, "≈ -70 °C EN UN AÑO", 540, 640, color=CIAN, texto_color="#06223F", tam=40, a=d.aparece(lt, dur * 0.6))
    elif i == 5:  # el mar se congela por arriba
        d.fondo(c, "#070B1E", "#070B1E")
        hielo = d.ease(d.clamp(p / 0.6))
        sup = 900
        d.rect(c, 0, sup, W, H, "#000000", shader=d.grad_lineal(0, sup, 0, H, ["#123A66", "#04101F"]))
        for k in range(5):
            C.pez(c, (k * 260 + gt * 60) % (W + 200) - 100, 1150 + k * 90, 0.9, gt + k, ("#FF8A3C", "#FFC93C", "#FF5FA2", "#20C9C2", "#9BE34A")[k])
        grosor = 40 + 110 * hielo
        d.rect(c, 0, sup - 20, W, sup + grosor, "#CFEFFF", shader=d.grad_lineal(0, sup - 20, 0, sup + grosor, ["#F4FBFF", "#9FD8FF"]))
        for k in range(8):
            d.linea(c, k * 150, sup + 10, k * 150 + 80, sup + grosor - 10, "#FFFFFF", ancho=4, a=120)
        px = d.lerp(-150, W + 150, d.clamp((p - 0.15) / 0.8))
        C.pinguino(c, px, sup - 10, 0.6, gt, rot=-70)
        d.etiqueta(c, "ABAJO: AGUA LÍQUIDA", 540, 1450, color=CIAN, texto_color="#06223F", tam=40, a=d.aparece(lt, dur * 0.55))
    else:  # fiesta en la fuente hidrotermal
        d.fondo(c, "#04101F", "#01060D")
        d.particulas(c, gt, 50, "#9FD8FF", a=50)
        d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#2A2420", "#100C0A"]))
        # chimenea volcánica
        d.figura(c, [(380, 1520), (430, 1150), (470, 1080), (610, 1080), (650, 1150), (700, 1520)], "#3A302A",
                 shader=d.grad_lineal(380, 0, 700, 0, ["#5A4A40", "#2A221C"]))
        d.brillo(c, 540, 1090, 260, "#FF8A3C", 170)
        for k in range(6):
            f = (gt * 0.5 + k / 6) % 1
            d.circulo(c, 540 + 40 * math.sin(f * 7 + k), 1070 - f * 500, 50 + f * 90, "#5A4A44", a=int(150 * (1 - f)), blur=12)
        # gusanos tubícolas bailando
        for k, bx in enumerate((160, 240, 320, 760, 840, 920)):
            alto = 220 + (k % 3) * 40
            ond = 25 * math.sin(gt * 3 + k)
            c.drawPath(d.camino([(bx, 1510), (bx + ond * 0.5, 1510 - alto * 0.5), (bx + ond, 1510 - alto)], False, True), d.pintura("#F4F0EA", trazo=26))
            C.esfera(c, bx + ond, 1510 - alto - 20, 34, "#E8413C", contorno=None)
        # cangrejos blancos
        for k, cx in enumerate((300, 800)):
            sx = cx + 40 * math.sin(gt * 2 + k)
            C.esfera(c, sx, 1480, 48, "#F4F0EA", contorno=None)
            for sd in (-1, 1):
                C.esfera(c, sx + sd * 70, 1440 - 20 * abs(math.sin(gt * 6 + k)), 22, "#F4F0EA", contorno=None)
                d.elipse(c, sx + sd * 16, 1450, 8, 10, "#111111")
        ruleta.globi(c, 540, 600 + 30 * math.sin(gt * 2), 0.8, gt, expresion="susto" if p < 0.5 else "feliz", mira=0.0)
        if p > 0.6:
            s = 1 + 0.08 * math.sin(gt * 6)
            d.emoji(c, "💬", 860, 860, int(150 * s))
