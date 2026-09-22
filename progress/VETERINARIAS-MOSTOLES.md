# Veterinarias de Móstoles — orden por "se puede atacar", no por gancho

Fecha: 2026-09-21 · Hoja: `/home/nexux/scraper-output/veterinarias_mostoles.csv`

## Los tres fallos que me marcaste

1. **Ordené por gancho, no por regla.** Puse de nº1 a Río Duero, que no tiene WhatsApp confirmado, y de nº3 a Rosales, cuyo número resultó ser falso. El orden nuevo empieza por `cita_whatsapp = SÍ`.
2. **Dejé `cita_whatsapp` vacío.** La causa: al montar la lista por `place_id` puse el campo de la web en blanco, así que la comprobación no tenía nada que mirar y todo salía "desconocido". Fue mío.
3. **Avisé del número raro en vez de comprobarlo.** Ya está comprobado, y era falso.

## Cómo se verifica ahora un WhatsApp

Que el número esté escrito en su web no vale. Se abre `wa.me/<numero>` con un navegador de verdad y se mira qué contesta:

- Sale **el nombre del perfil** ("Clínica veterinaria Veracruz") → tiene cuenta de WhatsApp. **SÍ.**
- Sale "Chatea en WhatsApp con el +34 649 56 57 93" → el número es español válido (WhatsApp lo formatea) pero **no hay perfil público**: no confirmado.
- Sale "Chatea en WhatsApp con el 34773124665", **sin formatear** → WhatsApp ni lo reconoce como número español. **Basura.**

Resultado:

| Número | Veredicto | Qué dice wa.me |
|---|---|---|
| +34626473880 Veracruz | **SÍ** | perfil "Clínica veterinaria Veracruz" |
| +34693253828 Barcelona | **SÍ** | perfil "Clinica Veterinaria Barcelona" |
| +34629150186 Coimbra | **SÍ** | perfil "Centro Veterinario Coimbra" |
| +34606748796 Perseo | SÍ, pero es cadena | perfil "Perseo Clinica Veterinaria" |
| +34649565793 Cl. Mascotas | no confirmado | número válido, sin perfil |
| +34614816532 Villa Animal | no confirmado | número válido, sin perfil |
| **+34773124665 Rosales** | **FALSO** | ni lo reconoce como español |
| +34753143512 Medivet | FALSO | ni lo reconoce como español |

**Falta la última comprobación, y es tuya:** abrir los tres enlaces y ver que responde un humano. Los enlaces están en la hoja, columna `prueba_whatsapp`.

---

# ORO — ya cogen cita por WhatsApp Y tienen queja leída

## 1. Veterinario en Móstoles | Veracruz
- C. Veracruz, 20, 28936 Móstoles · 916 45 48 08 · **WhatsApp +34 626 473 880**
- veterinarioveracruzmostoles.com · Google 4,3 (261)
- `cita_whatsapp`: **SÍ** · prueba: enlace `wa.me/+34626473880` en su propia web **y** perfil "Clínica veterinaria Veracruz" al abrirlo
- Prueba de lectura: 60 reseñas distintas, 44 de 3 estrellas o menos, 3 hablan de citas

**Qué le duele:**
> "**Citan a la misma hora a tres personas habiendo solo un veterinario.** Mienten diciendo que había una urgencia con la excusa de la cita a la misma hora."

> "Te citan a una hora que nunca te atienden, el caso que te cobran..."

**¿Lo arregla Lara?** Sí, y es literal: Lara no deja meter dos citas a la misma hora. Además ya usan WhatsApp, así que no hay que convencerles del canal, sólo de que lo coja solo.

**MENSAJE:**
Hola, buenos días. Soy Ricardo, de Móstoles.
Os escribo porque he visto que ya cogéis cita por WhatsApp, y justo por eso os puede interesar esto.
Hay un par de opiniones vuestras que dicen lo mismo: que citáis a tres personas a la misma hora habiendo un solo veterinario. Y eso no pasa por querer, pasa porque las citas entran por el móvil mientras estáis dentro con un animal y nadie está mirando el hueco real.
Lo que yo tengo contesta ese WhatsApp por vosotros al momento y **no deja meter dos cosas a la misma hora**. Vosotros veis la agenda ya cuadrada.
¿Te lo enseño? Te paso un enlace y le escribes tú como si fueras un cliente, un minuto. Si no te encaja, me lo dices y no insisto.

## 2. Clínica Veterinaria Barcelona
- C. Barcelona, 14, 28937 Móstoles · 912 36 26 64 · **WhatsApp +34 693 253 828**
- Google 4,7 (327), ~13 de una estrella
- `cita_whatsapp`: **SÍ** · prueba: perfil "Clinica Veterinaria Barcelona" al abrir `wa.me/34693253828`
- Prueba de lectura: 60 distintas, 24 de ≤3 estrellas, 4 de citas

**Qué le duele:**
> "he llamado a primera hora de la mañana pidiendo por favor que atiendan a mi perro que estaba vomitando y tienen la desfachatez de decirme que **no me dan cita hasta dentro de 2 SEMANAS**"

**¿Lo arregla Lara? A medias, y hay que decírselo.** No tienen hueco, y Lara no inventa huecos. Lo que sí hace es que quien escribe con una urgencia reciba una respuesta en el momento, con lo que haya, en vez de un portazo.

**MENSAJE:**
Hola, buenos días. Soy Ricardo, de Móstoles.
Ya tenéis WhatsApp puesto, así que esto va de aprovecharlo mejor, no de cambiaros nada.
He visto una opinión de alguien que llamó a primera hora con su perro vomitando y le dijeron que hasta dentro de dos semanas nada. Yo no te voy a vender que eso se arregla con una herramienta: si no hay hueco, no lo hay.
Lo que sí evita es que esa persona se quede con un "no" seco y se vaya. El WhatsApp contesta al momento, le dice lo que hay de verdad, y si es urgente le dice a dónde ir.
¿Te lo enseño un minuto? Te paso un enlace y escribes tú como si fueras ese cliente.

## 3. Centro Veterinario Coimbra — SÍ tiene WhatsApp, pero el dolor es flojo
- ZOCO COIMBRA, C. del Tamarindo, 15, 28935 Parque Coimbra (Móstoles) · 916 47 57 82 · **WhatsApp +34 629 150 186**
- centroveterinariocoimbra.es · Google 4,8 (396), sólo ~4 de una estrella
- `cita_whatsapp`: **SÍ** · perfil "Centro Veterinario Coimbra"
- Prueba: 60 distintas, 21 de ≤3 estrellas, **1 sola** de citas, y es esta:
> "No son demasiado amables. Los precios son correctos tirando a caretes. Y **siempre hay mucha gente**."

**Mi opinión, sin adornar:** entra en Oro por la regla, pero no tiene dolor de citas. Un 4,8 con 396 opiniones y cuatro de una estrella es una clínica que va bien. Si le escribes lo mismo que a Veracruz, se nota falso. Yo la dejaría para cuando haya algo que decirle, o le entraría por las esperas sin prometer nada.

---

# Sin WhatsApp confirmado — lista aparte

Tienen queja leída, pero **no se puede atacar por WhatsApp**. Van a su propia lista y sólo se tocan si decides hacer llamada o visita.

| Clínica | Quejas de citas | Leídas | Por qué está aquí |
|---|---|---|---|
| Estoril Veterinary Hospital | 17 | 60 | sin WhatsApp; además hay que confirmar si es franquicia |
| Clínica Veterinaria Río Duero | 6 | 60 | sin WhatsApp (y su web no responde) |
| Mostoles Veterinary Center | 5 | 60 | sin WhatsApp |
| Centro Veterinario Móstoles | 4 | 60 | sin WhatsApp |
| Clínica Veterinaria Bicharracos | 3 | 60 | sin web ni WhatsApp |
| Clínica Veterinaria Las Nieves | 3 | 60 | sin WhatsApp |
| Clínica Veterinaria Petconnection | 3 | 60 | sin WhatsApp |
| Puerta del Sur | 2 | 60 | sin WhatsApp |
| **Clínica Veterinaria Huellas** | 2 | 60 | **su web dice "muy pronto también podrás gestionar tu cita por WhatsApp"** — lo quieren y no lo tienen |
| **Centro Veterinario Rosales** | 2 | 40 | **su número de WhatsApp es falso** |
| Villa Animal | 1 | 40 | número sin perfil, sin confirmar |
| Veterinaria Don Vito | 1 | 40 | sin WhatsApp; y su queja marcada era falso positivo mío |
| Clinica Veterinaria Tropican | 1 | 40 | sin web ni WhatsApp |

**Dos de esta lista merecen una nota aparte:**
- **Huellas** lo está anunciando en su web y aún no lo tiene. Es el mejor candidato de los que no tienen WhatsApp: ya han decidido que lo quieren.
- **Rosales** tiene un número falso publicado. Eso, además, es un cliente perdido cada vez que alguien lo intenta.

# Sin leer todavía (3)
Clínica Veterinaria Mascotas (sólo 6 reseñas), Veterinario en Casa (10), y nada más: **de 29 fichas, 26 están leídas.**

# Fuera (11)
Cadenas: Perseo (2 sedes), Kivet, Medivet. Otra ciudad: Parque Oeste, Los Cantos, Neko, Azahar, Ohana, Mundo Animal (Alcorcón), Loranca y Nuevo Versalles (Fuenlabrada), Lily's Vet (Arroyomolinos). Otra vertical: Intercan y las demás tiendas y peluquerías.

---

# La hoja de cálculo

`/home/nexux/scraper-output/veterinarias_mostoles.csv` (separador `;`, se abre en Excel y en Sheets).

Columnas de datos: prioridad · nombre · municipio · dirección · teléfono · whatsapp · cita_whatsapp · **prueba_whatsapp** · web · nota y opiniones de Google · de_1_estrella_segun_google · reseñas_leidas · de_3_estrellas_o_menos · quejas_de_citas · orden_verificado · incidencias · queja_textual · maps

Columnas de seguimiento, vacías para ti: **escrito_el · por_donde · contesto · que_dijo · demo_enviada · estado · siguiente_paso · notas**

# Para convertirlo en skill

Ya está parametrizado por ciudad y por caja:
- `perrolia.py <zona> "<Municipio>"` — saca la lista, el municipio real, el teléfono, el reparto de estrellas y el horario.
- `ficha_vet.py <caja> [limite] [filtro]` — lee las quejas con el orden verificado y los contadores.
- `verifica_wa.py <numeros...>` — comprueba los WhatsApp de verdad.
- `hoja.py "<Municipio>"` — monta la hoja con la prioridad.

Lo que falta antes de empaquetarlo: que la vertical se elija por parámetro (ahora las cajas de "otra vertical" y "cadena" son listas escritas a mano para Móstoles), y cerrar las 3 fichas que Google sigue sin servir.
