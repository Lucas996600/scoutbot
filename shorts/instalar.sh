#!/usr/bin/env bash
# Instala MoneyPrinterTurbo + dependencias para el sistema de shorts.
# Se puede correr varias veces (idempotente). Instala en ../tools/MoneyPrinterTurbo (al lado del repo).
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$AQUI")"
DEST="${MPT_DIR:-$(dirname "$REPO")/tools/MoneyPrinterTurbo}"
COMMIT="c235354804104665b58679223847f78c2b5e27d4"

command -v ffmpeg >/dev/null || { apt-get update -qq && apt-get install -y -qq ffmpeg; }
[ -f /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf ] || apt-get install -y -qq fonts-noto-color-emoji || true
# Skia (dibujo 2D) necesita EGL/GL; Inter es la tipografía de los títulos
apt-get install -y -qq libegl1 libgl1 fonts-inter >/dev/null 2>&1 || true

if [ ! -d "$DEST/.git" ]; then
  mkdir -p "$(dirname "$DEST")"
  git clone -q https://github.com/harry0703/MoneyPrinterTurbo.git "$DEST"
fi
git -C "$DEST" fetch -q --depth 1 origin "$COMMIT" 2>/dev/null || true
git -C "$DEST" checkout -q "$COMMIT" 2>/dev/null || true

[ -x "$DEST/.venv/bin/python" ] || python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install -q -r "$DEST/requirements.txt"
python3 -m pip install -q edge-tts numpy pillow skia-python 2>/dev/null || python3 -m pip install -q --break-system-packages edge-tts numpy pillow skia-python

[ -f "$DEST/config.toml" ] || cp "$DEST/config.example.toml" "$DEST/config.toml"
python3 "$AQUI/parche_voz_proxy.py" "$DEST/app/services/voice.py"
echo "MoneyPrinterTurbo listo en $DEST"
