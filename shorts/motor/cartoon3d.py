"""Piezas con look "3D de caricatura" (volumen con luz, sombra, brillo especular y luz de contorno) para la serie
"¿Cómo sería el mundo sin...?". Todo es vectorial con Skia: personajes cabezones, edificios con caras, sol con cara."""
import math

import skia

import dibujo as d
from dibujo import W, H


def esfera(c, x, y, r, color, a=255, contorno="#FFFFFF", luz=(-0.38, -0.42)):
    lx, ly = x + luz[0] * r, y + luz[1] * r
    d.circulo(c, x, y, r, color, a=a, shader=d.grad_radial(lx, ly, r * 1.7, [d.mezcla(color, "#FFFFFF", 0.45), color, d.mezcla(color, "#000000", 0.45)], [0, 0.45, 1]))
    d.elipse(c, lx + r * 0.08, ly + r * 0.05, r * 0.28, r * 0.16, "#FFFFFF", a=int(0.55 * a), blur=max(2, r * 0.06))
    if contorno:
        d.circulo(c, x, y, r - 1, contorno, a=int(0.35 * a), trazo=max(2, r * 0.05))


def sombra(c, x, y, rx, ry=None, a=110):
    d.elipse(c, x, y, rx, ry or rx * 0.22, "#000000", a=a, blur=rx * 0.18)


def personaje(c, x, y, s=1.0, t=0.0, ropa="#E2574C", piel="#F2C28B", pelo="#3A2418", expresion="normal", mira=0.0,
              brazos="abajo", bufanda=None, aliento=False, tiembla=0.0, solo_ojos=False, camina=0.0):
    """Personaje cabezón de caricatura, de frente. (x, y) = pies. s=1 -> ~620 px de alto."""
    c.save()
    jit = tiembla * 6 * math.sin(t * 50)
    paso = math.sin(t * 8) * camina
    c.translate(x + jit, y - abs(paso) * 10)
    c.scale(s, s)
    if solo_ojos:
        for sx in (-1, 1):
            d.elipse(c, sx * 48, -440, 26, 32, "#FFFFFF")
            d.circulo(c, sx * 48 + mira * 8, -436, 12, "#000000")
            d.brillo(c, sx * 48, -440, 50, "#FFFFFF", 60)
        c.restore()
        return
    sombra(c, 0, 6, 150)
    # piernas
    for sx in (-1, 1):
        d.rect(c, sx * 45 - 26, -150 + sx * paso * 12, sx * 45 + 26, -10, "#2F4A7A", radio=24,
               shader=d.grad_lineal(sx * 45 - 26, 0, sx * 45 + 26, 0, ["#3F5F96", "#22365C"]))
        d.elipse(c, sx * 50, -10, 44, 22, "#2A2A2A")
    # cuerpo (cápsula con volumen)
    d.rect(c, -105, -330, 105, -120, ropa, radio=80,
           shader=d.grad_lineal(-105, 0, 105, 0, [d.mezcla(ropa, "#FFFFFF", 0.25), ropa, d.mezcla(ropa, "#000000", 0.35)]))
    # brazos
    for sx in (-1, 1):
        if brazos == "adelante":
            pts = [(sx * 95, -290), (sx * 130, -280), (sx * 160, -300)]
            mano = (sx * 165, -300)
        elif brazos == "abrazo":
            pts = [(sx * 95, -290), (sx * 70, -230), (-sx * 40, -230)]
            mano = (-sx * 40, -230)
        elif brazos == "arriba":
            pts = [(sx * 95, -300), (sx * 150, -380), (sx * 160, -460)]
            mano = (sx * 160, -470)
        else:
            pts = [(sx * 100, -300), (sx * 125, -230), (sx * 120, -170)]
            mano = (sx * 120, -165)
        c.drawPath(d.camino(pts, False, True), d.pintura(d.mezcla(ropa, "#000000", 0.15), trazo=44))
        esfera(c, mano[0], mano[1], 26, piel, contorno=None)
    if bufanda:
        d.rect(c, -90, -345, 90, -300, bufanda, radio=22)
        d.rect(c, 30, -320, 75, -230, bufanda, radio=18)
        for k in range(4):
            d.linea(c, -80 + k * 45, -345, -60 + k * 45, -300, d.mezcla(bufanda, "#FFFFFF", 0.4), ancho=8)
    # cabeza grande
    esfera(c, 0, -450, 125, piel, contorno=None)
    d.figura(c, [(-128, -460), (-118, -540), (-60, -585), (20, -590), (90, -560), (128, -480), (95, -515), (20, -540), (-60, -530)], pelo,
             shader=d.grad_lineal(0, -590, 0, -460, [d.mezcla(pelo, "#FFFFFF", 0.2), pelo]))
    for sx in (-1, 1):
        esfera(c, sx * 125, -440, 26, piel, contorno=None)
    # ojos
    for sx in (-1, 1):
        ex, ey = sx * 48, -440
        alto = 40 if expresion == "susto" else 32
        d.elipse(c, ex, ey, 27, alto, "#FFFFFF")
        if expresion == "feliz":
            c.drawPath(d.camino([(ex - 18, ey + 6), (ex, ey - 12), (ex + 18, ey + 6)], False, True), d.pintura("#1B1B1B", trazo=7))
        else:
            d.circulo(c, ex + mira * 9, ey + 4, 14, "#2B1A10")
            d.circulo(c, ex + mira * 9 - 5, ey - 2, 5, "#FFFFFF")
        if expresion in ("frio", "triste"):
            d.linea(c, ex - sx * 26, ey - 52, ex + sx * 20, ey - 40, "#3A2418", ancho=8)
    # boca
    if expresion == "susto":
        d.elipse(c, 0, -365, 26, 32, "#5A1028")
    elif expresion == "frio":
        d.rect(c, -40, -380, 40, -352, "#FFFFFF", radio=8)
        for k in range(5):
            d.linea(c, -32 + k * 16, -380, -32 + k * 16, -352, "#BBBBBB", ancho=2)
    elif expresion == "feliz":
        c.drawPath(d.camino([(-38, -385), (0, -355), (38, -385)], False, True), d.pintura("#5A1028", trazo=9))
    else:
        c.drawPath(d.camino([(-24, -372), (0, -365), (24, -372)], False, True), d.pintura("#5A1028", trazo=7))
    d.elipse(c, -80, -395, 20, 11, "#FF8A8A", a=110)
    d.elipse(c, 80, -395, 20, 11, "#FF8A8A", a=110)
    if aliento:
        f = (t * 0.8) % 1
        d.circulo(c, 40 + 60 * f, -360 - 40 * f, 20 + 30 * f, "#FFFFFF", a=int(150 * (1 - f)), blur=6)
    c.restore()


def edificio(c, x, y, w, h, color="#5B7BD6", prof=60, ventanas=1.0, techo=None, t=0.0, escarcha=0.0, semilla=0):
    """Edificio con frente, costado y techo. (x, y) = esquina inferior izquierda del frente."""
    lado = d.mezcla(color, "#000000", 0.35)
    tope = d.mezcla(color, "#FFFFFF", 0.25) if techo is None else techo
    d.figura(c, [(x + w, y), (x + w + prof, y - prof * 0.6), (x + w + prof, y - h - prof * 0.6), (x + w, y - h)], lado, suave=False)
    d.figura(c, [(x, y - h), (x + prof, y - h - prof * 0.6), (x + w + prof, y - h - prof * 0.6), (x + w, y - h)], tope, suave=False)
    d.rect(c, x, y - h, x + w, y, color, shader=d.grad_lineal(x, 0, x + w, 0, [d.mezcla(color, "#FFFFFF", 0.15), color]))
    filas, cols = int((h - 60) / 90), max(1, int((w - 30) / 70))
    for fy in range(filas):
        for fx in range(cols):
            wx, wy = x + 28 + fx * 70, y - h + 40 + fy * 90
            k = (fx * 7 + fy * 13 + semilla) % 10 / 10
            on = k < ventanas
            if on:
                d.rect(c, wx - 6, wy - 6, wx + 46, wy + 62, "#FFD27A", a=50, radio=10)
                d.rect(c, wx, wy, wx + 40, wy + 56, "#FFE6A3", radio=8, shader=d.grad_lineal(0, wy, 0, wy + 56, ["#FFF4CF", "#FFC860"]))
            else:
                d.rect(c, wx, wy, wx + 40, wy + 56, d.mezcla(color, "#000000", 0.55), radio=8)
            if escarcha > 0:
                d.rect(c, wx, wy, wx + 40, wy + 56, "#E8F6FF", a=int(170 * escarcha), radio=8)
    if escarcha > 0:  # nieve en el techo y carámbanos
        d.figura(c, [(x - 6, y - h + 4), (x + prof, y - h - prof * 0.6 - 10), (x + w + prof + 6, y - h - prof * 0.6 - 10), (x + w + 6, y - h + 4)],
                 "#F4FBFF", a=int(255 * escarcha), suave=True)
        for k in range(int(w / 40)):
            lx = x + 15 + k * 40
            largo = (20 + (k * 37) % 50) * escarcha
            d.figura(c, [(lx - 9, y - h), (lx + 9, y - h), (lx, y - h + largo)], "#CFEFFF", a=int(230 * escarcha), suave=False)


def sol_cara(c, x, y, r, t, prendido=1.0):
    if prendido <= 0:
        return
    a = int(255 * prendido)
    d.brillo(c, x, y, r * 2.6, "#FFD54A", int(120 * prendido))
    for k in range(12):
        ang = math.radians(k * 30 + t * 20)
        d.figura(c, [(x + math.cos(ang - 0.12) * r * 1.05, y + math.sin(ang - 0.12) * r * 1.05),
                     (x + math.cos(ang) * r * 1.5, y + math.sin(ang) * r * 1.5),
                     (x + math.cos(ang + 0.12) * r * 1.05, y + math.sin(ang + 0.12) * r * 1.05)], "#FFB830", a=a, suave=False)
    esfera(c, x, y, r, "#FFC93C", a=a, contorno="#FFF6C8")
    for sx in (-1, 1):
        d.elipse(c, x + sx * r * 0.32, y - r * 0.1, r * 0.11, r * 0.16, "#5A3A08", a=a)
    c.drawPath(d.camino([(x - r * 0.35, y + r * 0.25), (x, y + r * 0.5), (x + r * 0.35, y + r * 0.25)], False, True), d.pintura("#5A3A08", a, trazo=r * 0.08))
    d.elipse(c, x - r * 0.55, y + r * 0.22, r * 0.15, r * 0.08, "#FF7A5A", a=int(a * 0.6))
    d.elipse(c, x + r * 0.55, y + r * 0.22, r * 0.15, r * 0.08, "#FF7A5A", a=int(a * 0.6))


def murcielago(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    aleteo = math.sin(t * 14)
    for sx in (-1, 1):
        d.figura(c, [(sx * 40, -10), (sx * 200, -90 - 60 * aleteo), (sx * 230, 20 - 30 * aleteo), (sx * 170, 0), (sx * 130, 40), (sx * 80, 20)],
                 "#4B2A7A", shader=d.grad_lineal(0, -100, 0, 50, ["#6E44B0", "#2E1450"]))
    esfera(c, 0, 0, 70, "#5B3596", contorno="#C9A6FF")
    for sx in (-1, 1):
        d.figura(c, [(sx * 25, -55), (sx * 55, -120), (sx * 60, -45)], "#5B3596", suave=False)
        d.elipse(c, sx * 26, -8, 18, 22, "#FFFFFF")
        d.circulo(c, sx * 26 + 4, -4, 10, "#1B0B30")
        d.circulo(c, sx * 26, -10, 4, "#FFFFFF")
    c.drawPath(d.camino([(-20, 30), (0, 42), (20, 30)], False, True), d.pintura("#1B0B30", trazo=5))
    d.figura(c, [(-12, 34), (-6, 34), (-9, 46)], "#FFFFFF", suave=False)
    d.figura(c, [(6, 34), (12, 34), (9, 46)], "#FFFFFF", suave=False)
    c.restore()


def delfin(c, x, y, s, t, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot + 5 * math.sin(t * 3))
    c.scale(s, s)
    cola = 20 * math.sin(t * 6)
    d.figura(c, [(-230, -10), (-300, -70 + cola), (-270, 0), (-300, 60 + cola)], "#4F86B8", suave=False)
    d.figura(c, [(260, 10), (200, -50), (60, -90), (-120, -70), (-240, -10), (-120, 50), (80, 60), (220, 40)], "#6FA6D8",
             shader=d.grad_lineal(0, -90, 0, 60, ["#8FC2EE", "#5B8FC2", "#DDEBF7"], [0, 0.6, 1]))
    d.figura(c, [(-20, -80), (20, -150), (60, -82)], "#4F86B8", suave=False)
    d.elipse(c, 150, -20, 16, 18, "#FFFFFF")
    d.circulo(c, 154, -18, 9, "#14202E")
    c.drawPath(d.camino([(250, 25), (210, 35), (170, 25)], False, True), d.pintura("#2D4E70", trazo=5))
    c.restore()


def termometro(c, x, y, s, nivel, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -50, -520, 50, 0, "#F4F8FF", radio=50, shader=d.grad_lineal(-50, 0, 50, 0, ["#FFFFFF", "#C9D6E6"]))
    esfera(c, 0, 20, 85, "#E8F1FF", contorno=None)
    esfera(c, 0, 20, 62, "#3D9BFF" if nivel < 0.4 else "#E8413C", contorno=None)
    d.rect(c, -20, -480 + 440 * (1 - nivel), 20, 10, "#3D9BFF" if nivel < 0.4 else "#E8413C", radio=20)
    for k in range(8):
        d.linea(c, 25, -460 + k * 55, 45, -460 + k * 55, "#8892A6", ancho=4)
    for sx in (-1, 1):  # carita asustada
        d.elipse(c, sx * 22, -560, 16, 20, "#FFFFFF")
        d.circulo(c, sx * 22, -556, 8, "#1B1B1B")
    d.rect(c, -60, -620, 60, -510, "#F4F8FF", a=0)
    d.elipse(c, 0, -525, 12, 15, "#5A1028")
    c.restore()


def pinguino(c, x, y, s, t, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    sombra(c, 0, 0, 110)
    d.elipse(c, 0, -150, 100, 150, "#1E2433", shader=d.grad_lineal(-100, 0, 100, 0, ["#3A4560", "#151A26"]))
    d.elipse(c, 0, -130, 70, 120, "#F4F6FA")
    esfera(c, 0, -300, 75, "#1E2433", contorno="#8FA4C8")
    d.elipse(c, 0, -285, 52, 45, "#F4F6FA")
    for sx in (-1, 1):
        d.elipse(c, sx * 22, -300, 14, 18, "#FFFFFF")
        d.circulo(c, sx * 22, -296, 8, "#111111")
        d.figura(c, [(sx * 95, -200), (sx * 150, -120 + 20 * math.sin(t * 10)), (sx * 90, -110)], "#1E2433", suave=True)
        d.elipse(c, sx * 40, -2, 36, 14, "#FF9A3C")
    d.figura(c, [(-20, -275), (20, -275), (0, -248)], "#FF9A3C", suave=False)
    c.restore()


def pez(c, x, y, s, t, color="#FF8A3C", a=255):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = 15 * math.sin(t * 8)
    d.figura(c, [(-50, 0), (-90, -35 + w), (-90, 35 + w)], d.mezcla(color, "#000000", 0.2), a=a, suave=False)
    d.elipse(c, 0, 0, 60, 38, color, a=a, shader=d.grad_lineal(0, -38, 0, 38, [d.col(d.mezcla(color, "#FFFFFF", 0.3), a), d.col(color, a), d.col(d.mezcla(color, "#000000", 0.3), a)]))
    d.elipse(c, 28, -6, 12, 14, "#FFFFFF", a=a)
    d.circulo(c, 31, -4, 6, "#111111", a=a)
    c.restore()
