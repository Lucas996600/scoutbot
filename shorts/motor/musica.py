"""Música de fondo 100% original, sintetizada nota por nota (sin samples ni canciones de terceros).

Así YouTube/TikTok no encuentran coincidencias de Content ID. Cada `semilla` da otra canción
(tonalidad, tempo, progresión, melodía y timbres cambian).

    python3 musica.py salida.mp3 --segundos 75 --semilla 123
"""
import argparse
import os
import random
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
PROGRESIONES = [  # grados de la escala mayor (0 = I)
    [0, 4, 5, 3],   # I V vi IV
    [5, 3, 0, 4],   # vi IV I V
    [0, 5, 3, 4],   # I vi IV V
    [3, 4, 0, 5],   # IV V I vi
    [0, 3, 5, 4],   # I IV vi V
]
MAYOR = [0, 2, 4, 5, 7, 9, 11]
PENTA = [0, 2, 4, 7, 9]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, ataque=0.005, caida=0.3):
    t = np.arange(n) / SR
    e = np.exp(-t / max(caida, 1e-3))
    a = int(ataque * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def pasa_bajos(x, corte):
    """Pasa bajos suave (respuesta de 2 polos) aplicado en frecuencia."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / corte) ** 2), len(x))


def saw(f, n, fase=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f + fase) % 1) - 1


def acorde_notas(tonica, grado):
    return [tonica + MAYOR[(grado + k) % 7] + 12 * ((grado + k) // 7) for k in (0, 2, 4)]


def componer(segundos=75, semilla=0):
    rnd = random.Random(semilla)
    bpm = rnd.choice([92, 96, 100, 104, 108, 112])
    tonica = 48 + rnd.choice([0, 2, 3, 5, 7, 8, 10])  # C3..A#3
    prog = rnd.choice(PROGRESIONES)
    brillo = rnd.uniform(1400, 2600)
    beat = 60 / bpm
    compas = 4 * beat
    total = int(segundos * SR)
    mix = np.zeros(total + SR * 2)

    def poner(x, t0, vol):
        i = int(t0 * SR)
        j = min(len(mix), i + len(x))
        if i < len(mix):
            mix[i:j] += vol * x[: j - i]

    # motivo melódico (pentatónica) que se repite con variaciones
    motivo = [(rnd.choice([0, 1, 2, 3, 4]), rnd.choice([0.5, 0.5, 1.0])) for _ in range(6)]
    pads = {}
    n_comp = int(segundos / compas) + 1
    for k in range(n_comp):
        t0 = k * compas
        grado = prog[k % len(prog)]
        notas = acorde_notas(tonica, grado)
        intro = k < 2
        # pad
        clave = tuple(notas)
        if clave not in pads:
            n = int(compas * SR) + SR // 2
            x = sum(saw(hz(m + 12) * d, n, rnd.random()) for m in notas for d in (0.997, 1.003))
            x = pasa_bajos(x / 6, brillo * 0.5)
            e = np.minimum(1, np.arange(n) / (0.25 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.5 * SR))
            pads[clave] = x * e
        poner(pads[clave], t0, 0.22)
        # arpegio pulsado en corcheas
        arp = notas + [notas[0] + 12]
        for s in range(8):
            m = arp[[0, 1, 2, 3, 2, 1, 2, 3][s]] + 12
            n = int(beat * 0.9 * SR)
            t = np.arange(n) / SR
            f = hz(m)
            x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * env(n, 0.003, 0.18)
            poner(x, t0 + s * beat / 2, 0.10 if intro else 0.13)
        if intro:
            continue
        # bajo
        for s in range(4):
            n = int(beat * 0.95 * SR)
            t = np.arange(n) / SR
            f = hz(notas[0] - 12)
            x = np.tanh(1.6 * np.sin(2 * np.pi * f * t)) * env(n, 0.004, 0.35)
            poner(x, t0 + s * beat, 0.30)
        # batería sintetizada
        for s in range(4):
            if s in (0, 2):
                n = int(0.35 * SR)
                t = np.arange(n) / SR
                fr = 50 + 110 * np.exp(-t * 30)
                x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.001, 0.12)
                poner(x, t0 + s * beat, 0.45)
            else:
                n = int(0.2 * SR)
                ruido = np.random.default_rng(semilla + k * 7 + s).standard_normal(n)
                x = (ruido - pasa_bajos(ruido, 900)) * env(n, 0.001, 0.06)
                poner(x, t0 + s * beat, 0.09)
            for h in (0, 1):
                n = int(0.06 * SR)
                ruido = np.random.default_rng(semilla + k * 13 + s * 2 + h).standard_normal(n)
                x = (ruido - pasa_bajos(ruido, 6000)) * env(n, 0.0005, 0.015)
                poner(x, t0 + s * beat + h * beat / 2, 0.035)
        # melodía (cada 2 compases, en la segunda mitad del ciclo)
        if k % 2 == 1:
            tt = t0
            var = rnd.choice([0, 0, 1, 2])
            for (g, dur) in motivo:
                gg = (g + var) % 5
                m = tonica + 24 + PENTA[gg]
                n = int(dur * beat * SR)
                t = np.arange(n) / SR
                vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
                x = (np.sin(2 * np.pi * hz(m) * t * vib) + 0.2 * np.sin(4 * np.pi * hz(m) * t)) * env(n, 0.01, dur * beat * 0.7)
                poner(x, tt, 0.12)
                tt += dur * beat
    mix = mix[:total]
    fade = int(2.5 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix[: int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.85
    return mix


def guardar(ruta, segundos=75, semilla=0):
    audio = componer(segundos, semilla)
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav = tmp.name
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "160k", ruta], check=True)
    os.remove(wav)
    return ruta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("--segundos", type=float, default=75)
    ap.add_argument("--semilla", type=int, default=0)
    a = ap.parse_args()
    print(guardar(a.salida, a.segundos, a.semilla))
