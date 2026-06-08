# agents.md — nexux.pro (SaaS peluquerías B2B)
> ⛔ BOUNDARY CRÍTICO: nexux.pro es INDEPENDIENTE de nexux.es. No mezclar código, DB, bots ni tokens.

---

## FUENTE DE VERDAD
`~/nexus-brain/nexux-live-state.md` — leer SIEMPRE al inicio.

## ARQUITECTURA

| Componente | Repo/Path | Deploy |
|-----------|-----------|--------|
| Landing + portal | `~/nexux-pro/` | Vercel (main auto-deploy) |
| API clientes | `~/nexux-clients/` | Pi :3460 (PM2: nexux-clients) |
| Leads server | `~/nexux-pro/leads-server.cjs` | Pi (PM2: nexux-pro-leads) |
| Mint dashboard | `~/nexux-pro/mint-dashboard/` | Pi :3700 (PM2: mint-dashboard) |

## PRODUCTOS / PLANES

| Plan | Precio | Canal IA |
|------|--------|---------|
| Starter | Trial | Telegram bot |
| Pro | — | Baileys (WhatsApp Web) |
| Total | — | Twilio WA Business |

## REGLAS DE CÓDIGO

| Regla | Detalle |
|-------|---------|
| pnpm siempre | `pnpm add`, nunca `npm install` |
| Vercel SSR | prerender=false en páginas dinámicas del portal |
| Stripe | nunca duplicar sessions — verificar con `stripe-setup.js` |
| Portal auth | middleware en `src/middleware/auth.ts` — no bypassear |
| owner_email | campo obligatorio en config.json de clientes — sin él no llegan emails |

## CLIENTES EXISTENTES

```
~/nexux-clients/clients/[client-id]/config.json
```
Al modificar: verificar que `owner_email` existe. Si no → añadirlo.

## REGLAS PARA AGENTES AUTÓNOMOS

1. Pull antes de editar: `git -C ~/nexux-pro pull origin main`
2. Vercel despliega al push — testear staging antes si hay cambio en portal
3. Stripe webhooks: no cambiar endpoint path sin actualizar Vercel env
4. Cloudflared: `pi.nexux.pro` → :3460 (provision). No cambiar puerto.
5. Al finalizar: `cat > ~/nexux-pro/progress/YYYYMMDD_tarea.md` con resumen
6. Guardar en brain: `python3 ~/scripts/nexux-update-brain.py --notes-append "[nexux.pro] resumen"`

## CHECKPOINTS ANTES DE COMMIT

- [ ] `node -c` o `tsc --noEmit` sin errores
- [ ] No exponer Stripe secret key en frontend
- [ ] Portal APIs devuelven 200 (verificar con curl)
- [ ] `owner_email` presente en configs afectados
