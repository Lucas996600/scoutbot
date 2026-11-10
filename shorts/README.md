# Shorts virales de curiosidades

Sistema para crear reels / TikToks / Shorts de "¿sabías qué?" con IA: cada escena es una ilustración
2D animada de lo que cuenta la voz, con voz natural en español, subtítulos palabra por palabra y música. Usa
[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) para voz, subtítulos y armado final.

## Cómo se activa
En Claude Code, escribí:

    SHORT: por qué los gatos ronronean

Opcional en el mismo mensaje: `voz: mujer|hombre`.
Claude escribe el guion (sin "paso 1, paso 2": cuenta una historia), dibuja las escenas del tema
(`shorts/escenas/<tema>.py`, con `shorts/motor/dibujo.py`), genera el video y te lo manda.

## A mano
    bash shorts/instalar.sh                              # una vez
    python3 shorts/hacer_short.py shorts/guiones/gatos-ronronean.json

Salida en `shorts/salida/<nombre>/`.
