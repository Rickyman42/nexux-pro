#!/usr/bin/env node
/**
 * Mapa de calor de una pagina publica de nexux.pro.
 *
 * Parte del generador que escribio Codex el 13-sep-2026. Cambios: ya no hace
 * falta que el visitante acepte cookies (el mapa mide a todo el mundo, como
 * Umami), vale para cualquier pagina del embudo, pinta encima una foto de la
 * pagina de verdad --una cuadricula suelta no dice nada-- y anade el mapa que
 * mas ensena: los clics que NO dan en nada.
 *
 *   node scripts/generar-mapa-calor.mjs --dias 7 --ruta /paquetes/recepcionista
 */
import { execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync, existsSync, unlinkSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const COLUMNAS = 12;
const FILAS = 24;
const CONTENEDOR_BD = 'umami-db-1';
const DOMINIO = 'nexux.pro';

function argumento(nombre, porDefecto) {
  const i = process.argv.indexOf(nombre);
  return i === -1 ? porDefecto : process.argv[i + 1] || porDefecto;
}

const dias = Number.parseInt(argumento('--dias', '7'), 10);
const ruta = argumento('--ruta', '/paquetes/recepcionista');
const salida = resolve(argumento('--salida', '/tmp/nexux-mapa-calor.html'));
const sinFoto = process.argv.includes('--sin-foto');

if (!Number.isInteger(dias) || dias < 1 || dias > 365) {
  throw new Error('--dias tiene que ser un numero entre 1 y 365');
}
// La ruta entra en una consulta SQL: se comprueba en vez de confiar.
if (!/^\/[a-z0-9/-]*$/.test(ruta)) {
  throw new Error(`--ruta no vale: ${ruta}`);
}

// ── 1. Los datos ────────────────────────────────────────────────────────────
const sql = `
  SELECT
    e.event_name,
    MAX(CASE WHEN d.data_key = 'grid_x' THEN d.number_value END)::int AS grid_x,
    MAX(CASE WHEN d.data_key = 'grid_y' THEN d.number_value END)::int AS grid_y,
    MAX(CASE WHEN d.data_key = 'depth_percent' THEN d.number_value END)::int AS hasta,
    MAX(CASE WHEN d.data_key = 'device' THEN d.string_value END) AS aparato,
    MAX(CASE WHEN d.data_key = 'sobre' THEN d.string_value END) AS sobre
  FROM website_event e
  JOIN website w ON w.website_id = e.website_id
  LEFT JOIN event_data d ON d.website_event_id = e.event_id
  WHERE w.domain = '${DOMINIO}'
    AND (e.url_path = '${ruta}' OR e.url_path = '${ruta}/')
    AND e.created_at >= NOW() - INTERVAL '${dias} days'
    AND e.event_name IN ('heatmap_click', 'heatmap_hover', 'scroll_depth_reached')
  GROUP BY e.event_id, e.event_name;
`;

const salidaSql = execFileSync('docker', [
  'exec', CONTENEDOR_BD, 'psql', '-U', 'umami', '-d', 'umami', '-At', '-F', '\t', '-c', sql,
], { encoding: 'utf8' });

const eventos = salidaSql.trim()
  ? salidaSql.trim().split('\n').map((linea) => {
    const [nombre, x, y, hasta, aparato, sobre] = linea.split('\t');
    return {
      nombre,
      x: Number.parseInt(x, 10),
      y: Number.parseInt(y, 10),
      hasta: Number.parseInt(hasta, 10),
      aparato: aparato || 'desconocido',
      sobre: sobre || '',
    };
  })
  : [];

// ── 2. La foto de la pagina, para poner el mapa encima ──────────────────────
function foto(aparato) {
  if (sinFoto) return null;
  const ancho = aparato === 'mobile' ? 375 : 1280;
  const png = `/tmp/nexux-foto-${aparato}.png`;
  try {
    execFileSync('python3', [
      resolve(dirname(process.argv[1]), 'captura-pagina.py'),
      `https://${DOMINIO}${ruta}`, String(ancho), png,
    ], { encoding: 'utf8', timeout: 120000 });
    if (!existsSync(png)) return null;
    const datos = readFileSync(png).toString('base64');
    unlinkSync(png);
    return `data:image/png;base64,${datos}`;
  } catch (err) {
    console.warn(`  (sin foto de ${aparato}: ${String(err.message).slice(0, 80)})`);
    return null;
  }
}

// ── 3. Las cuadriculas ──────────────────────────────────────────────────────
function cuadricula(filtro) {
  const rejilla = Array.from({ length: FILAS }, () => Array(COLUMNAS).fill(0));
  let total = 0;
  for (const e of eventos) {
    if (!filtro(e)) continue;
    if (!Number.isInteger(e.x) || !Number.isInteger(e.y)) continue;
    if (e.x < 0 || e.x >= COLUMNAS || e.y < 0 || e.y >= FILAS) continue;
    rejilla[e.y][e.x] += 1;
    total += 1;
  }
  return { rejilla, total };
}

function pintar(titulo, explicacion, { rejilla, total }, fondo, color) {
  // `fondo` es el nombre de una clase de CSS, no la imagen: asi el PNG viaja
  // una sola vez por aparato en vez de repetirse en cada seccion.
  const max = Math.max(0, ...rejilla.flat());
  const celdas = rejilla.flatMap((fila, y) => fila.map((valor, x) => {
    const alpha = valor && max ? (0.15 + (valor / max) * 0.72).toFixed(2) : '0';
    const titulo = valor ? ` title="${valor} en la fila ${y + 1}"` : '';
    return `<i${titulo} style="background:rgba(${color},${alpha})"></i>`;
  })).join('');

  const cuerpo = total
    ? `<div class="mapa ${fondo || ''}">${celdas}</div>`
    : '<p class="vacio">Todavia no hay senales suficientes en esta vista.</p>';

  return `<section><h2>${titulo}</h2><p class="ayuda">${explicacion}</p>
    <p class="dato">${total} senales</p>${cuerpo}</section>`;
}

function barrasDeScroll(aparato) {
  const hitos = [25, 50, 75, 100].map((h) => ({
    h,
    n: eventos.filter((e) => e.nombre === 'scroll_depth_reached' && e.aparato === aparato && e.hasta === h).length,
  }));
  const max = Math.max(1, ...hitos.map((i) => i.n));
  const primera = hitos[0].n;
  const ultima = hitos[3].n;
  const resumen = primera
    ? `De cada 100 que empiezan a bajar, ${Math.round((ultima / primera) * 100)} llegan al final.`
    : 'Nadie ha bajado todavia en este aparato.';
  return `<section><h2>Hasta donde bajan · ${aparato === 'mobile' ? 'movil' : 'escritorio'}</h2>
    <p class="ayuda">${resumen}</p>
    ${hitos.map((i) => `<div class="barra"><span>${i.h}%</span><i style="width:${(i.n / max) * 100}%"></i><b>${i.n}</b></div>`).join('')}</section>`;
}

// ── 4. El informe ───────────────────────────────────────────────────────────
const fondoMovil = foto('mobile');
const fondoEscritorio = foto('desktop');
const cuando = new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' });

const secciones = [
  pintar('Donde pulsan · movil',
    'Cuanto mas intenso, mas dedos han caido ahi.',
    cuadricula((e) => e.nombre === 'heatmap_click' && e.aparato === 'mobile'), 'fondo-movil', '38,196,186'),
  pintar('🔴 Pulsan y no pasa nada · movil',
    'Clics que NO cayeron sobre un boton ni un enlace. Si aqui hay color, la gente esta intentando tocar algo que no responde.',
    cuadricula((e) => e.nombre === 'heatmap_click' && e.aparato === 'mobile' && e.sobre === 'nada'), 'fondo-movil', '229,90,70'),
  pintar('Donde pulsan · escritorio',
    'Lo mismo, en pantalla grande.',
    cuadricula((e) => e.nombre === 'heatmap_click' && e.aparato === 'desktop'), 'fondo-escritorio', '38,196,186'),
  pintar('🔴 Pulsan y no pasa nada · escritorio', 'Clics que no dieron en nada pulsable.',
    cuadricula((e) => e.nombre === 'heatmap_click' && e.aparato === 'desktop' && e.sobre === 'nada'), 'fondo-escritorio', '229,90,70'),
  pintar('Donde se para el raton · escritorio',
    'Donde se entretiene el cursor. Suele ir con lo que estan leyendo.',
    cuadricula((e) => e.nombre === 'heatmap_hover' && e.aparato === 'desktop'), 'fondo-escritorio', '120,110,220'),
  barrasDeScroll('mobile'),
  barrasDeScroll('desktop'),
].join('\n');

const html = `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mapa de calor · ${ruta}</title><style>
body{margin:0;background:#f7fbfb;color:#162026;font:16px/1.45 system-ui,-apple-system,sans-serif}
.envoltorio{max-width:1180px;margin:auto;padding:38px 20px}
h1{margin:0 0 6px;font-size:30px}h2{font-size:17px;margin:0 0 4px}
.cabecera p{color:#5b6870;margin:0 0 6px;max-width:70ch}
section{display:inline-block;vertical-align:top;width:calc(50% - 26px);min-width:320px;margin:13px;
  background:#fff;border:1px solid #dce9e8;border-radius:16px;padding:18px;box-sizing:border-box}
.ayuda{color:#5b6870;font-size:14px;margin:0 0 8px}
.dato{font-weight:600;margin:0 0 12px;font-size:14px}
.vacio{color:#8a969c;font-style:italic}
.mapa{display:grid;grid-template-columns:repeat(${COLUMNAS},1fr);grid-template-rows:repeat(${FILAS},1fr);
  gap:0;aspect-ratio:1/2;border:1px solid #e1eded;background-size:100% 100%;background-position:top center}
${fondoMovil ? `.fondo-movil{background-image:url('${fondoMovil}')}` : ''}
${fondoEscritorio ? `.fondo-escritorio{background-image:url('${fondoEscritorio}')}` : ''}
.mapa i{display:block;min-height:8px}
.barra{display:grid;grid-template-columns:52px 1fr 34px;gap:9px;align-items:center;margin:10px 0}
.barra i{display:block;height:11px;min-width:1px;border-radius:9px;background:#26c4ba}
.barra b{text-align:right}
@media(max-width:800px){section{width:100%;min-width:0;margin:10px 0}}
</style></head>
<body><main class="envoltorio">
<div class="cabecera">
<h1>Mapa de calor · ${ruta}</h1>
<p>Ultimos ${dias} dias · generado el ${cuando} · ${eventos.length} senales en total.</p>
<p>Se guarda la casilla de una cuadricula de ${COLUMNAS} x ${FILAS}, nunca el punto exacto. No hay
sesiones grabadas, ni texto escrito, ni recorridos de personas. No se mide en el portal de ningun
cliente ni en las paginas de reserva.</p>
</div>
${secciones}
</main></body></html>`;

mkdirSync(dirname(salida), { recursive: true });
writeFileSync(salida, html, 'utf8');
console.log(`Mapa generado: ${salida}`);
console.log(`Senales analizadas: ${eventos.length}`);
if (!eventos.length) {
  console.log('Sin datos todavia: o no esta desplegado, o aun no ha pasado nadie por esa pagina.');
}
