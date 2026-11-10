"""Voces con Edge TTS para diálogos: cada personaje con su voz, velocidad y tono, y el tiempo de cada palabra.

    audio, palabras = voces.sintetizar("Che, ¿se cortó la luz?", "es-AR-TomasNeural", "+0%", "+0Hz")
    # audio: np.float32 mono a 24 kHz; palabras: [(inicio, fin, "texto"), ...] en segundos
Se guarda en caché (shorts/.cache_voces) para no volver a pedir lo mismo.
"""
import asyncio
import hashlib
import json
import os
import subprocess

import numpy as np

SR = 24000
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache_voces")
CA = "/root/.ccr/ca-bundle.crt"


async def _pedir(texto, voz, rate, pitch, ruta_mp3):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch, boundary="WordBoundary",
                               proxy=os.environ.get("HTTPS_PROXY") or None, receive_timeout=60)
    palabras, datos = [], bytearray()
    async for ch in com.stream():
        if ch["type"] == "audio":
            datos += ch["data"]
        elif ch["type"] == "WordBoundary":
            t0 = ch["offset"] / 1e7
            palabras.append((t0, t0 + ch["duration"] / 1e7, ch["text"]))
    with open(ruta_mp3, "wb") as f:
        f.write(datos)
    return palabras


def sintetizar(texto, voz, rate="+0%", pitch="+0Hz", intentos=3):
    os.makedirs(CACHE, exist_ok=True)
    if os.path.exists(CA):
        os.environ.setdefault("SSL_CERT_FILE", CA)
    clave = hashlib.sha1(json.dumps([texto, voz, rate, pitch]).encode()).hexdigest()[:16]
    mp3, js = os.path.join(CACHE, clave + ".mp3"), os.path.join(CACHE, clave + ".json")
    if not (os.path.exists(mp3) and os.path.exists(js)):
        for k in range(intentos):
            try:
                palabras = asyncio.run(_pedir(texto, voz, rate, pitch, mp3))
                if os.path.getsize(mp3) > 1000:
                    json.dump(palabras, open(js, "w"))
                    break
            except Exception as e:  # red inestable: reintenta
                if k == intentos - 1:
                    raise RuntimeError(f"No se pudo sintetizar con {voz}: {e}")
    palabras = [tuple(p) for p in json.load(open(js))]
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                           capture_output=True, check=True).stdout
    audio = np.frombuffer(crudo, np.int16).astype(np.float32) / 32768
    return audio, palabras
