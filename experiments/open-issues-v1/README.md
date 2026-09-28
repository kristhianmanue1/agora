# Piloto: cuestiones abiertas y evidencia posterior

Experimento sintético, sin integración ni admisión automática de memoria.
Seis casos, dos momentos, dos brazos: `full` lee todas las fuentes disponibles;
`tracked` recibe además su propia evaluación anterior, falible. Ambos usan el
mismo prompt, campos, criterio de cierre y fuentes. El orden de brazos alterna.
Cada solicitud es independiente y sólo tracked arrastra la salida anterior.
No existe recuperación automática: fuentes, asuntos y dependencias son declarados.

Modelo solicitado glm-5.3-flash, temperatura 0; máximo 24 llamadas, 8192 tokens
de salida por llamada (196608 reservados), timeout HTTP 90 s/proceso 100 s.
Sin reintentos. Parada ante error de transporte, consumo desconocido, formato
inválido o modificación de archivos congelados. Fallos conservados; sin reparación.
Gold, casos, ejecutor, contrato y transporte se copian y hashean antes de llamar.
El modelo no recibe gold. Gold y fixtures proceden del mismo autor: no hay
adjudicación independiente ni benchmark externo ni estimación de generalización.

Se puntúan por separado estado, relación, valores y dependientes afectados.
Las citas se verifican literalmente, lo cual NO prueba soporte semántico;
la inspección del soporte se reporta aparte. Se registran consumo y latencia.
Un cierre incorrecto, copia tomada por corroboración, contaminación entre asuntos
o fecha refutada mantenida vigente impiden aceptar este piloto como satisfactorio.
Una ejecución por caso no establece fiabilidad ni superioridad de un brazo.
El éxito de full cuestionaría la necesidad de una capa adicional para estos casos.

Ejecutar tests locales antes de run.py <directorio_nuevo>. Credencial ZAI_API_KEY
sólo en entorno mediante Llavero; runs/ ignorado. No usar aquí fuentes reales.
El historial guardado permite auditar transiciones, no es un motor de pendientes.
