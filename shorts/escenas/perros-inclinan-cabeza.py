"""Escenas ilustradas: ¿Por qué los perros inclinan la cabeza cuando les hablás?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

AMARILLO, CIAN, ROSA = "#FFD400", "#7FE3FF", "#F28CA0"
COLLIE = dict(pelaje="#2B2B31", mancha="#F4F4F4", orejas="#1E1E22")
MARRON = dict(pelaje="#C68642", mancha="#F6DEB8", orejas="#8A5A2B")


# ------------------------------------------------------------------ el perro

def perro(c, x, y, s=1.0, t=0.0, inclina=0.0, pelaje="#C68642", mancha="#F6DEB8", orejas="#8A5A2B", lengua=False, cola=True, mirar=0.0):
    """Perro sentado de frente. (x, y) = piso. s=1 -> ~700 px de alto. inclina = grados de la cabeza."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.elipse(c, 0, 8, 220, 34, "#000000", a=90, blur=18)
    if cola:
        mov = 30 * math.sin(t * 9)
        pth = d.camino([(140, -40), (230, -80), (260 + mov, -170)], cerrado=False, suave=True)
        c.drawPath(pth, d.pintura(pelaje, trazo=40))
    d.figura(c, [(-175, 0), (-190, -130), (-150, -270), (-80, -340), (0, -355), (80, -340), (150, -270), (190, -130), (175, 0)], pelaje,
             shader=d.grad_lineal(-190, 0, 190, 0, [pelaje, d.mezcla(pelaje, "#000000", 0.2)]))
    d.figura(c, [(-80, -330), (0, -350), (80, -330), (95, -200), (0, -110), (-95, -200)], mancha)
    for sx in (-1, 1):  # patas
        d.rect(c, sx * 55 - 36, -170, sx * 55 + 36, -8, pelaje, radio=34)
        d.elipse(c, sx * 55, -14, 46, 26, mancha)
    # cabeza
    c.save()
    c.translate(0, -470)
    c.rotate(inclina)
    for sx in (-1, 1):  # orejas caídas
        c.save()
        c.translate(sx * 150, -70)
        c.rotate(sx * (18 + 0.4 * inclina * sx) + 4 * math.sin(t * 3))
        d.figura(c, [(-55, -30), (55, -30), (65, 120), (0, 175), (-65, 120)], orejas)
        c.restore()
    d.figura(c, [(-170, 40), (-165, -70), (-110, -140), (0, -160), (110, -140), (165, -70), (170, 40), (120, 125), (0, 150), (-120, 125)], pelaje,
             shader=d.grad_radial(-40, -60, 260, [d.mezcla(pelaje, "#ffffff", 0.12), pelaje]))
    d.figura(c, [(-30, -150), (30, -150), (55, 0), (-55, 0)], mancha)
    d.elipse(c, 0, 70, 110, 85, mancha)
    # ojos
    parpadeo = (t % 3.3) > 3.15
    for sx in (-1, 1):
        ex, ey = sx * 68, -20
        if parpadeo:
            c.drawPath(d.camino([(ex - 26, ey), (ex, ey + 12), (ex + 26, ey)], False, True), d.pintura("#1A1A1A", trazo=8))
        else:
            d.circulo(c, ex, ey, 30, "#2A1608")
            d.circulo(c, ex + mirar * 8, ey + 2, 20, "#0E0804")
            d.circulo(c, ex - 9 + mirar * 6, ey - 10, 9, "#FFFFFF")
            d.circulo(c, ex + 8 + mirar * 6, ey + 8, 4, "#FFFFFF", a=200)
        d.elipse(c, ex - sx * 4, ey - 52, 16, 9, d.mezcla(pelaje, "#ffffff", 0.35) if pelaje != COLLIE["pelaje"] else "#C98A4A")
    # nariz y boca
    d.elipse(c, 0, 40, 36, 26, "#1A1A1A")
    d.circulo(c, -10, 32, 8, "#FFFFFF", a=150)
    d.linea(c, 0, 62, 0, 88, "#1A1A1A", ancho=6)
    c.drawPath(d.camino([(-46, 92), (-22, 108), (0, 90), (22, 108), (46, 92)], False, True), d.pintura("#1A1A1A", trazo=6))
    if lengua:
        d.figura(c, [(-24, 100), (24, 100), (22, 150), (0, 165), (-22, 150)], ROSA)
        d.linea(c, 0, 108, 0, 150, "#D86B82", ancho=4)
    c.restore()
    c.restore()


def cabeza_inclinada(lt, inicio, ang, vel=0.5):
    return ang * d.ease_out_back(d.clamp((lt - inicio) / vel))


def globo(c, x, y, txt, tam=50, a=1.0, cola_dx=-1, color="#FFFFFF", texto_color="#111111"):
    if a <= 0:
        return
    s = d.ease_out_back(d.clamp(a))
    w = d.ancho_texto(txt, tam) + 70
    h = tam * 2.0
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.figura(c, [(-w / 2 + 40, h / 2 - 4), (-w / 2 + 40 + cola_dx * 10, h / 2 + 50), (-w / 2 + 100, h / 2 - 4)], color, suave=False)
    d.rect(c, -w / 2, -h / 2, w / 2, h / 2, color, radio=h / 2)
    d.texto(c, txt, 0, tam * 0.36, tam, texto_color, tipo="titulo", sombra=False)
    c.restore()


def pelota(c, x, y, r, t=0.0):
    d.circulo(c, x, y, r, "#C9E64A", shader=d.grad_radial(x - r * 0.3, y - r * 0.3, r * 1.3, ["#E6FF7A", "#9DBF22"]))
    c.drawPath(d.camino([(x - r * 0.95, y - r * 0.2), (x - r * 0.2, y + r * 0.1), (x + r * 0.3, y + r * 0.9)], False, True), d.pintura("#FFFFFF", trazo=r * 0.12))
    c.drawPath(d.camino([(x - r * 0.3, y - r * 0.92), (x + r * 0.25, y - r * 0.2), (x + r * 0.95, y + r * 0.15)], False, True), d.pintura("#FFFFFF", trazo=r * 0.12))


def hueso(c, x, y, s=1.0, rot=0.0, color="#F4E7CF"):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    d.rect(c, -70, -18, 70, 18, color, radio=16)
    for sx in (-1, 1):
        d.circulo(c, sx * 75, -18, 24, color)
        d.circulo(c, sx * 75, 18, 24, color)
    c.restore()


def patito(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.elipse(c, 0, 0, 70, 48, AMARILLO)
    d.circulo(c, 40, -45, 36, AMARILLO)
    d.figura(c, [(70, -50), (100, -40), (70, -32)], "#FF8A3C", suave=False)
    d.circulo(c, 50, -55, 6, "#111111")
    c.restore()


def living(c, t):
    d.fondo(c, "#F6D8B0", "#EBC08E")
    d.rect(c, 620, 560, 960, 960, "#8A5A3C", radio=16)
    d.rect(c, 640, 580, 940, 940, "#BFE6FF", radio=10, shader=d.grad_lineal(0, 580, 0, 940, ["#9FD8FF", "#E6F6FF"]))
    d.nube(c, 760, 700, 0.5)
    d.linea(c, 790, 580, 790, 940, "#8A5A3C", ancho=12)
    d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#B07A50", "#7A4E30"]))
    for k in range(6):
        d.linea(c, 0, 1560 + k * 60, W, 1560 + k * 60, "#6A4028", ancho=3, a=120)
    d.elipse(c, 540, 1720, 460, 110, "#3D7A8C", shader=d.grad_radial(540, 1720, 470, ["#4F98AD", "#2E5F6E"]))


def laboratorio(c, t):
    d.fondo(c, "#E8F1FA", "#C9DCEE")
    for x in range(0, W, 120):
        d.linea(c, x, 500, x, 1500, "#FFFFFF", ancho=3, a=160)
    d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#9AB0C4", "#6A8197"]))


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # le hablás y la inclina
        with d.camara(c, zoom=1.0 + 0.06 * p, cx=540, cy=1300):
            living(c, gt)
            perro(c, 560, 1740, 1.2, gt, inclina=cabeza_inclinada(lt, 1.2, 22), **MARRON)
        globo(c, 330, 690, "¿Quién es un buen perro?", 44, a=d.aparece(lt, 0.2))
        q = d.ease_out_back(d.clamp((lt - 1.8) / 0.4))
        if q > 0:
            d.circulo(c, 880, 900, 80 * q, AMARILLO)
            d.texto(c, "?", 880, 938, int(110 * q), "#111111", tipo="titulo", sombra=False)
    elif i == 1:  # Hungría 2021, perros con muchos juguetes
        laboratorio(c, gt)
        juguetes = [(150, 1560, "p"), (300, 1640, "h"), (820, 1580, "d"), (950, 1660, "p"), (700, 1700, "h"), (420, 1720, "d"), (200, 1760, "h"), (900, 1760, "p")]
        for k, (jx, jy, tipo) in enumerate(juguetes):
            a = d.aparece(lt, 0.3 + k * 0.18, 0.3)
            if a <= 0:
                continue
            yy = jy - 40 * (1 - d.ease_out_back(a))
            if tipo == "p":
                pelota(c, jx, yy, 44, gt)
            elif tipo == "h":
                hueso(c, jx, yy, 0.8, 15 * k)
            else:
                patito(c, jx, yy, 0.7)
        perro(c, 540, 1560, 1.05, gt, inclina=8 * math.sin(gt * 1.5), lengua=True, **COLLIE)
        # bandera de Hungría
        a = d.aparece(lt, 0.4)
        if a > 0:
            for k, colb in enumerate(("#CE2939", "#FFFFFF", "#477050")):
                d.rect(c, 150, 600 + k * 50, 330, 650 + k * 50, colb, a=int(255 * a))
            d.rect(c, 150, 600, 330, 750, "#333333", trazo=4, a=int(255 * a))
        d.etiqueta(c, "2021", 800, 660, color=AMARILLO, tam=56, a=d.aparece(lt, 0.8))
    elif i == 2:  # 43 % vs 2 %
        laboratorio(c, gt)
        perro(c, 300, 1580, 0.75, gt, inclina=cabeza_inclinada(lt, 0.8, -24), **COLLIE)
        perro(c, 790, 1580, 0.75, gt, inclina=0, **MARRON)
        n = d.ease_out((lt - 0.4) / max(0.8, dur * 0.5))
        for (bx, val, colb, etq) in ((300, 43, AMARILLO, "GENIOS"), (790, 2, CIAN, "COMUNES")):
            h = 300 * val / 43 * n
            if h > 4:
                d.rect(c, bx - 90, 880 - h, bx + 90, 880, colb, radio=18)
            d.texto(c, f"{round(val * n)}%", bx, 880 - h - 30, 84, "#1B2A44", tipo="titulo", sombra=False)
            d.etiqueta(c, etq, bx, 935, color="#1B2A44", texto_color="#FFFFFF", tam=40)
    elif i == 3:  # cara de pensar: imagina el juguete
        living(c, gt)
        perro(c, 560, 1740, 1.2, gt, inclina=cabeza_inclinada(lt, 0.6, 20), mirar=0.6, **COLLIE)
        globo(c, 290, 680, "¿Y la pelota?", 50, a=d.aparece(lt, 0.1))
        a = d.aparece(lt, 1.3, 0.5)
        if a > 0:
            for k, (bx, by, r) in enumerate(((760, 1000, 18), (800, 950, 26))):
                d.circulo(c, bx, by, r * a, "#FFFFFF")
            c.save()
            c.translate(860, 820)
            c.scale(d.ease_out_back(a), d.ease_out_back(a))
            for (dx, dy, r) in ((-90, 0, 90), (0, -40, 100), (90, 0, 90), (0, 40, 90)):
                d.circulo(c, dx, dy, r, "#FFFFFF")
            pelota(c, 0, 0, 70 + 6 * math.sin(gt * 4), gt)
            c.restore()
    elif i == 4:  # siempre para el mismo lado
        living(c, gt)
        ang = 20 * d.ease_out_back(d.clamp((lt - 0.5) / 0.5)) * (1 + 0.15 * math.sin(gt * 2))
        perro(c, 290, 1700, 0.8, gt, inclina=ang, **COLLIE)
        perro(c, 790, 1700, 0.8, gt, inclina=-ang, **MARRON)
        for (bx, sx, etq) in ((290, 1, "DERECHA"), (790, -1, "IZQUIERDA")):
            hx, hy = bx, 1700 - 470 * 0.8
            d.flecha(c, hx - sx * 120, hy - 220, hx + sx * 120, hy - 170, AMARILLO, ancho=12, progreso=d.aparece(lt, 0.9, 0.6))
            d.etiqueta(c, etq, bx, 720, color="#1B2A44", texto_color="#FFFFFF", tam=42, a=d.aparece(lt, 1.2))
    elif i == 5:  # otras teorías: oír mejor, ver tu cara, nos encanta
        living(c, gt)
        fase = 0 if p < 0.38 else (1 if p < 0.7 else 2)
        perro(c, 560, 1740, 1.2, gt, inclina=cabeza_inclinada(lt, 0.3, 18 if fase != 1 else -18) if fase == 0 else (-18 if fase == 1 else 18 + 4 * math.sin(gt * 3)),
              lengua=fase == 2, **MARRON)
        if fase == 0:
            d.onda_sonido(c, 330, 1060, gt, CIAN, n=3, r0=40, paso=50, angulo=180, apertura=70, ancho=10)
            d.flecha(c, 120, 900, 300, 1010, CIAN, ancho=10, progreso=d.aparece(lt, 0.5))
            d.etiqueta(c, "OÍR MEJOR", 540, 700, color=CIAN, tam=50, a=d.aparece(lt, 0.4))
        elif fase == 1:
            d.etiqueta(c, "VER TU CARA", 540, 700, color=AMARILLO, tam=50)
            d.emoji(c, "🙂", 880, 880, 150)
        else:
            d.etiqueta(c, "¡NOS ENCANTA!", 540, 700, color=ROSA, tam=50)
            for k in range(5):
                f = (gt * 0.5 + k / 5) % 1
                lado = -1 if k % 2 == 0 else 1
                d.emoji(c, "❤️", 560 + lado * (290 + 30 * k % 60), 1250 - f * 380, 60, a=int(255 * (1 - f)))
    else:  # cierre
        living(c, gt)
        perro(c, 560, 1740, 1.2, gt, inclina=20 * math.sin(gt * 1.6), lengua=True, **COLLIE)
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > 0.6:
            d.emoji(c, "💬", 870, 760, int(160 * s))
