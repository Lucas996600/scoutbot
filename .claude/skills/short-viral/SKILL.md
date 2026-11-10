---
name: short-viral
description: Crea un reel/TikTok/Short vertical de curiosidades en español, listo para subir (voz natural, subtítulos palabra por palabra, música y animación de textos), usando MoneyPrinterTurbo y el motor de shorts/ de este repo. Usar SIEMPRE que el mensaje empiece con "SHORT:" o "REEL:", o pida un reel, short, TikTok o video corto de curiosidades / "sabías que" sobre cualquier tema.
---

# Short viral de curiosidades

Palabra clave: `SHORT: <tema>` (también `REEL: <tema>`). Opciones que el usuario puede agregar en el mismo mensaje:
`tema visual: oceano | noche | fuego | selva | espacio | dulce` · `voz: mujer | hombre` · `largo: corto (~25 s) | normal (~35 s) | largo (~50 s)`.
Si no dice nada, elegí vos el tema visual que mejor pegue y voz de hombre (es-AR-TomasNeural). Voz de mujer: es-AR-ElenaNeural.

## 1. Instalación (solo si falta)
Si no existe `../tools/MoneyPrinterTurbo/.venv` (al lado del repo), corré `bash shorts/instalar.sh`.

## 2. Escribir el guion → `shorts/guiones/<slug>.json`
Formato (ver `shorts/guiones/pulpos.json` como ejemplo):
```json
{ "titulo": "...", "descripcion": "...", "tema": "noche", "etiqueta": "¿SABÍAS QUÉ?",
  "voz": "es-AR-TomasNeural", "velocidad": 1.2,
  "escenas": [ { "pantalla": "...", "destacar": "palabra", "emoji": "🐙", "dato": "3", "voz": "..." } ],
  "hashtags": ["#sabiasque", "..."] }
```
Reglas de escritura (son las que hacen que retenga):
- **Nada de "Paso 1", "Paso 2", "Primero", "Segundo", ni números de paso.** Contalo como una historia que fluye: cada escena empalma con la siguiente ("Y eso no es todo…", "Pero lo más loco…", "O sea…").
- **Escena 1 = gancho** que frene el scroll en 2 s: dato que choca con lo que la gente cree, pregunta intrigante o promesa ("te voy a demostrar…"). Antes de escribir, proponé mentalmente 3 ganchos y quedate con el más fuerte.
- 6 a 8 escenas. El dato más sorprendente va hacia el medio/final, no al principio.
- `pantalla`: máximo 7 palabras, frase corta y potente (no repite la voz entera). `destacar`: UNA palabra de `pantalla` que se pinta con marcador.
- `voz`: 1 o 2 oraciones, tono charlado rioplatense ("vos", "mirá", "posta"). Sin emojis ni símbolos en la voz; números escritos como se dicen si son raros.
- `emoji`: uno por escena, que ilustre la idea. `dato` (opcional, 1–3 escenas): número corto que aparece gigante y cuenta ("3", "0,3 s", "2/3", "100 %").
- Última escena: pregunta para comentarios + "seguime para más".
- **Solo datos verdaderos y verificables.** Si dudás de un dato, buscá en la web antes o no lo pongas. Nada inventado.
- `etiqueta`: chip superior corto (¿SABÍAS QUÉ?, DATO LOCO, NO LO SABÍAS, CIENCIA, HISTORIA…).

## 3. Generar
```bash
python3 shorts/hacer_short.py shorts/guiones/<slug>.json
```
Tarda ~3 min. Deja en `shorts/salida/<slug>/`: `<slug>.mp4`, `<slug>.srt`, `publicacion.txt` (título, descripción y hashtags).

## 4. Revisar y entregar
- Sacá 6–7 cuadros con ffmpeg en distintos segundos, armá una tira (`hstack`) y mirala: texto que no se corte, emoji visible, escena correcta para lo que dice la voz.
- Mandá el `.mp4` al usuario con SendUserFile y pegá en el chat el contenido de `publicacion.txt` listo para copiar.
- Decí con honestidad cualquier cosa que no haya salido (por ejemplo, si un emoji no se dibujó o el video quedó más largo de lo pedido).
- `shorts/salida/` no se sube al repo (está en .gitignore); el guion sí.
