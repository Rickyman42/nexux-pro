# Estrategia SEO v2 — Nexux.pro

> Actualizada el 21-ago-2026 tras revisar investigación, producción y SERP real.
> Este es el plan SEO canónico para cualquier agente.
> Investigación base: `progress/investigacion/investigacion-seo-20260821.md`.

## Objetivo

Conseguir clientes para la Recepcionista IA de 29 €/mes. El SEO debe describir el producto que existe
hoy: atención por WhatsApp y web. No atribuir llamadas, Instagram, resultados o clientes no demostrados.

## Decisión estratégica

"Recepcionista IA" es la única keyword medida con volumen relevante (100-1.000 búsquedas/mes y fuerte
crecimiento), pero la SERP actual está dominada por productos de voz. Por eso es la keyword principal
provisional, no una apuesta ciega.

Antes de crear páginas nuevas hay que comprobar si Nexux puede competir con su propuesta actual:
**recepcionista IA por WhatsApp y web, sin llamadas**. Si esa propuesta no obtiene impresiones o no
convierte, se revisará el enfoque; no se fabricarán funciones para encajar en la búsqueda.

## Orden obligatorio

### 0. Limpiar señales falsas o contradictorias — prioridad crítica

- Corregir en home: testimonios no verificados, métricas sin evidencia y copy todavía centrado en peluquerías.
- Corregir precios y funciones antiguas en blog, comparativa, footer, calculadora e imagen social.
- El FAQ schema solo puede contener preguntas visibles en la página.
- No usar valoraciones, clientes, ROI o porcentajes hasta tener evidencia real.

### 1. Dejar una base técnica coherente

- Redirigir `www` a `https://nexux.pro`.
- Unificar barra final entre URLs, canonicals y sitemap.
- El sitemap solo debe incluir páginas útiles, indexables y canónicas; excluir `/acceso-denegado/`.
- Revisar cada artículo antiguo: actualizar en su misma URL si sirve; redirigir si quedó obsoleto. No aplicar
  `noindex` masivo.
- Añadir `WebSite` schema y mantener `Organization`/`SoftwareApplication` solo con datos reales.
- Mantener `llms.txt`, pero no tratarlo como una palanca importante de ranking.

### 2. Hacer que home y demo vendan el producto real

- Home: qué es, qué hace, canales incluidos, 29 €/mes, garantía, límites y para quién sirve.
- Diferenciación explícita: WhatsApp y web; no llamadas mientras no exista voz.
- Sustituir falsa prueba social por una demostración reproducible y marcada como ejemplo.
- Añadir una sección ligera de demo en home; la página `/demo/` debe tener H1 y explicación clara.
- Medir móvil y velocidad antes de afirmar que están bien o mal.

### 3. Crear una línea base nueva

Los datos actuales de Search Console son anteriores al cambio y no sirven como referencia: solo había una
impresión para una búsqueda antigua.

Medir desde la fecha de publicación del nuevo posicionamiento:

- impresiones, posición y clics del grupo "recepcionista IA";
- páginas válidas indexadas;
- aperturas de demo, inicio de compra y clientes de pago;
- menciones y citas en ChatGPT, Perplexity y Copilot con preguntas fijas y varias repeticiones;
- Bing Webmaster Tools e IndexNow;
- permitir explícitamente `OAI-SearchBot` y describir correctamente cada bot en `robots.txt`.

### 4. Crear contenido de apoyo solo con una razón demostrable

Orden provisional, sujeto a datos y objeciones reales de clientes:

1. Precio y funcionamiento.
2. Privacidad/RGPD como contenido de confianza y venta, no como keyword asumida.
3. Comparativa con Booksy solo si se confirma intención útil para Nexux.
4. Dos o tres sectores únicamente con ejemplos y lenguaje realmente distintos.
5. Herramientas gratuitas solo si son útiles y sus cálculos muestran supuestos y fuentes.

No crear páginas por ciudades, una página por cada variante de keyword, contenido genérico en masa ni
páginas sobre centralita telefónica mientras Nexux no tenga voz.

### 5. Autoridad y negocio

- Google Business Profile solo se trabajará si Nexux cumple la elegibilidad por atención presencial.
  Un SaaS exclusivamente online no debe forzar una ficha local.
- Pedir reseñas únicamente a clientes reales.
- Mantener nombre, descripción, URL y oferta consistentes en web, schema y perfiles externos.

## Criterio de éxito y revisión

Revisar a las 8-12 semanas desde que la base corregida esté publicada. Una mejora SEO no se marca como
hecha por editar código: debe comprobarse en producción y, cuando corresponda, con Search Console o datos
de conversión. Ningún agente puede prometer posiciones; sí debe evitar contradicciones y dejar evidencia.

## Estado al guardar esta versión

- Hecho anteriormente: keyword en title/H1/meta, precio de 29 €, schema base, `llms.txt` y retirada de
  páginas de ciudades.
- Publicado: limpieza de la home, schema e imagen social (`fc9334f`).
- Publicado: sitemap sin `/acceso-denegado/`, página de acceso con `noindex` y artículos/comparativa
  antiguos reescritos (`08859a5`).
- Publicado: `robots.txt` distingue `OAI-SearchBot`, `GPTBot` y `ChatGPT-User` (`b9731ac`).
- Publicado: `www.nexux.pro` redirige al dominio principal desde middleware (`3bf18c4`); compilación correcta.
- Verificado en producción: `www` devuelve `308` a `https://nexux.pro/`; `robots.txt`, home, comparativa y
  blog sirven el contenido nuevo el 21-ago-2026.
- Publicado y verificado: sección de “Ejemplos de uso” en la home, etiquetada como ejemplos y no como
  testimonios (`5c39f54`).
- Publicado y verificado: sitemap y URLs sin barra final; la variante con barra redirige con `308`
  (`067baa9`).
- Publicado y verificado: home reescrita con técnicas Miralles + Bravo y SEO natural para “recepcionista IA”
  (`54cd2b7`).
- Publicado y verificado: hook de pérdida, cita de 42 €, recuperación y ROI dinámicos según los datos del
  visitante; CTA reforzado (`e957cc9`).
- Publicado: la incidencia de visibilidad queda anotada: Ricardo no ve el copy nuevo en su navegador,
  aunque `origin/main` y el HTML público servido con cachebuster ya contienen el cambio. Queda pendiente
  verificarlo visualmente en navegador y descartar caché o URL distinta; no se marca como resuelto para el usuario.
- Siguiente: nueva medición en Search Console y baseline de asistentes IA, sin inventar menciones ni citas.
