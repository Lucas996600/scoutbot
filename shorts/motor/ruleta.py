"""LA RULETA DEL MUNDO — intro oficial de la serie "¿Cómo sería el mundo sin...?".

Siempre el mismo diseño (identidad del canal): ruleta de juguete flotando en el espacio, 12 porciones de colores
con íconos, borde dorado con lamparitas, flecha-rayo roja arriba y Globi (la Tierra caricatura) que la patea.

Uso en una escena:   import ruleta; ruleta.dibujar(c, lt, dur, "luz", gt)
Sonido de marca:     ruleta.sfx("sfx.wav", dur)   (hacer_short.py lo mezcla solo si el guion tiene "ruleta")
"""
import math
import os
import random
import subprocess
import tempfile
import wave

import numpy as np
import skia

import dibujo as d
from dibujo import W, H

CX, CY, R = 540, 1060, 400
COLORES = ["#8E5BFF", "#20C9C2", "#FF8A3D", "#FF5FA2", "#9BE34A", "#FFC93C"]
ELEMENTOS = [  # (clave, emoji) — 12 porciones; la elegida se agrega si no está
    ("agua", "💧"), ("luz", "💡"), ("internet", "📶"), ("gravedad", "🪐"), ("ojos", "👀"), ("dinero", "💰"),
    ("animales", "🐾"), ("tiempo", "⏰"), ("arboles", "🌳"), ("sol", "☀️"), ("abejas", "🐝"), ("sonido", "🔊"),
]
EMOJIS_EXTRA = {"oxigeno": "🫧", "luna": "🌙", "viento": "🌬️", "lluvia": "🌧️", "dolor": "🤕", "sueño": "😴",
                "electricidad": "⚡", "plastico": "🧴", "relojes": "⌚", "colores": "🎨", "noche": "🌃", "silencio": "🤫",
                "ruedas": "🛞", "memoria": "🧠", "olfato": "👃", "oido": "👂", "huesos": "🦴", "volcanes": "🌋",
                "nubes": "☁️", "numeros": "🔢", "friccion": "🧊"}
VUELTAS = 6
FRENA = 0.68  # fracción de la escena en la que se detiene (si no se conoce el momento exacto)
T_FRENO = None  # segundos: hacer_short.py lo fija justo antes de que la voz diga el elemento elegido


def _porciones(elegido):
    el = list(ELEMENTOS)
    claves = [k for k, _ in el]
    if elegido not in claves:
        el[5] = (elegido, EMOJIS_EXTRA.get(elegido, "❓"))
    idx = [k for k, _ in el].index(elegido)
    return el, idx


def angulo(lt, dur, idx):
    """Rotación (grados, horario) en el tiempo lt. Arranca rapidísimo y frena justo en la porción idx."""
    fin = 360 * VUELTAS - (idx + 0.5) * 30
    tf = T_FRENO or dur * FRENA
    x = d.clamp(lt / tf)
    return fin * (1 - (1 - x) ** 3.2), x >= 1


def tiempos_tic(dur, idx, fps=200):
    tics, prev = [], 0
    for k in range(int((T_FRENO or dur * FRENA) * fps) + 1):
        a, _ = angulo(k / fps, dur, idx)
        n = int(a // 30)
        if n != prev:
            tics.append(k / fps)
            prev = n
    return tics


# ------------------------------------------------------------------ dibujo

def fondo_espacio(c, t):
    d.fondo(c, "#1A0B3D", "#07051A")
    d.elipse(c, 250, 700, 420, 260, "#FF5FA2", a=45, blur=120)
    d.elipse(c, 850, 1400, 460, 300, "#3D7BFF", a=45, blur=130)
    d.elipse(c, 800, 500, 300, 200, "#8E5BFF", a=50, blur=110)
    rnd = random.Random(21)
    for k in range(140):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.8, 3)
        tw = 0.55 + 0.45 * math.sin(t * rnd.uniform(1, 4) + k)
        d.circulo(c, x, y, r, "#FFFFFF", a=int(220 * tw))
    if d.TINTA:
        d.destellos(c, t, n=16, semilla=4, y_max=H - 200)
    # luna que espía
    mx, my = 960, 560
    d.circulo(c, mx, my, 120, "#E9E4FF", shader=d.grad_radial(mx - 40, my - 40, 170, ["#FFFFFF", "#BDB4E8"]))
    for (ox, oy, rr) in ((-30, 30, 22), (35, -20, 14), (10, 60, 12)):
        d.circulo(c, mx + ox, my + oy, rr, "#A99FD6", a=150)
    for sx in (-1, 1):
        ex = mx - 50 + sx * 26
        d.circulo(c, ex, my - 5, 13, "#FFFFFF")
        d.circulo(c, ex - 4, my - 3, 7, "#2B1D4D")


def globi(c, x, y, s, t, expresion="normal", mira=0.0, patea=0.0):
    """Globi: la Tierra caricatura con ojos enormes. (x, y) = centro."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    d.elipse(c, 0, 150, 120, 22, "#000000", a=110, blur=16)
    # piernitas y bracitos
    for sx in (-1, 1):
        ang = -35 * patea if sx == 1 else 0
        c.save()
        c.translate(sx * 45, 95)
        c.rotate(ang)
        d.rect(c, -9, 0, 9, 55, "#2B3A7A", radio=9)
        d.elipse(c, 6 * sx, 58, 22, 12, "#FF5FA2")
        c.restore()
        brazo = [(sx * 100, 0), (sx * 150, -30 + 15 * math.sin(t * 4 + sx)), (sx * 170, -70)]
        c.drawPath(d.camino(brazo, False, True), d.pintura("#2B3A7A", trazo=10))
        d.circulo(c, sx * 172, -74, 14, "#FFFFFF")
    # esfera con volumen
    d.circulo(c, 0, 0, 120, "#2E7BEF", shader=d.grad_radial(-40, -50, 190, ["#7FC4FF", "#2E7BEF", "#173E9A"]))
    c.save()
    pth = skia.Path()
    pth.addCircle(0, 0, 120)
    c.clipPath(pth, doAntiAlias=True)
    gir = (t * 18) % 240
    for (cx, cy, pts) in ((-60, -40, [(-50, -30), (10, -50), (40, -10), (0, 30), (-40, 20)]),
                          (60, 30, [(-30, -40), (30, -30), (45, 30), (0, 60), (-35, 20)])):
        for off in (0, -240, 240):
            sh = [(cx + px + gir + off - 120, cy + py) for px, py in pts]
            d.figura(c, sh, "#4CC36A", shader=d.grad_lineal(0, -80, 0, 80, ["#7BE38F", "#2E9A4E"]))
    c.restore()
    d.circulo(c, 0, 0, 120, "#FFFFFF", a=0, shader=d.grad_radial(30, 40, 150, [d.col("#000000", 0), d.col("#000000", 0), d.col("#0A1240", 140)], [0, 0.6, 1]))
    d.elipse(c, -45, -60, 40, 22, "#FFFFFF", a=150, blur=6)  # brillo especular
    d.circulo(c, 0, 0, 121, "#9FE6FF", a=110, trazo=5)  # luz de contorno
    # cara
    for sx in (-1, 1):
        ex, ey = sx * 38, -10
        alto = 34 if expresion != "susto" else 40
        d.elipse(c, ex, ey, 27, alto, "#FFFFFF")
        if expresion == "feliz":
            c.drawPath(d.camino([(ex - 18, ey + 6), (ex, ey - 10), (ex + 18, ey + 6)], False, True), d.pintura("#1B1B3A", trazo=7))
        else:
            d.circulo(c, ex + mira * 9, ey + 4, 15, "#1B1B3A")
            d.circulo(c, ex + mira * 9 - 5, ey - 3, 6, "#FFFFFF")
    if expresion == "susto":
        d.elipse(c, 0, 60, 22, 28, "#5A1028")
    elif expresion == "feliz":
        c.drawPath(d.camino([(-30, 45), (0, 70), (30, 45)], False, True), d.pintura("#1B1B3A", trazo=7))
    else:
        c.drawPath(d.camino([(-20, 52), (0, 60), (20, 52)], False, True), d.pintura("#1B1B3A", trazo=6))
    d.elipse(c, -70, 35, 16, 9, "#FF7FA8", a=150)
    d.elipse(c, 70, 35, 16, 9, "#FF7FA8", a=150)
    c.restore()


def rueda(c, rot, t, idx, gana=0.0, porciones=None):
    # sombra y grosor (canto) para que se vea como objeto 3D
    d.elipse(c, CX + 20, CY + R + 90, R * 0.9, 50, "#000000", a=120, blur=40)
    d.circulo(c, CX, CY + 34, R + 26, "#7A4A12", shader=d.grad_lineal(0, CY - R, 0, CY + R + 60, ["#C98A2E", "#6A3E0E"]))
    # aro dorado
    d.circulo(c, CX, CY, R + 26, "#FFC93C", shader=d.grad_radial(CX - 150, CY - 200, R * 1.6, ["#FFF2B0", "#FFC93C", "#B57A12"]))
    # porciones
    c.save()
    c.translate(CX, CY)
    c.rotate(rot)
    for k in range(12):
        a0 = -90 + k * 30
        colr = COLORES[k % len(COLORES)]
        pth = skia.Path()
        pth.moveTo(0, 0)
        pth.arcTo(skia.Rect.MakeLTRB(-R, -R, R, R), a0, 30, False)
        pth.close()
        c.drawPath(pth, d.pintura(shader=d.grad_radial(0, 0, R, [d.mezcla(colr, "#FFFFFF", 0.35), colr, d.mezcla(colr, "#000000", 0.25)], [0, 0.55, 1])))
        if k == idx and gana > 0:
            c.drawPath(pth, d.pintura("#FFFFFF", int(120 * gana * (0.6 + 0.4 * math.sin(t * 14)))))
        ang = math.radians(a0)
        d.linea(c, 0, 0, R * math.cos(ang), R * math.sin(ang), d.TINTA["color"] if d.TINTA else "#FFE58A", ancho=9 if d.TINTA else 7)
    for k in range(12):
        ang = math.radians(-90 + k * 30 + 15)
        ex, ey = R * 0.68 * math.cos(ang), R * 0.68 * math.sin(ang)
        emo = porciones[k][1]
        d.circulo(c, ex + 6, ey + 10, 52, "#000000", a=60, blur=8)
        d.emoji(c, emo, ex, ey, 96, rot=math.degrees(ang) + 90)
    c.restore()
    if d.TINTA:  # contornos de tinta del disco y del aro
        d.circulo(c, CX, CY, R, d.TINTA["color"], trazo=d.TINTA["ancho"] + 2)
        d.circulo(c, CX, CY, R + 26, d.TINTA["color"], trazo=d.TINTA["ancho"] + 2)
    # lamparitas del borde (persecución)
    for k in range(24):
        ang = math.radians(k * 15)
        bx, by = CX + (R + 13) * math.cos(ang), CY + (R + 13) * math.sin(ang)
        on = (k + int(t * 12)) % 3 == 0 or gana > 0 and (int(t * 8) % 2 == 0)
        if on:
            d.brillo(c, bx, by, 26, "#FFF6C8", 200)
        d.circulo(c, bx, by, 9, "#FFFDF0" if on else "#B88A2E")
    # brillo de vidrio (fijo, no gira): vende el volumen
    d.elipse(c, CX - 130, CY - 190, 210, 90, "#FFFFFF", a=55, blur=26)
    # cubo central
    d.circulo(c, CX, CY + 10, 92, "#000000", a=90, blur=12)
    d.circulo(c, CX, CY, 88, "#FFC93C", shader=d.grad_radial(CX - 30, CY - 35, 130, ["#FFF6CC", "#FFC93C", "#9A6408"]))
    d.circulo(c, CX, CY, 56, "#2E7BEF", shader=d.grad_radial(CX - 18, CY - 20, 80, ["#9FD8FF", "#2E7BEF", "#173E9A"]))
    d.elipse(c, CX - 18, CY - 22, 16, 9, "#FFFFFF", a=180)


def flecha(c, tic_fase):
    """Flecha-rayo roja arriba; se sacude con cada tic."""
    c.save()
    c.translate(CX, CY - R - 40)
    c.rotate(-18 * math.exp(-tic_fase * 18))
    d.figura(c, [(-50, -70), (40, -70), (8, -10), (42, -10), (-6, 90), (6, 20), (-34, 20)], "#000000", a=90, suave=False)
    d.figura(c, [(-46, -76), (44, -76), (12, -16), (46, -16), (-2, 84), (10, 14), (-30, 14)], "#FF3B4E", suave=False,
             shader=d.grad_lineal(-46, -76, 46, 84, ["#FF8A95", "#FF3B4E", "#B3122A"]))
    d.circulo(c, -2, 84, 12, "#FFF6C8")
    d.brillo(c, -2, 84, 40, "#FFF6C8", 160)
    c.restore()


def dibujar(c, lt, dur, elegido, gt):
    porciones, idx = _porciones(elegido)
    rot, parado = angulo(lt, dur, idx)
    t_stop = T_FRENO or dur * FRENA
    gana = d.clamp((lt - t_stop) / 0.2) if parado else 0.0
    vuela = d.clamp((lt - t_stop - 0.25) / 0.55)
    # empujón de cámara al frenar
    zoom = 1.0 + 0.06 * d.ease(d.clamp(lt / t_stop)) + 0.12 * d.ease(vuela)
    tics = tiempos_tic(dur, idx)
    ult = max([x for x in tics if x <= lt], default=-9)
    with d.camara(c, zoom=zoom, cx=CX, cy=CY - 60):
        fondo_espacio(c, gt)
        if lt < 0.6:  # estela de velocidad
            for k in range(10):
                d.linea(c, 0, 400 + k * 140, W, 400 + k * 140 - 60, "#FFFFFF", ancho=2, a=int(40 * (1 - lt / 0.6)))
        rueda(c, rot, gt, idx, gana, porciones)
        flecha(c, lt - ult)
        expresion = "feliz" if lt < 0.5 else ("susto" if gana > 0 else "normal")
        globi(c, 170, 1500, 0.95, gt, expresion=expresion, mira=0.6 * math.sin(gt * 9) if not parado else 1.0,
              patea=d.clamp(1 - lt / 0.35))
    if vuela > 0:  # el ícono ganador vuela hacia la cámara
        d.rect(c, 0, 0, W, H, "#07051A", a=int(160 * vuela))
        for k in range(16):  # rayos de revelación
            ang = math.radians(k * 22.5 + gt * 30)
            d.figura(c, [(CX, CY), (CX + 1400 * math.cos(ang - 0.06), CY + 1400 * math.sin(ang - 0.06)),
                         (CX + 1400 * math.cos(ang + 0.06), CY + 1400 * math.sin(ang + 0.06))], "#FFE58A", a=int(70 * vuela), suave=False)
        d.brillo(c, CX, CY, 420 * vuela, "#FFF2B0", int(200 * vuela))
        tam = int(d.lerp(110, 520, d.ease_out_back(vuela)))
        d.emoji(c, porciones[idx][1], CX, CY, tam, rot=10 * math.sin(gt * 3))


# ------------------------------------------------------------------ sonido de marca

SR = 44100


def _env(n, caida):
    return np.exp(-np.arange(n) / SR / caida)


def sfx(ruta, dur, elegido="luz", total=None, semilla=1):
    """Pista de efectos de la ruleta (wav): whoosh inicial, tics sincronizados, ding+platillo y whoosh del ícono."""
    _, idx = _porciones(elegido)
    total = total or dur + 1.5
    mix = np.zeros(int(total * SR))
    rng = np.random.default_rng(semilla)

    def poner(x, t0, vol):
        i = int(t0 * SR)
        j = min(len(mix), i + len(x))
        if 0 <= i < len(mix):
            mix[i:j] += vol * x[: j - i]

    def whoosh(largo, sube=True):
        n = int(largo * SR)
        ruido = rng.standard_normal(n)
        X = np.fft.rfft(ruido)
        f = np.fft.rfftfreq(n, 1 / SR)
        X *= np.exp(-((f - 1800) / 1400) ** 2)
        x = np.fft.irfft(X, n)
        forma = np.sin(np.linspace(0, np.pi, n)) ** (0.6 if sube else 1.5)
        return x / (np.max(np.abs(x)) + 1e-9) * forma

    poner(whoosh(0.5), 0.0, 0.5)
    for k, tt in enumerate(tiempos_tic(dur, idx)):
        n = int(0.03 * SR)
        tt_ = np.arange(n) / SR
        clic = (np.sin(2 * np.pi * 2300 * tt_) * 0.6 + rng.standard_normal(n) * 0.4) * _env(n, 0.006)
        poner(clic, tt, 0.55)
    t_stop = T_FRENO or dur * FRENA
    n = int(1.6 * SR)
    tt_ = np.arange(n) / SR
    ding = (np.sin(2 * np.pi * 1318.5 * tt_) + 0.5 * np.sin(2 * np.pi * 2637 * tt_) + 0.25 * np.sin(2 * np.pi * 3955 * tt_)) * _env(n, 0.45)
    poner(ding / 1.75, t_stop, 0.6)
    plat = rng.standard_normal(n)
    plat = plat - np.convolve(plat, np.ones(8) / 8, mode="same")
    poner(plat * _env(n, 0.35), t_stop + 0.02, 0.18)
    boom = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-tt_ * 8)) / SR) * _env(n, 0.3)
    poner(boom, t_stop + 0.25, 0.6)
    poner(whoosh(0.55), t_stop + 0.25, 0.45)
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.9
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    return ruta


def mezclar(video, sfx_wav, salida, vol=1.0):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", sfx_wav, "-filter_complex",
                    f"[1:a]volume={vol}[s];[0:a][s]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", salida], check=True)
