"""Escenas ilustradas: ¿Por qué ronronean los gatos?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

NARANJA, NARANJA_OSC, CREMA, ROSA = "#F2994A", "#C96A1E", "#FFE8C7", "#F7A1B0"


# ------------------------------------------------------------------ el gato

def gato(c, x, y, s=1.0, t=0.0, ojos="abiertos", cuerpo=NARANJA, rayas=NARANJA_OSC, rot=0.0, cola=True, venda=False, mirar=0.0):
    """Gato sentado de frente. (x, y) = base (piso). s=1 -> ~650 px de alto."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.elipse(c, 0, 8, 210, 34, "#000000", a=90, blur=18)
    if cola:
        bal = 25 * math.sin(t * 2.2)
        pth = d.camino([(120, -30), (230, -60), (265 + bal, -170), (225 + bal * 1.6, -270)], cerrado=False, suave=True)
        c.drawPath(pth, d.pintura(rayas, trazo=50))
        c.drawPath(pth, d.pintura(cuerpo, trazo=38))
    # cuerpo
    d.figura(c, [(-170, 0), (-188, -120), (-150, -250), (-95, -330), (0, -352), (95, -330), (150, -250), (188, -120), (170, 0)],
             cuerpo, sombra=0, shader=d.grad_lineal(-190, 0, 190, 0, [cuerpo, d.mezcla(cuerpo, "#000000", 0.18)]))
    for k in range(3):  # rayas del lomo
        yy = -110 - k * 70
        c.drawPath(d.camino([(-180 + k * 8, yy), (-140, yy - 18), (-110, yy - 6)], False, True), d.pintura(rayas, trazo=16))
        c.drawPath(d.camino([(180 - k * 8, yy), (140, yy - 18), (110, yy - 6)], False, True), d.pintura(rayas, trazo=16))
    d.elipse(c, 0, -170, 92, 150, CREMA)
    # patas delanteras
    for sx in (-1, 1):
        d.rect(c, sx * 45 - 32, -150, sx * 45 + 32, -10, cuerpo, radio=30)
        d.elipse(c, sx * 45, -14, 42, 26, CREMA)
        for dx in (-14, 0, 14):
            d.linea(c, sx * 45 + dx, -26, sx * 45 + dx, -6, d.mezcla(CREMA, "#000000", 0.2), ancho=3)
    if venda:
        d.rect(c, 45 - 40, -95, 45 + 40, -55, "#FFFFFF", radio=10)
        d.linea(c, 45 - 30, -75, 45 + 30, -75, "#D9D9D9", ancho=3)
    # cabeza
    c.save()
    c.translate(0, -440)
    c.rotate(rot)
    for sx in (-1, 1):  # orejas
        d.figura(c, [(sx * 165, -40), (sx * 150, -205), (sx * 55, -120)], cuerpo, suave=False)
        d.figura(c, [(sx * 140, -70), (sx * 135, -170), (sx * 80, -118)], ROSA, suave=False)
    d.figura(c, [(-190, 30), (-175, -60), (-110, -125), (0, -145), (110, -125), (175, -60), (190, 30), (140, 105), (0, 140), (-140, 105)],
             cuerpo, shader=d.grad_radial(-40, -60, 260, [d.mezcla(cuerpo, "#ffffff", 0.12), cuerpo]))
    for k, dx in enumerate((-28, 0, 28)):  # rayas de la frente
        c.drawPath(d.camino([(dx, -140), (dx * 1.1, -105), (dx * 0.9, -75)], False, True), d.pintura(rayas, trazo=13))
    for sx in (-1, 1):
        c.drawPath(d.camino([(sx * 188, -5), (sx * 150, 0), (sx * 125, 12)], False, True), d.pintura(rayas, trazo=12))
        c.drawPath(d.camino([(sx * 185, 40), (sx * 150, 40), (sx * 128, 48)], False, True), d.pintura(rayas, trazo=12))
    # hocico
    d.circulo(c, -38, 55, 48, CREMA)
    d.circulo(c, 38, 55, 48, CREMA)
    d.elipse(c, 0, 92, 40, 30, CREMA)
    # ojos
    parpadeo = (t % 3.6) > 3.45
    for sx in (-1, 1):
        ex, ey = sx * 72, -18
        if ojos == "cerrados" or parpadeo:
            c.drawPath(d.camino([(ex - 34, ey + 4), (ex, ey + 22), (ex + 34, ey + 4)], False, True), d.pintura("#3a2412", trazo=9))
        else:
            ry = 30 if ojos == "triste" else 40
            d.elipse(c, ex, ey, 36, ry, "#B8E05A", shader=d.grad_radial(ex, ey, 40, ["#E7FF9A", "#7FB82E"]))
            pup = 24 if ojos == "suplica" else 11
            d.elipse(c, ex + mirar * 10, ey + (6 if ojos == "suplica" else 0), pup, min(ry - 4, 34), "#14110f")
            d.circulo(c, ex - 10 + mirar * 10, ey - 14, 9, "#ffffff")
            d.circulo(c, ex + 9 + mirar * 10, ey + 8, 4, "#ffffff", a=200)
            if ojos == "triste":
                d.linea(c, ex - sx * 40, ey - 58, ex + sx * 32, ey - 44, rayas, ancho=10)
    # nariz y boca
    d.figura(c, [(-17, 28), (17, 28), (0, 46)], "#E86A82", suave=True)
    c.drawPath(d.camino([(-30, 72), (-14, 82), (0, 66), (14, 82), (30, 72)], False, True), d.pintura("#3a2412", trazo=6))
    for sx in (-1, 1):  # bigotes
        for k, dy in enumerate((-6, 12, 30)):
            d.linea(c, sx * 75, 60 + dy * 0.5, sx * 205, 40 + dy * 1.4 + 3 * math.sin(t * 3 + k), "#ffffff", ancho=4, a=230)
    if venda:
        c.save()
        c.rotate(-14)
        d.rect(c, -150, -125, 150, -80, "#FFFFFF", radio=14)
        d.rect(c, 40, -128, 90, -77, "#FFFFFF", radio=8)
        d.linea(c, 65, -115, 65, -90, "#E04848", ancho=8)
        d.linea(c, 52, -102, 78, -102, "#E04848", ancho=8)
        c.restore()
    c.restore()
    c.restore()


def ronroneo(c, x, y, t, color="#FFE7A8", escala=1.0):
    d.onda_sonido(c, x - 40 * escala, y, t, color, n=3, r0=30 * escala, paso=40 * escala, angulo=180, apertura=80, ancho=9 * escala)
    d.onda_sonido(c, x + 40 * escala, y, t, color, n=3, r0=30 * escala, paso=40 * escala, angulo=0, apertura=80, ancho=9 * escala)


# ------------------------------------------------------------------ escenografía

def living(c, t, tono=0.0):
    d.fondo(c, d.mezcla("#3A1F3D", "#203a4a", tono), d.mezcla("#8C4A3C", "#3f6f7a", tono))
    # ventana con noche y luna
    d.rect(c, 640, 560, 960, 980, "#2b1a12", radio=18)
    d.rect(c, 660, 580, 940, 960, "#0b1530", radio=10, shader=d.grad_lineal(0, 580, 0, 960, ["#0b1530", "#28407a"]))
    d.luna(c, 860, 660, 40, "#0f1c3c")
    d.linea(c, 800, 580, 800, 960, "#2b1a12", ancho=14)
    d.linea(c, 660, 770, 940, 770, "#2b1a12", ancho=14)
    # lámpara cálida
    d.brillo(c, 200, 700, 380, "#FFC870", 90)
    # piso de madera
    d.rect(c, 0, 1500, W, H, "#5A3826", shader=d.grad_lineal(0, 1500, 0, H, ["#7A4B30", "#3E2416"]))
    for k in range(7):
        d.linea(c, 0, 1560 + k * 55, W, 1560 + k * 55, "#2F1B10", ancho=3, a=120)
    d.elipse(c, 540, 1720, 470, 120, "#B23A48", shader=d.grad_radial(540, 1720, 480, ["#D9566A", "#8E2A39"]))


def corazones(c, t, x=540, y=1100, n=4):
    for k in range(n):
        f = (t * 0.5 + k / n) % 1
        lado = -1 if k % 2 == 0 else 1
        d.emoji(c, "❤️", x + lado * (250 + 40 * math.sin(k * 2.1)) + lado * 60 * f, y - f * 380, 56 + (12 * k) % 30, a=int(255 * (1 - f)))


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: gato feliz… ¿o no?
        with d.camara(c, zoom=1.0 + 0.06 * p):
            living(c, gt)
            gato(c, 540, 1760, 1.35, gt, ojos="cerrados")
            ronroneo(c, 540, 1300, gt)
            corazones(c, gt)
        s = d.ease_out_back((lt - dur * 0.55) / 0.4)
        if s > 0:
            d.circulo(c, 860, 820, 95 * s, "#FFD400")
            d.texto(c, "?", 860, 860, int(130 * s), "#111111", tipo="titulo", sombra=False)
    elif i == 1:  # la laringe vibra al inhalar y exhalar
        living(c, gt)
        gato(c, 540, 1880, 1.45, gt, ojos="cerrados", rot=-3)
        gx, gy = 540, 1880 - 340 * 1.45
        ronroneo(c, gx, gy, gt, escala=0.8)
        a = d.aparece(lt, 0.3, 0.5)
        lx, ly, r = 600, 760, 225 * a
        if r > 5:
            d.linea(c, gx, gy - 20, lx, ly + r, "#FFFFFF", ancho=6, a=int(220 * a))

            def dentro(cv):
                d.rect(cv, 0, 0, d.W, d.H, "#000", shader=d.grad_radial(lx, ly, 300, ["#F7B6B6", "#B5475C"]))
                d.rect(cv, lx - 70, ly - 260, lx + 70, ly + 260, "#7E2B3F", a=200, radio=40)
                abre = 10 + 26 * abs(math.sin(gt * 22))  # vibración rapidísima
                d.figura(cv, [(lx - 120, ly - 30), (lx - abre, ly - 8), (lx - abre, ly + 8), (lx - 120, ly + 30)], "#FFE1E1", suave=True)
                d.figura(cv, [(lx + 120, ly - 30), (lx + abre, ly - 8), (lx + abre, ly + 8), (lx + 120, ly + 30)], "#FFE1E1", suave=True)
                inhala = (gt % 2.4) < 1.2
                for dx in (-35, 35):
                    if inhala:
                        d.flecha(cv, lx + dx, ly - 210, lx + dx, ly - 70, "#7FD3FF", ancho=12, progreso=(gt % 1.2) / 0.6)
                    else:
                        d.flecha(cv, lx + dx, ly + 210, lx + dx, ly + 70, "#FFD400", ancho=12, progreso=(gt % 1.2) / 0.6)
                d.etiqueta(cv, "INHALA" if inhala else "EXHALA", lx, ly + 190, color="#7FD3FF" if inhala else "#FFD400", tam=38)
            d.lupa(c, lx, ly, r, dentro)
            d.etiqueta(c, "LARINGE", lx - 250, ly - 170, color="#FFFFFF", tam=40, a=d.aparece(lt, 0.8))
    elif i == 2:  # hasta 150 vibraciones por segundo
        d.fondo(c, "#14213D", "#0B0F1E")
        d.particulas(c, gt, 40, "#9FC3FF", a=70)
        x0, y0, x1, y1 = 90, 640, 990, 1060
        d.rect(c, x0, y0, x1, y1, "#04140C", radio=36, shader=d.grad_lineal(0, y0, 0, y1, ["#062417", "#020A06"]))
        for k in range(1, 9):
            d.linea(c, x0 + k * 100, y0 + 20, x0 + k * 100, y1 - 20, "#1D5C3B", ancho=2)
        for k in range(1, 4):
            d.linea(c, x0 + 20, y0 + k * 105, x1 - 20, y0 + k * 105, "#1D5C3B", ancho=2)
        frec = 0.02 + 0.10 * d.ease(p * 1.3)
        pts = [(x, (y0 + y1) / 2 + 120 * math.sin((x - gt * 600) * frec) * (0.6 + 0.4 * math.sin(x * 0.01))) for x in range(x0 + 20, x1 - 20, 4)]
        c.drawPath(d.camino(pts, False, False), d.pintura("#41FF8F", 90, trazo=18, blur=8))
        c.drawPath(d.camino(pts, False, False), d.pintura("#B6FFD2", trazo=6))
        d.rect(c, x0, y0, x1, y1, "#3BE38A", radio=36, trazo=6)
        d.contador(c, 150 * d.ease_out((lt - 0.2) / max(0.5, dur * 0.6)), 540, 1290, tam=170, caja=False)
        d.texto(c, "VECES POR SEGUNDO", 540, 1370, 52, "#FFFFFF", tipo="titulo")
        gato(c, 540, 1900, 0.62, gt, ojos="cerrados")
        ronroneo(c, 540, 1900 - 300 * 0.62, gt, escala=0.6)
    elif i == 3:  # desde bebés
        living(c, gt, tono=0.0)
        gato(c, 540, 1690, 1.15, gt, ojos="cerrados")
        for k, (bx, s, col, rayas) in enumerate(((300, 0.42, "#F7B267", NARANJA_OSC), (540, 0.45, "#E0E0E0", "#9E9E9E"), (780, 0.42, "#5B5B5B", "#2E2E2E"))):
            gato(c, bx, 1860 + 10 * math.sin(gt * 3 + k), s, gt + k, ojos="cerrados", cuerpo=col, rayas=rayas, cola=False)
            ronroneo(c, bx, 1860 - 300 * s, gt + k * 0.3, escala=0.45)
        d.etiqueta(c, "A LOS POCOS DÍAS", 540, 640, color="#FFD400", tam=46, a=d.aparece(lt, 0.4))
        corazones(c, gt, 540, 1150, 3)
    elif i == 4:  # también cuando sufren
        d.fondo(c, "#1D4E5F", "#0E2A35")
        d.rect(c, 0, 1500, W, H, "#A7C4C9", shader=d.grad_lineal(0, 1500, 0, H, ["#C9DEE1", "#7F9FA5"]))
        d.rect(c, 760, 600, 960, 800, "#FFFFFF", radio=24)
        d.rect(c, 835, 625, 885, 775, "#E04848", radio=8)
        d.rect(c, 785, 675, 935, 725, "#E04848", radio=8)
        tiembla = 4 * math.sin(gt * 40) * (1 - d.ease(p * 1.5))
        gato(c, 540 + tiembla, 1780, 1.3, gt, ojos="triste", venda=True, cola=False)
        ronroneo(c, 540, 1780 - 340 * 1.3, gt, color="#BFF3FF", escala=0.9)
        a = d.aparece(lt, dur * 0.45)
        d.etiqueta(c, "SE CALMA", 540, 700, color="#7FE3C4", tam=50, a=a)
    elif i == 5:  # ¿sanador natural?
        d.fondo(c, "#06223F", "#020B18")
        for k in range(0, W, 60):
            d.linea(c, k, 500, k, 1500, "#0F3B66", ancho=2)
        for k in range(500, 1500, 60):
            d.linea(c, 0, k, W, k, "#0F3B66", ancho=2)
        bx, by = 540, 1020
        sana = d.ease((p - 0.15) / 0.7)
        c.save()
        c.translate(bx, by)
        c.rotate(-12)
        d.brillo(c, 0, 0, 420, "#7FD3FF", int(60 + 120 * sana))
        hueso = "#EAF4FF"
        d.rect(c, -300, -45, 300, 45, hueso, radio=40)
        for sx in (-1, 1):
            d.circulo(c, sx * 310, -48, 70, hueso)
            d.circulo(c, sx * 310, 48, 70, hueso)
        grieta = [(-10, -45), (12, -18), (-14, 8), (10, 30), (-4, 45)]
        c.drawPath(d.camino(grieta, False, False), d.pintura("#06223F", int(255 * (1 - sana)), trazo=10))
        c.restore()
        for k in range(3):
            d.onda_sonido(c, 120, by, gt + k * 0.2, "#7FD3FF", n=3, r0=60, paso=70, angulo=0, apertura=60, ancho=10)
            d.onda_sonido(c, 960, by, gt + k * 0.2, "#7FD3FF", n=3, r0=60, paso=70, angulo=180, apertura=60, ancho=10)
        d.etiqueta(c, "25 a 150 Hz", 540, 1330, color="#7FD3FF", tam=50, a=d.aparece(lt, 0.4))
        d.etiqueta(c, "EN ESTUDIO", 540, 1450, color="#FFFFFF", tam=38, a=d.aparece(lt, 1.0))
    elif i == 6:  # te manipulan con un "llanto de bebé"
        d.fondo(c, "#F3E3C3", "#D8B98C")
        for x in range(0, W, 120):
            for y in range(560, 1500, 120):
                d.rect(c, x + 4, y + 4, x + 116, y + 116, "#FFFFFF", a=90, radio=10)
        d.rect(c, 0, 1500, W, H, "#8C5A3C", shader=d.grad_lineal(0, 1500, 0, H, ["#A56C48", "#5E3B25"]))
        gato(c, 430, 1800, 1.15, gt, ojos="suplica", rot=8, mirar=0.6)
        d.elipse(c, 850, 1790, 130, 40, "#2D6CDF")
        d.elipse(c, 850, 1770, 115, 28, "#9EC1FF")
        a = d.aparece(lt, 0.5)
        if a > 0:
            bx, by = 760, 880
            s = d.ease_out_back(a)
            c.save()
            c.translate(bx, by)
            c.scale(s, s)
            d.figura(c, [(-200, -150), (200, -150), (200, 110), (-60, 110), (-140, 200), (-120, 110), (-200, 110)], "#FFFFFF", suave=False, sombra=20)
            d.emoji(c, "👶", -80, -20, 150)
            d.emoji(c, "😭", 90, -20, 120)
            c.restore()
            d.onda_sonido(c, 560, 1250, gt, "#E04848", n=3, r0=30, paso=40, angulo=-40, apertura=70, ancho=10)
        d.etiqueta(c, "LLANTO DE BEBÉ", 760, 1150, color="#E04848", texto_color="#FFFFFF", tam=40, a=d.aparece(lt, 1.0))
    else:  # cierre
        living(c, gt)
        gato(c, 540, 1760, 1.3, gt, ojos="abiertos" if (gt % 2) > 0.6 else "cerrados", mirar=0)
        s = 1 + 0.08 * math.sin(gt * 6)
        d.emoji(c, "💬", 820, 860, int(170 * s))
        for k in range(5):
            f = d.aparece(lt, 0.3 + k * 0.25, 0.3)
            if f > 0:
                d.emoji(c, "🐾", 120 + k * 200, 1450 - (k % 2) * 60, 80, a=int(255 * f), rot=20)
