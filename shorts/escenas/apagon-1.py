"""Escenas: ¿Qué pasaría si el planeta se queda sin luz? — Parte 1 (fotos de Higgsfield animadas)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import skia  # noqa: E402
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import foto as F  # noqa: E402

FOTOS = F.ruta_fotos("apagon-1")
AMARILLO, ROJO, CIAN = "#FFD400", "#E04848", "#7FE3FF"


def f(k):
    return os.path.join(FOTOS, f"{k}.jpg")


def parpadeo(gt, fuerza=1.0):
    """1 = luz normal; baja de golpe a ratos (luz inestable)."""
    v = 1.0
    if (gt * 7.3) % 1 < 0.12:
        v -= 0.5 * fuerza
    if (gt * 3.1) % 1 < 0.06:
        v -= 0.35 * fuerza
    return max(0.25, v)


def bateria(c, x, y, nivel, color):
    d.rect(c, x, y, x + 150, y + 70, "#000000", a=160, radio=14)
    d.rect(c, x, y, x + 150, y + 70, "#FFFFFF", radio=14, trazo=6)
    d.rect(c, x + 150, y + 22, x + 164, y + 48, "#FFFFFF", radio=4)
    d.rect(c, x + 12, y + 12, x + 12 + 126 * d.clamp(nivel), y + 58, color, radio=8)


def senal(c, x, y, barras):
    for k in range(4):
        h = 22 + k * 18
        d.rect(c, x + k * 30, y - h, x + k * 30 + 20, y, "#FFFFFF", a=255 if k < barras else 70, radio=5)
    if barras == 0:
        d.linea(c, x - 10, y - 80, x + 120, y + 10, ROJO, ancho=10)


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # la ciudad se apaga
        F.foto(c, f(0), p, zoom=(1.0, 1.1), centro=(0.4, 0.55))
        corte = d.ease((p - 0.45) / 0.35)  # la oscuridad avanza de derecha a izquierda
        if corte > 0:
            borde = W * (1 - corte * 1.3)
            c.drawRect(skia.Rect.MakeLTRB(borde - 260, 0, W, H),
                       d.pintura(shader=d.grad_lineal(borde - 260, 0, borde, 0, [d.col("#000000", 0), d.col("#000000", 235)])))
        if 0.3 < p < 0.45:
            d.rect(c, 0, 0, W, H, "#000000", a=int(255 * (1 - parpadeo(gt, 1.2))))
    elif i == 1:  # semáforos muertos, caos
        F.foto(c, f(1), p, zoom=(1.05, 1.18), centro=(0.5, 0.6), brillo=0.85)
        for k in range(3):  # bocinazos
            d.onda_sonido(c, 300 + k * 260, 1150 + k * 60, gt + k * 0.3, "#FFFFFF", n=2, r0=25, paso=35, angulo=-90, apertura=70, ancho=6)
        d.etiqueta(c, "SEMÁFOROS APAGADOS", 540, 620, color=ROJO, texto_color="#FFFFFF", tam=44, a=d.aparece(lt, 0.6))
    elif i == 2:  # atrapados en el ascensor
        F.foto(c, f(2), p, zoom=(1.0, 1.15), centro=(0.5, 0.45), brillo=parpadeo(gt, 0.5))
        d.etiqueta(c, "ATRAPADOS", 540, 1450, color=AMARILLO, tam=50, a=d.aparece(lt, 0.5))
    elif i == 3:  # el celular contra reloj
        F.foto(c, f(3), p, zoom=(1.05, 1.2), centro=(0.5, 0.55))
        nivel = 0.8 - 0.7 * d.ease(p)
        bateria(c, 120, 560, nivel, "#46E08A" if nivel > 0.35 else ROJO)
        barras = 4 if p < 0.3 else (3 if p < 0.45 else (2 if p < 0.6 else (1 if p < 0.75 else 0)))
        senal(c, 820, 630, barras)
        d.etiqueta(c, "SIN SEÑAL", 540, 1450, color=ROJO, texto_color="#FFFFFF", tam=48, a=d.aparece(lt, dur * 0.78))
    elif i == 4:  # hospitales con generador
        F.foto(c, f(4), p, zoom=(1.0, 1.15), centro=(0.5, 0.6))
        pulso = 0.5 + 0.5 * math.sin(gt * 5)
        d.brillo(c, 465, 330, 300, "#FF9A3C", int(60 + 70 * pulso))
        d.rect(c, 0, 0, W, H, "#FF6A00", a=int(18 * pulso))
        d.etiqueta(c, "GENERADORES", 540, 1450, color=AMARILLO, tam=46, a=d.aparece(lt, 0.6))
        d.etiqueta(c, "¿Y EL COMBUSTIBLE?", 540, 1330, color="#FFFFFF", tam=40, a=d.aparece(lt, dur * 0.5))
    elif i == 5:  # la Vía Láctea
        F.foto(c, f(5), p, zoom=(1.18, 1.0), centro=(0.5, 0.35))
        for k in range(40):  # estrellas que titilan
            sx = (k * 263) % W
            sy = 450 + (k * 377) % 900
            tw = 0.5 + 0.5 * math.sin(gt * (2 + k % 5) + k)
            d.circulo(c, sx, sy, 2 + (k % 3), "#FFFFFF", a=int(200 * tw))
        d.etiqueta(c, "LOS ÁNGELES, 1994", 540, 1450, color=CIAN, tam=44, a=d.aparece(lt, 1.0))
    else:  # lo peor empieza mañana
        F.foto(c, f(6), p, zoom=(1.0, 1.12), centro=(0.5, 0.5), brillo=0.9)
        a = d.aparece(lt, dur * 0.35, 0.5)
        if a > 0:
            s = 1 + 0.05 * math.sin(gt * 5)
            c.save()
            c.translate(540, 1100)
            c.scale(s, s)
            d.etiqueta(c, "PARTE 2 →", 0, 0, color=AMARILLO, tam=70, a=a)
            c.restore()
