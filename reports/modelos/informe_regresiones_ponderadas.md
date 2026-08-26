# Contrastes ajustados y regresiones ponderadas

**Resultado:** salud autopercibida regular, mala o muy mala.  
**Modelo principal:** regresión logística ponderada, estandarización marginal y bootstrap estratificado aproximado.  
**Advertencia:** los IC no incorporan la sección censal y no equivalen a los errores oficiales.

## Especificación

- M0: exposición sin ajuste.
- M1: edad (término lineal y cuadrático) y sexo.
- M2 principal: M1 + país de nacimiento + comunidad autónoma.
- M3: M2 + actividad física en tiempo libre.
- M4: M3 + tres indicadores de apoyo social.
- Cada exposición se ajusta en un modelo separado.
- La atenuación M0–M4 se calcula sobre una muestra común por exposición.

## Resultados principales M2

| Exposición | Categoría | n | Prevalencia ajustada (IC95%) | Diferencia vs referencia, pp (IC95%) | Razón vs referencia (IC95%) |
|---|---|---:|---:|---:|---:|
| educacion | alto | 19.500 | 21.3% (19.8%, 22.8%) | Referencia | Referencia |
| educacion | medio | 19.500 | 27.3% (25.9%, 28.6%) | 6.0 (3.9, 7.8) | 1.28 (1.17, 1.38) |
| educacion | bajo | 19.500 | 31.0% (29.8%, 32.2%) | 9.7 (7.8, 11.7) | 1.46 (1.35, 1.58) |
| clase_social | 1 | 20.226 | 21.5% (19.6%, 23.5%) | Referencia | Referencia |
| clase_social | 2 | 20.226 | 24.9% (22.2%, 27.9%) | 3.4 (0.0, 6.9) | 1.16 (1.00, 1.33) |
| clase_social | 3 | 20.226 | 27.0% (25.2%, 28.8%) | 5.5 (2.7, 7.8) | 1.25 (1.12, 1.39) |
| clase_social | 4 | 20.226 | 30.6% (28.6%, 32.7%) | 9.0 (6.3, 11.9) | 1.42 (1.27, 1.60) |
| clase_social | 5 | 20.226 | 31.3% (29.9%, 32.7%) | 9.7 (7.4, 12.0) | 1.45 (1.32, 1.60) |
| clase_social | 6 | 20.226 | 33.7% (31.7%, 35.9%) | 12.2 (9.6, 14.9) | 1.57 (1.41, 1.74) |
| ingresos | 5 | 20.030 | 24.7% (23.3%, 26.3%) | Referencia | Referencia |
| ingresos | 4 | 20.030 | 30.2% (28.8%, 31.6%) | 5.5 (3.5, 7.5) | 1.22 (1.13, 1.32) |
| ingresos | 3 | 20.030 | 32.1% (30.3%, 34.0%) | 7.4 (5.1, 9.6) | 1.30 (1.20, 1.41) |
| ingresos | 2 | 20.030 | 29.9% (28.3%, 31.7%) | 5.2 (2.8, 7.6) | 1.21 (1.11, 1.32) |
| ingresos | 1 | 20.030 | 34.3% (32.2%, 36.5%) | 9.6 (6.9, 12.3) | 1.39 (1.27, 1.51) |

## Atenuación en muestra común

| Exposición | Modelo | n | Diferencia extremos, pp | Razón extremos |
|---|---|---:|---:|---:|
| educacion | M0_bruto | 18.640 | 14.3 | 1.71 |
| educacion | M1_edad_sexo | 18.640 | 9.6 | 1.45 |
| educacion | M2_principal | 18.640 | 9.6 | 1.45 |
| educacion | M3_actividad | 18.640 | 6.7 | 1.29 |
| educacion | M4_apoyo | 18.640 | 7.1 | 1.32 |
| clase_social | M0_bruto | 19.360 | 14.6 | 1.74 |
| clase_social | M1_edad_sexo | 19.360 | 11.9 | 1.56 |
| clase_social | M2_principal | 19.360 | 12.0 | 1.56 |
| clase_social | M3_actividad | 19.360 | 8.7 | 1.38 |
| clase_social | M4_apoyo | 19.360 | 8.9 | 1.39 |
| ingresos | M0_bruto | 19.165 | 11.4 | 1.50 |
| ingresos | M1_edad_sexo | 19.165 | 8.3 | 1.34 |
| ingresos | M2_principal | 19.165 | 9.0 | 1.36 |
| ingresos | M3_actividad | 19.165 | 6.9 | 1.27 |
| ingresos | M4_apoyo | 19.165 | 5.7 | 1.22 |

## Interpretación

Los resultados M2 son asociaciones ajustadas, no efectos causales. La estandarización traduce los modelos a prevalencias comparables y evita depender exclusivamente de odds ratios. Los cambios entre M2, M3 y M4 son compatibles con atenuación por actividad física o apoyo social, pero no demuestran mediación.

## Diagnóstico

- Ajustes puntuales: 30.
- Ajustes puntuales sin convergencia: 0.
- Réplicas bootstrap M2 válidas para clase_social: 1000 de 1000.
- Réplicas bootstrap M2 válidas para educacion: 1000 de 1000.
- Réplicas bootstrap M2 válidas para ingresos: 1000 de 1000.
