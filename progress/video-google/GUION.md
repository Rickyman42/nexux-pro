# Vídeo de verificación OAuth — Google Calendar

**App:** Nexux Recepcionista IA · **Client ID:** `839053342621-q5g6uo97vfgae4ghaikcsug49j10hjkm.apps.googleusercontent.com`
**Permisos a justificar:** `calendar.events` y `calendar.calendarlist.readonly`
**Cuenta de la demo:** arteenpixel@gmail.com · **Duración:** ~2 minutos

---

## Orden de trabajo (importante hacerlo en este orden)

1. **Primero la voz.** Copia los bloques de abajo en VoiceBox y genera el audio.
2. **Luego grabas la pantalla escuchando ese audio** con auriculares, siguiendo el ritmo.
   Así la imagen cuadra sola y no hay que cuadrarla en el montaje después. Es el truco
   que ahorra la tarde entera.
3. **Al final se monta**: captura + voz + rótulos.

**Antes de darle a grabar:** en el panel, pulsa *Desconectar* en Google Calendar. El vídeo
tiene que empezar con la cuenta sin conectar, o no se ve el flujo entero y lo rechazan.

**La pantalla se graba de verdad.** Nada de recrear la pantalla de Google en Remotion: eso
lo rechazan, y con razón. Remotion solo monta.

---

## Bloque 1 — Qué es la app (≈15 s)

> **Voz (inglés):**
> "This is Nexux Recepcionista IA, a booking assistant for hair and beauty salons in Spain.
> Our website is nexux.pro. The OAuth client ID for this application is
> 839053342621-q5g6uo97vfgae4ghaikcsug49j10hjkm.apps.googleusercontent.com."

**En pantalla:** la home de `nexux.pro`. Luego un rótulo con el Client ID completo, bien
legible, unos 4 segundos.

---

## Bloque 2 — El panel del negocio (≈15 s)

> **Voz:**
> "Salon owners sign in to their own dashboard. Here they manage their appointments,
> their staff and their clients. To keep their Google Calendar in sync, they connect it
> from the Channels section."

**En pantalla:** el panel del salón. Se pasa por Citas y Clientes sin pararse, y se entra
en **Canales**. Que se vea la URL `nexux.pro/cliente/...` en la barra.

---

## Bloque 3 — El consentimiento (≈25 s) · **el bloque que más miran**

> **Voz:**
> "When the owner clicks Connect, we send them to Google's consent screen. You can see our
> application name, Nexux Recepcionista IA, and our client ID in the address bar. We request
> two scopes: calendar dot events, and calendar dot calendarlist dot readonly."

**En pantalla:**
1. Pulsar **Conectar Google Calendar**.
2. **Parar un momento en la barra de direcciones** para que se lea el `client_id`. Si hace
   falta, amplía con Ctrl+rueda. Este es el fotograma que Google busca.
3. Elegir la cuenta `arteenpixel@gmail.com`.
4. La pantalla de permisos: que se vean **los dos permisos escritos**, sin prisa.
5. Aceptar.

---

## Bloque 4 — Para qué sirve leer la lista de calendarios (≈25 s)

> **Voz:**
> "After granting access, we read the list of the user's calendars. This is what the
> calendarlist readonly scope is for. The owner chooses which calendar each staff member
> uses. Ana works from one calendar, and Marta from another. We never read the contents
> of these calendars, only their names, so the owner can pick the right one."

**En pantalla:** de vuelta en el panel, se ve la lista con **arteenpixel@gmail.com** y
**Centro Lena**. Abre el desplegable de cada profesional para que se vea que se elige uno
por persona.

---

## Bloque 5 — Para qué sirve escribir eventos (≈35 s) · **la prueba de fuego**

> **Voz:**
> "Now the events scope. I create an appointment in the dashboard: a haircut with Ana,
> tomorrow at half past eleven. Nexux writes it to Ana's Google Calendar, with the client
> name, the service and the duration. Here it is in Google Calendar. If the appointment is
> moved or cancelled in the dashboard, we update or delete the same event, so the calendar
> always matches. We only create and manage appointments booked through Nexux."

**En pantalla:**
1. Crear la cita en **Citas** (cliente, servicio Corte, Ana, mañana 11:30).
2. Abrir **Google Calendar en otra pestaña** → se ve la cita en el calendario *Centro Lena*.
   Abrirla para que se lean el nombre y el servicio.
3. Volver al panel y **cancelarla** → refrescar Google Calendar → **ha desaparecido**.

Ese último gesto es el que convence: demuestra que no dejáis basura en su calendario.

---

## Bloque 6 — Cierre (≈15 s)

> **Voz:**
> "Calendar data stays between the salon and their own Google account. We do not sell it,
> we do not share it with third parties, and we do not use it for advertising or to train
> any model. Owners can disconnect at any time from the same screen, and we delete the
> stored token. Thank you."

**En pantalla:** volver a Canales y **enseñar el botón de Desconectar** (sin pulsarlo, o
pulsándolo, da igual).

---

## Repaso antes de subirlo a YouTube

- [ ] Se lee el **Client ID** completo en algún momento
- [ ] Se ve el nombre **Nexux Recepcionista IA** en la pantalla de Google
- [ ] Se ven **los dos permisos** escritos
- [ ] El flujo va **de principio a fin** sin cortes por el medio
- [ ] Se demuestra **cada permiso por separado** (lista de calendarios / crear y borrar cita)
- [ ] Se ve el **dominio** (nexux.pro y pi.nexux.pro)
- [ ] Sin datos personales de terceros a la vista en el calendario
- [ ] Subido a YouTube como **no listado** (no hace falta que sea público)

---

## Comprobado antes de escribir esto (9-sep, contra el sistema real)

- La pantalla de consentimiento abre bien, con el nombre de la app y sus enlaces de
  privacidad y términos.
- Crear una cita en el CRM **crea el evento en Google** (log: `✅ Evento creado`).
- Cancelarla **borra el evento** (log: `🗑 Evento eliminado`). No quedan eventos sueltos.
- La cita de Ana va a *Centro Lena* y la de Marta al calendario principal, porque cada
  profesional tiene el suyo. No es un fallo: es la función del plan de 79 €, y es
  justamente lo que justifica pedir los dos permisos.
