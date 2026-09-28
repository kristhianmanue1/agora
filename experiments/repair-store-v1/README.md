# Persistencia de reparaciones como derivados — experimental

Almacén separado (application_id 0x41475231, user_version 1) para derivados de
operaciones v4 rechazadas por formato. No convierte la respuesta reparada en una
respuesta original del modelo ni cambia el historial del almacén de procedencia.

capture lee operación y revisión base en un snapshot SQLite consistente y exige
cabeza externa esperada. derive reconstruye el paquete y request, verifica respuesta
completa, uso conocido, recibo de reparación exacto y enlace al original; después
valida el candidato con v4. Conserva respuesta original, recibo, request, input,
revisión base, candidato, evaluación y manifiesto de dependencias. La etiqueta es
host_format_repair y admission=not_admitted.

Store.put persiste un único registro autocontenido de forma transaccional. Mismo
ID y mismo contenido retorna el registro existente; mismo ID con distinto contenido
se rechaza. Store.get verifica hashes y reconstruye el derivado; puede exigir un
digest externo para detectar sustitución o pérdida. No hay llamadas a proveedores.

run.py BASE_FALLIDA RUTA_NUEVA crea una copia con SQLite backup, incorpora en otra
base, simula pérdida de confirmación y recupera en proceso nuevo. El proceso de
lectura sólo usa el almacén derivado, código compatible e identidad/digest externos;
no necesita reabrir la fuente. Los hashes antes/después comprueban que fuente y
copia no cambiaron durante el ensayo.

Esto es incorporación en un registro experimental de derivados, no una segunda
revisión dentro del historial original, ni aceptación en AN-KLA. No hay transacción
entre dos bases: se incorpora un snapshot capturado, no se promete que siga siendo
la cabeza actual después. No hay watcher, migración o reparación automática.

Hashes y snapshots no autentican al productor. Un caller que sustituya también el
original completo puede construir otra historia coherente; hace falta autoridad
externa para autenticación. No se ensaya pérdida de energía ni consenso distribuido.
