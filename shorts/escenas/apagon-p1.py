"""Escenas: ¿Y si el planeta entero se queda sin luz? — Parte 1 (la primera noche)."""
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "motor"))
import dibujo as d  # noqa: E402
from dibujo import W, H  # noqa: E402
import apagon_comun as A  # noqa: E402


def escena(c, i, lt, gt, dur, esc):
    p = lt / dur
    if i == 0:  # gancho: el planeta se apaga ya desde el primer segundo
        A.espacio(c, gt)
        apag = d.ease(d.clamp((lt - 0.25) / max(1.0, dur * 0.75)))
        with d.camara(c, zoom=1.0 + 0.1 * p, cx=540, cy=1050):
            A.planeta(c, 540, 1050, 470, gt, apagado=apag, rot=-0.05 * p)
        d.etiqueta(c, "20:00", 540, 500, color=A.ROJO, texto_color="#FFFFFF", tam=54, a=d.aparece(lt, 0.15, 0.3))
    elif i == 1:  # la ciudad se apaga, semáforos muertos, caos
        A.cielo_noche(c, gt)
        apag = d.ease(d.clamp(p / 0.45))
        A.ciudad(c, gt, suelo=1300, apagado=apag, parpadeo=1 - apag)
        d.rect(c, 0, 1300, W, H, "#16161C")
        for k in range(6):
            d.rect(c, 60 + k * 180, 1470, 160 + k * 180, 1484, "#F2F2F2", a=120)
        A.semaforo(c, 900, 1200, 0.9, luz=None if apag > 0.3 else 0)
        mov = 30 * math.sin(gt * 2)
        A.auto(c, 260 + mov * 0.3, 1420, 0.85, "#D9534F", t=gt)
        A.auto(c, 640 - mov * 0.2, 1560, 0.95, "#4F7BD9", t=gt)
        A.auto(c, -60, 1600, 0.8, "#E8B84A", t=gt)
        if apag > 0.5:
            for (bx, by) in ((300, 1300), (700, 1430)):
                d.onda_sonido(c, bx, by, gt, "#FFFFFF", n=3, r0=24, paso=34, angulo=-90, apertura=70, ancho=7)
            d.etiqueta(c, "¡BIP! ¡BIP!", 300, 1180, color="#FFFFFF", tam=40, a=d.aparece(lt, dur * 0.5))
    elif i == 2:  # atrapados en el ascensor
        d.fondo(c, "#0B0D12", "#050608")
        d.rect(c, 140, 520, 940, 1700, "#3C4250", radio=10, shader=d.grad_lineal(140, 0, 940, 0, ["#2A2F3A", "#4A5262", "#2A2F3A"]))
        d.linea(c, 540, 520, 540, 1700, "#14171D", ancho=10)
        tiembla = 6 * math.sin(gt * 30) * (1 - d.clamp(lt / 0.6))
        c.save()
        c.translate(tiembla, 0)
        A.persona(c, 330, 1480, 1.1, ropa="#B6433D", linterna=True, mira=0.5)
        A.persona(c, 560, 1500, 1.15, ropa="#3D6FB6", pelo="#C79A4A", mira=-0.5)
        A.persona(c, 790, 1480, 1.05, ropa="#4E8F5A", piel="#9C6B47", linterna=True, mira=-0.3)
        c.restore()
        d.rect(c, 0, 0, W, H, "#000000", a=110)
        # panel con piso trabado
        d.rect(c, 420, 560, 660, 650, "#0A0A0A", radio=12)
        d.texto(c, "-- " if (gt % 1) < 0.5 else "  ", 540, 628, 60, A.ROJO, tipo="titulo", sombra=False)
        d.etiqueta(c, "ATRAPADOS", 540, 1640 - 150, color=A.AMARILLO, tam=50, a=d.aparece(lt, 0.4))
    elif i == 3:  # el celular contra reloj
        d.fondo(c, "#0B1022", "#04060E")
        bat = 0.62 - 0.5 * d.ease(p)
        barras = 4 if p < 0.3 else 3 if p < 0.45 else 2 if p < 0.6 else 1 if p < 0.75 else 0
        d.brillo(c, 540, 1000, 500, "#3E8BD9", 60)
        A.celular_grande(c, 540, 1030, 1.2, bat, barras, gt)
        # torre de antena con batería
        tx, ty = 170, 1450
        d.linea(c, tx, ty, tx - 60, ty - 520, "#8892A6", ancho=10)
        d.linea(c, tx, ty, tx + 60, ty - 520, "#8892A6", ancho=10)
        for k in range(5):
            d.linea(c, tx - 60 + k * 10, ty - 100 * k, tx + 60 - k * 10, ty - 100 * k, "#8892A6", ancho=5)
        if barras > 0:
            d.onda_sonido(c, tx, ty - 540, gt, A.CIAN, n=3, r0=20, paso=40, angulo=0, apertura=80, ancho=6)
        d.etiqueta(c, "BATERÍA DE RESPALDO: HORAS", 540, 1420, color=A.AMARILLO, tam=36, a=d.aparece(lt, 0.8))
    elif i == 4:  # el cielo olvidado
        luz = d.ease(d.clamp(p / 0.6))
        A.cielo_noche(c, gt, estrellas=luz, via_lactea=d.ease(d.clamp((p - 0.35) / 0.4)))
        A.ciudad(c, gt, suelo=1560, apagado=1.0, escala=0.7)
        for k, (px, s) in enumerate(((330, 0.8), (560, 0.85), (770, 0.78))):  # siluetas mirando arriba
            c.save()
            c.translate(px, 1560)
            c.scale(s, s)
            d.figura(c, [(-70, 0), (-80, -150), (-40, -220), (40, -220), (80, -150), (70, 0)], "#05060A")
            d.circulo(c, 0, -280, 62, "#05060A")
            c.restore()
        d.etiqueta(c, "VÍA LÁCTEA", 760, 600, color="#E9DDFF", tam=44, a=d.aparece(lt, dur * 0.55))
    else:  # lo peor empieza mañana
        A.cielo_noche(c, gt, estrellas=0.6)
        A.ciudad(c, gt, suelo=1500, apagado=1.0)
        amanece = d.ease(p)
        d.rect(c, 0, 0, W, H, "#5A3A6E", a=int(70 * amanece))
        a = d.aparece(lt, dur * 0.3, 0.5)
        if a > 0:
            s = 1 + 0.06 * math.sin(gt * 6)
            c.save()
            c.translate(540, 1000)
            c.scale(s, s)
            d.etiqueta(c, "PARTE 2 →", 0, 0, color=A.AMARILLO, tam=84, a=a)
            c.restore()
