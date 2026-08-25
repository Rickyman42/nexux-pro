# EL NEGOCIO DEL ANUNCIO — ficha única

> Todo lo que se genere, se grabe o se escriba para el vídeo sale de aquí.
> Si una capa no cuadra con esta ficha, la equivocada es la capa.
> Aprobado por Ricardo el 25-ago-2026.

---

## Qué es

**Centro Lena** — centro de estética y bienestar, pequeño, con cita previa.
Móstoles. Cuatro profesionales y una cabina.

**Deliberadamente neutro.** No es "un sitio de masajes": la agenda mezcla cara, manos,
cuerpo y depilación para que se lea como un centro de estética. La manicura está a
propósito, porque las uñas son uno de los sectores objetivo.

## Por qué estética, y no dental ni taller

Decidido con datos de `progress/investigacion/investigacion-seo-20260821.md`, no por gusto:

- **35.000 pymes** de imagen personal (peluquería + estética) en España, 240.000 empleados
- **1.458 salones ya scrapeados**, de los cuales **1.063 (73 %) sin reserva online** — es la
  única lista de captación que existe hoy. No hay equivalente de dentistas ni de talleres
- En una clínica dental hay recepcionista, así que el dolor del anuncio («nadie contesta»)
  se desactiva solo
- La cabina que ya se generó en Flow **es estética**: estamos dentro del mercado medido

⚠️ Esto es el **escenario del anuncio**, no una verticalización del producto. El producto
sigue siendo horizontal y el guion no nombra ningún sector en sus 75 segundos.

---

## Servicios (los que se leen en el CRM y los que ofrece Lara)

| Servicio | Duración | Precio | Cabina |
|---|---|---|---|
| Primera consulta | 30 min | 0 € | |
| Manicura | 45 min | 22 € | |
| Tratamiento facial | 60 min | 48 € | sí |
| Depilación | 30 min | 25 € | |
| Masaje descontracturante | 60 min | 45 € | sí |
| Tratamiento corporal | 75 min | 60 € | sí |

**Profesionales:** Ana, Marta, Lucía, Noelia · **Recurso:** Cabina
**Horario:** L-J 9:00-19:00 · V 9:00-20:00 · S 9:00-14:00

---

## Dónde está aplicado

| Capa | Estado | Cómo se comprueba |
|---|---|---|
| `clients/estudio-ricardo-demo-mostoles-946279/config.json` | ✅ | copia en `config.json.bak-estetica` |
| Lo que dice Lara | ✅ | dice «servicios de estética y bienestar» y ofrece los seis |
| Agenda en Google Calendar | ✅ | 12 citas, una sola de masaje |
| `seed-agenda.mjs` | ✅ | la lista `DIA` lleva los servicios nuevos |
| CRM `nexux.pro/cliente/<id>` | ⬜ | **sin comprobar: hace falta la sesión de Ricardo** |
| Planos generados (P3, P11) | ⚠️ | son cabina de masaje. Decisión: se dejan y se revisan con el montaje entero |

---

## Un plano abierto

**P3** es un masaje: ella con las manos en la espalda de un cliente. Es el plano más fuerte
para el dolor —no puede levantarse— y a la vez lo más «masaje» del vídeo. Ricardo decidió el
25-ago **dejarlo por ahora** y revisarlo al ver el montaje completo. Si canta, se rehace con
una manicura o un facial: mismo bloqueo de manos, más neutro, 12 créditos.
