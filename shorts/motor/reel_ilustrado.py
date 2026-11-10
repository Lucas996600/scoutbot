"""Motor de reels ILUSTRADOS: cada escena es una animación 2D hecha a medida del tema.

El guion indica en "animacion" un archivo .py (en shorts/escenas/) que define:

    def escena(c, i, lt, gt, dur, esc):
        # c   = canvas Skia 1080x1920 (usar helpers de motor/dibujo.py)
        # i   = número de escena, lt = segundo dentro de la escena, gt = segundo global
        # dur = duración de la escena, esc = dict de la escena del guion
        ...

El motor agrega encima: el texto del dato ("pantalla") arriba, con la palabra
"destacar" en amarillo, y una viñeta suave. Sin barras ni etiquetas tipo historias.
"""
import importlib.util
import os
import subprocess

import skia

import dibujo as d

W, H, FPS = d.W, d.H, 30
AMARILLO = "#FFD400"


def cargar_modulo(ruta):
    spec = importlib.util.spec_from_file_location("escenas_tema", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def titulo(c, txt, destacar, lt, y_base=250):
    if not txt:
        return
    tam = 92 if len(txt) < 26 else (80 if len(txt) < 44 else 68)
    lineas = d.partir(txt, tam, 960, "titulo")
    a = d.ease_out(lt / 0.45)
    dy = (1 - a) * -60
    alto = len(lineas) * tam * 1.12
    # banda oscura suave arriba para que el texto se lea sobre cualquier ilustración
    d.rect(c, 0, 0, W, y_base + alto + 140, "#000", shader=d.grad_lineal(0, 0, 0, y_base + alto + 140, [d.col("#000000", 150), d.col("#000000", 0)]))
    marcadas = {_norm(x) for x in (destacar or "").split()}
    for k, ln in enumerate(lineas):
        palabras = ln.split()
        espacio = d.ancho_texto(" ", tam, "titulo")
        total = sum(d.ancho_texto(p, tam, "titulo") for p in palabras) + espacio * (len(palabras) - 1)
        x = (W - total) / 2
        y = y_base + k * tam * 1.12 + dy
        for p in palabras:
            color = AMARILLO if _norm(p) in marcadas and marcadas else "#FFFFFF"
            w = d.texto(c, p, x, y, tam, color, alinear="izquierda", tipo="titulo", contorno=10, a=int(255 * a))
            x += w + espacio


def render_clips(guion, duraciones, carpeta, ruta_animacion):
    os.makedirs(carpeta, exist_ok=True)
    mod = cargar_modulo(ruta_animacion)
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    escenas = guion["escenas"]
    rutas, gt0 = [], 0.0
    for i, esc in enumerate(escenas):
        ruta = os.path.join(carpeta, f"escena_{i:02d}.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                               "-pix_fmt", "yuv420p", ruta], stdin=subprocess.PIPE)
        n = max(1, round(duraciones[i] * FPS))
        for fr in range(n):
            lt = fr / FPS
            c = surf.getCanvas()
            c.clear(skia.ColorBLACK)
            c.save()
            mod.escena(c, i, lt, gt0 + lt, duraciones[i], esc)
            c.restore()
            d.vineta(c, 120)
            # en la 1ª escena el título ya está visible desde el cuadro 0 (gancho + miniatura)
            titulo(c, esc.get("pantalla", ""), esc.get("destacar", ""), lt if i > 0 else 1.0)
            # fundido corto de entrada entre escenas
            if i > 0 and lt < 0.2:
                d.rect(c, 0, 0, W, H, "#000000", a=int(200 * (1 - lt / 0.2)))
            ff.stdin.write(surf.makeImageSnapshot().tobytes())
        ff.stdin.close()
        ff.wait()
        gt0 += n / FPS
        rutas.append(ruta)
        print(f"  escena {i + 1}/{len(escenas)} lista ({duraciones[i]:.2f} s)", flush=True)
    return rutas


def previsualizar(guion, ruta_animacion, salida_png, momentos=(0.5,)):
    """Tira de cuadros (uno por escena) para revisar rápido sin generar el video."""
    from PIL import Image
    mod = cargar_modulo(ruta_animacion)
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    tiras = []
    for i, esc in enumerate(guion["escenas"]):
        for m in momentos:
            dur = 5.0
            lt = dur * m
            c = surf.getCanvas()
            c.clear(skia.ColorBLACK)
            c.save()
            mod.escena(c, i, lt, i * dur + lt, dur, esc)
            c.restore()
            d.vineta(c, 120)
            titulo(c, esc.get("pantalla", ""), esc.get("destacar", ""), lt)
            img = Image.frombytes("RGBA", (W, H), surf.makeImageSnapshot().tobytes()).convert("RGB").resize((270, 480))
            tiras.append(img)
    hoja = Image.new("RGB", (270 * len(tiras), 480))
    for k, im in enumerate(tiras):
        hoja.paste(im, (270 * k, 0))
    hoja.save(salida_png)
    return salida_png
