"""Escenas ilustradas: ¿Por qué el dorado salta cuando lo pescás?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

ORO, ORO_OSC, ORO_CLARO, ROJO = "#F2B32A", "#A86A0C", "#FFE7A3", "#E8452C"
AGUA_Y = 1150


# ------------------------------------------------------------------ el dorado

def a_mundo(x, y, s, rot, lx, ly):
    r = math.radians(rot)
    return x + (lx * math.cos(r) - ly * math.sin(r)) * s, y + (lx * math.sin(r) + ly * math.cos(r)) * s


def dorado(c, x, y, s=1.0, rot=0.0, t=0.0, abre=0.0, dientes=False, anzuelo=False, ojo_mira=0.0):
    """Dorado de perfil mirando a la derecha, centrado en (x, y). s=1 -> ~800 px de punta a cola."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    w = 30 * math.sin(t * 9)
    # cola roja con banda negra
    d.figura(c, [(-270, -24), (-420, -150 + w), (-372, w * 0.6), (-420, 150 + w), (-270, 24)], ROJO, suave=False)
    d.figura(c, [(-280, -10), (-395, -8 + w * 0.6), (-395, 12 + w * 0.6), (-280, 10)], "#1A1208", suave=False)
    # aletas
    d.figura(c, [(-30, -112), (30, -190), (95, -108)], "#F08A2A", suave=False)
    d.figura(c, [(-150, 88), (-100, 150), (-40, 96)], "#F08A2A", suave=False)
    d.figura(c, [(-235, -50), (-215, -95), (-185, -62)], "#F08A2A", suave=False)
    # boca abierta (interior)
    if abre > 0:
        d.figura(c, [(305, 2), (195, 22), (300, 30 + 60 * abre)], "#5A1414", suave=False)
    # cuerpo
    cuerpo = [(305, 0), (275, -42), (185, -98), (40, -122), (-100, -102), (-225, -58), (-290, -22),
              (-290, 22), (-225, 52), (-100, 88), (40, 104), (185, 84), (270, 46)]
    if abre > 0:
        cuerpo[-1] = (270, 46 + 50 * abre)
        cuerpo[0] = (305, -4)
    d.figura(c, cuerpo, ORO, sombra=0, shader=d.grad_lineal(0, -122, 0, 104, [ORO_OSC, ORO, ORO_CLARO], [0, 0.45, 1]))
    # rayitas negras (escamas)
    for fila in range(-75, 80, 24):
        for xx in range(-235, 175, 22):
            if (xx / 270) ** 2 + (fila / 100) ** 2 < 0.62:
                d.linea(c, xx, fila, xx + 10, fila + 3, "#3A2408", ancho=4, a=150)
    # opérculo y ojo
    c.drawPath(d.camino([(175, -85), (150, -20), (160, 50), (185, 78)], False, True), d.pintura(ORO_OSC, trazo=7))
    d.circulo(c, 228, -36, 25, "#FFF6CC")
    d.circulo(c, 228 + 5 * ojo_mira, -36, 13, "#111111")
    d.circulo(c, 222, -42, 5, "#FFFFFF")
    # boca
    if abre > 0:
        if dientes:
            for k in range(6):
                bx = 290 - k * 17
                d.figura(c, [(bx - 7, 4 + k * 3), (bx + 7, 4 + k * 3), (bx, 22 + k * 3)], "#FFFFFF", suave=False)
                lx, ly = bx - 4, 30 + 60 * abre - k * (6 + 8 * abre)
                d.figura(c, [(lx - 7, ly), (lx + 7, ly), (lx, ly - 18)], "#FFFFFF", suave=False)
    else:
        d.linea(c, 300, 12, 238, 26, "#5A3008", ancho=6)
    if anzuelo:
        anzuelo_dibujo(c, 296, 16, 0.9)
    c.restore()


def anzuelo_dibujo(c, x, y, s=1.0, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    pth = d.camino([(0, -60), (0, 10), (-8, 36), (-30, 44), (-46, 30), (-46, 12)], False, True)
    c.drawPath(pth, d.pintura("#5C6670", trazo=11))
    c.drawPath(pth, d.pintura("#DCE3EA", trazo=6))
    d.figura(c, [(-46, 8), (-56, 26), (-40, 22)], "#DCE3EA", suave=False)
    d.circulo(c, 0, -62, 8, "#DCE3EA", trazo=4)
    c.restore()


def sabalo(c, x, y, s=0.3, t=0.0, a=255):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = 18 * math.sin(t * 12)
    d.figura(c, [(-200, 0), (-290, -80 + w), (-270, w), (-290, 80 + w)], "#9FB3C2", a=a, suave=False)
    d.elipse(c, 0, 0, 230, 90, "#C9D6E0", a=a, shader=d.grad_lineal(0, -90, 0, 90, [d.col("#8FA4B5", a), d.col("#EEF4F8", a)]))
    d.circulo(c, 150, -15, 16, "#111111", a=a)
    c.restore()


# ------------------------------------------------------------------ escenografía

def rio_atardecer(c, t, agua_y=AGUA_Y):
    d.fondo(c, "#3B2A6B", "#FF9A5A")
    d.rect(c, 0, 0, W, agua_y, "#000000", shader=d.grad_lineal(0, 0, 0, agua_y, ["#2E2463", "#B5577A", "#FFB067"], ))
    d.sol(c, 790, agua_y - 120, 110, t, color="#FFD27A", rayos=False)
    d.brillo(c, 790, agua_y - 120, 380, "#FFC870", 110)
    d.nubes(c, t, filas=((560, 0.7, 12), (760, 0.5, 8)), a=110)
    d.colinas(c, agua_y + 10, 70, color="#2C3B2A", semilla=3)
    for k in range(9):
        d.pino(c, 40 + k * 130 + (k % 2) * 40, agua_y + 5, 120 + (k % 3) * 30, color="#1E2C1E")
    d.agua(c, agua_y, t, arriba="#C9726A", abajo="#1B2A44")
    for k in range(6):  # reflejo del sol
        yy = agua_y + 40 + k * 40
        d.rect(c, 790 - 120 + k * 12, yy, 790 + 120 - k * 12, yy + 10, "#FFD27A", a=150 - k * 22, radio=5)


def bajo_agua(c, t):
    d.fondo(c, "#2B8A8A", "#06283A")
    d.rayos_luz(c, t, n=6, a=20)
    d.rect(c, 0, 1560, W, H, "#000000", shader=d.grad_lineal(0, 1560, 0, H, ["#8C7A4E", "#4A3C22"]))
    for k in range(7):
        bx = 60 + k * 170
        c.drawPath(d.camino([(bx, 1600), (bx + 20 * math.sin(t * 1.5 + k), 1470), (bx - 15, 1360 + (k % 3) * 40)], False, True),
                   d.pintura("#2E7A4A", trazo=16))
    d.burbujas(c, t, n=25, y_min=450)


def bote(c, x, y, t, tension=0.0):
    """Bote con pescador. Devuelve la punta de la caña."""
    bal = 4 * math.sin(t * 1.8)
    c.save()
    c.translate(x, y + bal)
    c.rotate(bal * 0.4)
    # pescador
    d.rect(c, -40, -230, 40, -80, "#2F6B4F", radio=26)
    d.circulo(c, 0, -280, 46, "#F2C28B")
    d.rect(c, -62, -322, 62, -300, "#E8E0C8", radio=10)
    d.figura(c, [(-45, -300), (-40, -350), (40, -350), (45, -300)], "#E8E0C8")
    d.rect(c, 10, -200, 110, -170, "#2F6B4F", radio=15)
    d.circulo(c, 115, -185, 18, "#F2C28B")
    # bote
    d.figura(c, [(-230, -90), (230, -90), (180, 20), (-180, 20)], "#8C4A2A", suave=False,
             shader=d.grad_lineal(0, -90, 0, 20, ["#B0663A", "#6A3518"]))
    d.rect(c, -230, -100, 230, -84, "#5A2C14", radio=6)
    c.restore()
    # caña (curvada según la tensión)
    hx, hy = x + 115, y + bal - 185
    tx, ty = hx + 300, hy - 330 + 120 * tension
    mx, my = hx + 170 + 40 * tension, hy - 230 + 40 * tension
    c.drawPath(d.camino([(hx - 40, hy + 40), (mx, my), (tx, ty)], False, True), d.pintura("#2B2B2B", trazo=9))
    return tx, ty


def tanza(c, x0, y0, x1, y1, a=230):
    mx, my = (x0 + x1) / 2, max(y0, y1) + 20
    c.drawPath(d.camino([(x0, y0), (mx, my), (x1, y1)], False, True), d.pintura("#FFFFFF", a, trazo=3))


def salpicadura(c, x, y, edad, fuerza=1.0):
    """Gotas que salen de (x, y) durante ~1 s después del salto."""
    if edad < 0 or edad > 1.2:
        return
    for k in range(18):
        ang = math.radians(-160 + k * 140 / 17)
        v = (380 + (k * 53) % 220) * fuerza
        gx = x + math.cos(ang) * v * edad
        gy = y + math.sin(ang) * v * edad + 900 * edad * edad
        if gy < y + 20:
            d.circulo(c, gx, gy, 9 + (k % 3) * 4, "#E8F6FF", a=int(230 * (1 - edad / 1.2)))
    for k in range(2):
        r = 60 + edad * 260 + k * 60
        d.elipse(c, x, y + 10, r, r * 0.18, "#FFFFFF", a=int(200 * (1 - edad / 1.2)), trazo=5)


def salto(c, lt, dur, gt, x0, x1, pico, sacude=True, anzuelo=True, s=0.55):
    """Dorado saltando en arco de x0 a x1. Devuelve la posición de la boca."""
    f = d.clamp(lt / dur)
    x = d.lerp(x0, x1, f)
    y = AGUA_Y + 60 - (AGUA_Y + 60 - pico) * math.sin(math.pi * f)
    dy = -(AGUA_Y + 60 - pico) * math.pi * math.cos(math.pi * f) / (x1 - x0)
    rot = math.degrees(math.atan(dy)) + (9 * math.sin(gt * 16) if sacude else 0)
    salpicadura(c, x0 + 60, AGUA_Y, lt - 0.05)
    if f > 0.85:
        salpicadura(c, x1 - 40, AGUA_Y, (f - 0.85) * dur)
    for k in range(4):  # gotas que caen del pez
        ff = (gt * 2 + k / 4) % 1
        d.circulo(c, x - 120 + k * 50, y + 60 + ff * 160, 8, "#E8F6FF", a=int(200 * (1 - ff)))
    dorado(c, x, y, s, rot, gt, abre=0.3 if sacude else 0, anzuelo=anzuelo)
    return a_mundo(x, y, s, rot, 296, -40)


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: sale volando del agua
        with d.camara(c, zoom=1.04 - 0.04 * p, cx=540, cy=1000):
            rio_atardecer(c, gt)
            tip = bote(c, 230, 1260, gt, tension=0.8)
            boca = salto(c, lt, dur * 0.95, gt, 520, 960, 640)
            tanza(c, tip[0], tip[1], boca[0], boca[1])
    elif i == 1:  # el tigre del río
        bajo_agua(c, gt)
        for k in range(7):  # cardumen lejano
            sabalo(c, (900 - (gt * 60 + k * 140) % 1300) + 200, 760 + (k % 3) * 70, 0.18, gt + k, a=140)
        nado = 520 + 30 * math.sin(gt * 1.2)
        dorado(c, nado, 1150, 0.95, 3 * math.sin(gt * 1.5), gt, abre=0.15)
        d.etiqueta(c, "TIGRE DEL RÍO", 540, 640, color="#FFD400", tam=52, a=d.aparece(lt, 0.4))
        for k, rio in enumerate(("PARANÁ", "URUGUAY", "RÍO DE LA PLATA")):
            d.etiqueta(c, rio, (220, 540, 860)[k] if k < 2 else 540, 1420 if k < 2 else 1500, color="#FFFFFF", tam=38, a=d.aparece(lt, 1.6 + k * 0.6))
    elif i == 2:  # más de un metro y veinte kilos, persigue sábalos
        bajo_agua(c, gt)
        huye = d.ease((p - 0.45) / 0.55)
        for k in range(9):
            sx = 700 + (k % 3) * 110 + huye * 500
            sy = 720 + (k // 3) * 80 + 20 * math.sin(gt * 3 + k)
            sabalo(c, sx, sy, 0.22, gt * 2 + k)
        dx = 520 + huye * 220
        dorado(c, dx, 1110, 0.9, 0, gt, abre=0.2 * huye)
        regla = d.aparece(lt, 0.3, 0.5)
        if regla > 0 and huye < 0.4:
            a = int(255 * regla * (1 - huye / 0.4))
            x0, x1, y = dx - 380 * 0.9, dx + 305 * 0.9, 1290
            d.rect(c, x0 - 20, y, x1 + 20, y + 70, "#FFD400", a=a, radio=10)
            for k in range(0, 21):
                xx = d.lerp(x0, x1, k / 20)
                d.linea(c, xx, y, xx, y + (34 if k % 5 == 0 else 18), "#111111", ancho=4, a=a)
            d.texto(c, "+1 METRO", (x0 + x1) / 2, y + 60, 34, "#111111", tipo="titulo", sombra=False, a=a)
        if p < 0.5:
            d.contador(c, 20 * d.ease_out((lt - 0.8) / 1.2), 540, 1470, tam=110, sufijo=" KG", caja=True)
    elif i == 3:  # salta y sacude la cabeza para soltarse
        with d.camara(c, zoom=1.12, cx=700, cy=900):
            rio_atardecer(c, gt)
            tip = bote(c, 180, 1260, gt, tension=1.0)
            boca = salto(c, lt, dur * 0.95, gt, 540, 900, 700)
            tanza(c, tip[0], tip[1], boca[0], boca[1])
        if 0.15 < p < 0.85:
            for k in range(3):  # marcas de sacudida
                d.linea(c, 960 + k * 26, 640 + k * 22, 1000 + k * 26, 600 + k * 22, "#FFFFFF", ancho=7, a=200)
        d.etiqueta(c, "SACUDE LA CABEZA", 540, 1430, color="#FFD400", tam=44, a=d.aparece(lt, 0.8))
    elif i == 4:  # boca casi de hueso
        bajo_agua(c, gt)
        dorado(c, 380, 1150, 0.9, -4, gt, abre=0.2, anzuelo=False)

        def dentro(cv):
            d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(720, 860, 300, ["#2B8A8A", "#0B3A4A"]))
            dorado(cv, 300, 980, 2.3, -4, gt, abre=0.25)
            zafa = (gt * 0.8) % 1
            d.anillos(cv, 960, 830, gt, "#FFFFFF", n=2, rmax=90, ancho=5)
            anzuelo_dibujo(cv, 975 + 40 * d.ease(zafa), 825 - 60 * d.ease(zafa), 1.8, rot=-25 * d.ease(zafa))
        r = 270 * d.aparece(lt, 0.3, 0.5)
        if r > 5:
            d.linea(c, 650, 1110, 720, 860 + r, "#FFFFFF", ancho=6)
            d.lupa(c, 720, 860, r, dentro)
        d.etiqueta(c, "BOCA DURA", 300, 1430, color="#FFD400", tam=46, a=d.aparece(lt, 0.9))
        d.etiqueta(c, "SE ZAFA", 820, 1430, color="#FFFFFF", tam=46, a=d.aparece(lt, 1.8))
    elif i == 5:  # dientes que cortan la tanza → cable de acero
        bajo_agua(c, gt)
        corte = d.clamp((p - 0.35) / 0.12)
        dorado(c, 180, 1050, 2.2, 0, gt, abre=0.55 + 0.1 * math.sin(gt * 6), dientes=True)
        bx, by = 180 + 280 * 2.2, 1050 + 40 * 2.2
        if corte < 1:
            d.linea(c, bx - 40, by - 30, 1100, 560, "#FFFFFF", ancho=5)
        else:
            k = d.ease_out((p - 0.47) / 0.3)
            d.linea(c, 1100, 560 - 200 * k, 900 + 60 * k, 760 - 260 * k, "#FFFFFF", ancho=5)
            d.linea(c, bx - 40, by - 30, bx - 10 + 40 * k, by - 120 + 140 * k, "#FFFFFF", ancho=5)
            d.etiqueta(c, "¡CORTADA!", 760, 1380, color="#E04848", texto_color="#FFFFFF", tam=46, a=d.aparece(lt, dur * 0.47, 0.3) * (1 - d.aparece(lt, dur * 0.72, 0.3)))
        a = d.aparece(lt, dur * 0.72, 0.5)
        if a > 0:
            c.save()
            c.translate(840, 760)
            c.scale(d.ease_out_back(a), d.ease_out_back(a))
            d.rect(c, -150, -180, 150, 180, "#0B1A26", a=200, radio=30)
            for k in range(14):  # cable trenzado
                yy = -140 + k * 20
                d.linea(c, -14 + 14 * (k % 2), yy, 14 - 14 * (k % 2), yy + 20, "#C9D2DB", ancho=12)
            c.restore()
            d.etiqueta(c, "CABLE DE ACERO", 840, 1010, color="#C9D2DB", tam=40, a=a)
    elif i == 6:  # el más famoso, pesca con devolución
        rio_atardecer(c, gt)
        bote(c, 300, 1260, gt, tension=0.0)
        suelta = d.ease((p - 0.15) / 0.5)
        mx, my = 560 + 60 * suelta, d.lerp(1080, 1330, suelta)
        dorado(c, mx + 120, my, 0.4, 25 * suelta, gt)
        if suelta < 0.6:
            d.circulo(c, mx + 60, my - 10, 26, "#F2C28B")
            d.circulo(c, mx + 200, my - 10, 26, "#F2C28B")
        salpicadura(c, 700, AGUA_Y, lt - dur * 0.45, 0.6)
        d.etiqueta(c, "CON DEVOLUCIÓN", 540, 1480, color="#46E08A", texto_color="#0B1A12", tam=46, a=d.aparece(lt, dur * 0.5))
        d.etiqueta(c, "EL MÁS FAMOSO", 540, 650, color="#FFD400", tam=48, a=d.aparece(lt, 0.4))
    else:  # cierre
        rio_atardecer(c, gt)
        tip = bote(c, 230, 1260, gt, tension=0.8)
        boca = salto(c, lt, dur * 0.8, gt, 520, 960, 700)
        tanza(c, tip[0], tip[1], boca[0], boca[1])
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > dur * 0.4:
            d.emoji(c, "💬", 880, 640, int(150 * s))
