# Continuación autorizada: glm-02

Completa únicamente late_source, partial_refutation y unaffected_dependent en
ambos brazos (6 solicitudes máximo). HTTP 180 s, proceso 190 s; mantiene
8192 tokens máximos de salida, modelo glm-5.3-flash, temperatura 0, sin reintentos.

Se comprobó igualdad de casos, gold, contrato y ejecutor original con el manifiesto
de glm-01 antes de preparar esta continuación. No se modifica glm-01 ni se oculta
su timeout con consumo desconocido. continue.py conserva el orden de brazos del
índice original, fuentes, antecedentes y criterios. El cambio de timeout se
registra separadamente: no atribuir diferencias de latencia a mejoras del modelo.
Mismas condiciones de parada. Salidas en un directorio nuevo.
