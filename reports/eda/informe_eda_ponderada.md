# EDA ponderada y diagnóstico de ausencia

**Estado:** análisis descriptivo; no incluye todavía contrastes confirmatorios ni modelos ajustados.  
**Ponderación:** `FACTORADULTO`.  
**Resultado:** `salud_menos_que_buena` (`C1` = 3–5).

## Resumen general

- salud menos que buena: 29.1%.
- problema cronico: 57.7%.
- limitacion salud: 27.3%.
- fumador actual: 19.3%.
- ocio sedentario: 30.5%.
- cuadro depresivo bin: 14.6%.
- edad media: 49.4.
- bienestar medio: 73.3.

## Gradiente por educación

| Categoría | n | Distribución ponderada | Salud menos que buena |
|---|---:|---:|---:|
| Bajo | 8.394 | 40.4% | 34.6% |
| Medio | 6.409 | 34.6% | 24.2% |
| Alto | 4.697 | 25.1% | 20.1% |

## Gradiente por clase social

| Categoría | n | Distribución ponderada | Salud menos que buena |
|---|---:|---:|---:|
| 1 | 2.558 | 14.0% | 19.7% |
| 2 | 1.485 | 7.4% | 24.4% |
| 3 | 4.128 | 20.1% | 27.1% |
| 4 | 2.620 | 12.9% | 32.1% |
| 5 | 6.630 | 32.0% | 31.4% |
| 6 | 2.805 | 13.6% | 34.4% |

## Gradiente por ingresos

| Categoría | n | Distribución ponderada | Salud menos que buena |
|---|---:|---:|---:|
| 1 | 3.188 | 11.2% | 34.9% |
| 2 | 3.675 | 13.9% | 31.5% |
| 3 | 3.442 | 15.8% | 33.8% |
| 4 | 5.457 | 29.2% | 30.2% |
| 5 | 4.268 | 30.0% | 23.0% |

## Distribución por sexo

| Categoría | n | Distribución ponderada | Salud menos que buena |
|---|---:|---:|---:|
| hombre | 9.680 | 48.6% | 24.5% |
| mujer | 11.352 | 51.4% | 33.4% |

## Distribución por edad

| Categoría | n | Distribución ponderada | Salud menos que buena |
|---|---:|---:|---:|
| 15-24 | 1.513 | 12.5% | 10.2% |
| 25-44 | 5.206 | 28.9% | 17.4% |
| 45-64 | 7.415 | 35.3% | 31.1% |
| 65+ | 6.898 | 23.3% | 50.6% |

## Diagnóstico de ausencia

| Exposición | Estado | n | Peso poblacional | Edad media | Mujeres | Nacido extranjero | Salud menos que buena |
|---|---|---:|---:|---:|---:|---:|---:|
| educacion | observado | 19.500 | 94.4% | 48.0 | 50.7% | 18.1% | 27.4% |
| educacion | ausente | 1.532 | 5.6% | 71.8 | 62.3% | 14.8% | 58.1% |
| clase_social | observado | 20.226 | 96.3% | 49.3 | 50.6% | 17.9% | 28.9% |
| clase_social | ausente | 806 | 3.7% | 49.7 | 70.7% | 16.8% | 34.6% |
| ingresos | observado | 20.030 | 96.0% | 49.5 | 51.4% | 17.3% | 29.3% |
| ingresos | ausente | 1.002 | 4.0% | 46.7 | 50.5% | 32.3% | 23.4% |

## Lectura provisional

- Los tres indicadores muestran un patrón social amplio: la salud menos que buena es más frecuente en las posiciones menos favorecidas. El descenso es claro por educación y entre los extremos de clase e ingresos, pero no es estrictamente monotónico en todas las categorías intermedias.
- Las diferencias son asociaciones brutas y pueden reflejar en gran medida la estructura de edad y otras variables de confusión.
- La ausencia no es completamente neutra: los grupos con información ausente presentan perfiles de edad, origen y salud distintos según la exposición.
- Por ello, el análisis de casos completos deberá acompañarse de una comparación explícita de incluidos y excluidos y de análisis de sensibilidad.

## Límites

Las estimaciones son descriptivas y ponderadas. No se presentan todavía intervalos de confianza porque antes debe cerrarse el método de estimación de varianza compatible con la información pública del diseño muestral. No deben interpretarse como efectos causales ni como resultados ajustados.
