# MISIÓN: /goal — DESARROLLO DEL DASHBOARD DE CONTROL "MINT" PARA NEXUX PRO

> **Destinatario**: Agent Codex  
> **Instrucción de ejecución**: Iniciar con el comando `/goal` para asegurar una ejecución completa, de extremo a extremo, sin detenerse hasta que el dashboard esté funcional en la Raspberry Pi.

---

## 🎯 Objetivo General
Desarrollar una herramienta web interactiva, gráfica y visual (Dashboard de Control) para monitorizar en tiempo real el flujo de adquisición de clientes del sistema de prospección **"Mint"** de Nexux Pro. El dashboard debe permitir visualizar el estado de los envíos, aperturas, respuestas, contactos escrapeados y el flujo individualizado de cada lead.

---

## 🛠️ Stack Tecnológico Autorizado

Para mantener el sistema ultra-rápido, ligero y fácil de mantener en la Raspberry Pi:
1. **Backend**: Express.js integrado en el entorno de `mint` o `nexux-pro` (puerto `3700`).
2. **Frontend**: HTML5 vanilla, CSS nativo con diseño premium (colores oscuros, gradients, estilo moderno "Glassmorphism") y JavaScript nativo.
3. **Librería de Gráficas**: **Chart.js** (cargado vía CDN) para visualizaciones fluidas y reactivas.
4. **Diseño Responsivo**: Debe verse espectacular tanto en ordenadores como en pantallas móviles.
5. **Cero Webpack / Cero React**: Evitar procesos de compilación complejos. El frontend se servirá de forma estática o a través de plantillas simples de Express.
6. **Acceso VPN**: Configurado para ser accesible de manera segura vía Tailscale (`http://100.114.144.37:3700` o la IP de Tailscale de la Pi en el puerto `3700`).

---

## 📊 Orígenes de Datos (Rutas en la Pi)

Codex deberá localizar y mapear los siguientes archivos de datos en el entorno de la Raspberry Pi:
- **Contactos Escrapeados**: `/home/nexux/scraper-output/leads_clinicas.csv` (o los generados por `scraper_clinicas.py`).
- **Envíos y Tracking**:
  - `enviados.json`
  - `openers_log.json`
  - `respuestas_log.json`
  - `conversaciones.json`
  
*Nota: Si los logs de tracking no se encuentran en un directorio predeterminado, Codex deberá buscarlos en el backend de `nexux-project/backend/` o en su defecto inicializar la estructura localmente en el directorio de `mint` para integrarlos con los scripts de envío.*

---

## 📋 Requisitos y Funcionalidades del Dashboard

### 1. Embudo de Conversión (Conversion Funnel)
- Representación visual del embudo de ventas:
  $$\text{Leads Totales} \rightarrow \text{Enviados} \rightarrow \text{Abiertos (Opener \%)} \rightarrow \text{Respondidos (Responded \%)} \rightarrow \text{Conversión a Trial \%}$$
- Gráfico dinámico de embudo para evaluar qué paso del proceso requiere optimización.

### 2. Panel Gráfico Histórico
- Gráficas diarias de rendimiento (envíos frente a aperturas y respuestas) mediante Chart.js.
- Selector de rango de fechas (últimos 7 días, 30 días, histórico completo).

### 3. Cola de Leads Calientes (Hot Leads List)
- Un widget prioritario que muestre aquellos clientes que han respondido un correo o mensaje pero que **todavía no están marcados como Trial Activo**.
- Ordenados por "última actividad" (los más recientes primero) para facilitar el seguimiento diario del equipo.

### 4. Buscador y Visor de Flujo de Cliente (Customer Journey)
- Buscador global de leads por nombre de clínica, contacto o ciudad.
- Filtro avanzado por ciudad (usando los datos de localización extraídos).
- **Visor de Flujo Individual**: Al hacer clic en un cliente, el dashboard debe mostrar una línea de tiempo (Timeline) con las interacciones exactas que ha tenido con el sistema, por ejemplo:
  1. *25/05 09:00* — Lead escrapeado en Toledo.
  2. *25/05 10:15* — Email inicial enviado.
  3. *25/05 11:30* — WhatsApp enviado.
  4. *25/05 14:00* — Email abierto (Opener detectado).
  5. *25/05 15:45* — Respuesta recibida ("Me interesa saber más").
  6. *[Pendiente]* — Trial Activo.

### 5. Monitor de Límite / Riesgo de WhatsApp
- Indicador visual del número de mensajes de WhatsApp enviados en el día actual comparado con el límite de seguridad (límite recomendado: ~60 mensajes/día, máximo 20 por sesión).
- Alerta visual en color amarillo/rojo si el volumen del día se acerca al límite de riesgo.

### 6. Widget de Estado del Scheduler (Scheduler Health)
- Indicador de estado del proceso de envíos automáticos (`nexux-scheduler`):
  - Estado: Activo / Inactivo.
  - Hora del último envío registrado.
  - Mensajes restantes programados para el día de hoy.

### 7. Chat de Consulta del Sistema (Integración con Qwen LLM)
- Un componente de entrada de chat interactivo en el propio Dashboard.
- Este chat estará conectado a un modelo **Qwen** (o a la API interna de LLM que tenga acceso a la información indexada de Mint).
- El asistente virtual debe procesar preguntas en lenguaje natural y responder consultas específicas basadas en los archivos de datos (`leads_clinicas.csv`, `respuestas_log.json`, `enviados.json`, etc.).
- Ejemplo de consulta esperada: *"¿Qué fue lo que respondió Peluquería David?"* o *"¿Cuántos leads hemos contactado hoy en Albacete?"*.
- El backend del dashboard debe exponer un endpoint (`POST /api/chat`) que reciba la consulta, use RAG o inyecte los datos relevantes como contexto al modelo Qwen y devuelva la respuesta detallada.

---

## 🛡️ Protocolo y Reglas de Ejecución para Codex

1. **Router de Modelos (de `AGENTS.md`)**:
   - Codex debe seleccionar inteligentemente el modelo para trabajar:
     - `gpt-5-mini` para tareas normales de desarrollo, debug, y pequeños scripts de Express.
     - `gpt-5` o `gpt-5-pro` para la estructuración arquitectónica de datos, diseño de APIs complejas y el refinamiento de la interfaz visual premium.
2. **Uso de Herramientas**:
   - Tienes acceso total a las herramientas del sistema Nexux: Skills, Agentes y MCPs instalados en el entorno. Utilízalos para optimizar la codificación.
3. **Seguridad y Control de Cambios**:
   - NUNCA toques ni expongas archivos `.env`, credenciales ni bases de datos de producción críticas sin comprobar.
   - Realiza siempre un `git pull` antes de comenzar a editar en la Raspberry Pi.
   - Valida la sintaxis del backend con `node -c server.js` (o el script correspondiente) antes de commitear.
   - Realiza commits específicos: `git add archivo_exacto.js` (evita `git add .` o `git add -A`).

---

## 🚀 Plan de Verificación

Una vez finalizada la implementación:
- Iniciar el servidor Express en la Pi en el puerto `3700`.
- Comprobar que es accesible desde la red local/Tailscale.
- Comprobar la carga correcta de datos desde `leads_clinicas.csv` y los JSON de logs.
- Simular un evento de apertura de correo o respuesta de WhatsApp y comprobar que el dashboard se actualiza dinámicamente o tras el polling de 30 segundos.
