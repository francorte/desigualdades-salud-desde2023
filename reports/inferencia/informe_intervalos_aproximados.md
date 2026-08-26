# Intervalos de confianza aproximados

**Importante:** estos intervalos no reproducen los errores oficiales de Sanidad. El método oficial elimina secciones censales mediante jackknife; el microdato público no contiene el identificador de sección ni pesos replicados.

## Método adoptado

- Método principal exploratorio: bootstrap estratificado por `ESTRATO`, con 1.000 réplicas y remuestreo de personas dentro de cada estrato.
- Sensibilidad: intervalo Wilson usando el tamaño muestral efectivo de Kish.
- Ambos métodos incorporan la desigualdad de pesos; el bootstrap conserva el tamaño de cada estrato público.
- Ninguno incorpora la correlación dentro de secciones censales. Si esta correlación es positiva, los intervalos pueden ser demasiado estrechos.
- Los intervalos se usarán para análisis exploratorio y portfolio, no como equivalentes a la inferencia oficial del INE/MS.

## Prevalencia total

Salud regular/mala/muy mala: **29.1%**; IC95% bootstrap aproximado **28.3%–29.8%**; IC95% Kish–Wilson **28.3%–29.9%**.

## Contrastes brutos entre extremos

| Contraste | Prevalencias | Diferencia, puntos porcentuales (IC95%) | Razón de prevalencias (IC95%) |
|---|---:|---:|---:|
| educacion_bajo_vs_alto | 34.6% vs 20.1% | 14.4 (12.4, 16.3) | 1.72 (1.59, 1.85) |
| clase_6_vs_1 | 34.4% vs 19.7% | 14.7 (11.9, 17.6) | 1.75 (1.56, 1.96) |
| ingresos_1_vs_5 | 34.9% vs 23.0% | 11.9 (9.3, 14.6) | 1.52 (1.39, 1.66) |

## Decisión para las regresiones

1. Ajustar modelos ponderados con `FACTORADULTO`.
2. Presentar efectos ajustados mediante prevalencias marginales, diferencias y razones de prevalencia cuando sean estimables.
3. Calcular incertidumbre principal mediante el mismo bootstrap estratificado, reajustando el modelo en cada réplica.
4. Usar una covarianza sándwich ponderada a nivel individual como comprobación secundaria, no como corrección completa del diseño.
5. No interpretar valores p aislados; priorizar magnitud, dirección, intervalos y consistencia entre especificaciones.
6. Reetiquetar todo el bloque inferencial como aproximado hasta disponer de PSU o pesos replicados oficiales.

## Qué permitiría inferencia completa

Sería necesario obtener al menos uno de estos elementos: identificador anonimizado de sección censal, pesos jackknife/replicados o un servicio oficial que calcule errores para estimandos personalizados. Con cualquiera de ellos se sustituirá esta aproximación.
