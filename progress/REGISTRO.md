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
