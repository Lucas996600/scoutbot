"""Escenas ilustradas: ¿Sabías que los perros también sueñan?"""
import importlib.util
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "motor"))
import skia  # noqa: E402
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

_spec = importlib.util.spec_from_file_location("perros_cabeza", os.path.join(AQUI, "perros-inclinan-cabeza.py"))
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)

AMARILLO, CIAN, ROSA, LILA = "#FFD400", "#7FE3FF", "#F28CA0", "#C9B8FF"
MARRON = dict(pelaje="#C68642", mancha="#F6DEB8", orejas="#8A5A2B")
COLLIE = dict(pelaje="#2B2B31", mancha="#F4F4F4", orejas="#1E1E22")
CACHORRO = dict(pelaje="#E9C08A", mancha="#FFF1DC", orejas="#B98A52")
ABUELO = dict(pelaje="#8C8C8C", mancha="#E6E6E6", orejas="#666666")


# ------------------------------------------------------------------ perro de perfil

def perro_lado(c, x, y, s=1.0, t=0.0, pose="duerme", pelaje="#C68642", mancha="#F6DEB8", orejas="#8A5A2B", tiembla=0.0, rem=False, canas=False):
    """Perro de perfil mirando a la derecha. (x, y) = piso. pose: 'duerme' (acostado) o 'corre'."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    corre = pose == "corre"
    d.elipse(c, 0, 6, 240, 26, "#000000", a=80, blur=14)
    by = -170 if corre else -80
    hx, hy = (215, -270) if corre else (225, -95)

    def pata(px, py, ang, largo=150, delante=True):
        c.save()
        c.translate(px, py)
        c.rotate(ang)
        d.rect(c, -24, -10, 24, largo, pelaje if delante else d.mezcla(pelaje, "#000000", 0.18), radio=24)
        d.elipse(c, 6, largo, 34, 20, mancha)
        c.restore()

    tw = tiembla * math.sin(t * 26)
    if corre:
        sw = 38 * math.sin(t * 12)
        pata(-120, by + 30, 25 - sw, 140, False)
        pata(120, by + 30, -20 + sw, 140, False)
    else:
        pata(-150, by + 20, -80 + 8 * tw, 150, False)
        pata(120, by + 30, -95 + 12 * tw, 170, False)
    # cola
    cola = 25 * math.sin(t * (10 if corre else 1.5))
    c.drawPath(d.camino([(-190, by - 20), (-270, by - 60 + cola), (-300, by - 130 + cola)] if corre else
                        [(-200, by), (-280, by + 10), (-300, by - 40 + cola * 0.3)], False, True), d.pintura(pelaje, trazo=34))
    # cuerpo
    resp = 1 + (0 if corre else 0.03 * math.sin(t * 2.2))
    d.elipse(c, 0, by, 210, 85 * resp, pelaje, shader=d.grad_lineal(0, by - 90, 0, by + 90, [d.mezcla(pelaje, "#ffffff", 0.08), d.mezcla(pelaje, "#000000", 0.15)]))
    d.elipse(c, 60, by + 40 * resp, 120, 38, mancha)
    if corre:
        pata(-140, by + 20, -15 + sw, 150)
        pata(140, by + 20, 15 - sw, 150)
    else:
        pata(-110, by + 40, -85 - 10 * tw, 150)
        pata(150, by + 45, -92 - 14 * tw, 180)
    # cabeza
    c.save()
    c.translate(hx, hy)
    c.rotate(8 * math.sin(t * 12) if corre else 3 * math.sin(t * 1.1))
    d.figura(c, [(-70, -30), (-40, -75), (20, -82), (70, -50), (90, 0), (60, 55), (-20, 70), (-75, 30)], pelaje)
    d.elipse(c, 95, 20, 70, 40, mancha)
    d.elipse(c, 160, 8, 18, 14, "#1A1A1A")
    c.drawPath(d.camino([(160, 30), (130, 45), (95, 40)], False, True), d.pintura("#1A1A1A", trazo=5))
    if canas:
        d.elipse(c, 110, 35, 50, 22, "#FFFFFF", a=200)
    # oreja
    c.save()
    c.translate(-20, -55)
    c.rotate(20 + (15 * math.sin(t * 12) if corre else 0))
    d.figura(c, [(-30, -10), (35, -10), (30, 90), (0, 115), (-30, 90)], orejas)
    c.restore()
    # ojo
    if corre:
        d.circulo(c, 40, -20, 15, "#2A1608")
        d.circulo(c, 36, -25, 5, "#FFFFFF")
    else:
        c.drawPath(d.camino([(18, -18), (40, -8), (62, -18)], False, True), d.pintura("#1A1A1A", trazo=6))
        if rem:
            bx = 40 + 12 * math.sin(t * 9) * math.sin(t * 2.3)
            d.circulo(c, bx, -22, 9, d.mezcla(pelaje, "#000000", 0.25))
    c.restore()
    c.restore()


def zzz(c, x, y, t, color="#FFFFFF", tam=56):
    for k in range(3):
        f = (t * 0.45 + k / 3) % 1
        d.texto(c, "z" if k % 2 else "Z", x + 50 * f + 20 * math.sin(f * 6), y - 200 * f, int(tam * (0.6 + 0.6 * f)), color, tipo="titulo",
                a=int(255 * math.sin(math.pi * f)))


def nube_sueno(c, x, y, rx, ry, a, dentro, desde=None):
    """Nube de sueño (recorta su contenido). desde=(x,y) para los globitos que la unen al perro."""
    if a <= 0:
        return
    s = d.ease_out_back(d.clamp(a))
    if desde:
        for k, f in enumerate((0.25, 0.5)):
            d.circulo(c, d.lerp(desde[0], x - rx * 0.6, f), d.lerp(desde[1], y + ry * 0.8, f), (14 + 10 * k) * s, "#FFFFFF", a=230)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pth = skia.Path()
    n = 12
    for k in range(n):
        ang = 2 * math.pi * k / n
        pth.addCircle(rx * 0.85 * math.cos(ang), ry * 0.85 * math.sin(ang), min(rx, ry) * 0.32)
    pth.addOval(skia.Rect.MakeLTRB(-rx * 0.9, -ry * 0.9, rx * 0.9, ry * 0.9))
    c.drawPath(pth, d.pintura("#000000", 70, blur=18))
    c.drawPath(pth, d.pintura("#FFFFFF"))
    c.save()
    clip = skia.Path()
    clip.addOval(skia.Rect.MakeLTRB(-rx * 0.88, -ry * 0.85, rx * 0.88, ry * 0.85))
    c.clipPath(clip, doAntiAlias=True)
    dentro(c)
    c.restore()
    c.restore()


def dormitorio(c, t, luz=0.0):
    d.fondo(c, d.mezcla("#1B2350", "#2E3D7A", luz), d.mezcla("#2B2F5E", "#4A5594", luz))
    d.rect(c, 640, 560, 960, 920, "#121834", radio=16)
    d.rect(c, 656, 576, 944, 904, "#000000", radio=10, shader=d.grad_lineal(0, 576, 0, 904, ["#0B1530", "#24407A"]))
    d.luna(c, 860, 660, 40, "#0F1C3C")
    d.linea(c, 800, 576, 800, 904, "#121834", ancho=12)
    d.rect(c, 0, 1500, W, H, "#000000", shader=d.grad_lineal(0, 1500, 0, H, ["#3A2E52", "#1E1830"]))
    d.brillo(c, 800, 740, 420, "#9FB8FF", 50)


def cama(c, x, y, rx=380, ry=90):
    d.elipse(c, x, y - 10, rx, ry, "#B23A48", shader=d.grad_lineal(0, y - ry, 0, y + ry, ["#D9566A", "#7E2533"]))
    d.elipse(c, x, y - 30, rx * 0.8, ry * 0.55, "#E7B7BE")


def pasto(c, t):
    d.cielo(c, "#7EC8F2", "#D8F1FF")
    d.sol(c, 250, -200, 90, t)
    d.colinas(c, 160, 80, color="#5DBB63", semilla=2)


def cara_duenio(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.circulo(c, 0, 0, 120, "#F2C28B")
    d.figura(c, [(-125, -10), (-110, -90), (-40, -135), (40, -135), (110, -90), (125, -10), (90, -60), (0, -75), (-90, -60)], "#3A2418")
    for sx in (-1, 1):
        d.circulo(c, sx * 42, 0, 13, "#2A1A10")
        d.circulo(c, sx * 42 - 4, -4, 4, "#FFFFFF")
        d.elipse(c, sx * 70, 40, 22, 12, "#F29C9C", a=150)
    c.drawPath(d.camino([(-45, 45), (0, 75), (45, 45)], False, True), d.pintura("#8A3B2E", trazo=8))
    c.restore()


def corazones(c, t, x, y, n=4, ancho=260):
    for k in range(n):
        f = (t * 0.5 + k / n) % 1
        lado = -1 if k % 2 == 0 else 1
        d.emoji(c, "❤️", x + lado * (ancho + 30 * math.sin(k * 2.1)), y - f * 300, 54, a=int(255 * (1 - f)))


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # mueve las patitas dormido
        with d.camara(c, zoom=1.0 + 0.06 * p, cx=540, cy=1350):
            dormitorio(c, gt)
            cama(c, 520, 1470)
            perro_lado(c, 480, 1470, 1.0, gt, "duerme", tiembla=0.9, rem=True, **MARRON)
            zzz(c, 760, 1230, gt)
        for k in range(3):  # marcas de movimiento en las patas
            if (gt * 3 + k) % 1 < 0.5:
                d.linea(c, 700 + k * 22, 1440 + k * 8, 730 + k * 22, 1420 + k * 8, "#FFFFFF", ancho=6, a=200)

        def dentro(cv):
            d.rect(cv, -400, -300, 400, 300, "#BDE6FF")
            pc.pelota(cv, 0, 10 * math.sin(gt * 5), 70, gt)
        nube_sueno(c, 760, 900, 210, 150, d.aparece(lt, dur * 0.45), dentro, desde=(700, 1300))
    elif i == 1:  # fase REM: ojos moviéndose bajo los párpados
        dormitorio(c, gt)
        cama(c, 520, 1500)
        perro_lado(c, 480, 1500, 1.0, gt, "duerme", tiembla=0.2, rem=True, **MARRON)
        ex, ey = 480 + 225 + 40, 1500 - 95 - 18

        def dentro(cv):
            d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(540, 900, 300, ["#D9A066", "#A8692E"]))
            c2x, c2y = 540, 900
            d.elipse(cv, c2x, c2y, 200, 120, "#C68642", shader=d.grad_lineal(0, c2y - 120, 0, c2y + 120, ["#E0A462", "#B8783A"]))
            mover = 70 * math.sin(gt * 9) * math.sin(gt * 2.3)
            d.circulo(cv, c2x + mover, c2y + 5, 72, "#000000", a=45, blur=8)
            d.circulo(cv, c2x + mover - 15, c2y - 20, 34, "#FFFFFF", a=90)
            cv.drawPath(d.camino([(c2x - 190, c2y + 20), (c2x, c2y + 75), (c2x + 190, c2y + 20)], False, True), d.pintura("#3A2210", trazo=14))
            for k in range(-3, 4):
                d.linea(cv, c2x + k * 50, c2y + 60 - abs(k) * 12, c2x + k * 58, c2y + 95 - abs(k) * 12, "#3A2210", ancho=6)
            d.flecha(cv, c2x - 120, c2y - 150, c2x - 220, c2y - 150, AMARILLO, ancho=10, progreso=1)
            d.flecha(cv, c2x + 120, c2y - 150, c2x + 220, c2y - 150, AMARILLO, ancho=10, progreso=1)
        r = 250 * d.aparece(lt, 0.3, 0.5)
        if r > 5:
            d.linea(c, ex, ey, 540, 900 + r, "#FFFFFF", ancho=5)
            d.lupa(c, 540, 900, r, dentro)
        d.etiqueta(c, "FASE REM", 540, 590, color=LILA, tam=50, a=d.aparece(lt, 0.6))
        d.etiqueta(c, "≈ 20 MIN DESPUÉS", 540, 1250, color=AMARILLO, tam=40, a=d.aparece(lt, dur * 0.4))
    elif i == 2:  # cosas de perro: corre, pájaros, pelota
        dormitorio(c, gt)
        cama(c, 520, 1500)
        perro_lado(c, 480, 1500, 1.0, gt, "duerme", tiembla=1.0, rem=True, **MARRON)
        zzz(c, 780, 1260, gt)

        def dentro(cv):
            pasto(cv, gt)
            off = (gt * 260) % 900
            for k in range(3):  # pájaros
                bx, by = 250 - ((gt * 180 + k * 160) % 700) + 400, -120 + 30 * k + 15 * math.sin(gt * 6 + k)
                cv.drawPath(d.camino([(bx - 28, by), (bx - 12, by - 14 + 8 * math.sin(gt * 14)), (bx, by), (bx + 12, by - 14 + 8 * math.sin(gt * 14)), (bx + 28, by)], False, True),
                            d.pintura("#333333", trazo=5))
            pc.pelota(cv, 260, 120 - abs(80 * math.sin(gt * 4)), 40, gt)
            perro_lado(cv, -60, 230, 0.5, gt, "corre", **MARRON)
            del off
        nube_sueno(c, 540, 900, 440, 300, d.aparece(lt, 0.2), dentro, desde=(700, 1320))
        d.etiqueta(c, "COSAS DE PERRO", 540, 1250, color=AMARILLO, tam=44, a=d.aparece(lt, 1.0))
    elif i == 3:  # chicos más seguido, grandes más largo
        dormitorio(c, gt, luz=0.2)
        cama(c, 260, 1500, 200, 60)
        cama(c, 750, 1520, 330, 85)
        perro_lado(c, 240, 1500, 0.45, gt, "duerme", tiembla=0.8, rem=True, **CACHORRO)
        perro_lado(c, 720, 1520, 0.85, gt, "duerme", tiembla=0.4, rem=True, **COLLIE)
        f1 = (gt / 1.6) % 1
        nube_sueno(c, 300, 1180, 110, 75, 1 if f1 < 0.55 else 0, lambda cv: pc.pelota(cv, 0, 0, 34, gt), desde=(290, 1400))
        f2 = d.aparece(lt, 1.0, 0.6)
        nube_sueno(c, 760, 1050, 230, 150, f2, lambda cv: (pasto(cv, gt), perro_lado(cv, 0, 110, 0.32, gt, "corre", **COLLIE)), desde=(800, 1370))
        d.etiqueta(c, "CADA 10 MIN", 270, 700, color=AMARILLO, tam=42, a=d.aparece(lt, 0.4))
        d.etiqueta(c, "CADA 1 HORA", 760, 700, color=CIAN, tam=42, a=d.aparece(lt, dur * 0.4))
        d.etiqueta(c, "MÁS LARGOS", 760, 790, color="#FFFFFF", tam=36, a=d.aparece(lt, dur * 0.65))
    elif i == 4:  # cachorros y abuelos se mueven más
        dormitorio(c, gt, luz=0.15)
        cama(c, 290, 1500, 240, 70)
        cama(c, 790, 1500, 260, 75)
        perro_lado(c, 270, 1500, 0.55, gt, "duerme", tiembla=1.6, rem=True, **CACHORRO)
        perro_lado(c, 770, 1500, 0.62, gt * 0.9, "duerme", tiembla=1.6, rem=True, canas=True, **ABUELO)
        for bx in (330, 840):
            for k in range(3):
                if (gt * 4 + k * 0.3) % 1 < 0.5:
                    d.linea(c, bx + k * 20, 1440 - k * 30, bx + 30 + k * 20, 1420 - k * 30, "#FFFFFF", ancho=6, a=220)
        d.etiqueta(c, "CACHORRO", 280, 1250, color=AMARILLO, tam=42, a=d.aparece(lt, 0.3))
        d.etiqueta(c, "ABUELO", 790, 1250, color="#FFFFFF", tam=42, a=d.aparece(lt, 0.8))
        # cerebro con freno flojo
        a = d.aparece(lt, dur * 0.4, 0.5)
        if a > 0:
            c.save()
            c.translate(540, 820)
            c.scale(d.ease_out_back(a), d.ease_out_back(a))
            for (dx, dy, r) in ((-60, -10, 80), (20, -40, 90), (80, 10, 70), (0, 40, 80)):
                d.circulo(c, dx, dy, r, "#F2A7B8")
            for k in range(4):
                c.drawPath(d.camino([(-90 + k * 50, -60), (-70 + k * 50, -10), (-95 + k * 50, 40)], False, True), d.pintura("#D97A92", trazo=7))
            c.restore()
            d.etiqueta(c, "FRENO FLOJO", 540, 1000, color=ROSA, texto_color="#3A0E1A", tam=40, a=a)
    elif i == 5:  # sueña con vos
        dormitorio(c, gt, luz=0.25)
        cama(c, 520, 1520)
        perro_lado(c, 480, 1520, 1.0, gt, "duerme", tiembla=0.3, rem=True, **MARRON)

        def dentro(cv):
            d.rect(cv, -500, -400, 500, 400, "#FFE7EC")
            cara_duenio(cv, 0, 20 + 8 * math.sin(gt * 2), 1.0)
            for k in range(3):
                d.onda_sonido(cv, -230, 60, gt + k * 0.2, "#C68642", n=2, r0=20, paso=30, angulo=0, apertura=60, ancho=6)
            corazones(cv, gt, 0, 200, 4, 220)
        nube_sueno(c, 540, 930, 420, 300, d.aparece(lt, 0.2), dentro, desde=(700, 1350))
        d.etiqueta(c, "HARVARD", 230, 1270, color="#FFFFFF", tam=38, a=d.aparece(lt, 0.8))
        d.etiqueta(c, "PROBABLEMENTE", 760, 1270, color=ROSA, texto_color="#3A0E1A", tam=38, a=d.aparece(lt, 1.4))
    else:  # cierre
        dormitorio(c, gt)
        cama(c, 520, 1480)
        perro_lado(c, 480, 1480, 1.0, gt, "duerme", tiembla=0.8, rem=True, **COLLIE)
        zzz(c, 760, 1240, gt)
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > 0.6:
            d.emoji(c, "💬", 300, 900, int(160 * s))
