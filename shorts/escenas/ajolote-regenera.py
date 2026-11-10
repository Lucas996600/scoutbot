"""Escenas ilustradas: el ajolote, el animal que regenera partes de su cuerpo."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import cartoon3d as C  # noqa: E402

ROSA, ROSA_OSC, BRANQUIA = "#F7A8C4", "#E07FA2", "#E8457A"
AMARILLO, CIAN = "#FFD400", "#7FE3FF"


# ------------------------------------------------------------------ el ajolote

def ajolote(c, x, y, s=1.0, t=0.0, pata=1.0, rot=0.0, brillos=(), sonrisa=1.0, color=ROSA):
    """Ajolote de perfil 3/4 mirando a la derecha, centrado en (x, y). s=1 -> ~800 px de largo.
    pata: 0..1 cuánto creció la pata delantera cercana. brillos: partes que brillan ('pata','cola','medula','corazon')."""
    c.save()
    c.translate(x, y)
    c.rotate(rot + 3 * math.sin(t * 1.4))
    c.scale(s, s)
    osc = d.mezcla(color, "#000000", 0.15)
    ond = 18 * math.sin(t * 3)
    d.elipse(c, 0, 120, 300, 26, "#000000", a=60, blur=18)
    # cola con aleta
    cola = [(-180, -40), (-330, -60 + ond * 0.5), (-470, -20 + ond), (-500, 10 + ond), (-460, 40 + ond), (-320, 50 + ond * 0.5), (-180, 50)]
    d.figura(c, [(-160, -60), (-330, -100 + ond * 0.5), (-500, -30 + ond), (-500, 40 + ond), (-330, 80 + ond * 0.5), (-160, 70)], "#FFD3E2", a=200)
    d.figura(c, cola, color, shader=d.grad_lineal(0, -60, 0, 50, [d.mezcla(color, "#FFFFFF", 0.2), osc]))
    if "cola" in brillos:
        d.figura(c, cola, "#FFFFFF", a=int(110 + 80 * math.sin(t * 6)))

    def pata_(px, py, frac, atras=False, ang=20):
        if frac <= 0.02:
            d.circulo(c, px, py, 22, d.mezcla(color, "#C2185B", 0.3))
            return
        c.save()
        c.translate(px, py)
        c.rotate(ang + 8 * math.sin(t * 2 + px))
        c.scale(frac, frac)
        col = osc if atras else color
        d.rect(c, -20, 0, 20, 90, col, radio=18)
        for k in range(4):
            a = math.radians(60 + k * 22)
            d.linea(c, 0, 88, 40 * math.cos(a) - 6, 88 + 40 * math.sin(a), col, ancho=12)
            d.circulo(c, 40 * math.cos(a) - 6, 88 + 40 * math.sin(a), 8, col)
        c.restore()

    pata_(-120, 50, 1, True, 25)
    pata_(150, 55, 1, True, -10)
    # cuerpo
    d.elipse(c, 0, 0, 240, 82, color, shader=d.grad_lineal(0, -82, 0, 82, [d.mezcla(color, "#FFFFFF", 0.25), color, osc]))
    for k in range(5):  # manchitas
        d.circulo(c, -150 + k * 60, -30 + 12 * math.sin(k * 2), 7, osc, a=150)
    if "medula" in brillos:
        pts = [(-300, -20), (-150, -45), (0, -55), (150, -45), (230, -40)]
        c.drawPath(d.camino(pts, False, True), d.pintura(AMARILLO, 140, trazo=26, blur=8))
        c.drawPath(d.camino(pts, False, True), d.pintura("#FFF6C8", trazo=8))
    if "corazon" in brillos:
        pul = 1 + 0.15 * math.sin(t * 8)
        d.brillo(c, 120, 20, 70 * pul, "#FF4D6D", 220)
        d.emoji(c, "❤️", 120, 20, int(64 * pul))
    pata_(-90, 60, 1, False, 30)
    pata_(170, 62, pata, False, -5)
    if "pata" in brillos or 0 < pata < 1:
        d.brillo(c, 175, 110, 80, "#FFF6C8", 160)
    # cabeza ancha
    hx, hy = 250, -20
    d.elipse(c, hx, hy, 135, 100, color, shader=d.grad_radial(hx - 30, hy - 40, 180, [d.mezcla(color, "#FFFFFF", 0.3), color, osc]))
    # branquias (3 por lado, plumosas)
    for k, ang in enumerate((-150, -115, -80)):
        a = math.radians(ang + 6 * math.sin(t * 3 + k))
        bx0, by0 = hx - 70, hy - 50
        bx1, by1 = bx0 + 150 * math.cos(a), by0 + 150 * math.sin(a)
        d.linea(c, bx0, by0, bx1, by1, BRANQUIA, ancho=14)
        for j in range(6):
            f = 0.3 + j * 0.12
            px, py = d.lerp(bx0, bx1, f), d.lerp(by0, by1, f)
            for sd in (-1, 1):
                d.linea(c, px, py, px + 26 * math.cos(a + sd * 1.2), py + 26 * math.sin(a + sd * 1.2), BRANQUIA, ancho=8)
    # ojitos y sonrisa
    for (ex, ey) in ((hx + 50, hy - 40), (hx + 95, hy - 32)):
        d.circulo(c, ex, ey, 13, "#1B1B1B")
        d.circulo(c, ex - 4, ey - 4, 4, "#FFFFFF")
    c.drawPath(d.camino([(hx + 10, hy + 30), (hx + 70, hy + 30 + 22 * sonrisa), (hx + 125, hy + 15)], False, True), d.pintura("#8A2B4A", trazo=7))
    d.elipse(c, hx + 20, hy + 5, 18, 10, "#FF7FA8", a=150)
    c.restore()


def agua(c, t, fondo_y=1560):
    d.fondo(c, "#4FB7C9", "#0E4A63")
    d.rayos_luz(c, t, n=6, a=22)
    d.rect(c, 0, fondo_y, W, H, "#000000", shader=d.grad_lineal(0, fondo_y, 0, H, ["#7A6A48", "#3E3420"]))
    for k in range(6):
        bx = 70 + k * 190
        c.drawPath(d.camino([(bx, fondo_y + 10), (bx + 20 * math.sin(t * 1.4 + k), fondo_y - 140), (bx - 10, fondo_y - 260 + (k % 3) * 50)], False, True),
                   d.pintura("#2E8A5A", trazo=16))
    d.burbujas(c, t, n=20, y_min=450)


def destellos_magia(c, x, y, t, n=8, r=110):
    for k in range(n):
        f = (t * 0.9 + k / n) % 1
        ang = k * 2 * math.pi / n + t
        d.circulo(c, x + r * f * math.cos(ang), y + r * f * math.sin(ang), 8 * (1 - f) + 2, "#FFF6C8", a=int(255 * (1 - f)))


def trajinera(c, x, y, s, t, colores=("#E8413C", "#FFD23F", "#3D9BFF")):
    c.save()
    c.translate(x, y + 6 * math.sin(t * 1.5 + x))
    c.scale(s, s)
    d.figura(c, [(-230, 0), (230, 0), (190, 60), (-190, 60)], "#2E7A3E", suave=False)
    d.rect(c, -200, -170, 200, -140, colores[0], radio=6)
    for k, colr in enumerate(colores):
        d.rect(c, -200 + k * 134, -140, -70 + k * 134, -100, colr)
    for sx in (-170, 170):
        d.rect(c, sx - 8, -140, sx + 8, 0, "#6A4022")
    c.restore()


def planaria(c, x, y, s, t, ojos=True, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    ond = 10 * math.sin(t * 4)
    d.figura(c, [(-150, ond * 0.5), (-100, -30), (0, -38 + ond * 0.3), (110, -30), (160, -50), (175, -10), (160, 30), (110, 30), (0, 36), (-100, 30)],
             "#B07A50", shader=d.grad_lineal(0, -40, 0, 40, ["#C99366", "#8A5A34"]))
    if ojos:
        for sx in (130, 150):
            d.circulo(c, sx, -12, 9, "#FFFFFF")
            d.circulo(c, sx + 2, -11, 5, "#111111")
    c.restore()


# ------------------------------------------------------------------ escenas

def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: la pata le vuelve a crecer
        with d.camara(c, zoom=1.04 + 0.08 * p, cx=640, cy=1100):
            agua(c, gt)
            crece = d.ease(d.clamp((p - 0.3) / 0.55))
            ajolote(c, 560, 1100, 1.0, gt, pata=crece)
            if 0 < crece < 1:
                destellos_magia(c, 560 + 175, 1100 + 110, gt, r=160)
        d.etiqueta(c, "¡LE VUELVE A CRECER!", 540, 640, color=AMARILLO, tam=46, a=d.aparece(lt, dur * 0.55))
    elif i == 1:  # Xochimilco
        d.cielo(c, "#7EC8F2", "#D8F1FF", y1=900)
        d.colinas(c, 820, 60, color="#5DBB63", semilla=2)
        trajinera(c, 280, 860, 0.8, gt)
        trajinera(c, 820, 900, 0.7, gt, ("#9B5DE5", "#F15BB5", "#FEE440"))
        d.rect(c, 0, 900, W, H, "#000000", shader=d.grad_lineal(0, 900, 0, H, ["#4FB7A0", "#0E4A55"]))
        d.agua(c, 900, gt, arriba="#4FB7A0", abajo="#0E4A55")
        d.burbujas(c, gt, n=15, y_min=950)
        ajolote(c, 540, 1300, 1.0, gt, sonrisa=1.3)
        d.etiqueta(c, "XOCHIMILCO, MÉXICO", 540, 640, color="#FFFFFF", tam=44, a=d.aparece(lt, 0.4))
    elif i == 2:  # regenera casi todo
        agua(c, gt)
        partes = ["pata", "cola", "medula", "corazon"]
        activas = tuple(partes[:1 + int(d.clamp(p / 0.8) * 3.99)])
        ajolote(c, 560, 1080, 1.15, gt, brillos=activas)
        nombres = {"pata": ("PATAS", 820, 1360), "cola": ("COLA", 190, 860), "medula": ("MÉDULA", 540, 760), "corazon": ("CORAZÓN", 820, 1250)}
        for k, pt in enumerate(activas):
            txt, ex, ey = nombres[pt]
            d.etiqueta(c, txt, ex, ey, color=(AMARILLO, CIAN, "#FFF6C8", "#FF8FA3")[k], tam=40)
    elif i == 3:  # blastema
        agua(c, gt)
        etapa = d.clamp(p / 0.85)
        ajolote(c, 380, 1350, 0.8, gt, pata=0.0 if etapa < 0.25 else d.ease((etapa - 0.25) / 0.75))

        def dentro(cv):
            d.rect(cv, 0, 0, W, H, "#000000", shader=d.grad_radial(700, 860, 300, ["#FFE3EC", "#F2A7C0"]))
            d.rect(cv, 470, 760, 640, 960, ROSA_OSC, radio=60)  # muñón
            blob = d.ease(d.clamp(etapa / 0.35))
            crece = d.ease(d.clamp((etapa - 0.35) / 0.65))
            if crece < 1:
                d.circulo(cv, 640 + 20 * blob, 860, 70 * blob, "#FF8FB5")
                for k in range(int(12 * blob)):  # células
                    ang = k * 0.52 + gt
                    d.circulo(cv, 640 + 20 * blob + 40 * math.cos(ang), 860 + 40 * math.sin(ang), 12, "#FFC2D6", trazo=4)
            if crece > 0:
                d.rect(cv, 600, 820, 600 + 240 * crece, 900, ROSA, radio=40)
                d.linea(cv, 600, 860, 600 + 230 * crece, 860, "#FFFFFF", ancho=10)  # hueso
                d.linea(cv, 600, 840, 600 + 220 * crece, 840, "#FFE14D", ancho=4)  # nervio
                for k in range(4):
                    a = math.radians(-50 + k * 33)
                    ex = 600 + 240 * crece
                    d.linea(cv, ex, 860, ex + 70 * crece * math.cos(a), 860 + 70 * crece * math.sin(a), ROSA, ancho=22)
        r = 290 * d.aparece(lt, 0.2, 0.5)
        if r > 5:
            d.linea(c, 520, 1450, 600, 860 + r, "#FFFFFF", ancho=6)
            d.lupa(c, 680, 860, r, dentro)
        d.etiqueta(c, "BLASTEMA", 300, 640, color="#FF8FB5", texto_color="#3A0E1A", tam=44, a=d.aparece(lt, 0.6))
        d.etiqueta(c, "SIN CICATRIZ", 780, 1340, color=AMARILLO, tam=40, a=d.aparece(lt, dur * 0.7))
    elif i == 4:  # nosotros: el hígado
        d.fondo(c, "#E8F4FA", "#BFDCEB")
        C.personaje(c, 360, 1620, 1.05, gt, ropa="#FFFFFF", expresion="normal", mira=0.6)
        a = d.aparece(lt, 0.4, 0.5)
        if a > 0:  # hígado brillando en el cuerpo
            pul = 1 + 0.08 * math.sin(gt * 6)
            d.figura(c, [(300, 1310), (420, 1290), (440, 1330), (360, 1360), (290, 1350)], "#B5443A", a=int(255 * a))
            d.brillo(c, 370, 1325, 90 * pul, "#FFD400", int(150 * a))
            d.etiqueta(c, "SOLO EL HÍGADO", 360, 640, color=AMARILLO, tam=40, a=a)
        # microscopio y ajolote en el laboratorio
        d.rect(c, 640, 1100, 1000, 1500, "#9FD8FF", a=120, radio=30)
        d.rect(c, 640, 1100, 1000, 1500, "#FFFFFF", radio=30, trazo=8)
        ajolote(c, 820, 1330, 0.45, gt)
        d.emoji(c, "🔬", 820, 930, 150)
    elif i == 5:  # planaria: cada pedacito es un gusano nuevo
        d.fondo(c, "#163A4A", "#081A24")
        d.particulas(c, gt, 40, "#9FD8FF", a=50)
        corte = d.clamp((p - 0.2) / 0.15)
        nace = d.ease(d.clamp((p - 0.4) / 0.5))
        if corte < 1:
            planaria(c, 540, 1050, 2.4, gt)
            sx = d.lerp(1100, 540, corte)
            d.emoji(c, "✂️", sx, 1050, 160, rot=-20)
        else:
            for k, (px, py) in enumerate(((240, 900), (540, 1150), (840, 900))):
                s = d.lerp(0.8, 1.15, nace)
                planaria(c, px, py, s, gt + k, ojos=nace > 0.6, rot=-20 + k * 20)
                if nace < 1:
                    destellos_magia(c, px, py, gt + k, r=120)
            d.etiqueta(c, "¡3 GUSANOS NUEVOS!", 540, 1420, color=AMARILLO, tam=44, a=d.aparece(lt, dur * 0.75))
        d.etiqueta(c, "PLANARIA", 540, 640, color="#C99366", texto_color="#2A1608", tam=46, a=d.aparece(lt, 0.3))
    else:  # cierre
        agua(c, gt)
        ajolote(c, 520, 1150, 1.2, gt, sonrisa=1.4)
        s = 1 + 0.08 * math.sin(gt * 6)
        if lt > 0.5:
            d.emoji(c, "💬", 860, 760, int(170 * s))
