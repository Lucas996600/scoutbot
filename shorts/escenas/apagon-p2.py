"""Escenas: ¿Y si el planeta entero se queda sin luz? — Parte 2 (los días siguientes)."""
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import apagon_comun as A  # noqa: E402


def cocina(c):
    d.fondo(c, "#2A2F3E", "#1A1E29")
    for x in range(0, W, 90):
        for y in range(560, 1300, 90):
            d.rect(c, x + 4, y + 4, x + 86, y + 86, "#FFFFFF", a=18, radio=8)
    d.rect(c, 0, 1300, W, H, "#000000", shader=d.grad_lineal(0, 1300, 0, H, ["#3A2E26", "#1E1712"]))


def canilla(c, x, y, s, t, fluye):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -40, -60, 40, 0, "#B8C2CC", radio=12)
    d.rect(c, -20, -130, 20, -50, "#9AA5B1", radio=8)
    d.rect(c, -90, -150, 90, -120, "#C9D2DB", radio=14)
    d.figura(c, [(0, -20), (220, -40), (260, 10), (240, 60), (210, 60), (215, 20), (0, 20)], "#C9D2DB")
    if fluye > 0:
        d.rect(c, 210, 60, 240, 60 + 150 * fluye, "#7FD3FF", a=200, radio=12)
    else:
        f = (t * 0.6) % 1
        d.circulo(c, 225, 75 + f * 260, 12, "#7FD3FF", a=int(230 * (1 - f)))
    c.restore()


def heladera(c, x, y, s, t, abierta=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -230, -820, 230, 0, "#E6EBF0", radio=30, shader=d.grad_lineal(-230, 0, 230, 0, ["#F3F6F9", "#C9D2DB"]))
    d.linea(c, -230, -540, 230, -540, "#9AA5B1", ancho=8)
    d.rect(c, 170, -760, 190, -600, "#9AA5B1", radio=8)
    d.rect(c, 170, -480, 190, -260, "#9AA5B1", radio=8)
    c.restore()


def reloj_cuenta(c, x, y, r, frac, color, etiqueta, valor):
    d.circulo(c, x, y, r, "#0B1022", a=210)
    d.circulo(c, x, y, r, "#FFFFFF", a=50, trazo=12)
    import skia
    rr = skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r)
    c.drawArc(rr, -90, 360 * d.clamp(frac), False, d.pintura(color, trazo=14))
    d.texto(c, valor, x, y + 22, int(r * 0.55), "#FFFFFF", tipo="titulo", sombra=False)
    d.texto(c, etiqueta, x, y + r + 60, 40, "#FFFFFF", tipo="titulo")


def surtidor(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -130, -560, 130, 0, A.ROJO, radio=22, shader=d.grad_lineal(-130, 0, 130, 0, ["#E8574F", "#B23A33"]))
    d.rect(c, -100, -510, 100, -360, "#0D1A12", radio=12)
    d.texto(c, "----", 0, -410, 60, "#2E6B45", tipo="titulo", sombra=False)
    d.rect(c, -100, -320, 100, -280, "#FFFFFF", a=200, radio=8)
    c.drawPath(d.camino([(130, -300), (210, -260), (220, -120), (180, -60)], False, True), d.pintura("#1B1B1B", trazo=18))
    d.rect(c, 150, -80, 210, -30, "#2B2B2B", radio=10)
    c.restore()


def cajero(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.rect(c, -150, -620, 150, 0, "#5B6575", radio=20)
    d.rect(c, -110, -560, 110, -400, "#0B0E14", radio=10)
    d.texto(c, "FUERA DE", 0, -490, 34, A.ROJO, tipo="titulo", sombra=False)
    d.texto(c, "SERVICIO", 0, -445, 34, A.ROJO, tipo="titulo", sombra=False)
    for k in range(3):
        for j in range(3):
            d.rect(c, -80 + j * 60, -350 + k * 55, -40 + j * 60, -315 + k * 55, "#3A4250", radio=6)
    d.rect(c, -90, -150, 90, -130, "#111111", radio=6)
    c.restore()


def central_nuclear(c, t, combustible, vapor):
    d.cielo(c, "#2B3A55", "#6E7FA0")
    d.colinas(c, 1500, 80, color="#2F4A3A", semilla=4)
    for k, (tx, s) in enumerate(((330, 1.0), (680, 0.85))):  # torres de enfriamiento
        c.save()
        c.translate(tx, 1500)
        c.scale(s, s)
        d.figura(c, [(-200, 0), (-140, -300), (-150, -560), (150, -560), (140, -300), (200, 0)], "#C9CED6",
                 shader=d.grad_lineal(-200, 0, 200, 0, ["#E3E7EC", "#9EA6B2"]))
        for j in range(int(5 * vapor)):
            f = (t * 0.25 + j / 5 + k * 0.1) % 1
            d.circulo(c, 20 * math.sin(f * 6 + k), -600 - f * 400, 80 + f * 120, "#FFFFFF", a=int(170 * (1 - f) * vapor))
        c.restore()
    # edificio del reactor
    d.rect(c, 780, 1260, 1040, 1500, "#8C95A3", radio=10)
    d.elipse(c, 910, 1260, 130, 90, "#A2ABB8")
    # generador diésel con indicador de combustible (subido para no quedar bajo los subtítulos)
    c.save()
    c.translate(0, -190)
    d.rect(c, 60, 1530, 420, 1720, "#E2A23A", radio=18)
    d.texto(c, "DIÉSEL", 240, 1640, 50, "#2B1B05", tipo="titulo", sombra=False)
    for k in range(3):
        f = (t * 1.5 + k / 3) % 1
        d.circulo(c, 380, 1520 - f * 120, 18 + f * 20, "#555555", a=int(160 * (1 - f)))
    d.rect(c, 480, 1560, 1000, 1640, "#0B1022", a=210, radio=40)
    d.rect(c, 492, 1572, 492 + 496 * d.clamp(combustible), 1628, A.VERDE if combustible > 0.35 else A.ROJO, radio=28)
    d.texto(c, "COMBUSTIBLE", 740, 1617, 38, "#FFFFFF", tipo="titulo")
    c.restore()


def tortuga(c, x, y, s, t, k=0):
    c.save()
    c.translate(x, y)
    c.rotate(-90 + 10 * math.sin(t * 6 + k))
    c.scale(s, s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.save()
            c.translate(sx * 30, sy * 26)
            c.rotate(sx * sy * (25 + 20 * math.sin(t * 8 + k + sx)))
            d.elipse(c, sx * 18, 0, 26, 10, "#3E7A55")
            c.restore()
    d.circulo(c, 52, 0, 18, "#4F9468")
    d.elipse(c, 0, 0, 44, 36, "#2E5E40")
    d.elipse(c, 0, 0, 32, 26, "#3E7A55")
    c.restore()


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: DÍA 2
        A.cielo_noche(c, gt, estrellas=0.5)
        A.ciudad(c, gt, suelo=1560, apagado=1.0)
        voltea = d.ease(d.clamp((lt - 0.15) / 0.6))
        s = 0.85 + 0.15 * d.ease_out_back(d.clamp(lt / 0.35))
        A.calendario(c, 540, 980, 1.6 * s, 2, voltea=1 - voltea if voltea < 1 else 0)
        d.etiqueta(c, "SIN LUZ", 540, 1430, color=A.ROJO, texto_color="#FFFFFF", tam=54, a=d.aparece(lt, 0.6))
    elif i == 1:  # se corta el agua
        cocina(c)
        fluye = 1 - d.ease(d.clamp((p - 0.2) / 0.35))
        d.rect(c, 120, 1180, 960, 1300, "#8E98A6", radio=20)
        d.rect(c, 330, 1190, 750, 1290, "#5E6876", radio=40)
        canilla(c, 310, 1000, 1.1, gt, fluye)
        # bomba eléctrica apagada
        d.rect(c, 700, 640, 960, 860, "#3D4656", radio=20)
        d.circulo(c, 830, 750, 70, "#232A36")
        aspas = gt * 12 * fluye
        for k in range(3):
            ang = aspas + k * 2.09
            d.linea(c, 830, 750, 830 + 55 * math.cos(ang), 750 + 55 * math.sin(ang), "#9AA5B1", ancho=12)
        d.circulo(c, 920, 670, 14, A.VERDE if fluye > 0.5 else A.ROJO)
        d.etiqueta(c, "BOMBA ELÉCTRICA", 830, 930, color="#FFFFFF", tam=36, a=d.aparece(lt, 0.4))
        d.etiqueta(c, "SIN AGUA", 540, 1450, color=A.CIAN, tam=50, a=d.aparece(lt, dur * 0.6))
    elif i == 2:  # heladera: 4 horas / freezer 48 horas
        cocina(c)
        heladera(c, 290, 1500, 1.0, gt)
        prog = d.ease(d.clamp(p / 0.85))
        reloj_cuenta(c, 780, 780, 150, 1 - prog, A.NARANJA, "HELADERA", f"{max(0, 4 - 4 * prog):.0f} h")
        reloj_cuenta(c, 780, 1220, 150, 1 - prog * 0.08, A.CIAN, "FREEZER LLENO", f"{max(0, 48 - 4 * prog):.0f} h")
        d.etiqueta(c, "¡NO LA ABRAS!", 290, 600, color=A.AMARILLO, tam=40, a=d.aparece(lt, dur * 0.4))
    elif i == 3:  # nafta y cajeros
        A.cielo_noche(c, gt, estrellas=0.0)
        d.rect(c, 0, 0, W, H, "#C98A4A", a=40)
        d.rect(c, 0, 1500, W, H, "#2B2B31")
        d.rect(c, 60, 640, 640, 700, "#D9D9D9", radio=8)
        d.rect(c, 100, 700, 120, 1500, "#9AA5B1")
        d.rect(c, 580, 700, 600, 1500, "#9AA5B1")
        surtidor(c, 350, 1500, 1.0)
        cajero(c, 820, 1500, 0.95)
        a = d.aparece(lt, 0.6, 0.4)
        for (bx, by) in ((350, 1150), (820, 1250)):
            if a > 0:
                s = d.ease_out_back(a)
                d.linea(c, bx - 120 * s, by - 120 * s, bx + 120 * s, by + 120 * s, A.ROJO, ancho=26)
                d.linea(c, bx + 120 * s, by - 120 * s, bx - 120 * s, by + 120 * s, A.ROJO, ancho=26)
        d.etiqueta(c, "SOLO EFECTIVO", 540, 1400, color=A.VERDE, texto_color="#0B1A12", tam=44, a=d.aparece(lt, dur * 0.65))
    elif i == 4:  # centrales nucleares con generadores
        comb = 1 - 0.8 * d.ease(p)
        central_nuclear(c, gt, comb, vapor=1.0)
        if comb < 0.4 and (gt * 2) % 1 < 0.5:
            d.circulo(c, 910, 1180, 46, A.ROJO)
            d.texto(c, "!", 910, 1200, 70, "#FFFFFF", tipo="titulo", sombra=False)
        d.etiqueta(c, "HAY QUE ENFRIAR EL REACTOR", 540, 640, color=A.AMARILLO, tam=36, a=d.aparece(lt, 0.5))
    elif i == 5:  # tortugas encuentran el mar
        d.cielo(c, "#0B1530", "#2B4A7A")
        d.estrellas(c, gt, n=80, semilla=4, y_max=900)
        d.luna(c, 820, 650, 60, "#0B1530")
        d.brillo(c, 820, 650, 300, "#CFE3FF", 70)
        d.agua(c, 980, gt, arriba="#2D5E8C", abajo="#0E2440")
        for k in range(5):  # reflejo de la luna
            d.rect(c, 820 - 90 + k * 14, 1010 + k * 30, 820 + 90 - k * 14, 1018 + k * 30, "#CFE3FF", a=150 - k * 25, radio=4)
        d.rect(c, 0, 1180, W, H, "#000000", shader=d.grad_lineal(0, 1180, 0, H, ["#D9C08A", "#A48650"]))
        for k in range(9):
            sx = 120 + (k * 113) % 860
            sy0 = 1700 + (k * 37) % 150
            yy = sy0 - ((lt * 70 + k * 25) % 520)
            tortuga(c, sx, yy, 0.9, gt, k)
        d.etiqueta(c, "SIN LUCES ARTIFICIALES", 540, 1450, color="#CFE3FF", tam=38, a=d.aparece(lt, 0.6))
    else:  # ¿qué harías primero?
        A.cielo_noche(c, gt, estrellas=0.9, via_lactea=0.7)
        A.ciudad(c, gt, suelo=1560, apagado=1.0, escala=0.75)
        for k, (ex, em) in enumerate(((220, "🕯️"), (420, "💧"), (640, "🥫"), (860, "🔦"))):
            a = d.aparece(lt, 0.3 + k * 0.35, 0.3)
            if a > 0:
                d.emoji(c, em, ex, 1150 + 15 * math.sin(gt * 3 + k), int(120 * d.ease_out_back(a)))
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > dur * 0.5:
            d.emoji(c, "💬", 540, 880, int(170 * s))
