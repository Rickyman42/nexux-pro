let historyChart = null;
let currentDays = 7;

const $ = (id) => document.getElementById(id);

function fmtNum(n) {
  const v = Number(n || 0);
  return v.toLocaleString('es-ES');
}

function setPill(el, level, text) {
  el.classList.remove('good', 'warn', 'bad');
  if (level === 'good') el.classList.add('good');
  if (level === 'warn') el.classList.add('warn');
  if (level === 'bad') el.classList.add('bad');
  el.textContent = text;
}

async function api(path, opts) {
  const resp = await fetch(path, opts);
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

function renderHistory(series) {
  const labels = series.map((x) => x.day.slice(5));
  const sent = series.map((x) => x.sent);
  const opened = series.map((x) => x.opened);
  const responded = series.map((x) => x.responded);

  const ctx = $('historyChart').getContext('2d');

  if (historyChart) historyChart.destroy();
  historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Enviados',
          data: sent,
          borderColor: 'rgba(124,92,255,.95)',
          backgroundColor: 'rgba(124,92,255,.10)',
          tension: 0.35,
          fill: true,
        },
        {
          label: 'Abiertos',
          data: opened,
          borderColor: 'rgba(37,208,255,.95)',
          backgroundColor: 'rgba(37,208,255,.08)',
          tension: 0.35,
          fill: true,
        },
        {
          label: 'Respondidos',
          data: responded,
          borderColor: 'rgba(46,229,157,.95)',
          backgroundColor: 'rgba(46,229,157,.08)',
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: 'rgba(255,255,255,.75)' } },
        tooltip: { intersect: false, mode: 'index' },
      },
      scales: {
        x: { ticks: { color: 'rgba(255,255,255,.55)' }, grid: { color: 'rgba(255,255,255,.05)' } },
        y: { ticks: { color: 'rgba(255,255,255,.55)' }, grid: { color: 'rgba(255,255,255,.05)' } },
      },
    },
  });
}

function renderLeadsTable(items) {
  const rows = items.map((l) => {
    const name = esc(l.nombre || '—');
    const city = esc(l.ciudad || '—');
    const phone = esc(l.telefono || '—');
    const rating = esc(l.rating || '');
    const reviews = esc(l.reviews || '');
    const web = l.website ? `<a class="link" href="${escAttr(l.website)}" target="_blank" rel="noreferrer">web</a>` : '—';
    const ig = l.instagram ? `<a class="link" href="${escAttr(l.instagram)}" target="_blank" rel="noreferrer">ig</a>` : '—';
    const maps = l.maps_url ? `<a class="link" href="${escAttr(l.maps_url)}" target="_blank" rel="noreferrer">maps</a>` : '—';
    return `<tr>
      <td>${name}<div class="muted">${city}</div></td>
      <td class="mono">${phone}</td>
      <td class="mono">${rating}</td>
      <td class="mono">${reviews}</td>
      <td>${web} · ${ig} · ${maps}</td>
    </tr>`;
  });

  $('leadsTable').innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Lead</th>
          <th>Teléfono</th>
          <th>Rating</th>
          <th>Reviews</th>
          <th>Links</th>
        </tr>
      </thead>
      <tbody>${rows.join('')}</tbody>
    </table>
  `;
}

function renderHot(items) {
  if (!items.length) {
    $('hotList').innerHTML = `<div class="note">No hay hot leads (o no se pudo cargar conversaciones.json).</div>`;
    return;
  }
  $('hotList').innerHTML = items
    .slice(0, 30)
    .map((x) => {
      const name = esc(x.nombre || x.id);
      const city = esc(x.ciudad || '—');
      const msg = esc(x.last_message || '—');
      const badge = `<span class="badge">${esc(x.id)}</span>`;
      return `<div class="item" data-id="${escAttr(x.id)}">
        <div class="t">
          <div>
            <div class="name">${name}</div>
            <div class="city">${city}</div>
          </div>
          ${badge}
        </div>
        <div class="msg">${msg}</div>
      </div>`;
    })
    .join('');

  for (const el of $('hotList').querySelectorAll('.item')) {
    el.addEventListener('click', async () => {
      const id = el.getAttribute('data-id');
      await loadJourney(id);
    });
  }
}

function renderJourney(data) {
  const t = (data.timeline || [])
    .map((x) => {
      const at = x.at ? esc(x.at) : '—';
      return `<div class="jLine"><div class="jAt">${at} · ${esc(x.type)}</div><div class="jText">${esc(x.text)}</div></div>`;
    })
    .join('');
  $('journey').innerHTML = t || `<div class="note">Sin datos.</div>`;
}

async function loadJourney(id) {
  try {
    const data = await api(`/api/journey?id=${encodeURIComponent(id)}`);
    renderJourney(data);
  } catch {
    $('journey').innerHTML = `<div class="note">No se pudo cargar journey.</div>`;
  }
}

// ── Server clock ─────────────────────────────────────────────────────────────
var _clockOffset = 0; // ms difference: serverTime - Date.now()
async function initServerClock() {
  try {
    var d = await api('/api/time');
    _clockOffset = d.ts - Date.now();
  } catch(e) { _clockOffset = 0; }
  setInterval(function() {
    var now = new Date(Date.now() + _clockOffset);
    var el = $('serverClock');
    if (el) el.textContent = now.toLocaleTimeString('es-ES', {timeZone: 'Europe/Madrid', hour12: false});
  }, 1000);
}

async function refreshAll() {
  try {
    const status = await api('/api/status');
    const ok = status.ok && !status.load_error;
    setPill($('statusPill'), ok ? 'good' : 'warn', ok ? 'Online' : 'Degradado');

    const funnel = await api('/api/funnel');
    $('kLeads').textContent = fmtNum(funnel.leads_total);
    $('kSent').textContent = fmtNum(funnel.sent);
    $('kOpened').textContent = fmtNum(funnel.opened);
    $('kResp').textContent = fmtNum(funnel.responded);
    $('kTrial').textContent = fmtNum(funnel.trial);
    $('kOpenedPct').textContent = `(${funnel.opener_pct}%)`;
    $('kRespPct').textContent = `(${funnel.responded_pct}%)`;
    $('kTrialPct').textContent = `(${funnel.trial_pct}%)`;

    const history = await api(`/api/history?days=${currentDays}`);
    renderHistory(history.series || []);

    const wa = await api('/api/whatsapp');
    $('waTotal').textContent = fmtNum(wa.total);
    $('waOk').textContent = fmtNum(wa.ok);
    $('waErr').textContent = fmtNum(wa.error);
    $('waNo').textContent = fmtNum(wa.noWhatsapp);
    const pct = wa.recommendedLimit ? Math.min(100, Math.round((wa.total / wa.recommendedLimit) * 100)) : 0;
    $('waBar').style.width = `${pct}%`;
    $('waBar').style.background =
      wa.level === 'red'
        ? 'linear-gradient(90deg, var(--warn), var(--bad))'
        : wa.level === 'yellow'
        ? 'linear-gradient(90deg, var(--good), var(--warn))'
        : 'linear-gradient(90deg, var(--good), var(--accent2))';
    $('waNote').textContent = `Límite recomendado: ${wa.recommendedLimit}/día · Máx sesión: ${wa.sessionMax}.`;

    const sched = await api('/api/scheduler');
    if (!sched.ok) {
      setPill($('schedPill'), 'warn', 'unknown');
      $('schedUp').textContent = '—';
      $('schedRestarts').textContent = '—';
    } else {
      const level = sched.status === 'online' ? 'good' : sched.status === 'stopped' ? 'bad' : 'warn';
      setPill($('schedPill'), level, sched.status);
      $('schedUp').textContent = sched.pm_uptime ? new Date(sched.pm_uptime).toLocaleString('es-ES') : '—';
      $('schedRestarts').textContent = String(sched.restart_time ?? '—');
    }

    const hot = await api('/api/hot');
    renderHot(hot.items || []);
    await loadScraper();
  } catch (e) {
    setPill($('statusPill'), 'bad', 'Error');
  }
}

async function doSearch() {
  const q = $('qInput').value.trim();
  const city = $('cityInput').value.trim();
  const data = await api(`/api/leads?q=${encodeURIComponent(q)}&city=${encodeURIComponent(city)}&limit=60`);
  renderLeadsTable(data.items || []);
}

function appendChat(role, text) {
  const el = document.createElement('div');
  el.className = `bubble ${role === 'user' ? 'user' : 'ai'}`;
  el.textContent = text;
  $('chatLog').appendChild(el);
  $('chatLog').scrollTop = $('chatLog').scrollHeight;
}

async function sendChat() {
  const prompt = $('chatInput').value.trim();
  if (!prompt) return;
  $('chatInput').value = '';
  appendChat('user', prompt);
  appendChat('ai', '…');
  const bubbles = $('chatLog').querySelectorAll('.bubble.ai');
  const lastAi = bubbles[bubbles.length - 1];
  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!resp.ok || !resp.body) throw new Error('stream_failed');

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let text = '';

    lastAi.textContent = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      while (true) {
        const split = buffer.indexOf('\n\n');
        if (split < 0) break;
        const rawEvent = buffer.slice(0, split);
        buffer = buffer.slice(split + 2);

        const lines = rawEvent.split('\n');
        let eventName = 'message';
        let dataLine = '';
        for (const line of lines) {
          if (line.startsWith('event:')) eventName = line.slice(6).trim();
          if (line.startsWith('data:')) dataLine += line.slice(5).trim();
        }
        if (!dataLine) continue;

        if (eventName === 'error') {
          lastAi.textContent = 'Error en Ollama.';
          return;
        }
        if (eventName === 'done') return;

        try {
          const obj = JSON.parse(dataLine);
          if (obj.token) {
            text += obj.token;
            lastAi.textContent = text;
            $('chatLog').scrollTop = $('chatLog').scrollHeight;
          }
        } catch {
          // ignore malformed chunks
        }
      }
    }
  } catch (e) {
    lastAi.textContent = 'No pude conectar con Qwen (Ollama).';
  }
}


let currentLogType = 'scraper';

function fmtEta(min) {
  if (min === null || min === undefined || min < 0) return '-';
  if (min < 1) return '< 1 min';
  if (min < 60) return min + ' min';
  var h = Math.floor(min / 60), m = min % 60;
  return h + 'h ' + (m > 0 ? m + 'm' : '');
}

function fmtUptime(isoStr) {
  if (!isoStr) return '-';
  var ms = Date.now() - new Date(isoStr).getTime();
  var m = Math.floor(ms / 60000), h = Math.floor(m / 60);
  if (h > 0) return h + 'h ' + (m % 60) + 'm';
  return m + ' min';
}

function setPhaseUI(phase) {
  // phase: 1=mapeo, 4=extraccion, 9=done, 0=idle
  var p1 = $('scPhase1'), p4 = $('scPhase4'), pd = $('scPhaseDone');
  var l1 = $('scLine1'), l2 = $('scLine2');
  [p1, p4, pd].forEach(function(el) { if (el) { el.classList.remove('active', 'done'); } });
  [l1, l2].forEach(function(el) { if (el) { el.classList.remove('active', 'done'); } });
  if (phase === 1) {
    if (p1) p1.classList.add('active');
  } else if (phase === 4) {
    if (p1) p1.classList.add('done');
    if (l1) l1.classList.add('done');
    if (p4) p4.classList.add('active');
  } else if (phase === 9) {
    [p1, p4, pd].forEach(function(el) { if (el) el.classList.add('done'); });
    [l1, l2].forEach(function(el) { if (el) el.classList.add('done'); });
  }
}

async function loadScraper() {
  try {
    var d = await api('/api/scraper');
    var level = d.status === 'online' ? 'good' : d.status === 'stopped' ? 'bad' : 'warn';
    setPill($('scraperPill'), level, d.status || '?');
    if ($('scraperRestarts')) $('scraperRestarts').textContent = d.restarts != null ? d.restarts : '-';
    if ($('statUptime')) $('statUptime').textContent = fmtUptime(d.uptime);

    var eb = $('scraperErr');
    if (d.last_error && eb) { eb.style.display = 'block'; eb.textContent = d.last_error; }
    else if (eb) { eb.style.display = 'none'; }

    if (d.phase === 1 && d.phase1) {
      var p = d.phase1;
      setPhaseUI(1);
      if ($('scPhaseLabel')) $('scPhaseLabel').textContent = 'FASE 1 — Mapeando ciudades';
      if ($('scraperPct')) $('scraperPct').textContent = p.pct + '%';
      if ($('scraperBar')) $('scraperBar').style.width = p.pct + '%';
      if ($('scEta')) $('scEta').textContent = fmtEta(p.etaMin);
      if ($('scProgress')) $('scProgress').textContent = p.queriesDone.toLocaleString() + ' / ' + p.queriesTotal.toLocaleString() + ' consultas';
      if ($('scSpeed')) $('scSpeed').textContent = p.pairsPerMin + ' consultas/min';
      if ($('scActivity')) $('scActivity').textContent = '▶ ' + (p.currentActivity || '-');
      if ($('statBiz')) $('statBiz').textContent = p.businessesFound > 0 ? p.businessesFound.toLocaleString() : '-';
      if ($('statQueries')) $('statQueries').textContent = p.queriesDone + ' / ' + p.queriesTotal;
      if ($('statSpeed')) $('statSpeed').textContent = p.pairsPerMin + '/min';

    } else if (d.phase === 4 && d.phase4) {
      var p4 = d.phase4;
      setPhaseUI(4);
      if ($('scPhaseLabel')) $('scPhaseLabel').textContent = 'FASE 2 — Extrayendo datos';
      if ($('scraperPct')) $('scraperPct').textContent = p4.pct + '%';
      if ($('scraperBar')) $('scraperBar').style.width = p4.pct + '%';
      if ($('scEta')) $('scEta').textContent = fmtEta(p4.etaMin);
      if ($('scProgress')) $('scProgress').textContent = p4.current.toLocaleString() + ' / ' + p4.total.toLocaleString() + ' negocios';
      if ($('scSpeed')) { var rate = p4.etaMin && p4.etaMin > 0 ? Math.round((p4.total - p4.current) / p4.etaMin) : '-'; $('scSpeed').textContent = rate + ' neg/min'; }
      if ($('scActivity')) $('scActivity').textContent = '▶ ' + (p4.item || '-');
      if ($('statBiz')) $('statBiz').textContent = p4.current.toLocaleString();
      if ($('statQueries')) $('statQueries').textContent = p4.current + ' / ' + p4.total;
      if ($('statSpeed')) $('statSpeed').textContent = '-';

    } else {
      setPhaseUI(0);
      if ($('scPhaseLabel')) $('scPhaseLabel').textContent = d.status === 'online' ? 'Iniciando...' : 'Sin actividad';
      if ($('scraperPct')) $('scraperPct').textContent = '-';
      if ($('scraperBar')) $('scraperBar').style.width = '0%';
      if ($('scEta')) $('scEta').textContent = '-';
      if ($('scActivity')) $('scActivity').textContent = d.status === 'online' ? 'Cargando actividad...' : '-';
    }
  } catch (e) {}
  await loadScraperLog(currentLogType);
}

async function loadScraperLog(type) {
  try {
    var d = await api('/api/scraper-log?type=' + type + '&n=80');
    var lines = d.lines || [];
    if ($('scraperLog')) {
      $('scraperLog').innerHTML = lines.map(function(l) {
        var c = /error|Error|SIGINT|Traceback|Exception/i.test(l) ? 'logErr'
              : /warning|warn/i.test(l) ? 'logWarn'
              : /\[\d+\/\d+\]/.test(l) ? 'logInfo'
              : !/\//.test(l) && l.trim().length > 0 && l.trim().length < 40 ? 'logCity'
              : '';
        return '<div class="logLine' + (c ? ' ' + c : '') + '">' + esc(l) + '</div>';
      }).join('');
      $('scraperLog').scrollTop = $('scraperLog').scrollHeight;
    }
  } catch (e) {}
}

function handleScraperLogTab(btn) {
  var type = btn.getAttribute('data-logtype') || 'scraper';
  currentLogType = type;
  document.querySelectorAll('#scraperSection .segBtn').forEach(function(b) { b.classList.remove('isOn'); });
  btn.classList.add('isOn');
  loadScraperLog(type);
}

function esc(s) {
  return String(s ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
function escAttr(s) {
  return esc(s).replaceAll('`', '&#96;');
}

function wire() {
  $('refreshBtn').addEventListener('click', refreshAll);
  $('searchBtn').addEventListener('click', doSearch);
  $('qInput').addEventListener('keydown', (e) => e.key === 'Enter' && doSearch());
  $('cityInput').addEventListener('keydown', (e) => e.key === 'Enter' && doSearch());
  $('chatSend').addEventListener('click', sendChat);
  $('chatInput').addEventListener('keydown', (e) => e.key === 'Enter' && sendChat());

  for (const btn of document.querySelectorAll('.segBtn')) {
    btn.addEventListener('click', async () => {
      for (const b of document.querySelectorAll('.segBtn')) b.classList.remove('isOn');
      btn.classList.add('isOn');
      currentDays = Number(btn.getAttribute('data-days') || 7);
      initServerClock();
  await refreshAll();
    });
  }
}

wire();
refreshAll();
setInterval(refreshAll, 30_000);
