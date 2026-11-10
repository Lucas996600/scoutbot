"""Escenas ilustradas: ¿Cómo funciona el wifi de tu casa?"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import skia  # noqa: E402
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402

CIAN, AMARILLO, VERDE, NARANJA = "#5CE1FF", "#FFD400", "#46E08A", "#FF9A3C"


# ------------------------------------------------------------------ objetos

def router(c, x, y, s=1.0, t=0.0):
    """Router blanco con dos antenas y luces. (x, y) = base."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.elipse(c, 0, 6, 220, 26, "#000000", a=90, blur=16)
    for sx, ang in ((-1, -12), (1, 12)):
        c.save()
        c.translate(sx * 140, -100)
        c.rotate(ang)
        d.rect(c, -16, -230, 16, 0, "#2B3445", radio=16)
        d.rect(c, -10, -224, 2, -20, "#45526B", radio=6)
        c.restore()
    d.rect(c, -210, -120, 210, 0, "#FFFFFF", radio=34, shader=d.grad_lineal(0, -120, 0, 0, ["#FFFFFF", "#C7D0DE"]))
    d.rect(c, -210, -46, 210, 0, "#2B3445", radio=22)
    for k in range(5):
        on = math.sin(t * 9 + k * 1.9) > -0.3
        xx = -120 + k * 60
        if on:
            d.brillo(c, xx, -23, 26, VERDE, 160)
        d.circulo(c, xx, -23, 9, VERDE if on else "#1F5A3A")
    c.restore()


def ondas(c, x, y, t, color=CIAN, n=4, rmax=650, ancho=10, a_max=210, vel=0.6, r0=60):
    for k in range(n):
        f = (t * vel + k / n) % 1
        d.circulo(c, x, y, r0 + f * rmax, color, a=int(a_max * (1 - f) ** 1.3), trazo=ancho)


def wifi_icono(c, x, y, s=1.0, barras=3, color="#FFFFFF", apagado="#FFFFFF"):
    for k in range(3):
        r = (34 + k * 30) * s
        on = k < barras
        rr = skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r)
        c.drawArc(rr, -135, 90, False, d.pintura(color if on else apagado, 255 if on else 60, trazo=13 * s))
    d.circulo(c, x, y - 4 * s, 9 * s, color if barras > 0 else apagado, a=255 if barras > 0 else 60)


def foto_mini(c, x0, y0, x1, y1, a=255):
    """Mini foto de paisaje (sol y montañas) dentro de un rectángulo."""
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), doAntiAlias=True)
    d.rect(c, x0, y0, x1, y1, "#000000", a=a, shader=d.grad_lineal(0, y0, 0, y1, [d.col("#FF9E6B", a), d.col("#FFD27A", a)]))
    w, h = x1 - x0, y1 - y0
    d.circulo(c, x0 + w * 0.7, y0 + h * 0.35, h * 0.14, "#FFF3C4", a=a)
    d.figura(c, [(x0 - 10, y1), (x0 + w * 0.3, y0 + h * 0.4), (x0 + w * 0.6, y1)], "#6B4C8A", a=a, suave=False)
    d.figura(c, [(x0 + w * 0.35, y1), (x0 + w * 0.7, y0 + h * 0.55), (x1 + 10, y1)], "#3E2F66", a=a, suave=False)
    c.restore()


def celular(c, x, y, s=1.0, barras=3, contenido=None, alerta=False, t=0.0):
    """Celular de frente centrado en (x, y)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -132, -250, 132, 262, "#000000", a=110, radio=44, blur=20)
    d.rect(c, -130, -255, 130, 255, "#1B1F2A", radio=44)
    d.rect(c, -114, -238, 114, 238, "#000000", radio=32, shader=d.grad_lineal(0, -238, 0, 238, ["#1E3A6E", "#0E1A33"]))
    if contenido:
        c.save()
        pth = skia.Path()
        pth.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-114, -238, 114, 238), 32, 32))
        c.clipPath(pth, doAntiAlias=True)
        contenido(c)
        c.restore()
    d.rect(c, -40, -232, 40, -214, "#000000", radio=9)
    wifi_icono(c, 0, -120, 1.0, barras, "#FFFFFF")
    if alerta:
        d.circulo(c, 70, -190, 30, "#E04848")
        d.texto(c, "!", 70, -176, 44, "#FFFFFF", tipo="titulo", sombra=False)
    c.restore()


def persona(c, x, y, s=1.0, t=0.0, ropa="#E2574C"):
    """Persona sentada mirando el celular. (x, y) = cadera sobre el asiento."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    piel, pelo = "#F2C28B", "#3A2418"
    # piernas
    d.rect(c, -40, -40, 190, 40, "#2F4A7A", radio=40)
    d.rect(c, 150, -10, 215, 230, "#2F4A7A", radio=32)
    d.elipse(c, 205, 238, 60, 24, "#1C1C1C")
    # torso
    resp = 4 * math.sin(t * 2)
    d.figura(c, [(-95, 20), (-105, -150), (-80, -250 - resp), (0, -275 - resp), (80, -250 - resp), (100, -150), (90, 20)], ropa,
             shader=d.grad_lineal(-100, 0, 100, 0, [ropa, d.mezcla(ropa, "#000000", 0.25)]))
    # cabeza
    d.rect(c, -26, -305, 26, -260, piel, radio=12)
    c.save()
    c.translate(10, -370)
    c.rotate(14)
    d.circulo(c, 0, 0, 82, piel)
    d.figura(c, [(-86, 10), (-80, -50), (-40, -88), (20, -92), (70, -66), (88, -20), (60, -40), (0, -46), (-50, -30)], pelo)
    d.linea(c, 8, 18, 28, 18, "#2a1a10", ancho=7)
    d.linea(c, 48, 18, 66, 18, "#2a1a10", ancho=7)
    c.drawPath(d.camino([(26, 48), (40, 56), (54, 48)], False, True), d.pintura("#8A3B2E", trazo=5))
    c.restore()
    # brazo y celular
    d.rect(c, 40, -190, 160, -130, d.mezcla(ropa, "#000000", 0.15), radio=30)
    c.save()
    c.translate(175, -190)
    c.rotate(-20)
    d.rect(c, -32, -60, 32, 60, "#1B1F2A", radio=12)
    d.rect(c, -26, -52, 26, 52, "#7FD3FF", radio=8, shader=d.grad_lineal(0, -52, 0, 52, ["#9FE6FF", "#3E8BD9"]))
    c.restore()
    d.brillo(c, 160, -230, 90, "#9FE6FF", 90)
    d.circulo(c, 165, -150, 26, piel)
    c.restore()


def bits(c, x0, y0, x1, y1, t, n=9, color=CIAN, amp=40, vel=0.35, tam=50, a=255, semilla=0):
    """Unos y ceros viajando por una onda de (x0, y0) a (x1, y1)."""
    for k in range(n):
        f = (t * vel + k / n) % 1
        x = d.lerp(x0, x1, f)
        y = d.lerp(y0, y1, f) + amp * math.sin(f * 6 * math.pi)
        al = int(a * min(1, f * 6, (1 - f) * 6))
        d.circulo(c, x, y - tam * 0.35, tam * 0.62, "#0B1A33", a=int(al * 0.8))
        d.circulo(c, x, y - tam * 0.35, tam * 0.62, color, a=al, trazo=4)
        d.texto(c, "1" if (k * 7 + semilla) % 3 else "0", x, y, tam, color, tipo="titulo", sombra=False, a=al)


def onda_linea(c, x0, x1, y, t, amp=40, ciclos=4, color=CIAN, ancho=8, a=200, amp_fin=None):
    amp_fin = amp if amp_fin is None else amp_fin
    pts = []
    for k in range(80):
        f = k / 79
        pts.append((d.lerp(x0, x1, f), y + d.lerp(amp, amp_fin, f) * math.sin(f * ciclos * 2 * math.pi - t * 8)))
    c.drawPath(d.camino(pts, False, False), d.pintura(color, int(a * 0.4), trazo=ancho * 2.4, blur=8))
    c.drawPath(d.camino(pts, False, False), d.pintura(color, a, trazo=ancho))


def tilde(c, x, y, s=1.0, a=255, color=VERDE):
    d.circulo(c, x, y, 34 * s, color, a=a)
    c.drawPath(d.camino([(x - 15 * s, y), (x - 4 * s, y + 12 * s), (x + 17 * s, y - 12 * s)], False, False), d.pintura("#FFFFFF", a, trazo=8 * s))


# ------------------------------------------------------------------ escenografía

def living(c, t):
    d.fondo(c, "#1A1638", "#2B2350")
    d.rect(c, 640, 560, 960, 900, "#2b1a12", radio=18)
    d.rect(c, 660, 580, 940, 880, "#000000", radio=10, shader=d.grad_lineal(0, 580, 0, 880, ["#0b1530", "#28407a"]))
    d.luna(c, 870, 650, 36, "#0f1c3c")
    d.linea(c, 800, 580, 800, 880, "#2b1a12", ancho=12)
    d.rect(c, 0, 1520, W, H, "#000000", shader=d.grad_lineal(0, 1520, 0, H, ["#4A3A5C", "#231B30"]))
    # sofá
    d.rect(c, 60, 1180, 660, 1380, "#3D7A8C", radio=50)
    d.rect(c, 60, 1330, 660, 1530, "#2F6474", radio=40)
    d.rect(c, 30, 1260, 130, 1530, "#2A5866", radio=40)
    d.rect(c, 590, 1260, 690, 1530, "#2A5866", radio=40)
    # mueble del router
    d.rect(c, 760, 1280, 1040, 1530, "#5A3826", radio=16)
    d.rect(c, 780, 1300, 1020, 1400, "#4A2D1E", radio=10)


def casa(c, t, x0=110, x1=970, techo=560, alero=800, piso=1180, suelo=1550, noche=True):
    d.fondo(c, "#0F1B3D", "#3B5B9A") if noche else d.fondo(c, "#5EB3F0", "#CDEBFF")
    if noche:
        d.estrellas(c, t, n=50, semilla=2, y_max=900)
    d.rect(c, 0, suelo, W, H, "#000000", shader=d.grad_lineal(0, suelo, 0, H, ["#2F6B3F", "#173A22"]))
    d.figura(c, [(x0 - 50, alero), ((x0 + x1) / 2, techo), (x1 + 50, alero)], "#B9473F", suave=False, sombra=20)
    d.rect(c, x0, alero, x1, suelo, "#F3E3C8")
    d.rect(c, x0 + 20, alero + 20, x1 - 20, piso - 10, "#000000", shader=d.grad_lineal(0, alero, 0, piso, ["#FFE9C2", "#F6D49C"]))
    d.rect(c, x0 + 20, piso + 10, x1 - 20, suelo - 20, "#000000", shader=d.grad_lineal(0, piso, 0, suelo, ["#DDEBF5", "#B8D0E3"]))
    d.rect(c, x0, piso - 10, x1, piso + 10, "#7A5236")
    w = x1 - x0
    # cama arriba a la izquierda
    d.rect(c, x0 + 50, piso - 120, x0 + w * 0.42, piso - 30, "#5C7FD6", radio=18)
    d.rect(c, x0 + 50, piso - 150, x0 + 140, piso - 100, "#FFFFFF", radio=16)
    # escritorio arriba a la derecha
    d.rect(c, x1 - w * 0.38, piso - 140, x1 - 50, piso - 120, "#7A5236", radio=6)
    d.rect(c, x1 - w * 0.33, piso - 260, x1 - w * 0.12, piso - 150, "#222222", radio=10)
    d.rect(c, x1 - w * 0.32, piso - 250, x1 - w * 0.13, piso - 160, "#3E8BD9", radio=6)
    # sofá abajo y tele
    d.rect(c, x0 + 50, suelo - 160, x0 + w * 0.45, suelo - 40, "#E2574C", radio=30)
    d.rect(c, x1 - w * 0.36, suelo - 250, x1 - 60, suelo - 120, "#1B1F2A", radio=12)
    d.rect(c, x1 - w * 0.36 + 12, suelo - 238, x1 - 72, suelo - 132, "#2B4D7A", radio=6)


def cocina(c, t):
    d.fondo(c, "#F3E7D3", "#E4D3B6")
    for x in range(0, W, 90):
        for y in range(560, 1340, 90):
            d.rect(c, x + 4, y + 4, x + 86, y + 86, "#FFFFFF", a=110, radio=8)
    d.rect(c, 0, 1340, W, 1400, "#6E7B8B", radio=6)
    d.rect(c, 0, 1400, W, H, "#000000", shader=d.grad_lineal(0, 1400, 0, H, ["#9A6A45", "#5E3B25"]))


def microondas(c, x0, y0, x1, y1, t, encendido=True):
    d.rect(c, x0, y1 - 10, x1, y1 + 14, "#000000", a=80, radio=10, blur=12)
    d.rect(c, x0, y0, x1, y1, "#000000", radio=26, shader=d.grad_lineal(0, y0, 0, y1, ["#E9EDF2", "#AEB8C4"]))
    vx1 = x0 + (x1 - x0) * 0.68
    d.rect(c, x0 + 30, y0 + 30, vx1, y1 - 30, "#1A1A1A", radio=16)
    if encendido:
        d.rect(c, x0 + 40, y0 + 40, vx1 - 10, y1 - 40, "#000000", radio=12,
               shader=d.grad_radial((x0 + vx1) / 2, (y0 + y1) / 2, (vx1 - x0) * 0.6, ["#FFD27A", "#C8641E"]))
        cx, cy = (x0 + vx1) / 2, y1 - 80
        d.elipse(c, cx, cy, 100, 18, "#FFFFFF", a=160)
        g = math.sin(t * 2.5)
        d.figura(c, [(cx - 70 * abs(g) - 10, cy - 10), (cx - 60 * abs(g) - 5, cy - 80), (cx + 60 * abs(g) + 5, cy - 80), (cx + 70 * abs(g) + 10, cy - 10)],
                 "#3D7A8C", suave=False)
        for k in range(3):  # vapor
            f = (t * 0.7 + k / 3) % 1
            d.circulo(c, cx - 30 + k * 30, cy - 90 - f * 60, 10 + 8 * f, "#FFFFFF", a=int(150 * (1 - f)))
    px = (vx1 + x1) / 2
    d.rect(c, px - 60, y0 + 40, px + 60, y0 + 100, "#0D1A12", radio=8)
    d.texto(c, f"0:{int(30 - t) % 60:02d}", px, y0 + 86, 38, "#46E08A", tipo="bold", sombra=False)
    for k in range(3):
        d.circulo(c, px, y0 + 150 + k * 60, 20, "#7D8896")


def pecera(c, x0, y0, x1, y1, t):
    d.rect(c, x0 - 10, y1 - 10, x1 + 10, y1 + 30, "#2B3445", radio=10)
    d.rect(c, x0, y0, x1, y1, "#000000", radio=14, shader=d.grad_lineal(0, y0, 0, y1, ["#7FD3FF", "#1B6FB0"]), a=210)
    d.rect(c, x0, y0, x1, y0 + 26, "#BFEAFF", a=160, radio=8)
    for k in range(3):
        fx = x0 + 70 + ((t * (50 + k * 25) + k * 80) % (x1 - x0 - 140))
        fy = y0 + 110 + k * 90 + 10 * math.sin(t * 3 + k)
        colf = ("#FF8A3C", "#FFD400", "#FF5C8A")[k]
        d.elipse(c, fx, fy, 38, 24, colf)
        d.figura(c, [(fx - 30, fy), (fx - 64, fy - 24), (fx - 64, fy + 24)], colf, suave=False)
        d.circulo(c, fx + 18, fy - 6, 6, "#111111")
    for k in range(10):
        f = (t * 0.5 + k / 10) % 1
        d.circulo(c, x0 + 40 + (k * 53) % (x1 - x0 - 80), y1 - 20 - f * (y1 - y0 - 50), 6 + (k % 3) * 3, "#FFFFFF", a=int(200 * (1 - f)), trazo=3)
    for k in range(4):  # algas
        bx = x0 + 40 + k * (x1 - x0 - 80) / 3
        c.drawPath(d.camino([(bx, y1), (bx + 15 * math.sin(t * 2 + k), y1 - 70), (bx - 10, y1 - 140)], False, True), d.pintura("#2E9E5B", trazo=12))
    d.rect(c, x0, y0, x1, y1, "#E8F7FF", radio=14, trazo=8, a=230)


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # luz invisible que te atraviesa
        with d.camara(c, zoom=1.0 + 0.05 * p, cx=540, cy=1200):
            living(c, gt)
            router(c, 900, 1280, 0.6, gt)
            ondas(c, 900, 1210, gt, CIAN, n=5, rmax=1000, ancho=12)
            persona(c, 300, 1330, 1.1, gt)
        a = d.aparece(lt, dur * 0.4)
        if a > 0:
            d.etiqueta(c, "LUZ QUE NO VES", 540, 640, color=CIAN, tam=50, a=a)
    elif i == 1:  # internet llega por fibra al router
        casa(c, gt, x0=330, x1=1010)
        # poste y cable
        d.rect(c, 110, 700, 140, 1550, "#5A3826", radio=8)
        d.rect(c, 70, 720, 180, 745, "#4A2D1E", radio=6)
        cable = [(125, 735), (230, 820), (330, 900), (420, 1000), (420, 1440)]
        c.drawPath(d.camino(cable, False, True), d.pintura("#222222", trazo=14))
        for k in range(6):  # pulsos de luz por la fibra
            f = (gt * 0.6 + k / 6) % 1
            seg = f * (len(cable) - 1)
            j = min(int(seg), len(cable) - 2)
            u = seg - j
            px, py = d.lerp(cable[j][0], cable[j + 1][0], u), d.lerp(cable[j][1], cable[j + 1][1], u)
            d.brillo(c, px, py, 34, "#FFFFFF", 200)
            d.circulo(c, px, py, 10, AMARILLO)
        rx, ry = 560, 1440
        router(c, rx, ry, 0.55, gt)
        a = d.aparece(lt, dur * 0.35, 0.6)
        if a > 0:
            ondas(c, rx, ry - 60, gt, CIAN, n=4, rmax=520 * a, ancho=10)
        d.etiqueta(c, "FIBRA", 170, 640, 125, 735, color=AMARILLO, tam=40, a=d.aparece(lt, 0.3))
        d.etiqueta(c, "ROUTER", 790, 1300, rx + 60, ry - 80, color=CIAN, tam=40, a=d.aparece(lt, dur * 0.3))
    elif i == 2:  # 2.400 millones de veces por segundo
        d.fondo(c, "#0B1530", "#05091A")
        d.particulas(c, gt, 40, "#9FC3FF", a=60)
        d.etiqueta(c, "2,4 GHz", 360, 620, color=CIAN, tam=48, a=d.aparece(lt, 0.2))
        d.etiqueta(c, "5 GHz", 720, 620, color=AMARILLO, tam=48, a=d.aparece(lt, dur * 0.6))
        router(c, 170, 1120, 0.4, gt)
        ciclos = 2 + 10 * d.ease(p * 1.2)
        onda_linea(c, 280, 1040, 920, gt * (1 + 3 * p), amp=120, ciclos=ciclos, color=CIAN, ancho=9, a=240)
        v = 2.4e9 * d.ease_out((lt - 0.2) / max(0.6, dur * 0.65))
        d.contador(c, v, 540, 1300, tam=104, caja=False)
        d.texto(c, "VECES POR SEGUNDO", 540, 1390, 50, "#FFFFFF", tipo="titulo")
    elif i == 3:  # se parte en unos y ceros
        d.fondo(c, "#14213D", "#0B1022")
        rx, ry, cx, cy = 210, 1350, 860, 1130
        router(c, rx, ry, 0.5, gt)
        ondas(c, rx, ry - 60, gt, CIAN, n=3, rmax=260, ancho=6, a_max=120)
        # foto que se parte
        a = d.aparece(lt, 0.1, 0.4)
        fx0, fy0, fx1, fy1 = 90, 600, 420, 840
        partir = d.ease((lt - 0.8) / 1.0)
        for gx in range(3):
            for gy in range(3):
                w, h = (fx1 - fx0) / 3, (fy1 - fy0) / 3
                ox, oy = gx * 18 * partir, gy * 18 * partir
                cae = d.ease((lt - 1.2 - (gx + gy) * 0.15) / 0.8)
                x0 = fx0 + gx * w + ox + (rx - 60 - fx0 - gx * w) * cae
                y0 = fy0 + gy * h + oy + (ry - 140 - fy0 - gy * h) * cae
                sc = 1 - 0.7 * cae
                c.save()
                c.translate(x0, y0)
                c.scale(sc, sc)
                c.save()
                c.clipRect(skia.Rect.MakeWH(w, h))
                c.translate(-gx * w, -gy * h)
                foto_mini(c, 0, 0, fx1 - fx0, fy1 - fy0, a=int(255 * a * (1 - cae * 0.6)))
                c.restore()
                c.restore()
        bits(c, rx + 120, ry - 120, cx - 150, cy, gt, n=8, a=int(255 * d.aparece(lt, 1.2)))

        def pantalla(cv):
            llena = d.ease((lt - 1.5) / max(0.8, dur - 2.2))
            if llena > 0:
                cv.save()
                cv.clipRect(skia.Rect.MakeLTRB(-114, 238 - 476 * llena, 114, 238))
                foto_mini(cv, -114, -60, 114, 140)
                cv.restore()
        celular(c, cx, cy, 0.95, 3, pantalla)
    elif i == 4:  # el celular contesta
        d.fondo(c, "#14213D", "#0B1022")
        rx, ry, cx, cy = 210, 1350, 860, 1130
        router(c, rx, ry, 0.5, gt)
        bits(c, rx + 120, ry - 120, cx - 150, cy, gt, n=6, a=110, amp=30)
        for k in range(4):  # respuestas de vuelta
            f = (gt * 0.45 + k / 4) % 1
            x = d.lerp(cx - 150, rx + 110, f)
            y = d.lerp(cy + 120, ry - 50, f) + 25 * math.sin(f * 4 * math.pi)
            tilde(c, x, y, 1.0, a=int(255 * min(1, f * 5, (1 - f) * 5)))

        def pantalla(cv):
            foto_mini(cv, -114, -60, 114, 140)
        celular(c, cx, cy, 0.95, 3, pantalla)
        d.etiqueta(c, "¡LLEGÓ BIEN!", 760, 760, color=VERDE, texto_color="#0B1A12", tam=46, a=d.aparece(lt, dur * 0.35))
        d.etiqueta(c, "IDA Y VUELTA", 300, 900, color="#FFFFFF", tam=40, a=d.aparece(lt, 0.4))
    elif i == 5:  # pecera
        d.fondo(c, "#2A3550", "#1B2236")
        d.rect(c, 0, 1460, W, H, "#000000", shader=d.grad_lineal(0, 1460, 0, H, ["#6A5240", "#3B2C21"]))
        d.rect(c, 330, 1300, 750, 1470, "#5A3826", radio=12)
        rx, ry = 150, 1460
        router(c, rx, ry, 0.45, gt)
        pecera(c, 360, 900, 720, 1290, gt)
        debil = d.ease((p - 0.1) / 0.5)
        onda_linea(c, 240, 360, 1080, gt, amp=60, ciclos=1.5, color=CIAN, ancho=10, a=240)
        onda_linea(c, 360, 720, 1080, gt, amp=60, ciclos=4, color=CIAN, ancho=10, a=int(240 - 120 * debil), amp_fin=60 - 45 * debil)
        onda_linea(c, 720, 800, 1080, gt, amp=15 + 45 * (1 - debil), ciclos=1, color=CIAN, ancho=4 + 6 * (1 - debil), a=int(240 - 170 * debil))
        barras = 3 if debil < 0.35 else (2 if debil < 0.75 else 1)
        celular(c, 920, 1120, 0.6, barras, alerta=debil > 0.75, t=gt)
        d.etiqueta(c, "EL AGUA LA ABSORBE", 540, 700, color=CIAN, tam=46, a=d.aparece(lt, 0.6))
    elif i == 6:  # microondas
        cocina(c, gt)
        microondas(c, 60, 1000, 560, 1340, gt)
        router(c, 840, 1340, 0.5, gt)
        ondas(c, 250, 1170, gt, NARANJA, n=4, rmax=560, ancho=10, a_max=170, vel=0.8)
        ondas(c, 840, 1280, gt * 0.9, CIAN, n=4, rmax=560, ancho=10, a_max=200)
        lio = d.aparece(lt, dur * 0.3, 0.6)
        for k in range(14):  # interferencia
            f = (gt * 3 + k * 0.37) % 1
            if lio > 0 and f < 0.5:
                x = 560 + 160 * math.sin(k * 2.3 + gt * 5)
                y = 1100 + 140 * math.cos(k * 1.7 + gt * 4)
                c.drawPath(d.camino([(x, y), (x + 14, y + 18), (x - 6, y + 28), (x + 12, y + 46)], False, False), d.pintura("#FFFFFF", int(230 * lio), trazo=5))
        corte = lio > 0 and (gt * 2.3) % 1 < 0.55
        celular(c, 700, 760, 0.55, 0 if corte else 3, alerta=corte, t=gt)
        d.etiqueta(c, "2,45 GHz", 310, 920, color=NARANJA, tam=42, a=d.aparece(lt, 0.3))
        d.etiqueta(c, "2,4 GHz", 900, 1060, color=CIAN, tam=42, a=d.aparece(lt, 0.7))
    else:  # consejo: alto y al centro
        casa(c, gt)
        mueve = d.ease((lt - 0.4) / 1.4)
        rx, ry = d.lerp(230, 540, mueve), d.lerp(1530, 1170, mueve)
        alcance = d.lerp(330, 600, mueve)
        d.circulo(c, rx, ry - 50, alcance, CIAN, a=55, shader=d.grad_radial(rx, ry - 50, alcance, [d.col(CIAN, 110), d.col(CIAN, 0)]))
        ondas(c, rx, ry - 50, gt, CIAN, n=3, rmax=alcance, ancho=7, a_max=160)
        if mueve > 0.5:
            d.rect(c, rx - 130, ry - 5, rx + 130, ry + 12, "#7A5236", radio=4)
        router(c, rx, ry, 0.4, gt)
        for k, (tx, ty) in enumerate(((260, 960), (820, 960), (260, 1340), (820, 1340))):
            tilde(c, tx, ty, 1.1, a=int(255 * d.aparece(lt, 1.6 + k * 0.25)))
        d.etiqueta(c, "ALTO Y AL CENTRO", 540, 690, color=AMARILLO, tam=44, a=d.aparece(lt, 1.0))
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > dur * 0.55:
            d.emoji(c, "💬", 880, 640, int(150 * s))
