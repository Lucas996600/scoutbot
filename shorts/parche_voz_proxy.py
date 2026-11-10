"""Hace que la voz Edge TTS de MoneyPrinterTurbo use el proxy HTTPS del entorno (si hay uno).
Sin proxy no cambia nada. Idempotente."""
import sys

ruta = sys.argv[1]
s = open(ruta, encoding="utf-8").read()
if "_proxy = os.environ.get(\"HTTPS_PROXY\")" in s:
    print("parche de voz: ya aplicado")
    sys.exit(0)
viejo = "    return edge_tts.Communicate(text, voice_name, **communicate_kwargs)\n"
nuevo = (
    '    _proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")\n'
    '    if _proxy and "proxy" in communicate_signature.parameters:\n'
    '        communicate_kwargs["proxy"] = _proxy\n' + viejo
)
if s.count(viejo) != 1:
    sys.exit("parche de voz: no encontré dónde aplicarlo (¿cambió MoneyPrinterTurbo?)")
s = s.replace(viejo, nuevo)
if "\nimport os\n" not in s and not s.startswith("import os\n"):
    s = "import os\n" + s
open(ruta, "w", encoding="utf-8").write(s)
print("parche de voz: aplicado")
