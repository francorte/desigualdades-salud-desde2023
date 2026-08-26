# Operacionalización de variables y plan de limpieza

**Versión:** 0.1  
**Fecha:** 2026-08-26  
**Estado:** especificación previa a la creación de la tabla analítica  
**Documento anterior:** [01. Planteamiento, pregunta e hipótesis](01_planteamiento_pregunta_hipotesis.md)

## 2.1. Principios de trabajo

1. Los archivos de `data/raw/` y `data/extracted/` son inmutables.
2. Toda transformación se realizará sobre una copia analítica y será reproducible mediante código.
3. Se conservarán juntas la variable original y su versión recodificada.
4. Los códigos especiales se convertirán en valores ausentes solo en las variables analíticas, nunca en los originales.
5. Los blancos derivados de saltos del cuestionario se distinguirán de «no sabe/no contesta» siempre que el flujo lo permita.
6. Las etiquetas oficiales y las decisiones analíticas se mantendrán separadas: una agrupación creada para el proyecto no se presentará como categoría oficial.
7. Ningún registro se eliminará silenciosamente. Cada exclusión producirá un recuento verificable.

## 2.2. Fuentes y claves

### Fichero adulto

- Ruta: `data/extracted/adulto/CSV/ESdEadulto_2023.tab`.
- Dimensión verificada: 21.032 filas × 432 columnas.
- Unidad: persona adulta seleccionada.
- Identificación lógica: `IDENTHOGAR` + `NORDENa`.
- Ponderación: `FACTORADULTO`.

### Fichero de hogar

- Ruta: `data/extracted/hogar/CSV/ESdEhogar_2023.tab`.
- Dimensión verificada: 47.441 filas × 54 columnas.
- Unidad: miembro del hogar.
- Clave: `IDENTHOGAR` + `NORDEN`.
- Variables incorporadas: `A11`, `INGRESOS` y `ESTRATO`.

### Regla de unión

```text
adulto.IDENTHOGAR = hogar.IDENTHOGAR
adulto.NORDENa    = hogar.NORDEN
```

La clave compuesta del fichero de hogar es única. La unión uno-a-uno recupera `A11` e `INGRESOS` para los 21.032 adultos. Se exigirá que la unión conserve exactamente 21.032 filas.

## 2.3. Tabla analítica prevista

Nombre de trabajo: `esde2023_adultos_analitica`.

Cada fila representará a una persona adulta. La tabla contendrá:

- claves técnicas;
- variables originales seleccionadas;
- versiones recodificadas;
- indicadores de ausencia;
- variable de inclusión en cada análisis;
- ponderación muestral;
- controles automáticos de calidad.

## 2.4. Resultado primario

### Salud autopercibida

| Campo | Especificación |
|---|---|
| Variable original | `C1` |
| Etiqueta oficial | Estado de salud percibido en los últimos 12 meses |
| Códigos | 1 Muy bueno; 2 Bueno; 3 Regular; 4 Malo; 5 Muy malo |
| Ausencia observada | Ninguna |
| Variable derivada | `salud_menos_que_buena` |
| Recodificación | 0 si `C1` ∈ {1,2}; 1 si `C1` ∈ {3,4,5} |
| Papel | Resultado primario binario |

Se conservará `C1` como variable ordinal de cinco categorías para análisis de sensibilidad. La etiqueta de la variable binaria será «salud regular, mala o muy mala», no «enfermedad».

## 2.5. Exposiciones socioeconómicas

### Nivel educativo

Variable original: `NIVEST`.

Agrupación analítica primaria —no oficial—:

| Categoría analítica | Códigos `NIVEST` | Contenido |
|---|---|---|
| Bajo | 02, 03, 04, 05 | Sin alfabetización, primaria o primera etapa de secundaria |
| Medio | 06, 07, 08 | Bachillerato y formación profesional media o superior |
| Alto | 09 | Estudios universitarios o equivalentes |
| Ausente | 99 | No contesta |

El código 01 («No procede, es menor de 10 años») no debería aparecer en adultos de 15+; su presencia generaría un error de validación. En el CSV observado no aparece. Tampoco aparece el código 03, lo que no constituye un error.

Variables derivadas:

- `educacion_3`: bajo/medio/alto.
- `educacion_ordinal`: 1/2/3, solo para probar tendencia cuando la suposición sea defendible.
- `educacion_missing`: indicador de `NIVEST = 99`.

### Clase social ocupacional

Variable original: `CLASE_PR`.

- Códigos válidos: 1–6, desde las clases ocupacionales más favorecidas hasta trabajadores no cualificados según la clasificación oficial.
- Código 9: no contesta; se tratará como ausente en el análisis principal.
- Variable derivada: `clase_social_1_6`.

La clase se modelará inicialmente como categórica. El contraste lineal 1–6 se presentará únicamente como análisis de tendencia, porque la distancia entre categorías no es necesariamente uniforme.

### Ingresos mensuales netos del hogar

Variable original: `INGRESOS`, procedente del fichero de hogar actualizado.

| Código | Intervalo oficial |
|---|---|
| 01 | Menos de 1.100 euros |
| 02 | De 1.100 a menos de 1.650 euros |
| 03 | De 1.650 a menos de 2.300 euros |
| 04 | De 2.300 a menos de 3.800 euros |
| 05 | 3.800 euros o más |
| 99 | No contesta |

Variables derivadas:

- `ingresos_5`: factor ordenado de cinco intervalos.
- `ingresos_ordinal`: valores 1–5 para contraste de tendencia.
- `ingresos_missing`: indicador de código 99.

No se asignará el punto medio del intervalo ni se estimará renta continua en el análisis principal. Los ingresos no están ajustados por tamaño del hogar; por ello no se denominarán renta equivalente ni ingreso per cápita.

### Situación laboral

Variable original: `A11`, procedente del fichero de hogar.

Categorías: trabajando, desempleo, jubilación/prejubilación, estudiando, incapacidad para trabajar, labores del hogar y otros. El código 9 es no respuesta, aunque no se observa entre los adultos enlazados.

Variable derivada: `situacion_laboral`, conservando las siete categorías. Las agrupaciones adicionales —por ejemplo, activo ocupado/desempleado/inactivo— se considerarán análisis de sensibilidad y deberán preservar jubilación e incapacidad como categorías diferenciables.

## 2.6. Variables de ajuste y diseño

| Original | Variable analítica | Regla |
|---|---|---|
| `EDADa` | `edad` | Conservar 15–120; 999 → ausente. En los datos observados: 15–103, sin código 999 |
| `SEXOa` | `sexo` | 1 hombre; 2 mujer |
| `A1a` | `nacido_extranjero` | 0 España; 1 extranjero; 9 → ausente. No se observa 9 |
| `CCAA` | `ccaa` | Factor de 19 categorías oficiales |
| `FACTORADULTO` | `peso_adulto` | Numérica positiva; no recodificar ni usar como exposición |
| `ESTRATO` | `estrato_publico` | Códigos 0–6; incorporado desde hogar para aproximaciones de varianza |

Para la edad se compararán tres formas:

1. término lineal;
2. término flexible mediante spline restringido si la herramienta estadística lo permite;
3. grupos descriptivos 15–24, 25–44, 45–64 y 65+.

Los grupos se usarán para tablas y heterogeneidad, no como sustitución automática de la edad continua en modelos.

## 2.7. Posibles mecanismos y determinantes

### Actividad física

- `O1`: actividad física en la actividad principal. El código 5 («No aplicable») se conservará como categoría estructural, no como valor perdido.
- `O2`: actividad física en tiempo libre, desde sedentarismo hasta entrenamiento varias veces por semana; código 9 → ausente.
- `O7`: días por semana con deporte durante al menos 10 minutos; rango 0–7; código 9 → ausente.

Derivaciones previstas:

- `ocio_sedentario`: 1 si `O2 = 1`, 0 si `O2 = 2–4`.
- `deporte_dias`: `O7` en rango 0–7.
- `deporte_3omas_dias`: 1 si `O7 ≥ 3`, 0 si `O7 = 0–2`; análisis exploratorio.

### Tabaco

Variable original: `Q1`.

- 1: fuma a diario.
- 2: fuma, pero no a diario.
- 3: no fuma actualmente, pero fumó antes.
- 4: nunca fumó de manera habitual.
- 9: no contesta → ausente.

Se conservarán cuatro categorías en el análisis principal. La variable binaria `fumador_actual` agrupará 1–2 frente a 3–4 cuando resulte útil.

### Alcohol

- `R1`: frecuencia de consumo en los últimos 12 meses, categorías 01–09; 99 → ausente.
- `CMD1`: consumo medio diario semanal; 999 → ausente.

No se mezclará abstinencia de toda la vida (`R1 = 09`) con exconsumo (`R1 = 08`). `CMD1 = 0` es un valor válido, no ausencia. Los datos observados contienen 51 registros con `CMD1 = 999`.

No se construirá todavía una variable «consumo de riesgo». Requiere documentar previamente unidades, fórmula de la variable compuesta y límites diferenciados cuando corresponda.

### Apoyo social

- `S1`: número de personas con las que podría contar ante un problema grave.
- `S2`: interés de otras personas por lo que le ocurre.
- `S3`: facilidad para obtener ayuda vecinal.
- En las tres variables, el código 9 se tratará como ausente.

Se analizarán primero por separado. No se sumarán en un índice sin verificar que la escala resultante tenga sentido, que la dirección de los ítems esté armonizada y que exista respaldo metodológico.

## 2.8. Resultados secundarios

| Original | Resultado analítico | Ausencia especial | Regla principal |
|---|---|---|---|
| `C2` | `problema_cronico` | 9 | 1 sí; 0 si código 2 |
| `C3a` | `limitacion_salud` | 9 | 1 si grave o no grave (1–2); 0 si ninguna (3) |
| `IMC` | `imc_categoria` | 9 | Conservar 1 insuficiente, 2 normopeso, 3 sobrepeso, 4 obesidad; población 18+ |
| `INDICE_BIENESTAR` | `bienestar_0_100` | 999 | Conservar escala 0–100; en los datos observados no aparece 999 |
| `SEVERIDAD_DEPRESIVA` | `severidad_depresiva` | 9 | Factor ordinal 1–5 |
| `CUADROS_DEPRESIVOS` | `cuadro_depresivo` | 9 | Conservar tres categorías; alternativa binaria 1–2 frente a 3 |

`IMC` es una categoría derivada, no el valor continuo kg/m². `INDICE_BIENESTAR` adopta valores de 0 a 100 en incrementos observados de cuatro puntos; se comprobará su distribución antes de usar un modelo lineal.

## 2.9. Tratamiento de valores ausentes

Se distinguirán cuatro situaciones:

1. **Respuesta válida:** código incluido en el dominio sustantivo.
2. **No respuesta explícita:** 9, 99 o 999 según el diccionario.
3. **No aplicable estructural:** categoría oficial sustantiva, como `O1 = 5`.
4. **Blanco por flujo:** celda vacía porque la pregunta no correspondía según el cuestionario.

Reglas:

- Los códigos especiales no participarán como niveles sustantivos en los modelos principales.
- Antes del análisis completo se calculará porcentaje perdido no ponderado y ponderado por variable y exposición.
- Si una variable supera el 5% de ausencia se evaluará el patrón por edad, sexo, educación, ingresos y salud.
- No se realizará imputación automática.
- Una posible imputación múltiple requerirá un documento adicional con modelo de imputación, variables auxiliares y análisis de sensibilidad.
- Para educación, clase e ingresos se comparará el análisis de casos completos con un análisis que muestre explícitamente la magnitud de la no respuesta, sin interpretar «no contesta» como estrato social.

## 2.10. Controles automáticos de calidad

La creación de la tabla analítica debe detenerse si falla cualquiera de estos controles críticos:

| Control | Resultado esperado |
|---|---|
| Filas del adulto | 21.032 |
| Columnas del adulto original | 432 |
| Unicidad `IDENTHOGAR + NORDENa` | 21.032 claves únicas |
| Unión con hogar | 21.032 coincidencias, sin expansión de filas |
| Dominio `C1` | Solo 1–5 |
| Dominio `SEXOa` | Solo 1–2 |
| Dominio `CCAA` | Solo 1–19 |
| Rango de `EDADa` válido | 15–120 o código 999 |
| `FACTORADULTO` | No nulo y estrictamente positivo |
| Dominio `O7` | 0–7 o código 9 |
| Dominio de variables categóricas | Subconjunto de los códigos oficiales |
| Conservación de filas tras derivaciones | 21.032 antes de filtros analíticos |

Los controles no críticos producirán advertencias, por ejemplo categorías oficiales válidas que no aparezcan en la muestra.

## 2.11. Registro de exclusiones

Cada conjunto analítico tendrá un diagrama o tabla de flujo con:

- registros iniciales;
- exclusiones por edad cuando el resultado lo requiera;
- ausencias en el resultado;
- ausencias en la exposición;
- ausencias en covariables;
- muestra final del modelo.

Las exclusiones se calcularán de nuevo para cada exposición, porque educación, clase e ingresos no tienen el mismo patrón de no respuesta.

## 2.12. Nombres de variables derivadas

| Variable | Significado |
|---|---|
| `salud_menos_que_buena` | `C1` = 3–5 |
| `educacion_3` | Bajo, medio, alto |
| `clase_social_1_6` | Categoría oficial 1–6 |
| `ingresos_5` | Intervalo oficial 1–5 |
| `situacion_laboral` | Categorías oficiales de `A11` |
| `edad` | Edad válida en años |
| `grupo_edad_4` | 15–24, 25–44, 45–64, 65+ |
| `sexo` | Etiquetas oficiales de `SEXOa` |
| `nacido_extranjero` | Nacido fuera de España |
| `ccaa` | Comunidad autónoma |
| `peso_adulto` | Factor de elevación adulto |
| `ocio_sedentario` | `O2 = 1` |
| `fumador_actual` | `Q1` = 1–2 |
| `problema_cronico` | `C2 = 1` |
| `limitacion_salud` | `C3a = 1–2` |
| `cuadro_depresivo_bin` | `CUADROS_DEPRESIVOS = 1–2` |

## 2.13. Decisiones fijadas en esta etapa

| ID | Decisión | Estado |
|---|---|---|
| D009 | Unión uno-a-uno por `IDENTHOGAR + número de orden` | Fijada y verificada |
| D010 | Educación: bajo 02–05, medio 06–08, alto 09 | Fijada para análisis principal |
| D011 | Ingresos como factor ordinal de cinco intervalos, sin puntos medios | Fijada |
| D012 | Clase social como categórica; tendencia 1–6 solo secundaria | Fijada |
| D013 | `O1 = 5` es no aplicable estructural, no ausencia | Fijada |
| D014 | Abstinencia y exconsumo de alcohol permanecerán separados | Fijada |
| D015 | No construir índice de apoyo social sin validación previa | Fijada |
| D016 | No imputar valores ausentes en la primera tabla analítica | Fijada |

## 2.14. Siguiente paso

Implementar estas reglas en un proceso reproducible que produzca:

1. tabla analítica derivada;
2. informe de validación;
3. tabla de valores perdidos;
4. registro de exclusiones;
5. metadatos con fecha, fuentes y huellas de archivos.
