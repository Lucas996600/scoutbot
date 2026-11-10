---
name: short-viral
description: Crea un reel/TikTok/Short vertical de curiosidades en español, ILUSTRADO y animado en 2D (cada escena muestra lo que dice la voz), con voz natural, subtítulos palabra por palabra y música, usando MoneyPrinterTurbo y el motor de shorts/ de este repo. Usar SIEMPRE que el mensaje empiece con "SHORT:" o "REEL:", o pida un reel, short, TikTok o video corto de curiosidades / "sabías que" sobre cualquier tema.
---

# Short viral de curiosidades (ilustrado)

Palabra clave: `SHORT: <tema>` (o `REEL: <tema>`). Opcional en el mismo mensaje: `voz: mujer|hombre`, `largo: corto|normal`.

Lo que el usuario quiere (no negociable):
- **El video MUESTRA de lo que se habla.** Si se habla de montañas se ven montañas; de un gato, el gato; de la laringe, una lupa con la laringe. Nada de reels de solo texto, nada de fondos genéricos.
- **Sin barras de historias, sin chips, sin "Paso 1/Paso 2".** Arriba solo el dato curioso (`pantalla`) con una palabra en amarillo.
- Aspecto profesional y atractivo, en 2D vectorial animado (como `shorts/escenas/gatos-ronronean.py`). **No usar fotos ni imágenes de IA (Higgsfield) animadas con zoom**: al usuario no le gustó ese estilo (`motor/foto.py` queda solo si lo pide explícitamente).

## 1. Instalación (solo si falta)
Si no existe `../tools/MoneyPrinterTurbo/.venv` (al lado del repo), corré `bash shorts/instalar.sh`.

## 2. Guion → `shorts/guiones/<slug>.json`
```json
{ "titulo": "...", "descripcion": "...", "voz": "fr-FR-RemyMultilingualNeural", "velocidad": 1.05,
  "animacion": "escenas/<slug>.py",
  "escenas": [ { "pantalla": "...", "destacar": "palabra", "voz": "..." } ],
  "hashtags": ["#sabiasque", "..."] }
```
- Escena 1 = gancho que frena el scroll (dato que choca con lo que la gente cree, o promesa). Pensá 3 ganchos y elegí el mejor.
- Contalo como historia que fluye ("Pero lo más loco…", "Y eso no es todo…"). Nunca "primero/segundo/paso".
- 6–8 escenas, ~30–45 s. Dato más sorprendente hacia el final.
- `pantalla` ≤ 7 palabras. `destacar` = una palabra de `pantalla`. `voz` 1–2 oraciones, rioplatense, números raros escritos en letras.
- Última escena: pregunta para comentarios + "seguime para más".
- **Solo datos verdaderos.** Si dudás, buscá en la web; si no se puede confirmar, decilo como teoría o sacalo.
- Voz por defecto: **fr-FR-RemyMultilingualNeural** a 1.05 (voz "Multilingual": mucho más expresiva que Tomás, que suena robótica). Alternativas probadas: it-IT-GiuseppeMultilingualNeural, en-AU-WilliamMultilingualNeural, de-DE-FlorianMultilingualNeural (hombres); es-AR-TomasNeural / es-AR-ElenaNeural solo si piden acento argentino. `hacer_short.py` mete pausas `[pause: …]` entre escenas y oraciones, así cada tramo se sintetiza corto (las Multilingual se colgaban con textos largos) y la narración respira. Escribí la `voz` con puntuación expresiva (¿?, ¡!, …) porque estas voces la interpretan.

## 3. Animación → `shorts/escenas/<slug>.py`
Escribí un módulo con `def escena(c, i, lt, gt, dur, esc)` que dibuje la escena `i` (ver `shorts/escenas/gatos-ronronean.py` como modelo). Usá `shorts/motor/dibujo.py` (Skia): `fondo`, `cielo`, `sol`, `luna`, `estrellas`, `nubes`, `montanas`, `colinas`, `pino`, `agua`, `rayos_luz`, `burbujas`, `particulas`, `lluvia`, `nieve`, `figura` (formas suaves), `circulo`, `elipse`, `rect`, `linea`, `brillo`, `camara` (zoom/paneo), `onda_sonido`, `anillos`, `flecha`, `etiqueta` (cartel con línea a un punto), `contador`, `lupa` (zoom circular con contenido propio), `emoji` (solo como apoyo), `texto`, easing (`ease`, `ease_out`, `ease_out_back`, `aparece`).
- Cada escena ilustra concretamente su `voz`: el sujeto dibujado (personaje/objeto/paisaje con formas propias, no un emoji suelto), algo que se mueva (respira, gira, crece, sube, vibra) y, si suma, una etiqueta o flecha que explique.
- Personaje recurrente: hacé una función (como `gato(...)`) y reusala con poses/expresiones distintas.
- Composición: el título ocupa y≈180–420; dejá libre y≈1560–1720 para subtítulos (o no pongas detalles importantes ahí). El sujeto principal entre y≈600 y y≈1900.
- Revisá antes de generar el video: 
  ```bash
  cd shorts/motor && python3 -c "import json,reel_ilustrado as r; g=json.load(open('../guiones/<slug>.json')); r.previsualizar(g,'../escenas/<slug>.py','/ruta/scratchpad/prev.png',momentos=(0.6,))"
  ```
  Mirá la tira (Read) y corregí superposiciones, cosas tapadas o escenas que no se entienden.

## 4. Generar
```bash
python3 shorts/hacer_short.py shorts/guiones/<slug>.json
```
~4 min. Salida en `shorts/salida/<slug>/`: `<slug>.mp4`, `<slug>.srt`, `publicacion.txt`.
- La música es **original**: `shorts/motor/musica.py` la sintetiza para cada video (semilla = nombre, o `"semilla_musica"` en el guion para cambiarla). Nunca usar las canciones de `resource/songs` de MoneyPrinterTurbo: dan reclamos de Content ID en YouTube.

## 5. Revisar y entregar
- Sacá 6–8 cuadros del mp4 con ffmpeg (`hstack`) y miralos: subtítulos legibles, título completo, escena correcta para lo que dice la voz.
- Mandá el `.mp4` con SendUserFile y pegá `publicacion.txt` en el chat listo para copiar.
- Recordá: al subir a YouTube elegir **"No, no es contenido creado para niños"** (si no, se desactivan comentarios y notificaciones).
- Decí con honestidad lo que no haya salido o datos que sean teoría.
- Commiteá guion + escenas (no `shorts/salida/`, que está en .gitignore).

## Serie "¿Cómo sería el mundo sin…?" (palabra clave: `MUNDO SIN: <elemento>`)
- Escena 1 SIEMPRE es la ruleta oficial: en la escena llamá `ruleta.dibujar(c, lt, dur, "<elemento>", gt)` (motor/ruleta.py) y en el guion poné `"ruleta": "<elemento>"` (activa el sonido de marca y hace que frene justo antes de que la voz diga el elemento). Voz de la escena 1: "Hoy vamos a descubrir cómo sería el mundo sin… ¡<ELEMENTO>!" (la última palabra debe ser el elemento). Si el elemento no está en `ELEMENTOS`, agregá su emoji en `EMOJIS_EXTRA`.
- Estilo de la serie: `"estilo": "tinta"` en el guion (caricatura plana con contornos gruesos de tinta, títulos con letras gordas extruidas coral/rosa, palabra clave verde lima, destellos de 4 puntas; referencia que dio el usuario). Personajes y objetos: `motor/cartoon3d.py` (esfera, personaje cabezón, edificio con caras, sol con cara, murciélago, delfín, pingüino, pez, termómetro) y la mascota `ruleta.globi(...)`. Ver `escenas/mundo-sin-luz.py`.
- Estructura: ruleta → revelación (desaparece) → primeras consecuencias → consecuencias extremas (ciencia real) → final con revelación + pregunta. 6–8 escenas, ~40–55 s.
- Los 30 elementos propuestos: agua, luz, viento, árboles, lluvia, Luna, nubes, abejas, oxígeno, volcanes, ojos, oído, dolor, sueño, olfato, huesos, memoria, internet, electricidad, ruedas, plástico, dinero, relojes, gravedad, Sol, fricción, colores, noche, silencio, números.

### Formato con DIÁLOGOS (el que pidió el usuario para la serie — usar este por defecto en `MUNDO SIN:`)
Referencia: caricatura "garabato" (personajes blancos y pelados, ojos grandes con párpado caído, pastel apagado, líneas finas),
la escena en una FRANJA horizontal en el medio, fondo violeta con estrellitas, título arriba y subtítulos con el nombre de quien habla abajo.
Humor seco y absurdo con situaciones del tema. **SIN NARRADOR**: los datos reales los dicen los personajes dentro de los chistes; la ruleta la presenta Globi.
- Guion: `shorts/guiones/<slug>.json` con `"personajes"` (voz/velocidad/tono/color/nombre) y escenas con `"lineas": [{"quien","texto"}]`
  (ver `guiones/mundo-sin-luz-dialogo.json`). Escena 1 `"formato": "completo"` con la ruleta; la última línea de la escena 1 termina en el elemento.
- Escenas: `shorts/escenas/<slug>.py` dibujando en 1920x1080 con `motor/doodle.py` (persona(boca=esc["_habla"].get(quien)), banco, árbol, fondo_parque, murciélago).
- Generar: `cd shorts/motor && python3 reel_dialogo.py ../guiones/<slug>.json` (voces con caché, música original, sonido de la ruleta).
- Voces (solo Multilingual, SIN cambiar el tono: los cambios de tono y Tomás/Elena suenan robóticos): Tito = fr-FR-RemyMultilingualNeural +8%, abuelo = en-AU-WilliamMultilingualNeural -2%, Globi = en-US-AvaMultilingualNeural, mujeres/personajes chistosos = en-US-EmmaMultilingualNeural, pt-BR-ThalitaMultilingualNeural. El motor iguala el volumen de cada línea y normaliza a -15 LUFS.
- Apuntar a 45–60 s: líneas cortas, chistes de 2–4 réplicas, un dato real por escena dicho por un personaje.
