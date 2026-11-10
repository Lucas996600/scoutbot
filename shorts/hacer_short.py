"""guion.json -> short vertical terminado (voz, subtítulos palabra por palabra, música, animación).

Uso:
    python3 shorts/hacer_short.py shorts/guiones/delfines.json

Pasos:
  1. MoneyPrinterTurbo genera la voz (Edge TTS) y los subtítulos por palabra (--stop-at subtitle).
  2. Con los tiempos de cada palabra se calcula cuánto dura cada escena.
  3. El motor dibuja un clip por escena con esa duración exacta y se compone música original.
  4. MoneyPrinterTurbo arma el video final con esos clips, voz, subtítulos y música.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, "motor"))
import reel_textos  # noqa: E402
import reel_ilustrado  # noqa: E402
import musica  # noqa: E402
import zlib  # noqa: E402

MPT = os.environ.get("MPT_DIR", os.path.join(os.path.dirname(REPO), "tools", "MoneyPrinterTurbo"))
CA = "/root/.ccr/ca-bundle.crt"
VOZ_POR_DEFECTO = "fr-FR-RemyMultilingualNeural"  # la más expresiva en español (ver SKILL.md)


def mpt(args, log):
    env = dict(os.environ)
    if os.path.exists(CA):
        env.setdefault("SSL_CERT_FILE", CA)
    py = os.path.join(MPT, ".venv", "bin", "python")
    with open(log, "a") as fh:
        r = subprocess.run([py, "cli.py"] + args, cwd=MPT, env=env, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        sys.exit(f"MoneyPrinterTurbo falló (ver {log})")


def leer_srt(ruta):
    cues = []
    bloques = open(ruta, encoding="utf-8").read().strip().split("\n\n")
    for b in bloques:
        ls = b.strip().splitlines()
        if len(ls) < 3:
            continue
        a, z = ls[1].split(" --> ")
        seg = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(",", "."))
        cues.append((seg(a), seg(z), " ".join(ls[2:])))
    return cues


def norm(s):
    return re.sub(r"[^0-9a-záéíóúüñ]", "", s.lower())


def duraciones_por_escena(escenas, cues, total):
    """Reparte las palabras de los subtítulos entre escenas según la cantidad de letras de cada 'voz'."""
    largos = [len(norm(e["voz"])) for e in escenas]
    inicios = [0.0]
    acum, objetivo, i = 0, largos[0], 0
    for (a, z, txt) in cues:
        if i < len(escenas) - 1 and acum >= objetivo - 1:
            inicios.append(a - 0.08)
            i += 1
            objetivo += largos[i]
        acum += len(norm(txt))
    while len(inicios) < len(escenas):
        inicios.append(inicios[-1] + 2.0)
    bordes = inicios + [total]
    return [max(1.2, round(bordes[k + 1] - bordes[k], 3)) for k in range(len(escenas))]


def duracion_audio(ruta):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--voz", default=None, help="ej. es-AR-TomasNeural, es-AR-ElenaNeural, es-MX-DaliaNeural")
    ap.add_argument("--velocidad", type=float, default=None, help="1.0 normal, 1.2 = 20%% más rápido")
    a = ap.parse_args()

    g = json.load(open(a.guion, encoding="utf-8"))
    nombre = os.path.splitext(os.path.basename(a.guion))[0]
    salida = a.salida or os.path.join(AQUI, "salida", nombre)
    os.makedirs(salida, exist_ok=True)
    log = os.path.join(salida, "proceso.log")
    open(log, "w").close()

    voz = a.voz or g.get("voz", VOZ_POR_DEFECTO)
    genero = g.get("voz_genero") or ("Female" if any(n in voz for n in ("Elena", "Dalia", "Elvira", "Ximena", "Sofia", "Valentina", "Ava", "Emma", "Seraphina")) else "Male")
    vel = a.velocidad or g.get("velocidad", 1.05)
    # Pausas naturales: entre escenas y entre oraciones. MoneyPrinterTurbo sintetiza cada tramo por separado
    # (las voces Multilingual no se cuelgan con textos cortos) y une los tiempos de cada palabra.
    def con_pausas(txt):
        return re.sub(r"([.!?…])\s+(?=\S)", r"\1 [pause: 0.25s] ", txt.strip())
    guion_txt = " [pause: 0.45s] ".join(con_pausas(e["voz"]) for e in g["escenas"])
    comunes = ["--video-script", guion_txt, "--video-language", "es", "--video-aspect", "9:16",
               "--voice-name", f"{voz}-{genero}", "--voice-rate", str(vel)]

    print("1/4 Voz y subtítulos…", flush=True)
    t1 = str(uuid.uuid4())
    mpt(comunes + ["--video-terms", nombre, "--stop-at", "subtitle", "--task-id", t1], log)
    tarea1 = os.path.join(MPT, "storage", "tasks", t1)
    cues = leer_srt(os.path.join(tarea1, "subtitle.srt"))
    total = duracion_audio(os.path.join(tarea1, "audio.mp3"))
    durs = duraciones_por_escena(g["escenas"], cues, total)
    print(f"   audio {total:.1f} s · escenas {durs}", flush=True)

    print("2/4 Animando escenas…", flush=True)
    if g.get("animacion"):
        anim = g["animacion"] if os.path.isabs(g["animacion"]) else os.path.join(AQUI, g["animacion"])
        clips = reel_ilustrado.render_clips(g, durs, os.path.join(salida, "clips"), anim)
    else:
        clips = reel_textos.render_clips(g, durs, os.path.join(salida, "clips"))

    # música original sintetizada (las canciones que trae MoneyPrinterTurbo dan reclamos de Content ID)
    bgm = f"original-{nombre}.mp3"
    semilla = g.get("semilla_musica", zlib.crc32(nombre.encode()))
    musica.guardar(os.path.join(MPT, "storage", "bgm", bgm), total + 4, semilla)

    print("3/4 Armando el video final…", flush=True)
    t2 = str(uuid.uuid4())
    mpt(comunes + ["--video-terms", nombre, "--video-source", "local", "--video-materials", ",".join(clips),
                   "--video-concat-mode", "sequential", "--video-transition-mode", "none",
                   "--video-clip-duration", str(math.ceil(max(durs)) + 1),
                   "--bgm-type", "custom", "--bgm-file", bgm, "--bgm-volume", str(g.get("volumen_musica", 0.18)),
                   "--font-name", "BeVietnamPro-Bold.ttf", "--font-size", "84",
                   "--text-fore-color", "#FFFFFF", "--stroke-color", "#000000", "--stroke-width", "2.5",
                   "--subtitle-position", "custom", "--custom-position", str(g.get("posicion_subtitulos", 86 if g.get("animacion") else 76)),
                   "--subtitle-background-enabled", "--subtitle-background-color", "#000000", "--rounded-subtitle-background",
                   "--subtitle-display-mode", "word_by_word", "--subtitle-animation", "pop_spring",
                   "--task-id", t2], log)
    tarea2 = os.path.join(MPT, "storage", "tasks", t2)
    final = os.path.join(salida, f"{nombre}.mp4")
    shutil.copy(os.path.join(tarea2, "final-1.mp4"), final)
    shutil.copy(os.path.join(tarea2, "subtitle.srt"), os.path.join(salida, f"{nombre}.srt"))
    desfase = duracion_audio(os.path.join(tarea2, "audio.mp3")) - total

    print("4/4 Texto para publicar…", flush=True)
    with open(os.path.join(salida, "publicacion.txt"), "w", encoding="utf-8") as f:
        f.write(g.get("titulo", nombre) + "\n\n" + g.get("descripcion", "") + "\n\n" + " ".join(g.get("hashtags", [])) + "\n")
        f.write("\n---\nAl subir: Público → 'No, no es contenido creado para niños'. Música: original, generada para este video.\n")
    print(f"LISTO: {final}  (desfase de voz entre pasadas: {desfase:+.2f} s)")


if __name__ == "__main__":
    main()
