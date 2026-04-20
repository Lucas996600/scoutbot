const TelegramBot = require("node-telegram-bot-api");
const { GoogleGenerativeAI } = require("@google/generative-ai");

// ── CONFIG ────────────────────────────────────────────────
const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const GEMINI_KEY     = process.env.GEMINI_API_KEY;

const bot   = new TelegramBot(TELEGRAM_TOKEN, { polling: true });
const genAI = new GoogleGenerativeAI(GEMINI_KEY);

// ── ESTADO POR USUARIO ────────────────────────────────────
const userState = {};

// ── HELPERS ───────────────────────────────────────────────
function grabJSON(text) {
  if (!text) return null;
  let s = text.replace(/```json/gi,"").replace(/```/g,"").trim();
  try { return JSON.parse(s); } catch {}
  const a = s.indexOf("{"), b = s.lastIndexOf("}");
  if (a !== -1 && b > a) { try { return JSON.parse(s.slice(a,b+1)); } catch {} }
  return null;
}

function getArgentinaDate() {
  const now = new Date();
  const arg = new Date(now.toLocaleString("en-US",{timeZone:"America/Argentina/Buenos_Aires"}));
  const pad = n => String(n).padStart(2,"0");
  const iso = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const tom = new Date(arg); tom.setDate(tom.getDate()+1);
  return {
    todayISO    : iso(arg),
    tomorrowISO : iso(tom),
    currentTime : `${pad(arg.getHours())}:${pad(arg.getMinutes())}`,
    label       : arg.toLocaleDateString("es-AR",{weekday:"long",day:"numeric",month:"long",year:"numeric"})
  };
}

async function callGemini(prompt) {
  const model = genAI.getGenerativeModel({
    model : "gemini-2.0-flash",
  });
  const result = await model.generateContent(prompt);
  return result.response.text();
}

// ── PROMPTS ───────────────────────────────────────────────
function matchesPrompt(d) {
  return `Hoy es ${d.todayISO}. Hora actual en Argentina (UTC-3): ${d.currentTime}.

Buscá en internet los partidos de fútbol CONFIRMADOS para HOY ${d.todayISO} y MAÑANA ${d.tomorrowISO}.
Solo partidos que AÚN NO empezaron (hora > ${d.currentTime} para los de hoy).

Ligas: Liga Profesional Argentina Apertura 2026, Copa Argentina, Champions League, Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Copa Libertadores 2026, Copa Sudamericana 2026, MLS.

Devolvé ÚNICAMENTE este JSON (sin texto, sin markdown, empieza con {):
{"matches":[{"id":"1","league":"Liga Profesional Argentina","flag":"🇦🇷","teamA":"River Plate","teamB":"Boca Juniors","time":"20:00","date":"hoy"},{"id":"2","league":"Champions League","flag":"🏆","teamA":"PSG","teamB":"Bayern","time":"16:00","date":"mañana"}]}

Entre 10 y 20 partidos reales. SOLO el JSON.`;
}

function analysisPrompt(teamA, teamB, league) {
  return `Sos analista profesional de apuestas deportivas. Buscá datos reales y actualizados sobre: ${teamA} vs ${teamB} (${league}).

Buscá: forma últimos 5 partidos, posición tabla, goles/córners/tarjetas/remates promedio, H2H, jugadores clave, bajas, árbitro, máximos rematadores y datos del arquero de cada equipo.

Devolvé SOLO este JSON en español (sin texto antes ni después, empieza con {):
{"teamA":{"name":"${teamA}","position":"posición","form":"VVEDV","goalsScored":"1.8","goalsConceded":"1.2","cornersAvg":"5.1","cardsAvg":"2.0","shotsAvg":"13.5","keyPlayer":"nombre","injury":"Ninguna","notes":"nota breve","topShooters":[{"name":"Jugador","shotsPerGame":"3.0","shotProbability":75,"note":"descripción"},{"name":"Jugador2","shotsPerGame":"2.0","shotProbability":60,"note":"descripción"}],"goalkeeper":{"name":"Arquero","savesPerGame":"3.5","estimatedSaves":"3-4","saveProbability":68,"note":"nota"}},"teamB":{"name":"${teamB}","position":"posición","form":"DVVEE","goalsScored":"1.3","goalsConceded":"1.5","cornersAvg":"4.2","cardsAvg":"2.3","shotsAvg":"11.0","keyPlayer":"nombre","injury":"Ninguna","notes":"nota breve","topShooters":[{"name":"Jugador","shotsPerGame":"2.5","shotProbability":68,"note":"descripción"},{"name":"Jugador2","shotsPerGame":"1.8","shotProbability":52,"note":"descripción"}],"goalkeeper":{"name":"Arquero","savesPerGame":"4.0","estimatedSaves":"4+","saveProbability":72,"note":"nota"}},"h2h":{"summary":"resumen historial","lastResult":"1-0","tendency":"tendencia"},"referee":{"name":"nombre o Desconocido","cardsPerGame":"4.2","style":"estricto","redCardRisk":22},"probabilities":{"teamAWin":54,"draw":26,"teamBWin":20,"over25Goals":60,"over15Goals":78,"btts":52,"over85Corners":58,"over35Corners":83,"over45Cards":55,"teamAShots":66,"redCard":20},"bets":[{"tier":"gold","market":"Resultado","selection":"Victoria ${teamA}","reasoning":"razón concreta","odds":"1.70"},{"tier":"silver","market":"Goles","selection":"Más de 1.5","reasoning":"razón","odds":"1.45"},{"tier":"silver","market":"Córners","selection":"Más de 8.5","reasoning":"razón","odds":"1.85"},{"tier":"risky","market":"Goleador","selection":"jugador","reasoning":"razón","odds":"3.50"}],"summary":"análisis en 2 oraciones en español."}`;
}

// ── FORMATEAR ANÁLISIS ────────────────────────────────────
function formatAnalysis(d) {
  if (!d) return "❌ No se pudo procesar el análisis.";

  const bar = (pct) => {
    const n = Math.max(0, Math.min(100, parseInt(pct)||0));
    const filled = Math.round(n/10);
    const icon = n >= 65 ? "🟢" : n >= 45 ? "🟡" : "🔴";
    return `${icon} ${"█".repeat(filled)}${"░".repeat(10-filled)} ${n}%`;
  };

  const formEmoji = (f) => String(f||"").toUpperCase().split("").map(c=>{
    if(c==="V"||c==="W") return "✅";
    if(c==="E") return "➡️";
    if(c==="D"||c==="L") return "❌";
    return "";
  }).join("");

  const p = d.probabilities || {};
  const A = d.teamA || {};
  const B = d.teamB || {};
  const ref = d.referee || {};
  const h2h = d.h2h || {};

  let msg = `⚽ *ANÁLISIS: ${A.name} vs ${B.name}*\n`;
  msg += `━━━━━━━━━━━━━━━━━━━\n\n`;

  msg += `🔵 *${A.name}*\n`;
  msg += `📊 Posición: ${A.position||"—"}\n`;
  msg += `⚽ Goles: ${A.goalsScored||"—"} anotados / ${A.goalsConceded||"—"} recibidos\n`;
  msg += `📐 Córners: ${A.cornersAvg||"—"} | 🟨 Tarjetas: ${A.cardsAvg||"—"}\n`;
  msg += `🎯 Remates: ${A.shotsAvg||"—"}/partido\n`;
  msg += `⭐ Clave: ${A.keyPlayer||"—"}\n`;
  msg += `🚑 Bajas: ${A.injury||"Ninguna"}\n`;
  msg += `📈 Forma: ${formEmoji(A.form)}\n`;
  if (A.topShooters?.length) {
    msg += `\n🎯 *Top Rematadores ${A.name}:*\n`;
    A.topShooters.forEach(s => {
      msg += `• ${s.name}: ${s.shotsPerGame} rem/p — ${s.shotProbability}% prob\n`;
      if(s.note) msg += `  _${s.note}_\n`;
    });
  }
  if (A.goalkeeper) {
    msg += `🧤 Arquero: *${A.goalkeeper.name}*\n`;
    msg += `  Atajadas: ${A.goalkeeper.savesPerGame}/p | Est: ${A.goalkeeper.estimatedSaves}\n`;
  }

  msg += `\n🔴 *${B.name}*\n`;
  msg += `📊 Posición: ${B.position||"—"}\n`;
  msg += `⚽ Goles: ${B.goalsScored||"—"} anotados / ${B.goalsConceded||"—"} recibidos\n`;
  msg += `📐 Córners: ${B.cornersAvg||"—"} | 🟨 Tarjetas: ${B.cardsAvg||"—"}\n`;
  msg += `🎯 Remates: ${B.shotsAvg||"—"}/partido\n`;
  msg += `⭐ Clave: ${B.keyPlayer||"—"}\n`;
  msg += `🚑 Bajas: ${B.injury||"Ninguna"}\n`;
  msg += `📈 Forma: ${formEmoji(B.form)}\n`;
  if (B.topShooters?.length) {
    msg += `\n🎯 *Top Rematadores ${B.name}:*\n`;
    B.topShooters.forEach(s => {
      msg += `• ${s.name}: ${s.shotsPerGame} rem/p — ${s.shotProbability}% prob\n`;
      if(s.note) msg += `  _${s.note}_\n`;
    });
  }
  if (B.goalkeeper) {
    msg += `🧤 Arquero: *${B.goalkeeper.name}*\n`;
    msg += `  Atajadas: ${B.goalkeeper.savesPerGame}/p | Est: ${B.goalkeeper.estimatedSaves}\n`;
  }

  // Alerta arquero
  const aShots = parseFloat(A.shotsAvg)||0;
  const bShots = parseFloat(B.shotsAvg)||0;
  if (aShots >= 13 || bShots >= 13) {
    msg += `\n⚡ *ALERTA:* `;
    if (aShots >= 13 && bShots >= 13) msg += `Ambos arqueros pueden tener muchas atajadas.\n`;
    else if (aShots >= 13) msg += `El arquero de ${B.name} enfrenta equipo con muchos remates.\n`;
    else msg += `El arquero de ${A.name} puede estar muy ocupado.\n`;
  }

  msg += `\n📊 *HISTORIAL H2H*\n${h2h.summary||"—"}\n`;
  if (h2h.lastResult) msg += `Último: ${h2h.lastResult}\n`;
  if (h2h.tendency) msg += `Tendencia: ${h2h.tendency}\n`;

  if (ref.name) {
    msg += `\n🟨 *ÁRBITRO: ${ref.name}*\n`;
    msg += `Tarjetas/p: ${ref.cardsPerGame||"—"} | Estilo: ${ref.style||"—"}\n`;
    msg += `Riesgo roja: ${ref.redCardRisk||0}%\n`;
  }

  msg += `\n📈 *PROBABILIDADES*\n`;
  msg += `Victoria ${A.name}:\n${bar(p.teamAWin)}\n`;
  msg += `Empate:\n${bar(p.draw)}\n`;
  msg += `Victoria ${B.name}:\n${bar(p.teamBWin)}\n`;
  msg += `Más de 2.5 goles:\n${bar(p.over25Goals)}\n`;
  msg += `Más de 1.5 goles:\n${bar(p.over15Goals)}\n`;
  msg += `Ambos marcan:\n${bar(p.btts)}\n`;
  msg += `+8.5 córners:\n${bar(p.over85Corners)}\n`;
  msg += `+4.5 tarjetas:\n${bar(p.over45Cards)}\n`;
  msg += `Tarjeta roja:\n${bar(p.redCard)}\n`;

  if (d.bets?.length) {
    msg += `\n💎 *APUESTAS RECOMENDADAS*\n`;
    d.bets.forEach(b => {
      const icon = b.tier==="gold"?"🥇":b.tier==="silver"?"⚡":"🎲";
      msg += `${icon} *${b.market}:* ${b.selection} @ ${b.odds}\n`;
      msg += `   ↳ _${b.reasoning}_\n`;
    });
  }

  if (d.summary) msg += `\n📝 *ANÁLISIS FINAL*\n${d.summary}\n`;

  msg += `\n━━━━━━━━━━━━━━━━━━━\n`;
  msg += `⚠️ _Solo informativo · Las apuestas implican riesgo · +18_`;

  return msg;
}

// ── KEYBOARD ──────────────────────────────────────────────
function matchesKeyboard(matches) {
  return {
    inline_keyboard: matches.map((m, i) => ([{
      text: `${m.date==="mañana"?"🗓":"📅"} ${m.teamA} vs ${m.teamB} · ${m.time||""}`,
      callback_data: `match_${i}`
    }]))
  };
}

// ── COMANDOS ──────────────────────────────────────────────
bot.onText(/\/start/, async (msg) => {
  await bot.sendMessage(msg.chat.id,
    `🤖 *Bienvenido a ScoutBot* ⚽🏀\n\n` +
    `Soy tu analista deportivo con IA en tiempo real.\n\n` +
    `📋 *Comandos:*\n` +
    `/partidos — Ver partidos de hoy y mañana\n` +
    `/ayuda — Cómo usar el bot\n\n` +
    `Escribí /partidos para empezar 👇`,
    { parse_mode: "Markdown" }
  );
});

bot.onText(/\/ayuda/, async (msg) => {
  await bot.sendMessage(msg.chat.id,
    `🤖 *ScoutBot — Ayuda*\n\n` +
    `/partidos — Carga los partidos de hoy y mañana\n` +
    `/start — Mensaje de bienvenida\n\n` +
    `*¿Cómo funciona?*\n` +
    `1️⃣ Escribí /partidos\n` +
    `2️⃣ Tocá el partido que querés analizar\n` +
    `3️⃣ El bot busca datos reales y te da:\n` +
    `   • Estadísticas de ambos equipos\n` +
    `   • Top rematadores y arqueros\n` +
    `   • Probabilidades de cada mercado\n` +
    `   • Apuestas recomendadas\n\n` +
    `⚠️ _Solo informativo · +18_`,
    { parse_mode: "Markdown" }
  );
});

bot.onText(/\/partidos/, async (msg) => {
  const chatId = msg.chat.id;
  const loadMsg = await bot.sendMessage(chatId, "🔍 Buscando partidos de hoy y mañana...");
  try {
    const d = getArgentinaDate();
    const raw = await callGemini(matchesPrompt(d));
    const data = grabJSON(raw);
    if (!data?.matches?.length) {
      await bot.editMessageText("❌ No encontré partidos. Intentá /partidos de nuevo.", {
        chat_id: chatId, message_id: loadMsg.message_id
      });
      return;
    }
    userState[chatId] = { matches: data.matches };

    const byLeague = data.matches.reduce((acc,m)=>{
      const k=`${m.flag||"🌍"} ${m.league}`;
      (acc[k]=acc[k]||[]).push(m);
      return acc;
    },{});

    let text = `📅 *Partidos — ${d.label.toUpperCase()}*\n🕐 Argentina: ${d.currentTime}\n\n`;
    Object.entries(byLeague).forEach(([league,ms])=>{
      text += `*${league}*\n`;
      ms.forEach(m => { text += `${m.date==="mañana"?"🗓":"📅"} ${m.teamA} vs ${m.teamB} · ${m.time||"—"}\n`; });
      text += "\n";
    });
    text += "👇 *Tocá un partido para analizarlo:*";

    await bot.editMessageText(text, {
      chat_id: chatId,
      message_id: loadMsg.message_id,
      parse_mode: "Markdown",
      reply_markup: matchesKeyboard(data.matches)
    });
  } catch(e) {
    console.error(e);
    await bot.editMessageText("❌ Error buscando partidos. Intentá /partidos de nuevo.", {
      chat_id: chatId, message_id: loadMsg.message_id
    });
  }
});

bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data   = query.data;
  if (!data.startsWith("match_")) return;

  const idx   = parseInt(data.replace("match_",""));
  const state = userState[chatId];
  if (!state?.matches?.[idx]) {
    await bot.answerCallbackQuery(query.id, { text: "Usá /partidos de nuevo." });
    return;
  }

  const match = state.matches[idx];
  await bot.answerCallbackQuery(query.id);
  const loadMsg = await bot.sendMessage(chatId,
    `🔄 Analizando *${match.teamA} vs ${match.teamB}*...\n_Buscando datos en tiempo real..._`,
    { parse_mode: "Markdown" }
  );

  try {
    const raw    = await callGemini(analysisPrompt(match.teamA, match.teamB, match.league));
    const result = grabJSON(raw);
    const text   = formatAnalysis(result);

    if (text.length > 4000) {
      const mid = text.indexOf("\n📈");
      await bot.editMessageText(text.slice(0, mid), {
        chat_id: chatId, message_id: loadMsg.message_id, parse_mode: "Markdown"
      });
      await bot.sendMessage(chatId, text.slice(mid), { parse_mode: "Markdown" });
    } else {
      await bot.editMessageText(text, {
        chat_id: chatId, message_id: loadMsg.message_id, parse_mode: "Markdown"
      });
    }
  } catch(e) {
    console.error(e);
    await bot.editMessageText("❌ Error en el análisis. Tocá el partido de nuevo.", {
      chat_id: chatId, message_id: loadMsg.message_id
    });
  }
});

bot.on("message", (msg) => {
  if (msg.text && !msg.text.startsWith("/")) {
    bot.sendMessage(msg.chat.id, "Usá /partidos para ver los partidos de hoy 👇");
  }
});

console.log("🤖 ScoutBot con Gemini iniciado correctamente");
