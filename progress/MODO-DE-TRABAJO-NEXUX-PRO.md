# MODO DE TRABAJO — nexux.pro (2026-09-04, Ricardo)

> **Léeme antes de tocar nada.** Vale para Opus, Codex, y cualquier agente/harness que entre en este
> proyecto. Complementa a `~/nexus-brain/AGENTS.md` (ley universal) y a `./AGENTS.md` (propio del repo):
> esto solo define CÓMO se trabaja, no la arquitectura.

---

## 1. QUÉ PASÓ Y POR QUÉ EXISTE ESTE DOCUMENTO

El pago de 29 € "estaba bien" y a los días fallaba la mitad de las cosas: entradas que se dan por
hechas sin contrastarse, tareas grandes que se quedan a medias cuando un agente se queda sin contexto,
y parches encadenados donde nadie echa el cierre. Este documento es la respuesta.

**Resumen para Ricardo (lo que confirma el modelo):** tareas cortas, de una en una, cerradas al 100%
y probadas EN LA PRÁCTICA antes de pasar a la siguiente. No se confía en un "hecho"; se comprueba con
un comando.

---

## 2. ROLES (nadie los pisa)

| Rol | Qué hace | Qué NO hace |
|---|---|---|
| **Opus** | Jefe de equipo. Desarrolla y es responsable del proyecto. Decide cómo se ataca. | — |
| **Codex / otros agentes** | Desarrollan bajo la coordinación de Opus. | Edita lo que Opus o Ricardo no le hayan asignado en coordinación. |
| **Verificador (asistente técnico de Ricardo)** | **Contrasta** que lo que dicen "hecho" lo está de verdad y en la práctica. Anti "te digo que sí y luego falla la mitad". | NO desarrolla, NO dirige la estrategia, NO decide el orden de las tareas. |

**El verificador no estorba: es quien evita el incidente del pago.** Verifícalo/hay que darle acceso
a lo que necesite (SSH, repo) sin fricción; cuando reporte un FALLO, la tarea NO está hecha.

---

## 3. REGLAS DE TAREA — SIN EXCEPCIÓN

1. **UNA tarea corta a la vez.** Cerrada 100% y probada en la práctica antes de pasar a otra.
2. **Ricardo decide QUÉ se hace** (o lo proponéis vosotros y él lo valida antes de empezar). No se
   lanza una cascada de arreglos sin que Ricardo elija el orden.
3. **Ningún "hecho" sin cruzar:**
   - el código que **EJECUTA** (no el que documenta);
   - una comprobación **real** (funcionando, no solo "he corrido el test");
   - **el "segundo sitio/canal"** que suele olvidarse (dos listas blancas, dos receptores, dos canales,
     nombre exacto de una variable...);
   - test que se **sabotea** (romper a propósito y ver que se pone rojo) para cambios críticos.
   - `~/scripts/nexux-verify.py` no se salta.
4. **Cuando dos agentes se crucen o la cosa se desvíe → avisar antes**, no arreglar en silencio.
5. **Límites de contexto/uso:** si una tarea se acerca a su límite, párala en un punto limpio y déjala
   ESCRITA en el pendiente de `~/nexus-brain/nexux-live-state.md`. **Nunca** la des por hecha "a medias"
   ni la dejes morir en silencio. Poco y terminado > mucho y a medias.
6. **Críticas constructivas** entre agentes y con Ricardo, sin acritud.
7. Cada cierre significativo deja **una línea** en `progress/REGISTRO.md` (con `causa:` si es
   FALLO/PARCIAL) y en `~/nexus-brain/quality-ledger.md`.

---

## 4. CÓMO SE ENTREGA UNA TAREA

El desarrollador reporta a Ricardo (no al verificador directamente), con:

- qué tarea era y qué decidió Ricardo para ella;
- los commits y la rama/worktree donde está;
- **lo que NO hace falta verificar** y **lo que queda pendiente** (si queda algo, NO está cerrada);
- la(s) comprobación(es) real(es) ya hechas.

Entonces el verificador —con acceso a la Pi y al repo— la **contrasta de forma independiente** y Ricardo
da la luz de push/deploy/cobro cuando procede. **El push y el cobro los autoriza siempre Ricardo.**

---

## 5. HERRAMIENTAS Y ACCESO

- SSH a la Pi y acceso al repo: los tiene Opus/Codex y el verificador. Ante la duda, quien vaya a tocar
  pide acceso por el canal de Ricardo, no por uno propio.
- Verificación oficial: `export NEXUX_AGENT=<nombre>` + `python3 ~/scripts/nexux-verify.py <cheques>`.
- Estado vivo del proyecto (fuente de verdad): `~/nexus-brain/nexux-live-state.md`.

---

## 6. PENDIENTES ABIERTOS (referencia rápida para elegir la próxima tarea)

Se mantienen en `~/nexus-brain/nexux-live-state.md` (Pendientes Críticos). No se duplica aquí salvo
resumen; ante cualquier duda manda el live-state.
