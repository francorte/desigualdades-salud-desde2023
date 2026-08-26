# Informe de validación y valores perdidos

**Generado:** 2026-08-26T12:25:44.007106+00:00  
**Tabla analítica:** `data/processed/esde2023_adultos_analitica.csv.gz`  
**Dimensión:** 21.032 filas × 62 columnas  

## Resultado ejecutivo

- Controles críticos superados: 35.
- Controles críticos fallidos: 0.
- Coincidencias en la unión adulto-hogar: 21.032 de 21.032.
- La tabla conserva las 21.032 filas adultas; las exclusiones se aplican solo al construir cada muestra de análisis.
- Los originales y las variables derivadas conviven en la tabla para facilitar auditoría.

## Variables con mayor ausencia

| Variable | n ausente | % no ponderado | % ponderado |
|---|---:|---:|---:|
| `NIVEST` | 1.532 | 7.28% | 5.56% |
| `INGRESOS` | 1.002 | 4.76% | 4.01% |
| `IMC` | 997 | 4.74% | 4.67% |
| `CLASE_PR` | 806 | 3.83% | 3.69% |
| `CUADROS_DEPRESIVOS` | 699 | 3.32% | 3.16% |
| `SEVERIDAD_DEPRESIVA` | 699 | 3.32% | 3.16% |
| `S3` | 560 | 2.66% | 2.67% |
| `O1` | 343 | 1.63% | 1.55% |
| `O7` | 302 | 1.44% | 1.50% |
| `S1` | 287 | 1.36% | 1.49% |

Los porcentajes ponderados utilizan `FACTORADULTO`. Los códigos especiales se contabilizan como ausencia analítica; `O1 = 5` permanece como categoría estructural no aplicable.

## Muestras completas previstas

| Exposición | Registros finales | Exclusiones |
|---|---:|---:|
| educacion | 19.500 | 1.532 |
| clase_social | 20.226 | 806 |
| ingresos | 20.030 | 1.002 |
| situacion_laboral | 21.032 | 0 |

Estas cifras corresponden al resultado primario y a las covariables preespecificadas. Pueden cambiar en modelos que incorporen actividad física o apoyo social.

## Archivos de auditoría

- `reports/validacion_controles.csv`: resultado de cada control.
- `reports/valores_perdidos.csv`: ausencia no ponderada y ponderada.
- `reports/registro_exclusiones.csv`: flujo de exclusiones por exposición.
- `data/processed/esde2023_adultos_analitica.metadata.json`: fuentes, huellas y dimensión.

## Interpretación

El proceso de limpieza es reproducible y no altera los archivos oficiales. La ausencia más importante se concentra previsiblemente en educación, ingresos, IMC, clase social y variables de depresión. No se ha realizado imputación. Antes de modelizar se comparará el perfil de las personas incluidas y excluidas.
