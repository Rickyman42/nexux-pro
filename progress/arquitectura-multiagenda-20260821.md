# Arquitectura multiagenda — Nexux Recepcionista IA

> Diseñada por Sol y revisada contra el código real el 21-08-2026.
> **Estado: Fases 1 y 2 CERRADAS y verificadas en producción. Fases 3-5 sin empezar.**
> **Modo `single` (una agenda, sin solapes) es el producto actual y es intencionado.** El modo `team`
> es una capacidad distinta, no un arreglo del actual: se activa por configuración, no sustituye nada.
> Reparto: Sol diseña y refuta, Luna implementa. Ver "Estado real" al final.

## Decisión

No se crea un segundo producto ni un segundo motor. Nexux tendrá un único sistema de reservas con dos modos:

- `single`: una agenda profesional; mantiene el comportamiento actual.
- `team`: varias agendas profesionales y, cuando sea necesario, recursos compartidos.

Los inicios de sesión independientes, roles y permisos son otra fase. No son necesarios para permitir citas simultáneas atendidas por profesionales diferentes.

## Problemas comprobados en el sistema actual

- Las citas no guardan profesional ni recurso.
- Los servicios no tienen identificadores estables.
- La disponibilidad y los conflictos se calculan para toda la empresa.
- La duración completa del servicio no se comprueba en todos los caminos.
- WhatsApp, Telegram, portal y reserva pública crean citas por caminos distintos.
- El onboarding recoge el número de profesionales, pero el dato no gobierna la agenda.
- La configuración cargada por algunos bots puede quedarse desactualizada hasta reiniciar.
- Los ficheros JSON no permiten escalar con seguridad a varios procesos; el MVP solo es válido con una instancia Node.

## Contrato de configuración

```json
{
  "booking": {
    "schema_version": 2,
    "mode": "single",
    "slot_interval_min": 15,
    "lead_time_min": 90,
    "horizon_days": 60,
    "assignment_strategy": "least_loaded"
  },
  "professionals": [
    {
      "id": "pro_default",
      "name": "Agenda principal",
      "active": true,
      "color": "#2A9D97",
      "priority": 100,
      "schedule": null
    }
  ],
  "resources": [],
  "services": [
    {
      "id": "svc_pedicura",
      "name": "Pedicura",
      "duration": 60,
      "price": 25,
      "professional_ids": ["pro_default"],
      "resource_requirements": []
    }
  ]
}
```

Reglas:

- `config.schedule` sigue siendo el horario general.
- Un profesional con `schedule: null` hereda el horario general.
- Un horario propio se cruza con el general; nunca lo amplía.
- `professional_ids` determina quién puede prestar cada servicio.
- Los recursos son opcionales y tienen capacidad.
- Vacaciones, cierres y bloqueos vivirán fuera de la configuración fija.

## Contrato de cita

Cada cita nueva guardará como mínimo:

- `service_id` y el nombre histórico del servicio.
- `professional_id` y el nombre histórico del profesional.
- `assignment_mode`: `explicit` o `automatic`.
- `resource_allocations` cuando corresponda.
- Cliente, fecha, duración, estado y origen.
- Clave de idempotencia del mensaje o petición que la originó.
- Versión, fechas de creación/actualización y estado de recordatorios.

Los identificadores mandan para la lógica; los nombres son una fotografía histórica.

## Compatibilidad

El primer despliegue no reescribe cuentas existentes:

- Sin `professionals` se genera virtualmente `pro_default`.
- Los servicios existentes se asignan virtualmente a `pro_default`.
- Las citas antiguas sin profesional pertenecen a `pro_default`.
- Se normalizan los formatos antiguos al leer sin modificar los datos originales.
- En modo `single`, las citas simultáneas continúan bloqueadas.

La migración física se hará después mediante script con copia previa y `--dry-run`.

## Autoridad de reserva

Lara conversa, pero el motor decide si una cita cabe. Toda creación o modificación debe pasar por el mismo motor:

1. Resolver servicio y duración real.
2. Resolver profesionales autorizados y activos.
3. Aplicar profesional concreto o “me da igual”.
4. Cruzar horarios y bloqueos.
5. Comprobar el intervalo completo `[inicio, final)`.
6. Comprobar conflictos del profesional.
7. Asignar recursos con capacidad disponible.
8. Bloquear por negocio, releer y validar de nuevo.
9. Guardar de forma atómica.

Dos citas son compatibles si usan profesionales diferentes y no compiten por un recurso sin capacidad. Una cita que termina a las 11:00 no bloquea otra que empieza a las 11:00.

La asignación automática usa este orden: menor carga diaria, prioridad configurada e identificador como desempate estable.

## Conversación de Lara

- Con una sola persona disponible, no pregunta por profesional.
- Con varias: “¿Prefieres que te atienda Ana, Marta o te da igual?”.
- Si la persona elegida no está libre, ofrece otra hora con ella y la misma hora con otra persona.
- Nunca revela quién ocupa un hueco.
- Lara confirma una opción temporal generada por el servidor; no inventa horarios.
- Al confirmar se revalida. Si el hueco ya se ocupó, se ofrecen alternativas.
- Una cita con profesional elegido no se reasigna sin consentimiento.

## Orden de implantación

### Fase 1 — núcleo seguro aislado

- Normalizador de configuración antigua y v2.
- Almacén atómico de citas.
- Motor único con idempotencia, conflictos y bloqueo por negocio.
- Pruebas de compatibilidad, concurrencia, duración y recursos.
- Todavía no se conecta al servicio vivo.

### Fase 2 — integración monoagenda

- Hacer que portal, reserva pública, WhatsApp y Telegram usen el motor.
- Mantener `booking.mode=single`.
- Probar con fixtures y después con una cuenta interna.

### Fase 3 — multiprofesional bajo bandera

- Profesionales, asignación de servicios y horarios propios.
- Rutas de gestión de equipo y disponibilidad.
- Activación solo en una cuenta interna.

### Fase 4 — Lara y portal

- Orquestador de opciones y confirmaciones.
- Gestión de profesionales en el portal.
- Calendario con filtro, colores y citas simultáneas.
- Crear, editar y arrastrar conservando el profesional salvo consentimiento.

### Fase 5 — recursos y calendario externo

- Cabinas, sillones y otros recursos con capacidad.
- Actualización real de eventos externos.
- Calendarios Google separados quedan fuera del MVP.

## MVP comercial

Incluye una cuenta propietaria, entre 1 y 5 profesionales, asignación de servicios, horario propio opcional, elección explícita o automática y calendario por profesional.

No incluye usuarios con login propio, roles, nóminas, turnos avanzados, pagos por profesional, recurrencias, lista de espera ni calendarios Google separados.

## Condiciones para escalar

El almacenamiento JSON con bloqueo en memoria solo es aceptable para el MVP con un proceso Node. Antes de ejecutar varias instancias, las citas deben migrar a SQLite con WAL o PostgreSQL y usar control transaccional real.

## Límites de seguridad

- No tocar `.env`, credenciales, `auth`, Stripe ni datos reales de clientes.
- No desarrollar directamente sobre rutas críticas sin copia y revisión.
- `nexux-clients` no tiene repositorio independiente seguro: el núcleo nuevo se crea sin importarlo desde producción hasta resolver su versionado.
- El cambio ajeno de `leads-server.cjs` se conserva intacto.


---

## Estado real de ejecución (verificado 21-08-2026, 22:00)

### Fase 1 — núcleo aislado: ✅ CERRADA

Tres módulos nuevos en `nexux-clients`, **sin importar desde producción**:

| Fichero | Qué resuelve |
|---|---|
| `lib/config-normalizer.js` | Normaliza configuración antigua (v1) a v2 sin mutar el origen |
| `lib/appointment-store.js` | Persistencia atómica (temp+rename) con mutex por cliente |
| `lib/booking-engine.js` | Motor único: conflictos, duración real, recursos, asignación automática, idempotencia, versiones |

**23 pruebas en verde** (`node --test test/*.test.mjs`). Cubren el caso que motivó todo esto:
*"asignación automática es determinista y permite dos profesionales distintos"*.

Historial de la fase: Luna implementó, Sol refutó y encontró 17 defectos pese a tener 13 pruebas verdes,
Luna corrigió (21 pruebas), y una última pasada encontró el defecto de idempotencia descrito abajo.

#### Último defecto corregido (21-08-2026, 21:56)

`idempotencySignature` hacía `JSON.stringify(requestedAllocations(...))`, pero `requestedAllocations`
devuelve un `Map` y `JSON.stringify(Map)` produce siempre `"{}"`. Al comparar contra
`existing.resource_allocations` (un array), **ningún reintento con recursos explícitos coincidía nunca**:
todos se rechazaban con `idempotency_conflict`.

Consecuencia real: cuando WhatsApp o Telegram reenvían el mismo webhook —cosa que ocurre de forma
rutinaria al reintentar por red— el cliente recibiría un error en vez de su cita ya confirmada.

Corregido con `canonicalAllocations()`, que lleva `Map` y lista a la misma forma estable ordenada por
`resource_id` y `units`, aplicada en los dos lados de la comparación. Añadidas 2 pruebas de regresión.
**Verificado que la prueba detecta el fallo**: contra el motor sin corregir, `un reintento con recursos
explicitos identicos no duplica la cita` falla; con la corrección, pasa.

### Fase 2 — integración monoagenda: ✅ CERRADA y verificada en producción (21-08-2026)

Los cuatro caminos pasan ya por el motor, vía `lib/booking-bridge.js` (commit `507ad0f`):

| Camino | Dónde | `source` |
|---|---|---|
| CRM del portal | `provision-http.js` | `crm` |
| Reserva pública | `provision-http.js` | `web` |
| Telegram | `lib/telegram.js` | `telegram` |
| WhatsApp | `lib/whatsapp.js` | `whatsapp` |

**Qué cambia de verdad.** `createAppointment()` de `data.js` **no comprobaba conflictos**: escribía la
cita y ya. La protección contra solapes vivía solo en `getAvailableSlots()`, que *ofrece* huecos libres
— pero nada impedía escribir encima de una cita existente (dos clientes confirmando a la vez, o un POST
directo al endpoint). Ahora se valida antes de escribir.

**Verificado en producción**, no solo en tests:

```
POST /public/<cliente>/book  (misma hora, dos veces)
  1ª → HTTP 200  {"ok":true, ...service_id, professional_id: "pro_default"...}
  2ª → HTTP 409  {"ok":false,"error":"appointment_conflict"}
```

Antes de este cambio, la segunda creaba una cita encima de la primera.

#### Dos compatibilidades deliberadas, medidas contra los datos reales

1. **Servicios de texto libre.** Cuatro clientes reales tienen `services: []` y reservan por nombre
   libre. El motor exige que el servicio exista, así que el puente lo añade a una **copia** de la
   config con la duración que indica el llamador — la misma que ya se usaba. Sin este apaño, esos
   cuatro bots dejarían de coger citas.
2. **Reservas del dueño** (`source` = `crm`/`portal`): sin margen de antelación ni rejilla de huecos.
   Esas dos reglas existen para lo que se **ofrece** al cliente, no para lo que el negocio puede
   anotar; el CRM ya podía registrar una cita a las 10:07 o para dentro de un año.

#### Cuando el hueco no está libre

CRM y web devuelven **409** con el código; Lara responde ofreciendo otro momento en vez de romperse.
Los códigos de «no disponible» se sacaron del propio motor (`grep` de `fail(...)`), no inventados —
la primera versión llevaba dos que el motor nunca emite.

#### Evidencia

- **31/31 tests** (23 núcleo + 8 puente), incluido uno que comprueba que escribe en el mismo
  `clients/<id>/appointments.json` que lee el CRM.
- Probado contra **las 17 configuraciones reales con sus citas ya guardadas**, en copia: 17/17 reservan
  y el motor lee y valida las citas antiguas sin rechazarlas. *(Ojo con la prueba: un primer intento dio
  17/17 fallos porque la fecha elegida caía en domingo y los horarios reales tienen `sunday: null`.
  Era fallo de la prueba, no del motor.)*

### Fases 3-5: ❌ SIN EMPEZAR

Falta lo que da valor comercial al modo `team`:

- **Disponibilidad por profesional.** `getAvailableSlots` (`lib/data.js:84`) sigue calculando para todo
  el negocio. Mientras siga así, Lara no puede ofrecer dos huecos a la misma hora aunque el motor los
  acepte.
- **Gestión de profesionales en el portal** — en el front del CRM (`nexux-pro`) hay **cero**
  referencias a profesional.
- **Conversación de Lara** para elegir profesional («¿con Ana, con Marta o te da igual?»).
- **Recursos** (cabinas, sillones) y calendario externo.

**Traducido: con la Fase 2 el sistema ya no se pisa las citas. Para que dos personas puedan atender a
la misma hora hacen falta las fases 3 y 4.**

### ✅ Bloqueo de la Fase 2: LEVANTADO (21-ago-2026, 22:15)

El diseño condicionaba la Fase 2 a *"resolver el versionado"* de `nexux-clients`. **Resuelto.**

`~/nexux-clients` es ya un repositorio git independiente (commit inicial `578bc52`). Los seis ficheros
del núcleo están versionados y se puede revertir cualquier cambio. `git status` pasó de colgarse a
0,009 s porque antes escaneaba los 11.183 ficheros de la carpeta personal.

Se versiona **solo código y documentación** (89 ficheros). Quedan fuera, verificado uno a uno antes del
commit: `.env`, `**/creds.json`, `**/auth/`, `.wwebjs_auth/` (sesiones de WhatsApp Web), `clients/`
(conversaciones, citas y teléfonos reales — RGPD), `data/`, los `.jsonl` de correo y visitas,
`*-log.json` y `node_modules`. Auditoría: sin claves `sk_live`/`sk_test`, sin tokens de bot, sin cadenas
de conexión.

⚠️ **`/home/nexux` sigue siendo zona prohibida.** Es otro repo git, con la carpeta personal entera
dentro (incluidas `.ssh/authorized_keys` y varios `.credentials.json`) y remote `nexux-clients.git`.
Un `pull` o `rebase` allí puede dejarte sin acceso SSH a la Pi. Trabaja siempre desde
`~/nexux-clients`. Sus 91 commits locales con secretos no han llegado a GitHub.

**La Fase 2 ya se puede abordar.** Sigue tocando los bots vivos (`whatsapp.js`, `telegram.js`,
`provision-http.js`), pero ahora con posibilidad de revertir. Recomendación: conectar el motor primero
en `mode: single` —comportamiento idéntico al de hoy, pero pasando por las comprobaciones del motor— y
validar con una cuenta interna antes de que lo toque un cliente.
