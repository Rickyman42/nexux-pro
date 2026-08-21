# REGISTRO — nexux.pro

Una línea por tarea terminada. Formato:

```
YYYY-MM-DD | agente | qué se hizo | commit o evidencia | OK|PARCIAL|FALLO
```

Si es PARCIAL o FALLO, la línea siguiente lleva exactamente `  causa: <texto>`.
La evidencia completa va además a ~/nexus-brain/quality-ledger.md. Aquí solo el índice.

---

2026-08-21 | claude-code | Pivote a mono-producto: plan único Nexux Recepcionista IA 29 EUR, tres planes viejos retirados con 301 | commit 48fe2b9 · nexux-verify 4/4 OK · pnpm build completo | OK
2026-08-21 | claude-code | Fix del widget Lara: marca la conversación como trial cuando el launcher lleva data-trial | commit 1083e6f · sintaxis del script validada | OK
2026-08-21 | claude-code | Medición de Bing sobre nexux.pro: indexado y servido, NO suprimido | navegador real, site:nexux.pro devuelve home y /paquetes/starter con título y meta reales | PARCIAL
  causa: el control positivo (site:vercel.com) devolvió basura no relacionada, así que el recuento de páginas indexadas no es fiable; hace falta Bing Webmaster Tools
2026-08-21 | claude-code | Análisis SEO de competencia: sitemaps de recepcionista.com (615 URLs), engrana.es y citaflow.com + demanda por autocompletado | https://claude.ai/code/artifact/63206024-19f1-4c1e-9011-0e37fa00fad0 | PARCIAL
  causa: Google Trends devolvió error 429, así que el volumen absoluto de búsqueda sigue sin medir; pendiente Planificador de Palabras Clave con la cuenta de Google Ads de Ricardo
2026-08-21 | claude-code | Estudio de mercado y DAFO del producto, con veredicto go/no-go | https://claude.ai/code/artifact/90466fee-720d-43dd-aa26-7edd8cb62635 | OK
2026-08-21 | claude-code | AGENTS.md reescrito como norma de entrada al proyecto + CLAUDE.md puntero + este registro | commit pendiente | OK
  causa: (nota) el agents.md anterior mandaba escribir en progress/ desde el 30-may y la carpeta nunca existió
2026-08-21 | claude-code | Google Ads Planificador de Palabras Clave, España, ago-2025/jul-2026, cuenta Ytical: volumen exacto de las 9 keywords candidatas de SEO | recepcionista ia 100-1mil/mes +900% interanual competencia Alta CPC 3.78-15.92EUR; recepcionista virtual 10-100/mes Media CPC 1.85-10.39EUR; chatbot citas, bot whatsapp empresa, software citas peluqueria, agenda citas whatsapp, no perder llamadas, alternativa a booksy = todas 0-10/mes | OK
2026-08-21 | claude-code | Comprobado tambien 'recepcionista ia whatsapp' en Google Ads Keyword Planner, a peticion de Ricardo (dudaba si atacarla) | 0-10 busquedas/mes, sin dato de crecimiento ni CPC. recepcionista ia (sin whatsapp) sigue siendo la unica con volumen: 100-1mil, +900% interanual | OK
2026-08-21 | claude-code (Fable 5) | Plan estrategico definitivo: 5 pilares, 3 fases con criterios de salida, puerta a 2 meses, metricas semanales y lista de descartados | https://claude.ai/code/artifact/8e875ac3-a876-4e75-b028-148e5afcc47d | OK
2026-08-21 | claude-code (Fable 5) | Detectado bloqueante n1: checkout.ts sigue con planes 249/449/749, stripe_url del plan nuevo es placeholder y no existe precio de 29 EUR en Stripe; telefono no obligatorio en checkout | grep en src/scripts/checkout.ts L4-7 y src/data/plans.ts L36 | PARCIAL
  causa: la web publica un precio que aun no se puede pagar; primera tarea de Fase 0, requiere crear el precio en el dashboard de Stripe (accion de Ricardo o sesion con acceso)
2026-08-21 | claude-code | Demo /demo verificada en vivo: FUNCIONA (IA real consulta disponibilidad y propone huecos correctos, CRM devuelve citas) pero solo esta enlazada desde /promo, no desde home ni menu | POST pi.nexux.pro/demo/chat devolvio respuesta correcta con fecha real 21-ago y huecos del sabado; GET /demo/appointments devolvio citas; grep de href=/demo en src/ da 1 sola ocurrencia (promo.astro:73) | PARCIAL
  causa: el mejor activo de venta lleva meses invisible en la navegacion; ademas la sesion entera de estrategia se planteo sin tenerlo en cuenta hasta que Ricardo lo señalo. Enlazarlo es Fase 0.
2026-08-21 | claude-code | Lara (chat de la web) sigue vendiendo los planes viejos en produccion: dice 49 EUR promo / Starter 249, ofrece 7 dias de prueba y promete llamadas en el plan Pro (voz que no existe) | POST pi.nexux.pro/api/lara-web/chat en vivo devolvio: 'el plan ideal es el Starter... Precio especial de lanzamiento: 49 EUR/mes... prueba gratis de 7 dias'. Prompt en nexux-clients/lib/bot-prompt-lara.js L16,38-42,74,89-90 | PARCIAL
  causa: tres precios vivos a la vez (web 29, Lara 49/249, checkout 249/449/749). Lara es lo mas urgente porque es lo unico que habla con visitantes. Requiere decidir antes: mes gratis del plan nuevo vs los 7 dias que fija la regla de negocio anterior.
2026-08-21 | claude-code | Guion de Lara (web) reescrito al producto unico: 29 EUR, garantia 30 dias sin preguntas (fuera el trial de 7 dias, decision de Ricardo), retirados Instagram/llamadas/mini-web/blog SEO/Meta Ads/planes Starter-Pro-Total, anadida la demo como argumento y regla anti-invencion de enlaces. LARA_PLANS y parseo [DONE:] actualizados en provision-http.js | nexux-verify 6/6 OK + 4 pruebas en vivo contra pi.nexux.pro/api/lara-web/chat: precio dice 29 EUR; ante 'atiende llamadas?' responde que no y no lo vende; ante 'plan Starter 249 con Instagram' responde que eso era de antes; cierre emite done=true con tarjeta de 29 EUR | OK
2026-08-21 | claude-code | Cazado en pruebas: Lara inventaba la URL nexux.pro/registro (404 confirmado). Corregido con lista blanca de 3 enlaces y prohibicion de enlazar en el cierre | curl a /registro devuelve 404; retest tras el parche: 0 URLs inventadas, done=true | OK
2026-08-21 | claude-code | Auditados los canales que vendia Lara contra la configuracion real | templates/_base.json: instagram enabled=false, voice enabled=false; solo whatsapp (baileys) y telegram operativos. Sin codigo de integracion de Instagram en provision-http.js | OK
2026-08-21 | claude-code | Stripe creado y alineado: producto prod_V6xlRvLwrMTEJF (Nexux Recepcionista IA) y precio price_1U6jqd2SQwDzHtsFf3wEcuQe (29 EUR/mes recurrente) en la cuenta LIVE. Anadido plan a stripe-session.js, STRIPE_PRICE_RECEPCIONISTA al .env y a las DOS listas blancas de plan de provision-http.js (L230 y L942) | POST /api/stripe/create-session con plan=recepcionista devuelve clientSecret cs_live_...; la sesion en Stripe confirma importe 29.0 EUR, mode=subscription, metadata.plan=recepcionista, phone_number_collection=True, return_url a /paquetes/recepcionista. nexux-verify 5/5 OK | OK
2026-08-21 | claude-code | Limpieza de paginas: eliminadas prueba-gratis, oferta y promo (las tres servian precios viejos 249/49 en produccion) con 301 a /paquetes/recepcionista. Los 7 CTA que apuntaban a /prueba-gratis (5 de ellos en la demo) reapuntados antes de borrar, y arreglado el selector de tracking de la demo | grep de /prueba-gratis en src/ queda vacio; pnpm build completo OK; vercel.json con 6 redirects y JSON valido | OK
