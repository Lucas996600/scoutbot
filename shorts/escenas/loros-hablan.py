"""Escenas ilustradas: ¿Por qué los loros pueden hablar como nosotros?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import skia  # noqa: E402
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import cartoon3d as C  # noqa: E402

AMARILLO, CIAN, ROSA = "#FFD400", "#7FE3FF", "#F28CA0"
VERDE = dict(cuerpo="#3DBE5A", ala="#24863D", cola="#E8413C", frente="#FFD23F")
PERIQUITO = dict(cuerpo="#4FB3F0", ala="#2B6FA8", cola="#2B6FA8", frente="#FFE45C")
GRIS = dict(cuerpo="#9AA3AD", ala="#6E7781", cola="#D6342F", frente="#C2C9D1")


# ------------------------------------------------------------------ el loro

def loro(c, x, y, s=1.0, t=0.0, boca=0.0, mira=0.0, cuerpo="#3DBE5A", ala="#24863D", cola="#E8413C", frente="#FFD23F",
         rot=0.0, aletea=0.0, parpadea=True):
    """Loro de 3/4 mirando a la derecha, parado en (x, y). s=1 -> ~620 px de alto. boca 0..1 abre el pico."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    d.elipse(c, 0, 10, 130, 22, "#000000", a=90, blur=14)
    # cola
    d.figura(c, [(-40, -80), (-120, 160), (-60, 190), (10, -60)], cola, shader=d.grad_lineal(0, -80, 0, 190, [cola, d.mezcla(cola, "#000000", 0.3)]))
    d.figura(c, [(-30, -70), (-70, 150), (-30, 170), (20, -50)], d.mezcla(cola, "#3D5BD9", 0.5))
    # cuerpo
    d.elipse(c, 0, -230, 128, 195, cuerpo, shader=d.grad_radial(-40, -300, 260, [d.mezcla(cuerpo, "#FFFFFF", 0.25), cuerpo, d.mezcla(cuerpo, "#000000", 0.25)]))
    d.elipse(c, 35, -190, 70, 130, d.mezcla(cuerpo, "#FFFFFF", 0.3))
    # ala
    c.save()
    c.translate(-40, -300)
    c.rotate(-10 - 40 * aletea * (0.5 + 0.5 * math.sin(t * 18)))
    d.figura(c, [(0, 0), (60, 20), (70, 140), (20, 260), (-40, 200), (-50, 60)], ala,
             shader=d.grad_lineal(-50, 0, 70, 0, [d.mezcla(ala, "#000000", 0.2), ala]))
    for k in range(4):
        d.linea(c, -30 + k * 18, 120 + k * 25, 10 + k * 14, 240 - k * 10, d.mezcla(ala, "#000000", 0.35), ancho=5)
    c.restore()
    # patas
    for sx in (-1, 1):
        for k in (-1, 1):
            d.elipse(c, sx * 40 + k * 22, -6, 22, 10, "#8A8F98")
        d.rect(c, sx * 40 - 10, -60, sx * 40 + 10, -8, "#8A8F98", radio=8)
    # cabeza
    hx, hy = 30, -460
    C.esfera(c, hx, hy, 118, cuerpo, contorno=None)
    d.elipse(c, hx + 20, hy - 70, 70, 40, frente)
    # ojo con anillo
    parp = parpadea and (t % 3.1) > 2.95
    ex, ey = hx + 48, hy - 20
    d.circulo(c, ex, ey, 34, "#F4F4F4")
    if parp:
        d.linea(c, ex - 22, ey, ex + 22, ey, "#1B1B1B", ancho=6)
    else:
        d.circulo(c, ex + mira * 6, ey, 20, "#E89A2E")
        d.circulo(c, ex + mira * 6, ey, 12, "#111111")
        d.circulo(c, ex - 4 + mira * 6, ey - 6, 5, "#FFFFFF")
    # pico ganchudo que se abre
    bx, by = hx + 95, hy + 5
    ab = 40 * boca
    d.figura(c, [(bx - 40, by + 20 + ab * 0.3), (bx + 45, by + 25 + ab), (bx + 30, by + 60 + ab), (bx - 30, by + 55 + ab * 0.6)], "#3A3A40")
    if boca > 0.1:
        d.elipse(c, bx + 5, by + 35 + ab * 0.5, 28, 10 + ab * 0.3, "#C2566E")  # lengua
    d.figura(c, [(bx - 45, by - 40), (bx + 20, by - 50), (bx + 70, by - 10), (bx + 60, by + 45), (bx + 40, by + 20), (bx - 40, by + 25)],
             "#4A4A52", shader=d.grad_lineal(bx - 45, by - 50, bx + 70, by + 45, ["#6A6A74", "#2E2E34"]))
    c.restore()


def percha(c, x0, x1, y):
    d.rect(c, x0, y - 18, x1, y + 18, "#8C5A34", radio=18, shader=d.grad_lineal(0, y - 18, 0, y + 18, ["#A8723F", "#6A4022"]))


def globo(c, x, y, txt, tam=60, a=1.0, color="#FFFFFF", texto_color="#1B1B1B"):
    if a <= 0:
        return
    s = d.ease_out_back(d.clamp(a))
    w = d.ancho_texto(txt, tam, "titulo") + 80
    h = tam * 1.9
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.figura(c, [(-w / 2 + 30, h / 2 - 4), (-w / 2 - 20, h / 2 + 50), (-w / 2 + 90, h / 2 - 4)], color, suave=False)
    d.rect(c, -w / 2, -h / 2, w / 2, h / 2, color, radio=h / 2)
    d.texto(c, txt, 0, tam * 0.36, tam, texto_color, tipo="titulo", sombra=False)
    c.restore()


def living(c):
    d.fondo(c, "#FDE8C8", "#F3C99A")
    d.rect(c, 640, 560, 960, 920, "#8A5A3C", radio=16)
    d.rect(c, 660, 580, 940, 900, "#BFE6FF", radio=10, shader=d.grad_lineal(0, 580, 0, 900, ["#9FD8FF", "#E6F6FF"]))
    d.linea(c, 800, 580, 800, 900, "#8A5A3C", ancho=12)
    d.rect(c, 0, 1520, W, H, "#000000", shader=d.grad_lineal(0, 1520, 0, H, ["#B07A50", "#7A4E30"]))


def selva(c, t):
    d.fondo(c, "#7FD3A0", "#1F6B45")
    d.rayos_luz(c, t, n=5, a=20)
    for k in range(7):
        lx = (k * 190) % W
        d.figura(c, [(lx, 500), (lx + 140, 560), (lx + 60, 700)], "#2E8A55", a=200)
    d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#2A5A35", "#14301C"]))


# ------------------------------------------------------------------ escenas

def boca_habla(gt, intensidad=1.0):
    return intensidad * max(0.0, math.sin(gt * 14)) if (gt % 1.6) < 1.0 else 0.0


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: dice tu nombre sin cuerdas vocales
        with d.camara(c, zoom=1.0 + 0.06 * p, cx=540, cy=1200):
            living(c)
            percha(c, 200, 880, 1500)
            loro(c, 520, 1490, 1.25, gt, boca=boca_habla(gt), mira=0.4, **VERDE)
        globo(c, 760, 720, "¡HOLA, PEPE!", 64, a=d.aparece(lt, 0.3))
        a = d.aparece(lt, dur * 0.55, 0.4)
        if a > 0:
            d.etiqueta(c, "SIN CUERDAS VOCALES", 540, 1640 - 150, color="#E04848", texto_color="#FFFFFF", tam=40, a=a)
    elif i == 1:  # la siringe
        d.fondo(c, "#E8F4FA", "#BFDCEB")
        loro(c, 360, 1560, 1.2, gt, boca=0.3 * boca_habla(gt), **GRIS)

        def dentro(cv):
            d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(760, 900, 320, ["#FFE2E2", "#E9A2A8"]))
            d.rect(cv, 725, 560, 795, 1000, "#D9727E", radio=30)  # tráquea
            for k in range(8):
                d.rect(cv, 720, 580 + k * 50, 800, 598 + k * 50, "#F2B7BE", radio=8)
            vib = 8 * math.sin(gt * 40)
            for sx in (-1, 1):  # bronquios y siringe
                c_ = [(760, 1000), (760 + sx * 60, 1080), (760 + sx * 140, 1180)]
                cv.drawPath(d.camino(c_, False, True), d.pintura("#D9727E", trazo=50))
            d.elipse(cv, 760, 1010, 70 + vib, 46 - vib * 0.4, "#FFD400")
            d.brillo(cv, 760, 1010, 140, "#FFF1A8", 160)
            d.onda_sonido(cv, 760, 560, gt, "#7A2E3A", n=3, r0=30, paso=40, angulo=-90, apertura=70, ancho=8)
        r = 300 * d.aparece(lt, 0.3, 0.5)
        if r > 5:
            d.linea(c, 470, 1200, 640, 900 + r, "#FFFFFF", ancho=6)
            d.lupa(c, 760, 900, r, dentro)
        d.etiqueta(c, "SIRINGE", 880, 1290, color=AMARILLO, tam=48, a=d.aparece(lt, 0.9))
    elif i == 2:  # la lengua
        d.fondo(c, "#FFF1D6", "#FFD9A8")
        with d.camara(c, zoom=1.0, cx=540, cy=960):
            loro(c, 300, 2450, 2.6, gt, boca=0.6 + 0.4 * abs(math.sin(gt * 8)), mira=0.3, **VERDE)
        for k in range(3):
            d.onda_sonido(c, 900, 1260, gt + k * 0.2, "#E8413C", n=3, r0=40, paso=50, angulo=0, apertura=60, ancho=9)
        d.etiqueta(c, "LENGUA MUSCULOSA", 640, 1500, 760, 1300, color=ROSA, texto_color="#3A0E1A", tam=42, a=d.aparece(lt, 0.6))
    elif i == 3:  # cerebro con capa extra
        d.fondo(c, "#1B1F3A", "#0B0E1E")
        d.particulas(c, gt, 40, "#9FB8FF", a=60)
        loro(c, 330, 1600, 1.15, gt, **GRIS)

        def dentro(cv):
            d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(740, 860, 300, ["#2B2F55", "#11132A"]))
            d.elipse(cv, 740, 870, 230, 170, "#F2B7C9")
            for k in range(6):
                cv.drawPath(d.camino([(560 + k * 70, 760), (600 + k * 70, 860), (570 + k * 70, 960)], False, True), d.pintura("#D98AA3", trazo=8))
            pulso = 0.5 + 0.5 * math.sin(gt * 5)
            for (nx, ny) in ((680, 840), (800, 900)):
                d.circulo(cv, nx, ny, 70, "#7FE3FF", a=int(120 + 100 * pulso), trazo=16)  # capa extra
                d.circulo(cv, nx, ny, 40, "#FF9A3C")  # núcleo
        r = 300 * d.aparece(lt, 0.3, 0.5)
        if r > 5:
            d.linea(c, 400, 1080, 560, 860 + r, "#FFFFFF", ancho=6)
            d.lupa(c, 740, 870, r, dentro, color_borde=CIAN)
        d.etiqueta(c, "CAPA EXTRA", 780, 1280, color=CIAN, texto_color="#06223F", tam=44, a=d.aparece(lt, dur * 0.35))
        d.etiqueta(c, "2015", 230, 640, color=AMARILLO, tam=50, a=d.aparece(lt, 0.6))
    elif i == 4:  # la bandada: en la selva y en tu casa
        cambio = d.ease(d.clamp((p - 0.5) / 0.15))
        if cambio < 1:
            selva(c, gt)
            percha(c, 0, W, 1250)
            for k, (lx, col) in enumerate(((180, VERDE), (420, GRIS), (660, VERDE), (900, VERDE))):
                loro(c, lx, 1240, 0.62, gt + k, boca=boca_habla(gt + k * 0.4, 0.8), mira=0.3, **col)
                if boca_habla(gt + k * 0.4) > 0.3:
                    d.onda_sonido(c, lx + 80, 900, gt + k, "#FFFFFF", n=2, r0=20, paso=30, angulo=-60, apertura=60, ancho=6)
            d.etiqueta(c, "LLAMADOS DE LA BANDADA", 540, 640, color=AMARILLO, tam=40)
        if cambio > 0:
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(W * (1 - cambio), 0, W, H))
            living(c)
            C.personaje(c, 700, 1660, 0.95, gt, ropa="#3D9BFF", expresion="feliz", brazos="adelante")
            loro(c, 300, 1500, 0.9, gt, boca=boca_habla(gt), mira=0.5, **VERDE)
            percha(c, 120, 480, 1505)
            d.etiqueta(c, "¡LA BANDADA SOS VOS!", 540, 640, color=ROSA, texto_color="#3A0E1A", tam=44, a=cambio)
            c.restore()
    elif i == 5:  # Puck, 1.728 palabras
        d.fondo(c, "#2B1B5E", "#140C33")
        palabras = ["¡HOLA!", "¿QUÉ TAL?", "TE QUIERO", "¡CHAU!", "PUCK", "¡BUEN DÍA!", "AGUA", "MAMÁ", "¿Y VOS?"]
        for k, w in enumerate(palabras):
            f = (gt * 0.25 + k / len(palabras)) % 1
            x = 120 + (k * 271) % 840
            y = 1400 - f * 900
            d.texto(c, w, x, y, 46, ("#FFD400", "#7FE3FF", "#F28CA0", "#9BE34A")[k % 4], tipo="titulo", a=int(255 * math.sin(math.pi * f)))
        loro(c, 540, 1560, 1.0, gt, boca=boca_habla(gt * 1.3), mira=0.2, **PERIQUITO)
        percha(c, 300, 780, 1565)
        d.contador(c, 1728 * d.ease_out(d.clamp((lt - 0.3) / max(0.8, dur * 0.6))), 540, 760, tam=150, caja=True)
        d.etiqueta(c, "RÉCORD GUINNESS", 540, 880, color=AMARILLO, tam=40, a=d.aparece(lt, dur * 0.5))
    else:  # cierre
        living(c)
        percha(c, 200, 880, 1500)
        loro(c, 520, 1490, 1.25, gt, boca=boca_habla(gt), mira=0.6, aletea=0.4, **VERDE)
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > 0.5:
            d.emoji(c, "💬", 820, 760, int(170 * s))
