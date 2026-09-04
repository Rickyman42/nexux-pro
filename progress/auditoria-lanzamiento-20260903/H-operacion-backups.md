# ÁREA H — OPERACIÓN, COPIAS DE SEGURIDAD Y ARRANQUE
Auditoría de lanzamiento nexux.pro · 2026-09-03
Auditor: agente H (Opus 5) · Sesión en frío, sin herencia de verificaciones previas.
Regla aplicada: se verifica lo que EJECUTA, no lo que documenta.

> Este fichero se escribe A TROZOS, en el momento en que cada comprobación termina.
> Si el informe queda incompleto, lo escrito hasta el corte es válido y verificado.

## Contexto de la máquina (verificado 2026-09-03 20:49 CEST)
```
$ ssh 192.168.0.120 'date; uptime; free -m; df -h / /mnt/data'
Thu  3 Sep 20:49:57 CEST 2026
 20:49:57 up 17:12, 10 users, load average: 0.75, 0.91, 0.75
Mem: total 3796 MB · used 2152 · free 123 · buff/cache 1701 · available 1643
Swap: total 2047 MB · used 1295 · free 752
/dev/mmcblk0p2  117G  90G  23G  80% /
/dev/sda1       458G  99G 336G  23% /mnt/data
```
Usuario: nexux · host: nexux · uptime 17 h (último arranque ~2026-09-03 03:37).

---
## RESUMEN

Las copias que existen se restauran de verdad (probado hoy, byte a byte) y la Pi vuelve sola tras un corte (verificado en el arranque real de esta madrugada), pero **no hay ni una sola copia de los datos de clientas fuera de esta casa**: la única capa externa lleva desde el 9 de mayo copiando una carpeta que ya no existe, y todo lo demás cuelga de un disco USB que se ha desconectado dos veces este verano dejando casi 8 días sin copias ni vigilancia.

**Hallazgos: 2 bloqueantes · 7 altos · 5 medios · 6 bajos.**

**Veredicto: SÍ CON CORRECCIONES.** Nada de lo encontrado impide que el producto funcione hoy, pero lanzar con clientes de pago sin copia fuera de sitio y sin cifrado de datos personales es asumir un riesgo que se arregla en una tarde. Antes de lanzar hay que cerrar H-B1 (Duplicati a Drive), H-A1 (cifrado), H-A2 (rescatar la copia del 24-ago antes de que la borre la rotación del lunes), H-A3 (aviso cuando NO se hace la copia) y H-A4 (monitor sobre pi.nexux.pro). Son unas 4 horas en total.

### Lo primero que hay que hacer, por orden
1. **Antes del lunes 7-sep:** renombrar `D:\nexux-backup-pi\pi-sistema-20260824.tar.gz` para que la rotación no borre la única copia de sistema utilizable que hay fuera de la Pi (2 min).
2. Arreglar el origen de Duplicati y verificar que sube a Drive (H-B1, 45 min).
3. Dar de alta el monitor de `pi.nexux.pro/health` en Uptime Kuma y uno externo (H-A4, 15 min).
4. Aviso por Telegram cuando la copia más reciente tenga más de 26 horas (H-A3, 1 h).
5. Cifrar el paquete diario (H-A1, 30 min).
6. Cambiar el cable USB del disco y alimentarlo aparte (H-B2, 20 min).

### Lo que está bien y conviene no tocar
- `docker-stack-watchdog.sh` es la pieza mejor diseñada del área: vive fuera de lo que vigila, distingue "disco sin montar" de "disco ausente", y avisa sólo en los cambios de estado. Ya ha demostrado su valor en dos incidentes reales.
- El script de copia diaria se auto-verifica: cuenta ficheros, exige un mínimo y extrae un fichero de prueba del propio paquete antes de declararse OK.
- El arranque automático está completo y probado: 0 unidades fallidas, 2 min 11 s, todo en pie.

---
## H.2 — Registro de ejecuciones (¿se puede saber si un cron corrió?)

> *Va la primera aunque se llame H.2 porque condiciona todo lo demás: sin registro no hay
> forma de auditar nada del resto del área.*

### H.2.1 · No existen /var/log/syslog ni /var/log/cron — CONFIRMADO, y la causa es peor
```
$ ls -la /var/log/syslog* /var/log/cron*
ls: cannot access '/var/log/syslog*': No such file or directory
ls: cannot access '/var/log/cron*': No such file or directory
$ dpkg -l | grep -i rsyslog      -> (vacío)
$ systemctl status rsyslog       -> Unit rsyslog.service could not be found.
```
**rsyslog no está instalado.** Por eso no hay esos ficheros. Hasta aquí no sería grave: el journal
de systemd sustituye a syslog. El problema real es el siguiente.

### H.2.2 · 🔴 El journal de systemd es VOLÁTIL: se borra entero en cada reinicio
```
$ journalctl --disk-usage
Archived and active journals take up 66.8M in the file system.
$ ls -la /var/log/journal/        -> VACÍO (solo . y ..)
$ du -sh /run/log/journal         -> 67M   (/run = tmpfs = RAM)
$ journalctl --list-boots
IDX BOOT ID                          FIRST ENTRY                  LAST ENTRY
  0 f06ef4b8...  Thu 2026-09-03 03:34:00 CEST  Thu 2026-09-03 20:50:57 CEST
```
Solo hay **un** arranque en el historial: el de hoy. Causa exacta encontrada:
```
$ cat /usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf
[Journal]
Storage=volatile
```
Es un fichero que **trae de fábrica Raspberry Pi OS** (paquete del sistema, no lo puso nadie de Nexux)
para no desgastar la tarjeta SD. `/etc/systemd/journald.conf` dice `#Storage=auto` comentado, así que
el drop-in del sistema gana.

**En cristiano:** la Pi apunta todo lo que pasa en una libreta que está en la memoria RAM. Cuando se
apaga o se reinicia, la libreta se borra entera. Hoy la Pi arrancó a las 03:34, así que de todo lo
anterior a esa hora no queda absolutamente nada: ni por qué se reinició, ni qué crons corrieron ayer,
ni si alguno falló.

**Impacto:** cero capacidad forense. Si mañana un cliente dice "ayer no me llegó la cita" y la Pi se
ha reiniciado por medio, no hay forma de investigarlo. También impide auditar históricamente los crons.

**Arreglo (5 minutos, sin riesgo):**
```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nStorage=persistent\nSystemMaxUse=300M\nMaxRetentionSec=1month\n' \
  | sudo tee /etc/systemd/journald.conf.d/50-nexux-persistent.conf
sudo systemctl restart systemd-journald
```
El drop-in en /etc gana sobre el de /usr/lib. El tope de 300 MB evita comerse la SD (hay 23 GB libres).
Nota: escribe en la SD; es el precio a pagar por tener registro. Alternativa mejor si preocupa el
desgaste: apuntar el journal al disco externo /mnt/data (458 GB, 23% usado).

### H.2.3 · Lo que SÍ funciona: el journal del arranque actual sí registra los crons
```
$ journalctl -u cron --since "-24h" | tail
Sep 03 20:50:01 nexux CRON[1970529]: (nexux) CMD (/bin/bash /home/nexux/scripts/docker-stack-watchdog.sh ...)
Sep 03 20:50:01 nexux CRON[1970530]: (nexux) CMD (/usr/bin/python3 /home/nexux/scripts/nexux-vigila-whatsapp.py ...)
Sep 03 20:50:01 nexux CRON[1970533]: (nexux) CMD (cd /home/nexux/fb-responder && ... gmail_monitor.py ...)
$ systemctl is-enabled cron -> enabled ; systemctl is-active cron -> active
```
**Matiz al hallazgo de otro auditor:** decir "no hay forma de saber si los crons se ejecutaron" es
correcto para el pasado (antes de las 03:34 de hoy) e **incorrecto para el presente**: `journalctl -u cron`
sí lo muestra dentro del arranque actual. El agujero es la persistencia, no la ausencia de registro.

## H.1 — Las capas de copia de seguridad, una a una

### Capa 1 · Datos diarios — `~/scripts/nexux-backup.sh` (cron nexux, 04:00) — FUNCIONA
```
$ cat /mnt/data/backup/nexux/estado.txt
ULTIMA COPIA: OK
Fecha:        2026-09-03 a las 04:00
Fichero:      nexux-20260903-0400.tar.gz
Tamano:       13M  (999 ficheros)
Se restaura:  si  (probado extrayendo un fichero del paquete)
Copias guardadas: 8   ·  Espacio libre en el disco: 336G
```
Qué incluye exactamente (leído del `tar` del script, no de la documentación):
`nexux-clients/clients`, `nexus-brain`, `/home/nexux/.env`, `nexux-pro/progress`,
`seo-auditor`, `scripts/aeo-auditor`, más `crontab.txt`, `pm2-procesos.json` y un
`pg_dumpall` de la base de Umami. Excluye node_modules, .git, venv, dist, caché y *.log.
Destino: `/mnt/data/backup/nexux/` (disco USB externo). Rotación 14 días, conservando el día 1 de cada mes.
Permisos del paquete: `chmod 600` (lleva el `.env` dentro).

El script es de los buenos: se auto-verifica (cuenta ficheros, exige >20, y extrae un
fichero de prueba del propio tar antes de declarar OK) y deja un parte legible.

### 🔴 Capa 1 · HUECO REAL: 4 días sin copia, del 25 al 28 de agosto
```
$ ls /mnt/data/backup/nexux/*.tar.gz
nexux-20260823-1205  nexux-20260824-0400  nexux-20260829-0400  nexux-20260830-0400
nexux-20260831-0400  nexux-20260901-0400  nexux-20260902-0400  nexux-20260903-0400
```
Faltan el 25, 26, 27 y 28. Y en `backup.log` **no hay ni la línea "=== inicio ==="** de
esos días: el script ni siquiera arrancó, no es que fallara.

Descartado que fuera la Pi apagada — otro cron diario sí corrió esos días:
```
$ grep -oE "202[0-9]-[0-9]{2}-[0-9]{2}" /home/nexux/logs/seo-guard.log | sort -u
... 2026-08-24  2026-08-25  2026-08-26  2026-08-27  2026-08-28  2026-08-29 ...
```

**Causa exacta, encontrada en el log del watchdog:**
```
$ grep "disco ausente" /home/nexux/logs/docker-stack-watchdog.log | head -1
2026-08-24 18:40:02 FALLO hardware: disco ausente. prev=OK
$ ... | tail -1
2026-08-28 09:10:02 FALLO hardware: disco ausente. prev=HARDWARE
$ grep -c "disco ausente" ...   ->  1039 comprobaciones seguidas en fallo
```
**El disco USB externo se desconectó solo el 24-ago a las 18:40 y no volvió hasta el
28-ago a las 09:20: 3 días y 14 horas.** Con el disco fuera, `/mnt/data` no existe, el
script muere en la primera redirección al log y no deja rastro. Además el cron lo lanza
con `>/dev/null 2>&1`, así que el error de arranque se tira a la basura.

**Y no es la primera vez.** La cabecera del propio watchdog documenta el incidente anterior:
> "POR QUE EXISTE (incidente 22-jul-2026 02:27 -> 26-jul-2026 02:39, 4 dias 12 min): el disco
> USB que aloja /mnt/data se desconecto fisicamente... Todo siguio muerto 4 dias: umami, n8n,
> grafana, prometheus, portainer, duplicati y -- la ironia -- uptime-kuma, que era justo lo que
> deberia haber avisado. El monitor murio con lo monitorizado."

**Dos desconexiones del mismo disco USB en cinco semanas (22-26 jul y 24-28 ago), sumando
casi 8 días sin copias de seguridad de ningún tipo.** Es un patrón, no mala suerte.

**En cristiano:** todas las copias de seguridad y toda la vigilancia viven en el mismo disco
USB, y ese disco se ha caído dos veces este verano. Cuando se cae, no hay copia, no hay
vigilancia y no hay analítica — todo a la vez. Es una única pieza de la que cuelga todo.

### Capa 2 · Sistema completo — `~/scripts/nexux-backup-sistema.sh` (cron root, domingos 03:00) — FUNCIONA
```
$ cat /mnt/data/backup/nexux/estado-sistema.txt
COPIA DEL SISTEMA: OK
Fecha:    2026-08-30 a las 03:36  (tardo 30 min)
Tamano:   89G  ·  1428765 ficheros
Destino:  /mnt/data/backup/sistema
```
Es un `rsync -aAXH --numeric-ids --delete` de la raíz entera al disco externo. Última
ejecución el domingo 30-ago (cadencia semanal correcta; la próxima toca el 6-sep).
El log de esa pasada solo tiene un aviso benigno:
```
file has vanished: "/home/nexux/.pm2/pids/nexux-blog-autopilot-1.pid"
rsync warning: some files vanished before they could be transferred (code 24)
```
Código 24 = ficheros que desaparecieron durante la copia. No compromete la copia.

El propio script ya avisa de su límite, y tiene razón:
> "AVISO: este disco esta pinchado en la propia Pi. Protege contra que la tarjeta se
> corrompa, NO contra un incendio, una inundacion o un robo."

### 🔴🔴 Capa 3 · Duplicati a Google Drive — LLEVA CASI 4 MESES SIN COPIAR NADA

Es la única capa que saca los datos FUERA de la Pi. Y está muerta desde mayo.

Configuración real, leída de su propia base de datos (no de la interfaz):
```
$ docker inspect duplicati --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
/mnt/data/docker/volumes/<hash>/_data -> /backups
/mnt/data/docker/volumes/duplicati_data/_data -> /config
/home/nexux -> /source          <-- el bind que se mencionaba, montado en LECTURA-ESCRITURA

$ sudo cp .../Duplicati-server.sqlite /tmp/ && python3 (sqlite3)
Backup  : "Backup Nexux Backend"  ·  Description: "Back en Drive"
TargetURL: enc-v1:C44F43B5...  (destino cifrado en la config; es Google Drive según la descripción)
Source  : /source/Backend        <-- o sea, /home/nexux/Backend
Opciones: encryption-module=aes · passphrase=<439 bytes> · compression=zip · dblock-size=50MB
Schedule: repite 1D · próxima 2026-09-04 05:00 · última ejecución 2026-09-03 05:00
```

**El origen no existe:**
```
$ ls -ld /home/nexux/Backend
ls: cannot access '/home/nexux/Backend': No such file or directory
```

**Y Duplicati lo lleva diciendo todos los días:**
```
$ SELECT COUNT(*), MIN(Timestamp), MAX(Timestamp) FROM ErrorLog
56 errores, del 2026-08-04 05:00 al 2026-09-03 05:00   (dos por día, todos los días)

Mensaje: "Backup aborted since the source path /source/Backend does not exist.
          Please verify that the source path exists, or remove the source path
          from the backup configuration, or set the allow-missing-source option."
```

**Cuándo fue la última copia que sí subió** (tabla Fileset de la base del trabajo):
```
$ SELECT Timestamp FROM Fileset ORDER BY Timestamp DESC LIMIT 5
  2026-05-09 05:00   <-- LA ÚLTIMA BUENA
  2026-04-27 05:00
  2026-04-25 05:00
  2026-04-22 05:00
  2026-04-20 05:00
Total: 10 versiones · 30 volúmenes remotos · 23.611 ficheros
```

**Conclusión, sin adornos: la copia en la nube tiene fecha del 9 de mayo de 2026, hace
casi cuatro meses, y contiene un directorio (`Backend`) que ya ni existe. No contiene
`nexux-clients`, ni el brain, ni `nexux-pro`, ni el `.env`. No hay NINGUNA copia de los
datos de clientas fuera de la Pi.**

Lo único bueno: cuando funcionaba, iba cifrada con AES y passphrase. La configuración
de cifrado sigue puesta, así que arreglarlo es cambiar el origen, no rehacerlo.

**En cristiano:** el sistema que debía subir una copia a Google Drive lleva desde mayo
intentando copiar una carpeta que se borró. Todos los días lo intenta, todos los días
falla, y nadie se ha enterado porque el aviso se queda dentro de Duplicati. Si la Pi
arde o le roban el disco, lo que hay en la nube es el backend viejo de mayo.

**Arreglo (15 min):** entrar a `http://192.168.0.120:8200`, editar el trabajo y cambiar
el origen `/source/Backend` por lo que de verdad importa — `/source/nexux-clients/clients`,
`/source/nexus-brain`, `/source/nexux-pro`, `/source/.env` — y lanzarlo a mano una vez para
comprobar que sube. Requiere que las credenciales de Google Drive sigan siendo válidas
(el token OAuth de mayo puede haber caducado: verificar en la misma pasada).
Y dejar activada la notificación de fallo por correo/Telegram, que hoy no está.

### Riesgos adicionales de Duplicati (verificados, no supuestos)
| Detalle | Comprobación | Riesgo |
|---|---|---|
| El bind `/home/nexux -> /source` está en **RW** | `docker inspect` | Un fallo o compromiso del contenedor puede escribir en TODO el home, incluido `.ssh`. Debería ser `:ro`. |
| El volumen de destino `/backups` está **vacío** y es **anónimo** (nombre de 64 hex) | `sudo ls -la .../_data` -> vacío | Un `docker volume prune` lo borraría sin avisar. Hoy da igual porque no hay nada dentro. |
| El puerto **8200 escucha en 0.0.0.0** | `docker port duplicati` -> `0.0.0.0:8200` | La consola de Duplicati (que gestiona copias y claves) es accesible desde toda la red local. |

### Aclaración: cuáles son las 4 capas de verdad (Duplicati NO es ninguna)
Según el quality-ledger del 23-ago (línea 1177), las cuatro capas montadas son:
1. Datos diarios en la Pi (cron 04:00 -> disco USB)
2. Sistema completo semanal en la Pi (cron root, domingos 03:00 -> disco USB)
3. **Datos diarios copiados a Windows C:** (tarea `Nexux-BackupDiario-PiAWindows`, 09:30)
4. **Sistema completo semanal al disco D: de Windows** (tarea `Nexux-BackupSistema-PiADisco`, lunes 10:00)

Duplicati es una **quinta pieza heredada**, anterior y no contada en las 4 — y está rota
desde mayo (ver arriba). Importa mucho porque era la única con destino fuera de la casa.

### Capa 3 · Datos diarios Pi -> Windows C: — FUNCIONA
Verificado en el propio Windows (no por SSH, para no fiarme de lo que dice la Pi):
```
PS> Get-ScheduledTask -TaskName Nexux-BackupDiario-PiAWindows | Get-ScheduledTaskInfo
UltimaEjec : 03/09/2026 9:30:01   Resultado : 0   ProximaEjec : 04/09/2026 9:30:00

PS> Get-ChildItem C:\Users\Nexux\backups\nexux-pi
nexux-20260823-1205.tar.gz  11,71 MB   23/08/2026 12:47
nexux-20260824-0400.tar.gz  11,72 MB   24/08/2026 9:30
nexux-20260829-0400.tar.gz  12,07 MB   29/08/2026 9:30
nexux-20260830 / 0831 / 0901 / 0902 / 0903 ...  12,32 MB   03/09/2026 9:30

C:\...\estado-windows.txt:
COPIA EN WINDOWS: OK · Fecha 2026-09-03 09:30 · nexux-20260903-0400.tar.gz (12.3 MB)
Integra: si - la huella coincide con la de la Pi
```
El script compara md5 con el de la Pi antes de dar por buena la descarga. Correcto.
**Arrastra el mismo hueco del 25 al 28 de agosto** — lógico: no puede bajar lo que no existe.
**Aviso de fragilidad:** la tarea corre como `LogonType = Interactive`, es decir **solo si
Ricardo tiene la sesión de Windows abierta**. Si el PC está apagado o sin sesión, no hay copia
y nadie avisa.

### 🔴 Capa 4 · Sistema completo -> disco D: — NUNCA HA COMPLETADO UNA COPIA BUENA
```
PS> Get-ScheduledTask -TaskName Nexux-BackupSistema-PiADisco | Get-ScheduledTaskInfo
UltimaEjec : 31/08/2026 10:00:00   Resultado : 3221225786   ProximaEjec : 07/09/2026 10:00

PS> Get-ChildItem D:\nexux-backup-pi
pi-sistema-20260824.tar.gz   23,34 GB   24/08/2026 12:29
pi-sistema-20260831.tar.gz    7,47 GB   31/08/2026 10:47
estado-sistema-windows.txt              24/08/2026 12:29

D:\nexux-backup-pi\estado-sistema-windows.txt:
COPIA DEL SISTEMA EN EL DISCO D: FALLO
Fecha del intento: 2026-08-24 12:29
Motivo: La transferencia fallo (codigo 2)
```
Tres pruebas independientes de que esta capa no ha funcionado nunca:
1. El parte de estado dice **FALLO**, y es del **24 de agosto**: el intento del 31 ni siquiera
   llegó a escribirlo.
2. El código de salida del 31-ago es **3221225786 = 0xC000013A**, que en Windows significa
   "el proceso fue terminado" (Ctrl+C / cierre de sesión). Se cortó a mitad.
3. Los tamaños no cuadran: en la Pi el sistema son **89 GB / 1.428.765 ficheros**; los ficheros
   de D: pesan 23,34 GB y 7,47 GB, y cada uno es más pequeño que el anterior. El script sólo
   escribe "OK" cuando el tar termina, y nunca lo ha escrito.

**Causa más probable (hipótesis, no confirmada):** la tarea corre como `Interactive` y la
transferencia dura ~40-60 minutos; si la sesión de Windows se bloquea, se cierra o el equipo
suspende, el `ssh ... | tar` se corta. El código 0xC000013A encaja exactamente con eso.

**En cristiano:** el disco D: tiene dos ficheros grandes que parecen copias del sistema pero
son ficheros a medias. Si mañana hay que reconstruir la Pi desde cero, esos ficheros no sirven.
La copia buena del sistema existe **sólo** en el disco USB de la Pi — el mismo que se ha
desconectado dos veces este verano.

## H.3 — ¿Se puede RESTAURAR? Prueba real hecha hoy

No basta con que el fichero exista. Restauré de verdad y comparé con el original:
```
$ tar xzf /mnt/data/backup/nexux/nexux-20260903-0400.tar.gz -C /tmp/audit-restore <fichero>
$ md5sum /tmp/audit-restore/<f>   vs   md5sum /home/nexux/<f>

nexux-clients/clients/ricarda-1e1caf/appointments.json
   restaurado: 21c8daefa5af8fb7133de9a7310edaea  (1273 bytes)
   original  : 21c8daefa5af8fb7133de9a7310edaea  (1273 bytes)   -> IDENTICO
nexux-clients/clients/ricarda-1e1caf/config.json
   restaurado: 3fb86b7f90cbd72dcc6c6d14adc76894  (2186 bytes)
   original  : 3fb86b7f90cbd72dcc6c6d14adc76894  (2186 bytes)   -> IDENTICO
nexus-brain/nexux-live-state.md
   restaurado: 5ca16ca6...(79984 b)  ·  original: 82681cd1...(79913 b)  -> DIFIERE
   (correcto: ese fichero se ha modificado hoy después de las 04:00)
```
**Veredicto: la copia diaria de datos SÍ se restaura, y sale idéntica byte a byte.**
Es la única de las cinco piezas cuya restauración está probada hoy.

Contenido verificado del paquete (`tar tzf`): 306 entradas bajo `nexux-clients/clients/`,
21 clientes, con `appointments.json`, `conversations.json`, `config.json` y `auth/` de cada uno.

### 🔴 H.3.1 · Los datos personales de clientas viajan SIN CIFRAR en 3 de las 4 capas
```
$ file /mnt/data/backup/nexux/nexux-20260903-0400.tar.gz
gzip compressed data, from Unix, original size modulo 2^32 83712000
```
Es un `.tar.gz` plano. No hay GPG, ni `openssl enc`, ni `age` en ninguna parte del script.
La única protección es `chmod 600` en la Pi, que no viaja con el fichero.

Dentro van, en claro: nombres, teléfonos y citas de clientas (`appointments.json`,
`conversations.json`), el `.env` con todas las claves de producción, y las carpetas `auth/`
con las credenciales de sesión de WhatsApp de cada cliente.

Ese mismo fichero sin cifrar se copia cada día a `C:\Users\Nexux\backups\nexux-pi\`
(capa 3), y la copia del sistema (capa 2 y 4) arrastra además `/home/nexux/.ssh`.

**Impacto RGPD:** son datos personales de terceros (las clientas de las peluquerías, que no
son ni clientes de Nexux). El art. 32 del RGPD pide medidas técnicas apropiadas, y el cifrado
de las copias es la medida estándar. Con Nexux como encargado del tratamiento, un disco USB
o un portátil perdido es una brecha notificable.

**Arreglo (30 min):** cifrar el paquete al crearlo, con la clave guardada fuera de la Pi:
```bash
# al final de nexux-backup.sh, sustituyendo el tar suelto:
tar czf - ... | gpg --batch --yes --symmetric --cipher-algo AES256 \
     --passphrase-file /root/.backup-key -o "$ARCH.gpg"
```
La prueba de restauración del script debe seguir haciéndose DESPUÉS de descifrar, o no
prueba nada. Lo único cifrado hoy es Duplicati (AES + passphrase)... que no copia nada.

## H.4 — Procesos de PM2

```
$ pm2 list   (3-sep 20:59)
17 procesos · 12 online · 5 stopped
online desde 2026-09-03 03:38 (el arranque de hoy): claude-mem-proxy, nexux-dashboard,
  tg-monitor, company-builder-api, nexux-pro-leads, cloudflared-provision, mint-dashboard,
  aeo-auditor, outreach-api, inbound-reply-receiver, telegram-claude-bot
nexux-site       online desde 04:05 · 1 reinicio
nexux-clients    online desde 20:48 · 4 reinicios  <- los parches autorizados de hoy, NO es inestabilidad
stopped a propósito: lead-finder, meta-ads-monitor, opencode-server (autorestart=false)
stopped hoy 16:01: nexux-blog-autopilot · 5307 reinicios
```
Revisado el log de errores de `nexux-clients`: **no hay ninguna traza de caída**. Lo último
son un `SyntaxError` de body-parser (una petición entrante con JSON inválido, que Express
captura sin morir) y un aviso del normalizador de configuración. Coherente con lo que dice
el encargo: los 4 reinicios son los parches, no inestabilidad.

### 🟠 H.4.1 · `nexux-blog-autopilot`: 5.307 reinicios, y el porqué exacto
Está **parado desde hoy a las 16:01** (parada manual: figura `stopped` teniendo
`autorestart=true`; si hubiera muerto solo, PM2 lo habría relanzado).

**Por qué se reiniciaba en bucle** — causa mecánica confirmada, no hipótesis:
```
$ python3 -c "categories.json"
categorias: 4 | activas: 0
  Alternativas a Tinder España  enabled=False
  Citas en Madrid               enabled=False
  Apps de citas España          enabled=False
  Psicología del amor           enabled=False
(fichero modificado el 24/08/2026 19:09)

$ tail index.js
  logger.info('Starting Nexux Blog Autopilot scheduler...');
  startScheduler(logger);
  logger.info('Scheduler running.');
```
Con las 4 categorías desactivadas, `startScheduler` no registra ninguna tarea. Node se queda
sin nada pendiente, **sale con código 0 (éxito)** y PM2, viendo un proceso que "terminó bien",
lo vuelve a lanzar 5 segundos después. Y otra vez. Y otra.

**Frecuencia y fechas medidas en el log:**
```
$ grep "Starting Nexux Blog Autopilot scheduler" ...out.log | grep -oE "^\[[0-9-]{11}" | uniq -c
      4 [2026-07-30     1 [2026-08-13
   7195 [2026-08-28    10340 [2026-08-29    10260 [2026-08-30
  10279 [2026-08-31    10296 [2026-09-01    10268 [2026-09-02    5752 [2026-09-03
Total en el log: 64.441 arranques (desde 2026-04-20)
```
Uno cada 8,4 segundos, ~10.300 al día, **desde el 28 de agosto**. Esa fecha es justo el día
en que volvió el disco USB (28-ago 09:20), lo que encaja con que el bucle empezara al
recuperarse la pila. *(La correlación con el disco es hipótesis; el mecanismo de salida
limpia + relanzado está verificado.)*

**Por qué el propio PM2 no lo frenó** — un vigilante programado para ignorar este fallo:
```
max_restarts: 10   min_uptime: None (por defecto 1000 ms)   restart_delay: 5000
```
PM2 solo cuenta un reinicio contra `max_restarts` si el proceso muere **antes** de `min_uptime`.
Aquí el proceso vive unos 3 segundos, más que el segundo de guardia, así que PM2 lo trata como
un reinicio sano y **nunca** lo marca como `errored`. El tope de 10 no llegó a aplicarse jamás:
llevaba 5.307. Este es el ejemplo exacto de "vigilante configurado para no ver justo el fallo
que debería detectar".

**¿Volverá solo?** No. `dump.pm2` (guardado hoy 16:01) lo tiene con `status_guardado=stopped`,
así que tras un reinicio de la Pi seguirá parado. Es el comportamiento deseado, pero conviene
saberlo: **nadie va a reactivar el blog automáticamente**; hay que hacerlo a mano.

**Arreglo, cuando se quiera reactivar:** que `index.js` no salga si no hay categorías activas
(un `setInterval` de guardia o un `process.exit(1)` explícito para que PM2 sí lo cuente), y
poner `min_uptime: "60s"` en la configuración de PM2 para que el tope de 10 reinicios funcione.

### 🟠 H.4.2 · Los logs de PM2 crecen sin límite: no hay rotación
```
$ du -sh /home/nexux/.pm2/logs/     ->  122M
$ ls -laS /home/nexux/.pm2/logs/ | head
41.895.547  opencode-nvidia-error.log      (proceso que ya ni existe)
37.762.304  nexux-blog-autopilot-out.log
21.242.894  nexux-site-error.log
 9.228.826  opencode-nvidia-out.log
$ pm2 conf | grep logrotate   ->  (nada)
$ ls /home/nexux/.pm2/modules/ ->  (vacío)
```
**`pm2-logrotate` no está instalado.** 122 MB en la tarjeta SD, que está al 80% (23 GB libres).
No es urgente hoy, pero un solo proceso en bucle (como el autopilot: 37 MB) puede engordar
rápido. Además hay 51 MB de logs de `opencode-nvidia`, un proceso que ya no existe.

**Arreglo (2 min):** `pm2 install pm2-logrotate` y `pm2 set pm2-logrotate:max_size 10M` +
`retain 7`. (Nota: instalar un módulo de PM2 estaba fuera del alcance de esta auditoría; no lo he hecho.)

## H.5 — Vigilantes: qué vigilan de verdad y qué NO

### H.5.1 · `docker-stack-watchdog.sh` (cron cada 5 min) — el bueno
Corre en la SD, sin Docker y sin Python, precisamente para no morir con lo que vigila.
Comprueba: disco presente -> montaje -> `docker.service` -> heartbeat de Umami. Distingue
"disco presente sin montar" (lo arregla solo) de "disco ausente" (avisa y no insiste), y
notifica sólo en los cambios de estado. Está probado en fuego real: detectó y registró las
dos desconexiones del disco. Es la pieza mejor diseñada de todo el área.
Log vivo: `/home/nexux/logs/docker-stack-watchdog.log` (última entrada 2026-09-03 03:45).

### 🔴 H.5.2 · `nexux-vigila-whatsapp.py` (cron cada 10 min) — vigila 1 cliente de 21, y
### está programado para ignorar los dos fallos que más importan
Leído el código entero (143 líneas). Dos exclusiones explícitas:

**(a) Se salta a todo cliente cuya carpeta `auth/` esté vacía:**
```python
# Solo se vigila a quien ya vinculo su WhatsApp: si nunca lo conecto, no esta caido
if not (os.path.isdir(auth_dir) and os.listdir(auth_dir)):
    continue
```
La intención es razonable. El problema es que **"auth/ vacía" es exactamente el síntoma del
fallo conocido de sesiones de WhatsApp** (el guardado de credenciales falla en silencio y deja
la carpeta vacía). O sea: el vigilante salta justo el caso que debería cazar.

Estado real hoy:
```
$ for d in clients/*/; do echo "$d $(ls -A $d/auth | wc -l)"; done
estudio-ricardo-demo-mostoles-946279  ->  231 ficheros
los otros 20 clientes                 ->  0 ficheros
$ cat nexus-brain/estado-whatsapp.json  ->  vigilados: 1  (Centro Lena, conectado, 21:00:01)
```
**De 21 carpetas de cliente, el vigilante vigila UNA.** Hoy la mayoría son de prueba, pero
en el momento en que entre un cliente de pago cuya vinculación falle, quedará fuera del radar
sin que nadie lo note.

**(b) Si la API entera se cae, NO cuenta como caída:**
```python
def conectado(...):
    try: ... return bool(d[...]["connected"])
    except Exception: return None          # <-- API caída, timeout, error 500...
...
if ok is None:
    continue                               # "no se pudo comprobar: no se cuenta como caida"
```
**El fallo más grave posible — que `nexux-clients` esté muerto y ningún cliente reciba
respuesta — es precisamente el que este vigilante está escrito para ignorar.** Pregunta al
API por el estado del socket; si el API no contesta, se encoge de hombros y pasa al siguiente.

**Arreglo (20 min):** contar `None` como fallo cuando el propio `/health` del API no responde
(distinguir "el API no contesta" de "este cliente concreto da error"), y avisar de los clientes
con `auth/` vacía que llevan más de X horas sin vincular, en vez de saltárselos.

### 🔴 H.5.3 · Uptime Kuma NO vigila nexux.pro
```
$ sqlite3 kuma.db "SELECT id,name,url,active FROM monitor"
1  Nexux Backend  https://nexux-backend-production.up.railway.app/health   activo
2  Grafana        http://192.168.0.120:3001/api/health                     activo
3  N8N            http://192.168.0.120:5678/healthz                        activo
4  Open WebUI     http://192.168.0.120:3002                                activo
5  Portainer      http://192.168.0.120:9000/api/status                     activo
```
**Cinco monitores y ninguno apunta a `pi.nexux.pro`.** Vigila el backend de la *otra* marca
(nexux.es, en Railway) y cuatro herramientas internas. El producto que se va a lanzar no está
vigilado por nadie.

El endpoint existe y va bien — lo he probado ahora:
```
$ curl -s -w "HTTP %{http_code} en %{time_total}s" https://pi.nexux.pro/health
HTTP 200 en 0.118727s   ->  {"ok":true,"ts":"2026-09-03T19:03:28.382Z"}
```
Sólo hay que darlo de alta. Es un monitor HTTP de 2 minutos de trabajo.

Latidos y avisos de Kuma sí funcionan (el contenedor va en UTC, por eso las horas parecen
atrasadas dos horas):
```
Nexux Backend  ultimo=2026-09-03 18:59:57 UTC (=20:59 CEST)  ARRIBA
Open WebUI     ultimo=2026-09-03 18:59:52 UTC                CAIDO   <- lleva un rojo permanente
notificaciones: 2 activas (webhook a n8n + "Telegram Directo"), 10 enlaces monitor<->aviso
```
`Open WebUI` está caído de forma permanente. Una alerta que siempre está en rojo enseña a
ignorar el panel: conviene arreglarla o quitar el monitor.

**Y el punto ciego estructural:** Uptime Kuma es un contenedor Docker cuyos datos viven en
`/mnt/data`, y `docker.service` declara `RequiresMountsFor=/mnt/data` (verificado con
`systemctl show docker`). Si el disco USB se va, **Kuma se va con él**. Ya pasó en julio, y
está escrito en la cabecera del watchdog. Hoy el único vigilante que sobrevive a eso es el
`docker-stack-watchdog.sh` del cron. Es suficiente para el disco, pero **no hay nada externo
a la Pi que vigile si la Pi entera se apaga o se queda sin red.**

## H.6 — Alertas de Telegram: probado hoy, funciona
```
$ curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
{"ok":true,"result":{"id":8363869188,"is_bot":true,"first_name":"Nexux Soporte",
 "username":"nexux_soporte_bot", ...}}

$ curl --data-urlencode "text=PRUEBA-AUDITORIA (area H, 3-sep 21:05)..." --data "chat_id=511455969" .../sendMessage
HTTP 200 · ok: True · entregado a: Richy (private) · message_id: 2102
```
**Canal verificado en vivo el 3-sep a las 21:05.** Se envió un único mensaje, al chat privado
del administrador, marcado como PRUEBA-AUDITORIA. Ningún cliente recibió nada.

Quién avisa por ese canal: el watchdog de Docker (cambios de estado del disco/pila), el
vigilante de WhatsApp (caída y recuperación por cliente) y Uptime Kuma (notificación
"Telegram Directo", que apunta al mismo chat 511455969).

**Lo que NO avisa por Telegram, y debería:**
| Suceso | ¿Avisa hoy? |
|---|---|
| Disco USB desconectado | Sí (watchdog) |
| WhatsApp de un cliente caído | Sólo si su `auth/` no está vacía y el API responde |
| **La copia de seguridad no se hizo** | **NO** — el `estado.txt` sólo se escribe si el script llega a correr |
| **Duplicati falla (lleva 4 meses)** | **NO** — el error se queda dentro de Duplicati |
| **La copia a D: se corta a mitad** | **NO** — el parte queda en el disco y nadie lo mira |
| **`pi.nexux.pro` caído** | **NO** — no hay monitor |
| La Pi entera apagada o sin red | NO — todo lo que avisa vive dentro de la propia Pi |

## H.7 — Salud de la máquina (3-sep 21:06)

```
$ uptime          -> load average: 0.69, 0.67, 0.70   (4 núcleos: holgado)
$ free -h         -> Mem 3.7Gi total · 2.3Gi usada · 100Mi libres · 1.5Gi disponibles
                     Swap 2.0Gi total · 1.3Gi USADA (65%) · 728Mi libres
$ df -h           -> /            117G  90G  23G  80%   <- vigilar
                     /mnt/data    458G  99G 336G  23%
                     /boot/firmware 510M 78M 433M 16%
$ df -i           -> inodos: raíz 22% · /mnt/data 5%   (sin problema)
```

### 🟠 H.7.1 · Temperatura 78 °C y limitación térmica YA ocurrida en este arranque
```
$ vcgencmd measure_temp   -> temp=77.9'C
$ vcgencmd get_throttled  -> throttled=0xe0000
```
Descodificado bit a bit:
```
[   ] bajo voltaje AHORA                [   ] limitada por calor AHORA
[   ] HA HABIDO bajo voltaje            [ X ] HA HABIDO limitacion de frecuencia
[ X ] HA HABIDO limitacion por calor    [ X ] SE HA SUPERADO el limite blando de temperatura
```
**En las 17 horas que lleva encendida, la Pi ya se ha frenado por calor.** Ahora mismo no
está limitada, pero ha pasado. La alimentación está bien (ningún bit de bajo voltaje), así
que es puramente disipación.

**En cristiano:** la Pi va a 78 grados y hoy ya ha tenido que bajar de marcha para no
quemarse. Cuando eso pasa, todo va más lento: la web, el bot, las respuestas a las clientas.
No se rompe nada, pero con carga real de lanzamiento el margen es estrecho.
**Arreglo:** ventilación/disipador, o mover el rsync semanal de 30 min a una hora fresca.

### H.7.2 · Memoria: la swap está al 65%
1,3 GB de los 2 GB de swap en uso con `swappiness=60`. No hay proceso desbocado (el mayor es
un Astro de 188 MB), pero el margen es corto: por eso `pnpm build` en la Pi la tumbó hoy.
Es un dato a tener presente, no un fallo.

### 🟡 H.7.3 · Logs sin rotación: 122 MB de PM2 + un fichero de 73 MB
```
$ grep -rl -i -E "pm2|nexux" /etc/logrotate.d/   ->  NO hay regla de rotación para nexux ni pm2
$ du -sh /home/nexux/.pm2/logs   -> 122M
$ du -sh /home/nexux/logs        -> 13M
$ du -sh /tmp                    -> 208M
$ find /home/nexux -size +50M
  73M  /home/nexux/nexux-blog-autopilot/logs/autopilot.log   <- el mismo bucle, por otro sitio
  41M  (.pm2) opencode-nvidia-error.log   <- proceso que ya no existe
```
`logrotate` está vivo (última pasada hoy 00:18) pero sólo cubre paquetes del sistema. Ningún
log de Nexux rota. Con 23 GB libres en una SD al 80%, no es urgente hoy, pero un solo proceso
en bucle ya ha generado 110 MB entre los dos ficheros del autopilot.

## H.8 — ¿Vuelve todo solo tras un corte? SÍ — y está probado en un arranque real de HOY

No hace falta especular: **la Pi se reinició hoy a las 03:34** y puedo auditar ese arranque.
```
$ who -b                 -> system boot  2026-09-03 03:34
$ systemd-analyze        -> Startup finished in 8.480s (kernel) + 2min 3.159s (userspace)
$ systemctl --failed     -> 0 loaded units listed        <- ninguna unidad falló
```

| Pieza | Cómo arranca | Comprobación | Resultado |
|---|---|---|---|
| PM2 y sus 17 procesos | `pm2-nexux.service` -> `ExecStart=/usr/lib/node_modules/pm2/bin/pm2 resurrect` | `is-enabled`=enabled, `Active since 2026-09-03 03:39:00` | OK |
| Lista guardada de PM2 | `~/.pm2/dump.pm2` (73.949 bytes, 3-sep 16:01) + `.bak` | 17 procesos con su estado correcto (autopilot=stopped) | OK |
| Docker y los 8 contenedores | `docker.service` enabled | los 8 contenedores llevan `Up 17 hours` | OK |
| Montaje del disco | `LABEL=nexux-data /mnt/data ext4 defaults,nofail,x-systemd.device-timeout=5` | `nofail` -> si el disco falta, el arranque NO se cuelga | OK |
| Túnel de Cloudflare | **NO es servicio de systemd** (`systemctl is-enabled cloudflared` -> `not-found`); lo levanta PM2 como `cloudflared-provision` | proceso 2807 vivo desde las 03:38; `pi.nexux.pro/health` -> HTTP 200 | OK |
| cron | enabled + active | el backup de las 04:00 corrió 21 min después del arranque | OK |
| Xvfb/Chromium del auditor AEO | `@reboot sleep 45 && start_copilot_xvfb.sh` | `/tmp/copilot_reboot.log` escrito a las 03:39: "Copilot env listo" | OK |
| ssh / fail2ban / nginx | enabled + active | — | OK |

**Veredicto de arranque: si la Pi se reinicia ahora, vuelve todo sola.** Es la parte más sólida
del área, y no es una promesa: pasó hoy y salió bien.

Dos matices:
- **El túnel de Cloudflare depende de PM2**, no de systemd. Funciona (probado hoy), pero si
  PM2 no arranca, el dominio público se cae con él. Además el token del túnel va **en la línea
  de comandos**, visible con un simple `ps aux` para cualquier usuario de la Pi.
- **`docker.service` declara `RequiresMountsFor=/mnt/data`** (verificado con `systemctl show
  docker`). Sin el disco USB, systemd no arranca Docker — y ahí se van Umami, n8n, Grafana,
  Portainer, Duplicati y Uptime Kuma. Es la dependencia que ya causó los dos incidentes.
- **Por qué se reinició hoy a las 03:34: NO SE PUEDE SABER.** El journal es volátil y se borró
  con el reinicio. Es el coste práctico del hallazgo H.2.2.

## H.9 — Barrido de TODAS las tareas programadas

`crontab -l` del usuario `nexux`: 26 líneas, de las que **8 están comentadas/apagadas** con su
motivo escrito al lado (buena práctica: se ve por qué se apagaron y cuándo). Activas: 17.
`sudo crontab -l` de root: 1 (la copia del sistema, domingos 03:00). `/etc/cron.d`: sólo
`e2scrub_all` del sistema.

| Tarea | Cada cuánto | Última ejecución (mtime del log) | Estado |
|---|---|---|---|
| `nexux-backup.sh` | diario 04:00 | 2026-09-03 04:00 | OK (con el hueco del 25-28 ago) |
| `nexux-backup-sistema.sh` (root) | domingos 03:00 | 2026-08-30 03:36 | OK |
| `docker-stack-watchdog.sh` | cada 5 min | 2026-09-03 03:45 | OK (sólo escribe si hay algo que decir) |
| `nexux-vigila-whatsapp.py` | cada 10 min | 2026-09-03 21:00 | Corre, pero ver H.5.2 |
| `monitor-embudo.py --check` | cada 15 min | 2026-09-03 21:00 | OK |
| `monitor-embudo.py --submit` | diario 09:00 | 2026-09-03 09:00 | OK |
| `gmail_monitor.py` | cada 5 min | 2026-09-03 21:05 | OK |
| `seo-guard.js` | diario 08:30 | 2026-09-03 08:30 | OK |
| `vigilante-calendario.mjs` | diario 08:20 | 2026-09-03 08:20 | OK (1 cliente: "1 OK, 0 con problemas") |
| `kaizen-scan.py` | diario 08:00 | 2026-09-03 08:00 | OK ("Sin causas repetidas") |
| `gsc.py nexux-es` | diario 06:30 | 2026-09-03 06:30 | OK |
| `notebooklm-keepalive.py` | diario 07:00 | 2026-09-03 07:00 | OK |
| `recordatorio-seo-ia-30d.py` | diario 10:00 | 2026-09-03 10:00 | OK |
| `ig draft` | mar/jue/sáb 20:30 | 2026-09-03 20:30 | OK |
| `analitica-check.js` | lunes 09:00 | 2026-08-31 09:00 | OK (toca el lunes) |
| `@reboot` Xvfb/Copilot | al arrancar | 2026-09-03 03:39 | OK |
| `informe_viernes.py` | viernes 18:00 | log ausente | NO VERIFICABLE (ver abajo) |
| `cuadro-ventas-semanal.py` | viernes 18:30 | log ausente | NO VERIFICABLE (ver abajo) |

### 🟡 H.9.1 · Varios crons escriben su log en `/tmp`, que es memoria RAM
```
$ findmnt /tmp
/tmp   tmpfs  tmpfs  rw,nosuid,nodev,size=1943904k
$ du -sh /tmp   ->  208M
```
Dos consecuencias, ambas reales:
1. **Esos logs desaparecen en cada reinicio.** Por eso `nexux-informe-viernes.log` y
   `nexux-cuadro-ventas.log` no existen: son tareas de viernes y la Pi arrancó hoy. No puedo
   decir si corrieron el viernes 29-ago; el registro se ha borrado. Se declara NO VERIFICADO.
2. **Ocupan RAM.** 208 MB de `/tmp` + 67 MB del journal en `/run` = **275 MB de los 3,7 GB
   metidos en ficheros temporales**, en una máquina que ya tira 1,3 GB de swap.

**Arreglo (10 min):** mover los logs de cron de `/tmp/*.log` a `/home/nexux/logs/`, y añadir
una regla de logrotate para esa carpeta.

## H.10 — Qué queda FUERA de todas las copias

### 🔴 H.10.1 · Los volúmenes de Docker no entran en ninguna copia
```
$ docker info --format "Docker Root Dir: {{.DockerRootDir}}"   ->  /mnt/data/docker
$ cat /etc/docker/daemon.json                                  ->  "data-root": "/mnt/data/docker"
$ grep exclude ~/scripts/nexux-backup-sistema.sh
  --exclude='/tmp/*' --exclude='/mnt/*' --exclude='/media/*' ...
```
Docker guarda todo en `/mnt/data/docker`, y el rsync del sistema **excluye `/mnt/*` entero**.
La copia diaria tampoco lo toca. Resultado: si el disco USB muere, se pierden para siempre:
- **n8n**: flujos y credenciales
- **Grafana**: paneles
- **Uptime Kuma**: `kuma.db` (173 MB) con la configuración de los monitores y 1.127.419 latidos
- **Duplicati**: su configuración, **incluida la passphrase de cifrado** — sin ella, las copias
  antiguas que hay en Drive (las de abril-mayo) son ilegibles para siempre
- Umami **se salva**, y sólo porque `nexux-backup.sh` hace un `pg_dumpall` aparte. Bien visto,
  pero es el único de los ocho contenedores que tiene esa red.

**Y aquí está el nudo del área:** el mismo disco USB es a la vez **dónde viven los datos de
Docker** y **dónde se guardan las copias 1 y 2**. Si muere, se lleva los datos y las copias a
la vez. Lo único que quedaría fuera son los 13 MB de la capa 3 en Windows.

### 🟠 H.10.2 · Código de hoy que no está ni en las copias ni en GitHub
```
$ git -C /home/nexux/nexux-clients ...
  remoto: git@github.com:Rickyman42/nexux-clients-core.git · rama main
  último commit: efd9797 2026-09-03 "fix(seguridad): el enlace de dueno de Telegram..."
  commits sin subir: 3        ficheros sin commitear: 14
$ git -C /home/nexux/nexux-pro ...
  commits sin subir: 0        ficheros sin commitear: 32
```
El **código** de `nexux-clients` no entra en la copia diaria (esa sólo se lleva
`nexux-clients/clients`, los datos). Entra en la copia del sistema, que es semanal y del
**30-ago**. Así que los 3 commits de hoy — entre ellos los parches de seguridad — y los 14
ficheros sin commitear **no están en ninguna copia ni en GitHub**. Si la tarjeta SD muere esta
noche, se pierden.
(No he hecho `push`: está expresamente fuera del alcance de esta auditoría.)

---

# TABLA DE COMPROBACIONES

| # | Qué se comprueba | Cómo (comando exacto) | Resultado | Evidencia |
|---|---|---|---|---|
| 1 | Copia diaria de datos se hizo hoy | `cat /mnt/data/backup/nexux/estado.txt` | **OK** | "ULTIMA COPIA: OK · 2026-09-03 04:00 · 13M · 999 ficheros" |
| 2 | Continuidad de la copia diaria | `ls /mnt/data/backup/nexux/*.tar.gz` + `cat backup.log` | **FALLO** | Faltan 25,26,27,28-ago; el log no tiene ni "inicio" esos días |
| 3 | Causa del hueco | `grep "disco ausente" ~/logs/docker-stack-watchdog.log` | **FALLO** | 1.039 comprobaciones en fallo, 24-ago 18:40 -> 28-ago 09:10 |
| 4 | Que ese hueco no fuera la Pi apagada | `grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" ~/logs/seo-guard.log \| sort -u` | **OK** | seo-guard sí corrió el 25,26,27 y 28 |
| 5 | Copia del sistema (Pi) | `cat /mnt/data/backup/nexux/estado-sistema.txt` | **OK** | "COPIA DEL SISTEMA: OK · 2026-08-30 03:36 · 89G · 1.428.765 ficheros" |
| 6 | Copia diaria replicada a Windows | `Get-ScheduledTaskInfo Nexux-BackupDiario-PiAWindows` + `Get-ChildItem` | **OK** | Última 03/09 09:30, resultado 0; md5 coincide con la Pi |
| 7 | Copia del sistema al disco D: | `Get-ScheduledTaskInfo Nexux-BackupSistema-PiADisco` | **FALLO** | Resultado 3221225786 (0xC000013A, proceso terminado) |
| 8 | Integridad de los ficheros de D: | `gzip -t pi-sistema-*.tar.gz` | **FALLO parcial** | 20260824: GZIP VALIDO · **20260831: "unexpected end of file" = truncado** |
| 9 | El parte de D: dice OK alguna vez | `cat D:\nexux-backup-pi\estado-sistema-windows.txt` | **FALLO** | "COPIA DEL SISTEMA EN EL DISCO D: FALLO · 2026-08-24 · codigo 2" |
| 10 | Duplicati: a dónde escribe | `docker inspect duplicati` + sqlite de su config | **FALLO** | Destino Drive (URL cifrada); origen `/source/Backend` |
| 11 | Duplicati: el origen existe | `ls -ld /home/nexux/Backend` | **FALLO** | "No such file or directory" |
| 12 | Duplicati: cuándo corrió y con qué resultado | `SELECT * FROM ErrorLog` (Duplicati-server.sqlite) | **FALLO** | 56 errores, del 04-ago al 03-sep, dos por día, todos los días |
| 13 | Duplicati: última copia válida | `SELECT Timestamp FROM Fileset ORDER BY Timestamp DESC` | **FALLO** | **2026-05-09** — hace casi 4 meses |
| 14 | Duplicati: va cifrada | `SELECT Name,Value FROM Option WHERE BackupID=1` | **OK** | `encryption-module=aes`, `passphrase` de 439 bytes |
| 15 | **Restauración real de un fichero** | `tar xzf ...tar.gz -C /tmp/audit-restore <f>` + `md5sum` | **OK** | `appointments.json` y `config.json`: md5 **idénticos** al original |
| 16 | Los datos de clientas entran en la copia | `tar tzf ... \| grep "^nexux-clients/clients/"` | **OK** | 306 entradas, 21 clientes |
| 17 | Las copias van cifradas | `file /mnt/data/backup/nexux/nexux-*.tar.gz` | **FALLO** | "gzip compressed data" — tar.gz plano, sin cifrar |
| 18 | Existen `/var/log/syslog*` o `/var/log/cron*` | `ls -la /var/log/syslog* /var/log/cron*` | **FALLO (confirmado)** | "No such file or directory"; `rsyslog` no está instalado |
| 19 | El journal registra los crons | `journalctl -u cron --since "-24h"` | **OK** | Muestra cada CMD con su hora, hasta las 20:50 |
| 20 | El journal sobrevive a un reinicio | `journalctl --list-boots` + `ls /var/log/journal` | **FALLO** | 1 solo arranque; `/var/log/journal` vacío; journal en `/run` (RAM) |
| 21 | Causa del journal volátil | `cat /usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` | — | `Storage=volatile` (fichero de fábrica de Raspberry Pi OS) |
| 22 | Todos los crons corrieron hoy | mtime de los 17 logs de cron | **OK (15/17)** | 2 semanales sin log porque `/tmp` es tmpfs y se borró en el reinicio |
| 23 | Uptime Kuma vigila `pi.nexux.pro` | `SELECT id,name,url,active FROM monitor` (kuma.db) | **FALLO** | 5 monitores, **ninguno** apunta a nexux.pro |
| 24 | El endpoint de salud responde | `curl -w "%{http_code}" https://pi.nexux.pro/health` | **OK** | HTTP 200 en 0,119 s -> `{"ok":true}` |
| 25 | Kuma sigue latiendo y tiene avisos | `SELECT MAX(time)... FROM heartbeat` + tabla notification | **OK** | Latidos de las 18:59 UTC (=20:59 CEST); 2 avisos activos, 10 enlaces |
| 26 | El canal de Telegram funciona hoy | `curl .../getMe` y `.../sendMessage` al chat 511455969 | **OK** | HTTP 200, ok:true, message_id 2102, entregado a "Richy" |
| 27 | El vigilante de WhatsApp cubre a todos | lectura del código + `estado-whatsapp.json` | **FALLO** | Vigila **1 de 21** clientes; salta `auth/` vacía y trata la API caída como "no comprobable" |
| 28 | El watchdog de Docker funciona | `cat ~/logs/docker-stack-watchdog.log` | **OK** | Detectó y registró las dos caídas del disco; auto-reparó Umami hoy |
| 29 | PM2 tiene la lista guardada | `ls -la ~/.pm2/dump.pm2` + contenido | **OK** | 73.949 bytes, 3-sep 16:01, 17 procesos con su estado |
| 30 | El servicio de arranque de PM2 | `systemctl is-enabled/is-active pm2-nexux` | **OK** | enabled + active desde 2026-09-03 03:39, `ExecStart=pm2 resurrect` |
| 31 | Docker arranca solo | `systemctl is-enabled docker` | **OK** | enabled + active; los 8 contenedores "Up 17 hours" |
| 32 | El túnel de Cloudflare arranca solo | `systemctl is-enabled cloudflared` + `ps aux` | **OK con matiz** | No es servicio de systemd (`not-found`); lo levanta PM2. Funciona. |
| 33 | Ninguna unidad falló en el arranque | `systemctl --failed` | **OK** | "0 loaded units listed" |
| 34 | Temperatura y limitación térmica | `vcgencmd measure_temp` / `get_throttled` | **FALLO** | 77,9 °C; `0xe0000` = ya ha habido limitación por calor en este arranque |
| 35 | Disco, inodos, RAM, swap | `df -h`, `df -i`, `free -h` | **OK con aviso** | Raíz al 80% (23 GB libres); swap al 65%; inodos 22% |
| 36 | Rotación de logs de Nexux/PM2 | `grep -rl -iE "pm2\|nexux" /etc/logrotate.d/` | **FALLO** | Sin regla; 122 MB en `.pm2/logs` + un `autopilot.log` de 73 MB |
| 37 | Por qué el autopilot está parado | `categories.json` + `index.js` + log de arranques | **OK (diagnosticado)** | 0 de 4 categorías activas -> sale con código 0 -> PM2 relanza; 10.300/día desde el 28-ago |
| 38 | Si el autopilot volverá solo | `dump.pm2` | **OK** | Guardado como `stopped`: no volverá tras un reinicio |
| 39 | Los volúmenes de Docker entran en alguna copia | `docker info` + excludes del rsync | **FALLO** | Docker en `/mnt/data/docker`; el rsync excluye `/mnt/*` |
| 40 | Código respaldado en GitHub | `git -C ... rev-list --count @{u}..HEAD` | **FALLO parcial** | nexux-clients: 3 commits sin subir + 14 ficheros sin commitear |


## H.11 — Verificación profunda de los ficheros del disco D: (resultado tardío)

Además del `gzip -t`, listé el archivo entero para saber si el TAR (no sólo el gzip) está completo:
```
$ cd D:\nexux-backup-pi
$ gzip -t pi-sistema-20260824.tar.gz   ->  GZIP VALIDO
$ gzip -t pi-sistema-20260831.tar.gz   ->  gzip: unexpected end of file  -> TRUNCADO

$ tar tzf pi-sistema-20260824.tar.gz | wc -l
1296576            (y cero errores de tar)
```
Comparado con la copia origen en la Pi (1.428.765 ficheros, medidos el 30-ago), son el 90,7%,
diferencia compatible con lo que creció el sistema entre el 24 y el 30 de agosto.

**Conclusión que corrige el parte de estado:** `pi-sistema-20260824.tar.gz` (23,34 GB) **SÍ es
una copia del sistema completa y utilizable**, aunque el script la marcó como FALLO. El motivo
del falso negativo es que el script aborta con `if ($LASTEXITCODE -ne 0) { throw }`, y `tar`
devuelve código 2 por errores no fatales de lectura (ficheros de `/var/lib` y similares que
cambian o no se pueden leer) aunque haya escrito el archivo entero.

Así que hay **una** copia del sistema fuera de la Pi, con fecha del 24 de agosto. Y aquí está
el problema urgente:

### 🔴 H.11.1 · La rotación va a BORRAR la única copia de sistema buena que hay fuera de la Pi
```powershell
# backup-sistema-pi-a-D.ps1
$Conservar = 2      # cuantas copias del sistema se guardan
...
Get-ChildItem $Destino -Filter 'pi-sistema-*.tar.gz' |
    Sort-Object LastWriteTime -Descending | Select-Object -Skip $Conservar | Remove-Item -Force
```
Hoy en D: hay dos: la del **24-ago (buena)** y la del **31-ago (truncada)**. El próximo lunes
**7 de septiembre** la tarea generará una tercera y la rotación borrará la más antigua — que es
justo la única que sirve. La copia rota es más reciente, así que sobrevive.

**Acción inmediata, antes del lunes:** renombrar `pi-sistema-20260824.tar.gz` a algo que no
case con el patrón `pi-sistema-*.tar.gz` (por ejemplo `GUARDAR-pi-sistema-20260824.tar.gz`), y
borrar a mano la del 31-ago, que es basura. Son 2 minutos y evitan quedarse sin ninguna.
*(No lo he hecho: modificar copias de seguridad estaba fuera del alcance de esta auditoría.)*

---

# HALLAZGOS POR SEVERIDAD

## BLOQUEANTE

### H-B1 · No existe NINGUNA copia de los datos de clientas fuera de la casa
- **Síntoma:** Duplicati, la única capa con destino externo (Google Drive), lleva desde el **9 de mayo de 2026** sin subir nada. Las otras cuatro capas viven todas en la misma casa: el disco USB pinchado en la Pi y el PC de Windows a un metro.
- **Causa:** el trabajo apunta a `/source/Backend` (= `/home/nexux/Backend`), una carpeta que ya no existe. Duplicati aborta sin escribir nada y sin avisar a nadie.
- **Cómo reproducirlo:** `ls -ld /home/nexux/Backend` -> "No such file or directory". Y en su base de datos: `SELECT COUNT(*),MIN(Timestamp),MAX(Timestamp) FROM ErrorLog` -> 56 errores, del 4-ago al 3-sep; `SELECT Timestamp FROM Fileset ORDER BY Timestamp DESC LIMIT 1` -> 2026-05-09.
- **Impacto:** un incendio, una inundación o un robo se lleva a la vez la Pi, su disco USB y el PC de Windows. Con clientes de pago dentro, eso es pérdida total de las agendas y del historial de conversaciones, sin vuelta atrás. Con el RGPD por medio, además, es un incidente de disponibilidad notificable.
- **Propuesta:** cambiar el origen del trabajo de Duplicati a `/source/nexux-clients/clients`, `/source/nexus-brain`, `/source/nexux-pro` y `/source/.env`; comprobar que el token de Google Drive sigue vivo (es de mayo); lanzarlo a mano y verificar que sube de verdad; activar la notificación de fallo. Y guardar la passphrase de cifrado FUERA de la Pi: hoy sólo existe dentro de un volumen de Docker que vive en el disco que se cae.
- **Esfuerzo:** 30-45 min (15 de configuración más la primera subida).

### H-B2 · El disco USB es un punto único de fallo del que cuelga TODO, y ya ha fallado dos veces
- **Síntoma:** del 22 al 26 de julio (4 días) y del 24 al 28 de agosto (3 días y 14 h) el disco USB desapareció. En ambos casos se cayeron a la vez las copias 1 y 2, los ocho contenedores (incluido Uptime Kuma, que era el que debía avisar) y los datos de Docker.
- **Causa:** `docker.service` declara `RequiresMountsFor=/mnt/data` (verificado con `systemctl show docker`), el data-root de Docker es `/mnt/data/docker`, y el destino de las copias es `/mnt/data/backup`. Todo cuelga del mismo cable USB.
- **Cómo reproducirlo:** `grep -c "disco ausente" ~/logs/docker-stack-watchdog.log` -> 1039. Primera línea: `2026-08-24 18:40:02 FALLO hardware: disco ausente. prev=OK`.
- **Impacto:** casi 8 días de este verano sin ninguna copia de seguridad y sin monitorización, y nadie lo detectó hasta que se miró a mano. Si vuelve a pasar durante el lanzamiento, Nexux se queda a ciegas y sin red en el peor momento.
- **Propuesta:** (a) la causa física primero — cambiar el cable USB y alimentar el disco por fuente externa, que es la causa típica de estas desconexiones en Raspberry Pi; (b) que el destino de las copias no sea el mismo disco que aloja Docker; (c) resolver H-B1, que es lo que rompe la dependencia de una sola casa.
- **Esfuerzo:** (a) 20 min y un cable · (b) 1 h · (c) ver H-B1.

## ALTA

### H-A1 · Los datos personales de las clientas se copian SIN CIFRAR
- **Síntoma:** `file nexux-20260903-0400.tar.gz` -> "gzip compressed data". Dentro van `appointments.json` y `conversations.json` de 21 clientes (nombres, teléfonos, citas), el `.env` con las claves de producción y las carpetas `auth/` de WhatsApp. Ese mismo fichero sin cifrar se copia cada día a `C:\Users\Nexux\backups\nexux-pi\`.
- **Causa:** el script comprime con `tar czf` y protege sólo con `chmod 600`, un permiso que no viaja con el fichero. No hay `gpg`, `openssl enc` ni `age` en ninguna parte de los scripts.
- **Cómo reproducirlo:** `tar tzf ...tar.gz | grep -c "^nexux-clients/clients/"` -> 306 entradas.
- **Impacto:** RGPD art. 32. Nexux es encargado del tratamiento de datos de personas que ni siquiera son clientes suyos, sino clientas de las peluquerías. Un portátil o un disco perdido es una brecha notificable.
- **Propuesta:** canalizar el `tar` por `gpg --symmetric --cipher-algo AES256` con la clave guardada fuera de la Pi, y mover la prueba de restauración del script a DESPUÉS de descifrar; si no, deja de probar nada.
- **Esfuerzo:** 30 min.

### H-A2 · La copia semanal del sistema a D: se corta a mitad, y la rotación va a borrar la única buena
- **Síntoma:** dos ficheros en `D:\nexux-backup-pi`: el del 24-ago (23,34 GB, verificado completo: 1.296.576 ficheros listados sin errores) y el del 31-ago (7,47 GB, truncado). El parte de estado dice FALLO y es del 24-ago.
- **Causa del corte:** la tarea corre como `LogonType=Interactive` y la transferencia dura 40-60 min; si la sesión de Windows se cierra o el equipo suspende, el proceso muere. *(Esta razón concreta es hipótesis; el corte en sí está probado.)*
- **Causa del falso "FALLO" del 24-ago:** el script hace `if ($LASTEXITCODE -ne 0) { throw }` y `tar` devuelve código 2 por errores no fatales de lectura, aunque el archivo se haya escrito entero.
- **Cómo reproducirlo:** `Get-ScheduledTaskInfo Nexux-BackupSistema-PiADisco` -> resultado 3221225786 (0xC000013A = proceso terminado). `gzip -t pi-sistema-20260831.tar.gz` -> "unexpected end of file".
- **Impacto y urgencia:** el script guarda `$Conservar = 2` copias. El lunes 7 de septiembre creará una tercera y la rotación borrará la más antigua, que es justo la única utilizable; la rota, por ser más reciente, sobrevive.
- **Propuesta:** ANTES DEL LUNES, renombrar `pi-sistema-20260824.tar.gz` fuera del patrón (p. ej. `GUARDAR-pi-sistema-20260824.tar.gz`) y borrar la del 31-ago. Después: pasar la tarea a `ServiceAccount` con "ejecutar aunque el usuario no haya iniciado sesión", desactivar la suspensión durante la copia, tolerar el código 2 de `tar` y avisar por Telegram cuando el parte diga FALLO.
- **Esfuerzo:** 2 min lo urgente · 45 min el arreglo.

### H-A3 · Nadie se entera de que una copia no se ha hecho
- **Síntoma:** cuatro días sin copia (25-28 ago), Duplicati fallando cuatro meses y la copia a D: rota desde el principio. Ninguno de los tres generó un aviso.
- **Causa:** los partes (`estado.txt`, `estado-sistema-windows.txt`) sólo se escriben si el script llega a ejecutarse, y hay que ir a mirarlos. Cuando el disco no está, el script muere en la primera redirección al log y el cron tira el error a la basura (`>/dev/null 2>&1`).
- **Impacto:** el sistema de copias sólo avisa cuando funciona. El silencio se lee como "todo bien" y significa justo lo contrario.
- **Propuesta:** un vigilante independiente (cron diario a las 09:00, en la SD, sin Docker) que mire LA EDAD del fichero de copia más reciente y avise por Telegram si pasa de 26 horas. Es la comprobación que ninguna de las cinco piezas hace hoy.
- **Esfuerzo:** 1 h.

### H-A4 · No hay ninguna alarma si `pi.nexux.pro` se cae
- **Síntoma:** Uptime Kuma tiene 5 monitores y ninguno apunta al producto que se va a lanzar.
- **Cómo reproducirlo:** `SELECT id,name,url FROM monitor` sobre `kuma.db` -> Railway, Grafana, N8N, Open WebUI, Portainer. El endpoint existe y responde: `curl https://pi.nexux.pro/health` -> HTTP 200.
- **Impacto:** si el API se cae de madrugada, nadie lo sabrá hasta que una clienta se queje.
- **Propuesta:** dar de alta el monitor sobre `https://pi.nexux.pro/health` con el aviso "Telegram Directo" que ya existe. Arreglar o retirar el monitor de "Open WebUI", que lleva un rojo permanente y enseña a ignorar el panel. Y montar un monitor EXTERNO gratuito (UptimeRobot o similar): hoy todo lo que vigila la Pi vive dentro de la Pi.
- **Esfuerzo:** 15 min los dos monitores.

### H-A5 · El vigilante de WhatsApp está escrito para ignorar los dos fallos que más importan
- **Síntoma:** vigila 1 cliente de 21.
- **Causa (leída en el código, no supuesta):** `if not (os.path.isdir(auth_dir) and os.listdir(auth_dir)): continue` salta a todo cliente con la carpeta `auth/` vacía, que es exactamente el síntoma del fallo conocido de sesiones de WhatsApp. Y `if ok is None: continue` hace que la caída completa del API no cuente como caída.
- **Cómo reproducirlo:** `cat nexus-brain/estado-whatsapp.json` -> `vigilados: 1`. Contando ficheros: 20 de los 21 clientes tienen `auth/` vacía.
- **Impacto:** cuando entre un cliente de pago cuya vinculación falle, quedará fuera del radar. Y si `nexux-clients` muere entero, este vigilante no dirá nada.
- **Propuesta:** separar "el API no responde" (avisar siempre, mirando su `/health`) de "este cliente concreto da error"; y avisar de los clientes con `auth/` vacía más de X horas en lugar de saltárselos.
- **Esfuerzo:** 20 min.

### H-A6 · Los logs del sistema se borran en cada reinicio: cero capacidad forense
- **Síntoma:** `journalctl --list-boots` sólo muestra el arranque de hoy. No se puede saber por qué se reinició la Pi a las 03:34 de esta madrugada.
- **Causa:** `/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` contiene `Storage=volatile`; es un fichero de fábrica de Raspberry Pi OS. Y `rsyslog` no está instalado, de ahí que tampoco existan `/var/log/syslog*` ni `/var/log/cron*`.
- **Impacto:** ante cualquier incidente con un cliente, no hay registro que consultar si por medio hubo un reinicio.
- **Propuesta:**
```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nStorage=persistent\nSystemMaxUse=300M\nMaxRetentionSec=1month\n' \
  | sudo tee /etc/systemd/journald.conf.d/50-nexux-persistent.conf
sudo systemctl restart systemd-journald
```
- **Esfuerzo:** 5 min.

### H-A7 · Los volúmenes de Docker no entran en ninguna copia
- **Síntoma:** n8n, Grafana, Uptime Kuma y la configuración de Duplicati se perderían con el disco.
- **Causa:** `data-root: /mnt/data/docker` y el rsync del sistema excluye `/mnt/*`.
- **Impacto:** además de perder flujos y paneles, se pierde la passphrase de Duplicati, y con ella la capacidad de leer las copias antiguas que hay en Drive.
- **Propuesta:** añadir al backup diario un volcado de los volúmenes pequeños (`uptime_kuma_data`, `duplicati_data`, n8n): son megas, no gigas. Y guardar la passphrase de Duplicati en un gestor de contraseñas fuera de la Pi.
- **Esfuerzo:** 45 min.

## MEDIA

### H-M1 · La Pi ya se ha frenado por calor en este arranque
`vcgencmd measure_temp` -> 77,9 grados. `get_throttled` -> `0xe0000`, que descodificado significa que en las últimas 17 h ha habido limitación de frecuencia, limitación por calor y superación del límite blando de temperatura. No hay bajo voltaje: es disipación. Cuando ocurre, todo va más lento: la web, el bot y las respuestas a las clientas. **Propuesta:** ventilación o disipador, y mover el rsync semanal de 30 min a una hora fresca. **Esfuerzo:** 20 min más el hardware.

### H-M2 · `nexux-blog-autopilot`: 5.307 reinicios que PM2 estaba configurado para no ver
Parado a mano hoy a las 16:01; no volverá tras un reinicio de la Pi porque el `dump.pm2` lo guarda como `stopped`. Con las 4 categorías desactivadas el proceso sale con código 0 y PM2 lo relanza cada 8,4 segundos: unos 10.300 al día desde el 28-ago, 64.441 arranques en el log. `max_restarts: 10` nunca llegó a aplicarse porque el proceso vive más que `min_uptime` (1 segundo por defecto) y PM2 lo contaba como reinicio sano. **Propuesta:** que `index.js` no salga si no hay categorías activas, y poner `min_uptime: "60s"`. **Esfuerzo:** 30 min. *(No afecta a nexux.pro; es un proceso vecino.)*

### H-M3 · Logs sin rotación
122 MB en `.pm2/logs` (41 MB de ellos de un proceso que ya ni existe), un `autopilot.log` de 73 MB, y ninguna regla de logrotate para nexux ni para PM2, con la SD al 80%. **Propuesta:** `pm2 install pm2-logrotate` con `max_size 10M` y `retain 7`, más una regla de logrotate para `/home/nexux/logs`. **Esfuerzo:** 15 min.

### H-M4 · Los logs de cron viven en `/tmp`, que es memoria RAM
`findmnt /tmp` -> tmpfs. Esos logs desaparecen en cada reinicio (por eso no puedo verificar los dos crons de los viernes) y ocupan 208 MB de RAM en una máquina con la swap al 65%. **Propuesta:** moverlos a `/home/nexux/logs/`. **Esfuerzo:** 10 min.

### H-M5 · Código de hoy sin respaldo en ningún sitio
`nexux-clients`: 3 commits sin subir a GitHub (entre ellos parches de seguridad de hoy) y 14 ficheros sin commitear. El código de ese repo no entra en la copia diaria, y la copia del sistema es del 30-ago. **Propuesta:** decisión de Ricardo; hacer `push` estaba fuera del alcance de esta auditoría. **Esfuerzo:** 5 min.

## BAJA

- **H-Bj1 · El bind de Duplicati `/home/nexux -> /source` está en lectura-escritura.** Debería ser `:ro`: un contenedor de copias no necesita escribir en el home, y ese home contiene `.ssh`. 5 min.
- **H-Bj2 · El token del túnel de Cloudflare va en la línea de comandos**, visible con un simple `ps aux` para cualquier usuario de la Pi. Debería ir en un fichero de credenciales. 15 min.
- **H-Bj3 · El puerto 8200 de Duplicati escucha en 0.0.0.0**, accesible desde toda la red local; desde esa consola se gestionan copias y claves. Limitarlo a 127.0.0.1. 10 min.
- **H-Bj4 · El volumen de destino de Duplicati es anónimo** (nombre de 64 hexadecimales) y está vacío: un `docker volume prune` lo borraría sin avisar. Darle nombre. 5 min.
- **H-Bj5 · `kuma.db` pesa 173 MB** con 1.127.419 latidos y crece sin poda. Configurar la retención. 5 min.
- **H-Bj6 · El monitor "Open WebUI" lleva un rojo permanente.** Una alerta que siempre suena deja de ser una alerta. 10 min.

---

# NO VERIFICADO (y por qué)

| Qué | Por qué no he podido verificarlo |
|---|---|
| Si los crons de los viernes (`informe_viernes.py`, `cuadro-ventas-semanal.py`) se ejecutaron el 29-ago | Sus logs están en `/tmp`, que es tmpfs, y la Pi se reinició hoy a las 03:34: el registro se borró. El journal tampoco lo tiene por ser volátil. |
| Por qué se reinició la Pi hoy a las 03:34 | Misma causa: `Storage=volatile` borró el journal del arranque anterior. `wtmp` sólo conserva el arranque actual y `last` no está instalado. |
| Si las copias de Duplicati que hay en Google Drive (abril-mayo) siguen ahí y son legibles | El `TargetURL` está cifrado en la configuración (`enc-v1:...`) y descifrarlo exige la clave del servidor. Habría que entrar a la consola de Duplicati o a la cuenta de Drive, cosa que no he hecho para no tocar credenciales. |
| Si el token de Google Drive de Duplicati sigue siendo válido | No he lanzado el trabajo: hacerlo habría modificado el estado de las copias. Se sabrá al arreglar H-B1. |
| Si la copia del sistema en la Pi (`/mnt/data/backup/sistema`, rsync, 89 GB) restaura una máquina arrancable | Verificarlo de verdad exige otra tarjeta SD y otra Pi. Sí he verificado que existe, su fecha (30-ago), su tamaño y que el único aviso de rsync es el benigno código 24. |
| El cifrado o no de la capa 4 en el disco D: más allá de estos dos ficheros | Sólo hay esos dos ficheros; ambos son `.tar.gz` planos, sin cifrar, igual que el resto. Verificado por extensión y por `gzip -t`, no por inspección de un contenedor cifrado (no lo hay). |
| Si los avisos de Uptime Kuma llegan de verdad a Telegram | Verifiqué que el canal de Telegram funciona hoy (mensaje entregado) y que Kuma tiene 2 notificaciones activas con 10 enlaces a monitores, pero no he forzado una caída para ver el aviso salir de Kuma. |
| El estado de la sesión de Windows durante la copia del lunes (hipótesis de H-A2) | No hay registro de eventos consultado del lado de Windows para confirmar la suspensión o el cierre de sesión. El corte está probado; su causa concreta, no. |
