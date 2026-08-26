#!/usr/bin/env python3
"""Plano 7: la pantalla del movil con la conversacion.

Los textos NO se escriben aqui: se leen de /tmp/conversa-rodaje.json, que es lo
que ha contestado Lara de verdad al pasar por handleMessage(). Si alguien quiere
cambiar lo que dice el producto, que lo cambie en el producto.

Lo unico simulado es la pantalla. Deliberadamente **sin el logotipo ni el nombre
de WhatsApp**: se reconoce por la disposicion y por el verde de las burbujas, que
es lo que hace falta para que el espectador piense "esto ya lo tengo". Poner una
marca ajena en un anuncio propio es una decision de Ricardo, no mia.

Genera /tmp/p7/chat.html, que expone window.pintar(t) para que el grabador pueda
pedir el estado exacto en el segundo t. Asi el video sale identico cada vez, en
vez de depender de la velocidad a la que vaya la Pi ese dia.
"""
import html
import json
import re
from pathlib import Path

ORIGEN = Path('/tmp/conversa-rodaje.json')
SALIDA = Path('/tmp/p7/chat.html')

NEGOCIO = 'Centro Lena'
HORA = '17:32'

# Cuando entra cada mensaje. Pensado para que los 10 s del plano acaben en la
# confirmacion, con aire suficiente para leer las respuestas largas de Lara.
TIEMPOS = [0.4, 2.1, 4.6, 6.0, 7.8, 9.0]
ESCRIBIENDO = 0.9   # segundos de puntitos antes de cada respuesta


def formato(t):
    """El *negrita* de WhatsApp, los saltos de linea y los enlaces."""
    t = html.escape(t)
    t = re.sub(r'\*([^*\n]+)\*', r'<b>\1</b>', t)
    t = re.sub(r'(https?://\S+)', r'<span class="url">\1</span>', t)
    return t.replace(chr(10), '<br>')


PLANTILLA = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:720px; height:1560px; overflow:hidden;
               font-family:"Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  body { display:flex; flex-direction:column; background:#ece5dd; }

  .estado { height:44px; background:#0d6b5e; color:#fff; display:flex;
            align-items:center; justify-content:space-between; padding:0 22px;
            font-size:21px; font-weight:600; }

  .cabecera { height:104px; background:#0d6b5e; color:#fff; display:flex;
              align-items:center; gap:18px; padding:0 20px; }
  .atras { font-size:34px; line-height:1; opacity:.95; }
  .avatar { width:64px; height:64px; border-radius:50%; background:#cfd8d4;
            color:#0d6b5e; display:flex; align-items:center; justify-content:center;
            font-size:30px; font-weight:700; }
  .quien { display:flex; flex-direction:column; }
  .quien .n { font-size:27px; font-weight:600; }
  .quien .e { font-size:19px; opacity:.85; }

  .hilo { flex:1; overflow:hidden; padding:20px 18px 12px; position:relative; }
  /* min-height + flex-end pega los mensajes ABAJO mientras no llenan la pantalla,
     que es como se comporta un chat de verdad. Alineados arriba se notaba al
     instante que la pantalla era de mentira. */
  .lienzo { display:flex; flex-direction:column; justify-content:flex-end;
            gap:14px; min-height:100%; }

  .b { max-width:78%; padding:14px 16px 10px; border-radius:16px; font-size:23px;
       line-height:1.42; color:#111b21; position:relative;
       box-shadow:0 1px 1px rgba(0,0,0,.13); }
  .b.suya { background:#fff; align-self:flex-start; border-top-left-radius:4px; }
  .b.mia  { background:#d9fdd3; align-self:flex-end; border-top-right-radius:4px; }
  .b .pie { font-size:17px; color:#667781; text-align:right; margin-top:4px; }
  .b .pie .v { color:#53bdeb; font-weight:700; letter-spacing:-3px; margin-left:4px; }
  /* El enlace del calendario que manda Lara son 180 caracteres y ocupaba cinco
     lineas, comiendose la confirmacion, que es lo que el plano tiene que contar.
     El texto sigue entero en la pagina: solo se recorta lo que se ve, como hace
     cualquier cliente de mensajeria con una URL larga. */
  .url { color:#1d7ec7; text-decoration:underline; display:inline-block;
         max-width:100%; white-space:nowrap; overflow:hidden;
         text-overflow:ellipsis; vertical-align:bottom; }

  .puntos { align-self:flex-start; background:#fff; border-radius:16px;
            border-top-left-radius:4px; padding:18px 20px; display:none;
            box-shadow:0 1px 1px rgba(0,0,0,.13); }
  .puntos.on { display:flex; gap:8px; }
  .puntos i { width:11px; height:11px; border-radius:50%; background:#9aa6ac; display:block; }

  .barra { height:104px; background:#f0f2f5; display:flex; align-items:center;
           gap:14px; padding:0 18px; }
  .campo { flex:1; height:66px; background:#fff; border-radius:33px; display:flex;
           align-items:center; padding:0 24px; color:#8696a0; font-size:23px; }
  .redondo { width:66px; height:66px; border-radius:50%; background:#0d6b5e;
             display:flex; align-items:center; justify-content:center;
             color:#fff; font-size:28px; }
</style></head>
<body>
  <div class="estado"><span>__HORA__</span><span>&#9646;&#9646;&#9646;</span></div>
  <div class="cabecera">
    <div class="atras">&lsaquo;</div>
    <div class="avatar">L</div>
    <div class="quien"><span class="n">__NEGOCIO__</span><span class="e">en l&iacute;nea</span></div>
  </div>
  <div class="hilo" id="hilo"><div class="lienzo" id="lienzo"></div></div>
  <div class="barra">
    <div class="campo">Mensaje</div>
    <div class="redondo">&#10148;</div>
  </div>

<script>
var DATOS = __DATOS__;
var ESCRIBIENDO = __ESCRIBIENDO__;
var HORA = "__HORA__";
var hilo = document.getElementById('hilo');
var lienzo = document.getElementById('lienzo');

function burbuja(m) {
  var d = document.createElement('div');
  d.className = 'b ' + (m.mio ? 'mia' : 'suya');
  d.innerHTML = m.texto + '<div class="pie">' + HORA +
                (m.mio ? '<span class="v">&#10003;&#10003;</span>' : '') + '</div>';
  return d;
}

// Cuanto hay que bajar el hilo con los k primeros mensajes puestos. Se mide una
// sola vez, al cargar: asi pintar(t) no tiene que medir nada y el scroll puede
// interpolarse entre un estado y el siguiente.
var TOPES = [0];
for (var k = 1; k <= DATOS.length; k++) {
  lienzo.innerHTML = '';
  for (var i = 0; i < k; i++) lienzo.appendChild(burbuja(DATOS[i]));
  TOPES.push(Math.max(0, hilo.scrollHeight - hilo.clientHeight));
}
lienzo.innerHTML = '';

var puntos = document.createElement('div');
puntos.className = 'puntos';
puntos.innerHTML = '<i></i><i></i><i></i>';

function suave(x) { return x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x); }

window.pintar = function (t) {
  var k = 0;
  for (var i = 0; i < DATOS.length; i++) if (t >= DATOS[i].t) k = i + 1;

  lienzo.innerHTML = '';
  for (var j = 0; j < k; j++) lienzo.appendChild(burbuja(DATOS[j]));

  // Puntitos justo antes de que conteste Lara
  var siguiente = DATOS[k];
  var escribiendo = !!(siguiente && !siguiente.mio && t >= siguiente.t - ESCRIBIENDO);
  if (escribiendo) { puntos.className = 'puntos on'; lienzo.appendChild(puntos); }

  var destino = escribiendo
    ? Math.max(0, hilo.scrollHeight - hilo.clientHeight)
    : TOPES[k];

  // El salto de scroll se reparte en 0,45 s desde que entra el mensaje, para que
  // no de un tiron. Con los puntitos ya se va directo al fondo.
  var desde = TOPES[Math.max(0, k - 1)];
  var avance = k > 0 ? suave((t - DATOS[k - 1].t) / 0.45) : 1;
  hilo.scrollTop = escribiendo ? destino : desde + (destino - desde) * avance;

  return { mensajes: k, escribiendo: escribiendo, scroll: Math.round(hilo.scrollTop) };
};
window.pintar(0);
</script>
</body></html>
'''


def main():
    msgs = json.loads(ORIGEN.read_text(encoding='utf-8'))
    if len(msgs) != len(TIEMPOS):
        raise SystemExit('hay %d mensajes y %d tiempos: ajusta TIEMPOS'
                         % (len(msgs), len(TIEMPOS)))

    datos = [
        {'mio': m['quien'] == 'Cliente', 'texto': formato(m['texto']), 't': TIEMPOS[i]}
        for i, m in enumerate(msgs)
    ]

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        PLANTILLA
        .replace('__DATOS__', json.dumps(datos, ensure_ascii=False))
        .replace('__NEGOCIO__', NEGOCIO)
        .replace('__HORA__', HORA)
        .replace('__ESCRIBIENDO__', str(ESCRIBIENDO)),
        encoding='utf-8')
    print('escrito', SALIDA, 'con', len(datos), 'mensajes')


if __name__ == '__main__':
    main()
