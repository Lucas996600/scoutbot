# Shorts virales de curiosidades

Sistema para crear reels / TikToks / Shorts de "¿sabías qué?" con IA: voz natural en español,
subtítulos palabra por palabra, música y animación de textos. Usa
[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) para voz, subtítulos y armado final.

## Cómo se activa
En Claude Code, escribí:

    SHORT: por qué los gatos ronronean

Opcional en el mismo mensaje: `tema visual: oceano|noche|fuego|selva|espacio|dulce`, `voz: mujer|hombre`.
Claude escribe el guion (sin "paso 1, paso 2": cuenta una historia), genera el video y te lo manda.

## A mano
    bash shorts/instalar.sh                              # una vez
    python3 shorts/hacer_short.py shorts/guiones/pulpos.json

Salida en `shorts/salida/<nombre>/`.
