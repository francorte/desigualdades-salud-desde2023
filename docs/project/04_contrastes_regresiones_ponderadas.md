# Contrastes ajustados y regresiones ponderadas

**Versión:** 1.0  
**Fecha:** 2026-08-26  
**Estado:** análisis primario ajustado completado

## Modelo y estimando

Se ajustaron regresiones logísticas ponderadas para el resultado `salud_menos_que_buena`. Educación, clase social e ingresos se analizaron en modelos separados. Los coeficientes logísticos no constituyen el resultado principal: cada modelo se transformó mediante estandarización marginal a prevalencias ajustadas, diferencias de prevalencia y razones de prevalencia.

Las ponderaciones se normalizaron durante la optimización numérica, lo que no altera los coeficientes. Todos los modelos se ajustaron mediante máxima verosimilitud ponderada con un algoritmo IRLS reproducible.

## Secuencia de modelos

- M0: exposición sin ajuste.
- M1: edad y sexo.
- M2 principal: M1 + país de nacimiento + comunidad autónoma.
- M3: M2 + actividad física en tiempo libre.
- M4: M3 + apoyo social (`S1`, `S2`, `S3`).

La edad se incorporó centrada en 50 años y escalada por décadas, con términos lineal y cuadrático. La CCAA se incorporó como factor. Las categorías de referencia fueron educación alta, clase social 1 e ingresos 5.

## Muestras

- Educación, M2: 19.500 personas.
- Clase social, M2: 20.226 personas.
- Ingresos, M2: 20.030 personas.
- Muestra común M0–M4: 18.640, 19.360 y 19.165, respectivamente.

La muestra común permite interpretar la atenuación sin confundir el cambio de coeficientes con cambios en las personas incluidas.

## Resultados M2 entre extremos

### Educación baja frente a alta

- Prevalencia ajustada: 31,0% frente a 21,3%.
- Diferencia: 9,7 puntos porcentuales; IC95% aproximado 7,8–11,7.
- Razón de prevalencias: 1,46; IC95% 1,35–1,58.

### Clase social 6 frente a clase 1

- Prevalencia ajustada: 33,7% frente a 21,5%.
- Diferencia: 12,2 puntos; IC95% 9,6–14,9.
- Razón: 1,57; IC95% 1,41–1,74.

### Ingresos 1 frente a ingresos 5

- Prevalencia ajustada: 34,3% frente a 24,7%.
- Diferencia: 9,6 puntos; IC95% 6,9–12,3.
- Razón: 1,39; IC95% 1,27–1,51.

## Atenuación

El ajuste por edad y sexo explica una parte importante del contraste bruto, especialmente para educación. Sin embargo, los tres gradientes permanecen después del ajuste M2.

En muestra común, al incorporar actividad física y apoyo social:

- educación: la diferencia pasa de 9,6 puntos en M2 a 7,1 en M4;
- clase social: de 12,0 a 8,9 puntos;
- ingresos: de 9,0 a 5,7 puntos.

El patrón es compatible con que actividad física y apoyo social participen en las desigualdades observadas. No demuestra mediación causal: exposición, posibles mecanismos y resultado se observan en el mismo estudio transversal.

## Incertidumbre

Los intervalos M2 se obtuvieron reajustando cada modelo en 1.000 réplicas bootstrap estratificadas por `ESTRATO`. Todas las réplicas convergieron. Los intervalos siguen siendo aproximados porque los microdatos no identifican la sección censal.

## Controles

- 30 de 30 ajustes puntuales convergieron.
- 1.000 de 1.000 réplicas válidas para cada exposición.
- Las categorías de referencia producen diferencia 0 y razón 1.
- Las estimaciones puntuales quedan dentro de sus intervalos.
- Las prevalencias marginales se estandarizan sobre la distribución ponderada de covariables de la muestra correspondiente.

## Interpretación permitida

Los resultados muestran desigualdades socioeconómicas ajustadas en salud autopercibida. No identifican efectos causales ni permiten afirmar que actividad física o apoyo social sean mediadores demostrados.

## Archivos

- Informe: `reports/modelos/informe_regresiones_ponderadas.md`.
- Contrastes M2: `reports/modelos/contrastes_ajustados_m2.csv`.
- Atenuación: `reports/modelos/atenuacion_modelos_muestra_comun.csv`.
- Diagnóstico: `reports/modelos/diagnostico_modelos.csv`.
- Réplicas: `reports/modelos/bootstrap_m2_replicas.csv.gz`.
- Código: `scripts/regresiones_ponderadas.py`.

## Registro de decisiones

| ID | Decisión | Estado |
|---|---|---|
| D023 | Ajustar cada exposición socioeconómica en un modelo separado | Fijada |
| D024 | Usar logística ponderada y estandarización marginal | Fijada |
| D025 | Edad con términos lineal y cuadrático por décadas | Fijada |
| D026 | M2 como modelo principal | Fijada |
| D027 | Comparar M0–M4 sobre muestra común | Fijada |
| D028 | Presentar diferencias y razones de prevalencia, no solo odds ratios | Fijada |
| D029 | Interpretar M3–M4 como atenuación compatible, no mediación causal | Fijada |
