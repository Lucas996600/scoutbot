"""Motor de episodios con DIÁLOGOS (estilo caricatura "garabato" con la escena en una franja central).

Guion (JSON):
{
  "titulo": "...", "descripcion": "...", "hashtags": [...],
  "animacion": "escenas/<slug>.py", "ruleta": "luz", "estilo": "tinta",
  "personajes": {"narrador": {"voz": "fr-FR-RemyMultilingualNeural", "velocidad": "+5%", "tono": "+0Hz", "color": "#E9FF8A", "nombre": ""},
                 "tito": {"voz": "es-AR-TomasNeural", "color": "#7FE3FF", "nombre": "TITO"}},
  "escenas": [ {"pantalla": "...", "destacar": "...", "formato": "completo"|"franja",
                "lineas": [ {"quien": "tito", "texto": "..."} , ... ]} ]
}
La escena recibe en esc["_habla"] un dict {personaje: apertura_de_boca 0..1} para mover la boca de quien habla.
En formato "franja" la escena dibuja en un lienzo de 1920x1080 que el motor ubica en el centro del vertical.
"""
import importlib.util
import json
import math
import os
import subprocess
import zlib

import numpy as np
import skia

import dibujo as d
import musica
import reel_ilustrado
import ruleta
import voces

W, H, FPS = d.W, d.H, 24
BW, BH = 1920, 1080
ESC = W / BW
BY0 = (H - BH * ESC) / 2 - 40  # franja un poco arriba del centro: deja más lugar abajo para subtítulos
FONDO, ESTRELLAS = "#170D33", ("#C8F27A", "#7FE3D0", "#FFFFFF")
PAUSA_LINEA, PAUSA_ESCENA = 0.14, 0.25


def armar_audio(g):
    pers = g["personajes"]
    pista, t, lineas, escenas = [], 0.0, [], []
    for i, esc in enumerate(g["escenas"]):
        t0 = t
        for ln in esc["lineas"]:
            p = pers[ln["quien"]]
            audio, pal = voces.sintetizar(ln["texto"], p["voz"], p.get("velocidad", "+0%"), p.get("tono", "+0Hz"))
            audio = _nivelar(audio)
            pista.append((t, audio))
            dur = len(audio) / voces.SR
            lineas.append(dict(escena=i, quien=ln["quien"], texto=ln["texto"], t0=t, t1=t + dur,
                               palabras=[(t + a, t + b, w) for a, b, w in pal]))
            t += dur + ln.get("pausa", PAUSA_LINEA)
        t += esc.get("pausa_final", PAUSA_ESCENA)
        escenas.append((t0, t))
    total = t + 0.3
    voz = np.zeros(int(total * voces.SR) + 1, np.float32)
    for (t_, a) in pista:
        i = int(t_ * voces.SR)
        voz[i:i + len(a)] += a[: len(voz) - i]
    return voz, lineas, escenas, total


def _nivelar(a, objetivo=0.085):
    """Todas las voces al mismo volumen (RMS de las partes habladas) y sin picos."""
    if len(a) == 0:
        return a
    tramos = a[: len(a) // 240 * 240].reshape(-1, 240)
    rms = np.sqrt((tramos ** 2).mean(axis=1))
    hablado = rms[rms > rms.max() * 0.15]
    nivel = np.sqrt((hablado ** 2).mean()) if len(hablado) else 1e-3
    a = a * (objetivo / max(nivel, 1e-4))
    return np.tanh(a * 1.2) / 1.2  # limitador suave


def boca(lineas, t):
    """{personaje: apertura} según quién está diciendo una palabra en el instante t."""
    out = {}
    for ln in lineas:
        if ln["t0"] - 0.05 <= t <= ln["t1"]:
            for (a, b, _) in ln["palabras"]:
                if a <= t <= b + 0.04:
                    out[ln["quien"]] = 0.35 + 0.65 * abs(math.sin((t - a) * 13))
                    break
            else:
                out.setdefault(ln["quien"], 0.0)
    return out


def subtitulo(c, ln, t, pers):
    if ln is None:
        return
    p = pers[ln["quien"]]
    nombre = p.get("nombre", ln["quien"].upper())
    y = 1530
    if nombre:
        d.etiqueta(c, nombre, W / 2, y - 105, color=p.get("color", "#FFFFFF"), texto_color="#170D33", tam=36)
    palabras = ln["texto"].split()
    tam = 62
    lineas_txt, actual = [], []
    for w in palabras:
        prueba = " ".join(actual + [w])
        if d.ancho_texto(prueba, tam, "titulo") > 960 and actual:
            lineas_txt.append(actual)
            actual = [w]
        else:
            actual.append(w)
    lineas_txt.append(actual)
    # palabra que se está diciendo (por orden); se muestran de a 2 filas (paginado) para textos largos
    dichas = sum(1 for (a, b, _) in ln["palabras"] if t >= a)
    acum, fila_actual = 0, 0
    for j, fila in enumerate(lineas_txt):
        if dichas > acum:
            fila_actual = j
        acum += len(fila)
    inicio = fila_actual - fila_actual % 2
    k = sum(len(f) for f in lineas_txt[:inicio])
    esp = d.ancho_texto(" ", tam, "titulo")
    for j, fila in enumerate(lineas_txt[inicio:inicio + 2]):
        total = sum(d.ancho_texto(w, tam, "titulo") for w in fila) + esp * (len(fila) - 1)
        x = (W - total) / 2
        for w in fila:
            k += 1
            color = "#FFE14D" if k == dichas else ("#FFFFFF" if k < dichas else "#B9B2D6")
            ancho = d.texto(c, w, x, y + j * tam * 1.15, tam, color, alinear="izquierda", tipo="titulo", contorno=10,
                            color_contorno="#170D33", sombra=False)
            x += ancho + esp


def cargar_modulo(ruta):
    spec = importlib.util.spec_from_file_location("escenas_dialogo", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def marco(c, t):
    d.rect(c, 0, 0, W, H, FONDO)
    d.destellos(c, t * 0.5, n=26, semilla=12, colores=ESTRELLAS, y_max=H - 40)


def cuadro(c, mod, g, lineas, escenas, t):
    i = max(k for k, (a, b) in enumerate(escenas) if t >= a or k == 0)
    a, b = escenas[i]
    esc = dict(g["escenas"][i])
    esc["_habla"] = boca(lineas, t)
    lt, dur = t - a, b - a
    c.clear(skia.ColorBLACK)
    if esc.get("formato") == "completo":
        mod.escena(c, i, lt, t, dur, esc)
    else:
        marco(c, t)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(0, BY0, W, BH * ESC), doAntiAlias=True)
        c.translate(0, BY0)
        c.scale(ESC, ESC)
        mod.escena(c, i, lt, t, dur, esc)
        c.restore()
        d.rect(c, 0, BY0, W, BY0 + BH * ESC, "#0B0620", trazo=6, a=200)
    reel_ilustrado.titulo(c, esc.get("pantalla", ""), esc.get("destacar", ""), lt if i > 0 else 1.0, y_base=230)
    if i > 0 and lt < 0.18:
        d.rect(c, 0, 0, W, H, "#000000", a=int(200 * (1 - lt / 0.18)))
    actual = next((ln for ln in lineas if ln["t0"] - 0.1 <= t <= ln["t1"] + 0.25), None)
    subtitulo(c, actual, t, g["personajes"])


def hacer(ruta_guion, salida=None):
    g = json.load(open(ruta_guion, encoding="utf-8"))
    aqui = os.path.dirname(os.path.abspath(ruta_guion))
    nombre = os.path.splitext(os.path.basename(ruta_guion))[0]
    salida = salida or os.path.join(aqui, "..", "salida", nombre)
    os.makedirs(salida, exist_ok=True)
    reel_ilustrado.aplicar_estilo(g)

    print("1/3 Voces de cada personaje…", flush=True)
    voz, lineas, escenas, total = armar_audio(g)
    wav_voz = os.path.join(salida, "voces.wav")
    _guardar_wav(wav_voz, voz, voces.SR)
    if g.get("ruleta"):
        primera = lineas[0]
        ultima = primera["palabras"][-1] if primera["palabras"] else (primera["t1"] - 0.4, primera["t1"], "")
        ruleta.T_FRENO = max(1.5, ultima[0] - 0.15)
    print(f"   {len(lineas)} líneas · {total:.1f} s · escenas {[round(b - a, 2) for a, b in escenas]}", flush=True)

    print("2/3 Animando…", flush=True)
    anim = g["animacion"] if os.path.isabs(g["animacion"]) else os.path.join(aqui, "..", g["animacion"])
    mod = cargar_modulo(anim)
    mus = os.path.join(salida, "musica.mp3")
    musica.guardar(mus, total + 2, g.get("semilla_musica", zlib.crc32(nombre.encode())))
    entradas = ["-i", wav_voz, "-i", mus]
    mezcla = f"[1:a]volume=1.0[v];[2:a]volume={g.get('volumen_musica', 0.12)}[m]"
    pistas = "[v][m]"
    if g.get("ruleta"):
        sfx = ruleta.sfx(os.path.join(salida, "sfx.wav"), escenas[0][1], g["ruleta"], total=escenas[0][1] + 2.5)
        entradas += ["-i", sfx]
        mezcla += f";[3:a]volume={g.get('volumen_ruleta', 0.8)}[s]"
        pistas += "[s]"
    n_p = pistas.count("[")
    final = os.path.join(salida, f"{nombre}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", *entradas, "-filter_complex", f"{mezcla};{pistas}amix=inputs={n_p}:duration=first:normalize=0[a0];[a0]loudnorm=I=-15:TP=-1.5:LRA=11[a]",
                           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", final], stdin=subprocess.PIPE)
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    n = int(total * FPS)
    for fr in range(n):
        cuadro(surf.getCanvas(), mod, g, lineas, escenas, fr / FPS)
        ff.stdin.write(surf.makeImageSnapshot().tobytes())
        if fr % (FPS * 10) == 0:
            print(f"   {fr / FPS:.0f}/{total:.0f} s", flush=True)
    ff.stdin.close()
    ff.wait()

    print("3/3 Texto para publicar…", flush=True)
    with open(os.path.join(salida, "publicacion.txt"), "w", encoding="utf-8") as f:
        f.write(g.get("titulo", nombre) + "\n\n" + g.get("descripcion", "") + "\n\n" + " ".join(g.get("hashtags", [])) + "\n")
        f.write("\n---\nAl subir: Público → 'No, no es contenido creado para niños'. Música: original, generada para este video.\n")
    json.dump(dict(lineas=lineas, escenas=escenas, total=total), open(os.path.join(salida, "tiempos.json"), "w"), ensure_ascii=False)
    print(f"LISTO: {final}")
    return final


def previsualizar(ruta_guion, salida_png, momentos=(0.5,)):
    """Tira de cuadros con los tiempos reales (necesita sintetizar las voces, que quedan en caché)."""
    from PIL import Image
    g = json.load(open(ruta_guion, encoding="utf-8"))
    aqui = os.path.dirname(os.path.abspath(ruta_guion))
    reel_ilustrado.aplicar_estilo(g)
    _, lineas, escenas, _ = armar_audio(g)
    if g.get("ruleta"):
        ruleta.T_FRENO = max(1.5, lineas[0]["palabras"][-1][0] - 0.15)
    mod = cargar_modulo(os.path.join(aqui, "..", g["animacion"]))
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    tiras = []
    for (a, b) in escenas:
        for m in momentos:
            cuadro(surf.getCanvas(), mod, g, lineas, escenas, a + (b - a) * m)
            tiras.append(Image.frombytes("RGBA", (W, H), surf.makeImageSnapshot().tobytes()).convert("RGB").resize((270, 480)))
    hoja = Image.new("RGB", (270 * len(tiras), 480))
    for k, im in enumerate(tiras):
        hoja.paste(im, (270 * k, 0))
    hoja.save(salida_png)
    return salida_png


def _guardar_wav(ruta, audio, sr):
    import wave
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    import sys
    hacer(sys.argv[1])
