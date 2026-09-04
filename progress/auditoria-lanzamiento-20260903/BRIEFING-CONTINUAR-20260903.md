# Briefing para continuar Nexux.pro desde otra cuenta de Claude

## Resumen para Ricardo

- Objetivo: retomar la auditoría de lanzamiento desde cero, ejecutar la Ola 1 del PRP v5 (ya cerrado) hasta demostrar el recorrido completo del producto de 29 €.
- Código: exclusivamente en la Pi. El fichero PRP vive en Windows, pero los repositorios ejecutables están en `/home/nexux/nexux-pro` y `/home/nexux/nexux-clients`.
- Autorizado: lectura, diagnóstico, revisión y cambios locales en worktrees después de confirmar el estado actual.
- No autorizado sin una confirmación nueva: push, despliegue, reinicios de producción, cambios en Stripe, edición de `.env`, pagos/reembolsos, borrado de clientes o rotación de credenciales.
- Política: compras sin prueba gratuita; demos manuales de 7 días; altas manuales pagadas no son demos.

## Prompt final para Claude Code

```text
You are taking over the Nexux.pro launch-hardening work from a different Claude account. You inherit no reliable conversational context. Treat every statement below as a pointer to verify, not as current truth.

OBJECTIVE

Bring the €29 Nexux Recepcionista IA path to a release-ready, evidence-backed state:

flyer/advert → QR → /f/dN → /demo → Lara → €29 Checkout → exactly one complete account → exactly one welcome email → working portal → connected channel → real appointment → subscription cancellation → the connected channel stops responding.

The audit is complete, but implementation has not started. The PRP is v5 and its money-path diagnosis was re-measured line by line against the executing code on 3-4 Sep; re-ground it briefly, then execute. Then implement the approved local code changes in isolated worktrees. Do not claim launch readiness until the complete acceptance path has passed.

AUTHORITATIVE LOCATIONS

- Universal rules: `/home/nexux/nexus-brain/AGENTS.md`
- Live state: `/home/nexux/nexus-brain/nexux-live-state.md`
- Coordination: `/home/nexux/nexus-brain/COORDINACION-IA.md`
- Kaizen flags: `/home/nexux/nexus-brain/kaizen-flags.md`
- Skill registry: `/home/nexux/nexus-brain/skill-registry.md`
- Web repo: `/home/nexux/nexux-pro`
- Runtime/client repo: `/home/nexux/nexux-clients`
- Audit reports: `/home/nexux/nexux-pro/progress/auditoria-lanzamiento-20260903/`
- Cross-audit table: `/home/nexux/nexux-pro/progress/auditoria-lanzamiento-20260903/TABLA-CRUZADA.md`
- Final PRP **v5** (closed for execution) on Windows: `C:\Users\Nexux\.claude\PRPs\20260903_213000_arreglo-lanzamiento-nexux-pro.md`
- Same PRP v5 on the Pi (byte-identical): `/home/nexux/nexux-pro/progress/auditoria-lanzamiento-20260903/PRP-ARREGLO-LANZAMIENTO-V5.md` (V4 kept there as history)

SSH FROM WINDOWS

`ssh -i C:/Users/Nexux/.ssh/nexux_pi -p 2222 nexux@192.168.0.120`

MANDATORY STARTUP — READ ONLY

1. Read the five Nexux authority files listed above, the project AGENTS file, the skill registry, the seven audit reports, TABLA-CRUZADA.md, and the PRP v5 completely.
2. Inspect both real repositories and the files that execute. Do not infer execution from documentation or rewrites.
3. Run read-only git checks in both repos: branch, status, recent log, remotes, worktrees, and ahead/behind after `git fetch origin`.
4. Do not run `git pull` in either dirty main checkout.
5. Confirm that `nexux-clients` still contains the local security commits `abd1c26` and `efd9797`, and identify the exact commit that each new worktree must start from.
6. Recheck production health and route fingerprints without creating clients, appointments, emails, payments, or alerts.

ADVERSARIAL REVIEW GATE

Before editing, briefly re-ground the PRP v5 (its section 2 is measured fact, not hypothesis). Pay special attention to these already identified risks:

- Vercel receives Checkout, but automatic provisioning still depends on the Pi. A Pi failure must produce a retryable non-2xx response; never describe the flow as Pi-independent.
- Stripe must use two direct endpoints with distinct secrets and event sets. Do not forward Stripe signatures between Vercel and the Pi.
- The Pi webhook route must receive the untouched raw body before `express.json()` and must fail closed when the secret, signature, timestamp, or body is invalid.
- Vercel signature verification also needs a 300-second tolerance.
- Do not store webhook deduplication only in Vercel memory. Do not mark an event completed before every mandatory effect finishes. Persistent state must distinguish processing, completed, and retryable failure.
- `/provision` currently starts its email after returning the HTTP response. The final design must await Brevo, verify a 2xx response, persist email status, retry a missing email, and suppress duplicates. Vercel must not send a second welcome email. Telegram payment alerts must also be idempotent.
- Account type must be explicit: Stripe-paid, manually-paid, or demo. Only demo gets seven days. Never infer trial status solely from a missing Stripe subscription ID.
- Cancellation must stop the channel used in the acceptance test. Audit WhatsApp, Telegram, scheduled jobs, and any other message entry point; changing only `lib/whatsapp.js` is insufficient if Telegram is tested.
- The portal appointment bug covers create, edit, and drag. Time-zone conversion must use the target appointment date and must be tested in summer and winter.
- A real public launch must not keep known active published secrets. Verify which leaked credentials remain active without printing them, and stop for Ricardo before rotation.

If the v4 still has a material flaw, update the PRP with evidence before implementation. If it passes, state the verdict and continue with local worktree implementation. Use Opus only for the critical Stripe/adversarial design review; use Sonnet for implementation and routine checks.

AUTHORIZATION AND STOP CONDITIONS

This message authorizes read-only inspection and local code changes in isolated worktrees after the review gate. It does NOT authorize:

- editing or displaying `.env` or any secret;
- creating, modifying, disabling, or deleting Stripe endpoints;
- a real charge, cancellation, refund, or customer deletion;
- pushing, merging, deploying, or restarting production;
- rotating credentials;
- changing unrelated infrastructure.

Stop immediately before each of those operations and ask Ricardo for the exact authorization. Do not combine them into one vague approval request. The recommended current business state is to keep real purchase CTAs closed until the acceptance test passes; present the smallest reversible way to do that, but do not deploy it without approval.

IMPLEMENTATION RULES

- Work only on the Pi code. Never edit Nexux.pro code in Windows.
- Preserve all unrelated dirty changes.
- Use separate worktrees based on explicitly verified commits, with `task/ola1-lanzamiento-pro` and `task/ola1-lanzamiento-clients` branches unless those names already exist.
- Never use `git add .`, `git add -A`, force push, hard reset, broad clean, or destructive filesystem commands.
- Do not edit `.env`, credentials, generated dependencies, or unrelated Nexux projects.
- Keep the €29 product horizontal. The customer field is “Nombre de tu negocio”, not “Nombre de tu salón”.
- Paid purchases have no free trial and use the 30-day refund guarantee. Manual demos may last seven days. A manual recovery account for a paying customer is a normal paid account.
- Follow the order and gates in PRP v5. Do not compress critical Stripe, email, Telegram, time-zone, security, or acceptance work to meet an arbitrary one-day estimate.

MINIMUM IMPLEMENTATION SCOPE

1. Secure and correctly route both Stripe webhook handlers.
2. Make Checkout provisioning retryable and persistently idempotent under duplicate and concurrent deliveries.
3. Produce one complete account, one controlled welcome email, and one idempotent owner alert.
4. Collect “Nombre de tu negocio” before Checkout and preserve all €29 paths.
5. Make paid/manual/demo account mode explicit.
6. Ensure cancellation disables every runtime entry point used by the connected channel.
7. Prevent Telegram truncation from losing or exposing booking actions; verify the actual AI stop signal or use a separate structured action step.
8. Fix expired-session handling without weakening tenant isolation.
9. Add consent to `/demo`, gate the OpenAI Ads pixel correctly across the site, preserve Meta/GA behavior, and repair UTM attribution.
10. Restore `/api/book` and analytics through the proven public API route pattern, with validation and abuse protection.
11. Fix the Telegram QR script.
12. Fix appointment create/edit/drag time zones and test DST-sensitive dates.
13. Prepare legal text without inventing NIF, address, legal basis, or guarantee conditions; stop for Ricardo to approve real legal data.
14. Add API outage monitoring only after confirming the chosen monitor is independent enough to detect a Pi/disk outage.

VERIFICATION

For every fix:

- show the executable file and the failing behavior first;
- add a regression test and deliberately sabotage the tested condition once to prove the test fails;
- run syntax checks and focused tests;
- run the full relevant suite;
- for the web, run `NODE_OPTIONS=--max-old-space-size=1400 pnpm build` on the Pi;
- use a Vercel preview before production;
- record exact commands and outputs without secrets;
- keep implemented, locally verified, preview verified, and production verified as separate states.

Before any production push, present:

1. exact commits and file list;
2. clean worktree status;
3. test and build outputs;
4. preview evidence;
5. previous deployment ID and rollback plan;
6. the remaining approvals Ricardo must give.

After an authorized deployment, run five health-check rounds over five minutes. Three consecutive failures require immediate rollback. Finish with `nexux-verify.py`, the quality ledger, progress register, and live-state update.

FINAL ACCEPTANCE

Use the real €29 product; a coupon on that same product is acceptable, but a temporary replacement product is not. Immediately before the test, ask Ricardo for authorization for the charge and external Stripe actions. Prove all eight links:

1. payment completes;
2. exactly one full client account is created;
3. exactly one welcome email is received;
4. its portal link works;
5. one real channel connects;
6. one real appointment appears in both the client data and Google Calendar;
7. cancellation reaches the Pi lifecycle endpoint;
8. the connected channel stops responding and the account is inactive.

Record duplicate-delivery behavior and the `/pub-api/book` response. Cleanup must target only the uniquely named test subscription, event data, calendar event, and client created during this run, and requires Ricardo’s approval before destructive or financial actions.

COMMUNICATION

Keep updates concise and in Spanish. Lead with evidence and current status. Do not say “done”, “fixed”, “safe”, or “launch-ready” without executed proof. When blocked, state the exact blocker and the smallest decision Ricardo needs to make.

VERIFIED STATE AT HANDOVER — measured 2026-09-03 ~23:00 CEST, read-only

These were checked with live commands at handover time. They are still pointers to re-verify, but they
were true at this moment. If any differs when you check, trust your own measurement and say so.

- SSH works in both forms from this Windows machine: the long one above, and plain
  `ssh nexux@192.168.0.120 "<cmd>"`.
- Production: `GET https://nexux.pro/` 200 (0.35s) · `/demo` 200 · `/f/d1` 302 · `https://pi.nexux.pro/health` 200.
- The blocker is still live: `POST https://nexux.pro/api/book` -> 404 and `POST /api/analytics/ob` -> 404.
- Ola 0 holds: `GET https://pi.nexux.pro/admin/stats` returns 401 with no key and 401 with the old
  hardcoded key. Do not re-fix it. (Note: the route is `/admin/stats`; `/admin/clients` does not exist
  and returns 404 — a 404 there is not proof of anything.)
- `nexux-clients`: on `main` at `efd9797`, **3 local commits not pushed** (`44241c0`, `abd1c26`, `efd9797`),
  1 modified file, 8+ untracked. Its remote branch is `origin/main`.
- `nexux-pro`: on `main` at `71a2e03`, **level with origin/main (0 ahead, 0 behind)**, 2 modified
  (`AGENTS.md`, `progress/REGISTRO.md`) and ~30 untracked (video/advertising working files under `tmp/`,
  `output/`, plus the audit folder itself). Do not sweep these into a commit.
- `git worktree list` in `nexux-pro` shows **6 stale worktrees marked `prunable`** with broken UNC paths
  (`//192.168.0.120/nexux/nexux-pro-wt-*`, branches `codex/*`). They are leftovers. Check whether any
  `codex/*` branch holds unmerged work BEFORE pruning, and ask Ricardo before removing anything.
- Branches `task/ola1-lanzamiento-pro` and `task/ola1-lanzamiento-clients` do not exist yet: the names are free.
- The PRP is byte-different but CONTENT-IDENTICAL in both locations (the Pi copy just has two trailing
  blank lines). Either is fine to read; the Pi copy lives next to the seven audit reports.
- PM2: `nexux-clients` online with 4 restarts (those restarts are the two deliberate security patches of
  3-sep, not crashes). `nexux-blog-autopilot` is stopped with 5307 restarts — that belongs to nexux.es,
  NOT to nexux.pro; do not touch it.

TRAPS THIS PROJECT HAS ALREADY PAID FOR — do not rediscover them

1. The `api/` folder at the ROOT of `~/nexux-pro` are Vercel serverless functions and they WIN over
   `vercel.json` rewrites and over `src/pages/api/`. This single fact is the root cause of four of the
   fourteen blockers, including the `/api/book` 404. Anything you add under `/api/` in Astro is born dead
   and silent. Always confirm who really answers: `curl -sD- https://nexux.pro/api/...` — header
   `Server: Vercel` means the Pi never saw it.
2. `/home/nexux` is ANOTHER git repository that tracks the entire home folder, including `.ssh` and
   credential files. A `pull`/`rebase`/`stash` there has already caused an SSH lockout. NEVER run git
   write operations from `/home/nexux`. Work from `~/nexux-pro` and `~/nexux-clients`, which are their
   own repositories.
3. `pnpm build` on the Pi WITHOUT `NODE_OPTIONS=--max-old-space-size=1400` took the whole Pi down on
   3-sep (out of RAM, every service restarted). With the flag the build also drops from 652s to 89s.
   Never build on the Pi without it.
4. There are TWO plan allowlists in `nexux-clients/provision-http.js` (around lines 230 and 942).
   Changing only one leaves payment broken with an unhelpful `invalid_plan`.
5. Vercel's CDN caches HTML for minutes. Verify with a cache-buster (`?cb=<n>`) or you will read the old
   page and conclude the deploy failed.
6. Astro does not apply scoped styles to elements created by JavaScript (use `:global()`).
7. Editing over SSH with a heredoc lets bash expand `${...}` inside your script. Write the file locally
   and pipe it (`ssh 'python3 -' < script.py`) or `scp` it.
8. Structured data and prices are never in one place only. Before closing any price/schema task:
   `grep -rl "application/ld+json" src/`.

HOW A TASK IS CLOSED IN THIS PROJECT

- One line appended to `~/nexux-pro/progress/REGISTRO.md`:
  `YYYY-MM-DD | agente | qué se hizo | commit o evidencia | OK|PARCIAL|FALLO`
  If PARCIAL or FALLO, the NEXT line must be exactly `  causa: <texto>` (two leading spaces) or the kaizen
  scanner never sees it.
- Evidence also goes to `~/nexus-brain/quality-ledger.md`, and state to
  `python3 ~/scripts/nexux-update-brain.py --notes-append "[agente fecha] ..."`.
- Before saying anything is done: `export NEXUX_AGENT=<your-name>` then
  `python3 ~/scripts/nexux-verify.py gitclean:/home/nexux/nexux-pro syntax:<file> url:<url>
   service:nexux-clients`. A FALLO verdict means it is NOT done. That command's output IS the evidence.
  It does not validate `.css` or `.astro` — for those, the build is the check.

OPEN DECISIONS RICARDO HAS NOT MADE YET (do not assume either way)

1. Authorize ONE push to `nexux-pro` from the worktree, with preview and rollback noted. Without it no web
   fix exists. NOT GRANTED YET.
2. Whether the real purchase button stays open while provisioning is broken. NOT DECIDED. Until he decides,
   anyone who pays is charged and gets no account.
3. Rotating the 21 secrets already published on GitHub. NOT DONE.
4. Stripe webhook endpoint changes, the Pi's own signing secret, and the acceptance-test charge/refund all
   need his explicit approval at the moment of doing them.

REVIEW FINDINGS AT HANDOVER — a 6-lens review of THIS briefing and of PRP v5, run 2026-09-03 23:00

Read this section as claims to re-measure, not as truth. Its adversarial verification stage was cut off by
a session limit, so only the items marked CONFIRMED were independently re-measured. Everything marked
UNVERIFIED comes from a single reviewer and MUST be re-measured before you act on it. The full raw output
is on the Pi: `~/nexux-pro/progress/auditoria-lanzamiento-20260903/REVISION-BRIEFING-Y-PRP-20260903.json`.

CONFIRMED — re-measured by a second party, these are real

1. THERE IS A SECOND `/webhook/stripe` HANDLER AND PRP v5 DOES NOT MENTION IT.
   `~/nexux-clients/provision-http.js:1611` is the one the PRP describes. But
   `~/nexux-clients/lib/admin.js:49` registers ANOTHER `app.post('/webhook/stripe', ...)` on a separate
   Express server (`ADMIN_PORT || 3458`), started via `startAdmin` imported by `~/nexux-clients/index.js:9`.
   It reads `req.body.toString('utf8')`, `JSON.parse`s it, and calls `handleStripeWebhook(body, rawBody,
   sigHeader, ...)` from `lib/stripe-webhook.js`.
   → Fixing only `provision-http.js` leaves this one untouched. BEFORE designing the webhook work, measure:
     is port 3458 reachable from outside (cloudflared/nginx/firewall)? does `handleStripeWebhook` actually
     enforce the signature, or only when a secret is present? Report what you measure; do not assume either.
2. PRP v5 CONTAINS A FACTUAL ERROR ABOUT THE TRIAL EXPIRER. Its section 7 says no trial-expiry script
   exists. `~/nexux-clients/scripts/trial-expiry.js` DOES exist (8360 bytes, 25-jul). What is true is that
   `lib/trial-expiry.js` does not. Check whether that script is wired to a cron before repeating either claim.
3. `~/nexux-pro/src/pages/api/book.ts` EXISTS in source and still returns 404 in production — which is the
   root-cause trap above (the root `api/` folder wins). The root folder holds `api/stripe/create-session.js`,
   `api/webhook/stripe.js` and `api/leads/pro.js`; there is no `book` there, so the Astro route is shadowed
   into nothing. Confirm the routing fix against production, not against the build output.

UNVERIFIED — single-reviewer claims. Re-measure each before acting; several may be wrong.

4. RESOLVED AND MEASURED (was: disputed) — the reviewer was RIGHT. `provision-http.js:39`
   (`app.use(express.json())`) consumes the body before the route at line 1611; `express.raw()` skips
   itself; `String(req.body)` is `"[object Object]"`; `JSON.parse` throws -> 400 `invalid_json` for EVERY
   event. That route (the one the Cloudflare tunnel exposes as `pi.nexux.pro/webhook/stripe`, directly to
   port 3460, no nginx) has never verified nor executed anything. The real hole is in the FUNCTION
   `lib/stripe-webhook.js:223` (`if (secret && sigHeader)`: no header -> no check), unreachable today,
   and it opens to the internet the moment someone fixes the route without fixing the function first.
   PRP v5 sections 2 and 4 carry the full measured picture and the mandatory order: function first,
   route second, retire `lib/admin.js:49`.

5. Claimed plan defects in v4 (now addressed in v5 sections 5, 6 and 12; re-measure only if v5 looks wrong): D3 may cause repeated emails/alerts on every Stripe retry; P2 cannot be
   verified until D7 is done (ordering problem); acceptance links 7-8 assume an immediate cancellation the
   code does not implement; a signature-forwarding helper still exists in the repo, contradicting the
   "never forward signatures" rule.
6. Claimed briefing gaps: the Vercel preview gate may be unreachable (CLI not installed; deployment is
   push-to-main only) — if so, propose a different pre-production check instead of skipping it silently.
   The `?cb=` cache-buster documented in the project reportedly does NOT defeat the CDN (same ETag/Age).
   The line numbers for the two plan allowlists in `provision-http.js` are stale (reported today as ~237
   and ~1629, not 230/942). `nexux-verify.py gitclean:` will always return FALLO while main is dirty —
   expect it and use a different check, do not "fix" it by committing unrelated files.
7. Claimed coverage gaps: four open blockers (offsite backups H2, the USB single point of failure H3, the
   79 € portal showing 749 € D2, Twilio C2) are in neither the briefing nor Ola 1, and drop to Ola 2 with
   no consequence written down. Task D6 (audit both Stripe endpoints' delivery rates BEFORE touching
   anything) is missing from the minimum scope even though the PRP flags it as one where stopping halfway
   is worse than not starting.
8. `~/nexux-clients` has its own rules file at `agents.md` (lowercase) that this briefing never cites.
   Treat it as partly stale (its plan list predates the 29 € pivot) but read it.

UNCOMMITTED WORK — protect this before you start

The entire launch-audit folder (7 reports, TABLA-CRUZADA.md, the Pi copy of PRP v5, and this review's raw
JSON), plus `AGENTS.md` and `progress/REGISTRO.md` with 40+ session lines, are UNCOMMITTED in `nexux-pro`.
That is the single point of failure of this whole handover. Commit those specific paths (commit only, no
push, name each file explicitly, never `git add .`) before Ola 1 touches anything.

ADDITIONAL PROHIBITIONS — the original list was written for a code repo and misses what actually hurts here

- REAL CUSTOMER DATA: `~/nexux-clients/clients/` holds ~21 client directories, 3 of them active paying
  businesses, one with a live paired WhatsApp session and 55 real appointments. It is git-ignored, so git
  will not protect you. Do not modify, move, delete or "clean up" any file under it. Do not print tokens,
  access keys or customers' personal data; count and classify instead.
- REAL PEOPLE: the WhatsApp and Telegram bots message actual customers. Never send a test message through
  a channel bound to a real client. Never run repo scripts that deactivate clients or send email
  (`roi-report.js`, `upgrade-nudge.js`, `trial-expiry.js`, blast/outreach scripts) — not even "just to see".
- STRIPE BEYOND WEBHOOKS: the account is LIVE. Do not touch prices, products, coupons, the billing portal
  configuration (`bpc_...`) or any real customer's subscription. Read-only inspection is fine.
- PROCESSES AND CRONS: do not `pm2 restart/stop/delete` anything (a restart drops paired WhatsApp
  sessions), and do not add, edit or enable any cron entry.
- Closing the purchase CTA is a PRODUCTION CHANGE. Proposing it is fine; making it live — by any route,
  including editing anything the running site reads — needs Ricardo's explicit approval like any deploy.

```
