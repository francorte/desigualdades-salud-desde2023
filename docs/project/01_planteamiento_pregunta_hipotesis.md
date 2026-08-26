# Desigualdades socioeconómicas y determinantes de la salud en España

## 1. Planteamiento, pregunta, objetivos e hipótesis

**Versión:** 0.1  
**Fecha:** 2026-08-26  
**Estado:** decisiones iniciales fijadas antes del análisis de resultados  
**Fuente de datos:** Encuesta de Salud de España 2023 (ESdE 2023), Ministerio de Sanidad e Instituto Nacional de Estadística

## 1.1. Finalidad del proyecto

Este proyecto estudia la distribución social de la salud en la población residente en España mediante los microdatos anonimizados de adultos de la ESdE 2023. Se concibe como un proyecto de portfolio reproducible: cada definición, transformación y decisión analítica debe quedar documentada antes de examinar asociaciones o ajustar modelos.

El punto de partida es que la salud no se distribuye de manera uniforme. La educación, la clase social ocupacional, la situación laboral y los recursos económicos del hogar pueden asociarse con diferencias en exposición a riesgos, acceso a recursos protectores y resultados de salud. La ESdE permite estudiar conjuntamente posición socioeconómica, salud autopercibida, limitaciones, IMC, bienestar, sintomatología depresiva, actividad física, consumo de tabaco y alcohol y apoyo social.

El diseño de la encuesta es transversal. Por tanto, el proyecto estimará **desigualdades y asociaciones**, no efectos causales. Expresiones como «explica», «provoca» o «produce» se reservarán para diseños que permitan identificación causal.

## 1.2. Población y alcance

- Población objetivo: personas residentes en viviendas familiares principales de España.
- Población excluida: personas que viven en establecimientos colectivos.
- Ámbito geográfico: todo el territorio nacional.
- Unidad analítica principal: persona adulta seleccionada de 15 años o más.
- Tamaño del fichero adulto inspeccionado: 21.032 personas y 432 variables.
- Inferencia principal: población adulta no institucionalizada residente en España, aplicando `FACTORADULTO`.

La interpretación del IMC mediante categorías adultas se restringirá a personas de 18 años o más. Los análisis cuya variable dependiente no tenga esta restricción podrán conservar a la población de 15–17 años, con ajuste adecuado por edad y análisis de sensibilidad si procede.

## 1.3. Pregunta de investigación primaria

> ¿Existe un gradiente socioeconómico en la prevalencia de salud autopercibida regular, mala o muy mala entre la población adulta residente en España, y en qué medida se mantiene después de ajustar por edad, sexo, país de nacimiento y comunidad autónoma?

La formulación principal prioriza la salud autopercibida (`C1`) porque:

1. es un resultado general, interpretable y comparable;
2. está disponible para los 21.032 registros adultos;
3. permite una presentación descriptiva clara de desigualdades absolutas y relativas;
4. evita comenzar con variables derivadas cuya construcción todavía no está publicada íntegramente por Sanidad;
5. es adecuada para una primera secuencia EDA → contrastes → regresión.

## 1.4. Exposiciones socioeconómicas

Se estudiarán tres indicadores complementarios, sin combinarlos inicialmente en un índice único:

- Nivel educativo individual: `NIVEST`.
- Clase social basada en la ocupación de la persona de referencia: `CLASE_PR`.
- Intervalo de ingresos mensuales netos del hogar: `INGRESOS`, incorporado desde el fichero de hogar.

La situación laboral actual (`A11`, fichero de hogar) se considerará una exposición adicional y una variable de estratificación. No se incluirán simultáneamente todas las exposiciones socioeconómicas en el primer modelo sin comprobar antes colinealidad, distribución y significado conceptual.

## 1.5. Resultado primario

Variable original: `C1`, «Estado de salud percibido en los últimos 12 meses».

Categorías oficiales:

- 1: Muy bueno.
- 2: Bueno.
- 3: Regular.
- 4: Malo.
- 5: Muy malo.

Operacionalización principal:

- 0: salud buena o muy buena (`C1` = 1–2).
- 1: salud regular, mala o muy mala (`C1` = 3–5).

Se conservará también la variable ordinal original para análisis de sensibilidad. La elección binaria debe describirse como «salud menos que buena» o «salud regular/mala/muy mala»; no se denominará enfermedad ni mala salud clínica.

## 1.6. Covariables de ajuste preespecificadas

- Edad: `EDADa`, inicialmente continua; se comprobará no linealidad.
- Sexo registrado: `SEXOa`.
- País de nacimiento: `A1a`.
- Comunidad autónoma: `CCAA`.
- Factor de elevación: `FACTORADULTO`, utilizado como ponderación y no como predictor sustantivo.

La edad, el sexo, el país de nacimiento y la comunidad autónoma se seleccionan a priori por su relación plausible tanto con la posición socioeconómica como con la salud. Su inclusión no dependerá de significación estadística bivariada.

## 1.7. Hipótesis preespecificadas

### Hipótesis primaria

**H1.** La prevalencia ponderada de salud regular, mala o muy mala será mayor en los grupos con menor nivel educativo, menor clase social ocupacional y menor intervalo de ingresos del hogar.

**H0.** No existe asociación entre cada indicador socioeconómico y la prevalencia de salud regular, mala o muy mala.

La hipótesis se evaluará para cada exposición por separado. Se estimarán diferencias absolutas de prevalencia y medidas relativas con intervalos de confianza, además de los valores p cuando correspondan.

### Hipótesis ajustada

**H2.** El gradiente socioeconómico permanecerá después de ajustar por edad, sexo, país de nacimiento y comunidad autónoma, aunque su magnitud podrá reducirse.

### Hipótesis secundaria sobre posibles mecanismos

**H3.** La actividad física (`O1`, `O2`, `O7`) y el apoyo social (`S1`, `S2`, `S3`) atenuarán parcialmente la asociación entre posición socioeconómica y salud autopercibida cuando se incorporen secuencialmente al modelo.

Esta atenuación se interpretará como compatible con mediación, pero no como prueba de un mecanismo causal, debido al carácter transversal de los datos.

## 1.8. Objetivo general

Cuantificar y describir las desigualdades socioeconómicas en salud autopercibida entre la población adulta no institucionalizada residente en España utilizando los microdatos ponderados de la ESdE 2023.

## 1.9. Objetivos específicos

1. Describir la distribución ponderada de la salud autopercibida y de los principales indicadores socioeconómicos.
2. Estimar la prevalencia de salud regular/mala/muy mala por nivel educativo, clase social, ingresos y situación laboral.
3. Cuantificar desigualdades absolutas y relativas con intervalos de confianza.
4. Evaluar si las asociaciones persisten tras ajustar por edad, sexo, país de nacimiento y comunidad autónoma.
5. Explorar si actividad física y apoyo social atenúan las asociaciones observadas.
6. Examinar heterogeneidad por sexo y grupos de edad mediante análisis estratificados o términos de interacción predefinidos.
7. Realizar análisis secundarios con limitación crónica (`C2`), limitación de actividad (`C3a`), IMC, bienestar y sintomatología depresiva.

## 1.10. Secuencia analítica prevista

1. Validar claves, rangos, códigos especiales y saltos de cuestionario.
2. Construir una tabla analítica sin modificar los microdatos originales.
3. Aplicar recodificaciones documentadas y generar indicadores de control de calidad.
4. Describir valores perdidos y comparar su distribución entre grupos.
5. Realizar EDA ponderada sin contrastes confirmatorios prematuros.
6. Estimar prevalencias y tamaños del efecto.
7. Ajustar modelos secuenciales preespecificados.
8. Ejecutar análisis de sensibilidad.
9. Separar resultados confirmatorios de análisis exploratorios.

## 1.11. Modelos previstos

- Modelo 0: asociación cruda entre cada exposición socioeconómica y el resultado.
- Modelo 1: ajuste por edad y sexo.
- Modelo 2: Modelo 1 + país de nacimiento + comunidad autónoma.
- Modelo 3: Modelo 2 + actividad física.
- Modelo 4: Modelo 3 + apoyo social.

La elección entre regresión logística, Poisson robusta u otra parametrización se decidirá después de examinar la prevalencia del resultado y las posibilidades reales del diseño muestral disponible. Se priorizarán estimaciones interpretables, como prevalencias ajustadas, diferencias de prevalencia o razones de prevalencia, frente a presentar únicamente odds ratios.

## 1.12. Análisis secundarios

Los siguientes resultados no sustituyen al resultado primario:

- enfermedad o problema crónico (`C2`);
- limitación por problemas de salud (`C3a`);
- categoría de IMC (`IMC`), en población de 18 años o más;
- índice de bienestar (`INDICE_BIENESTAR`);
- severidad depresiva (`SEVERIDAD_DEPRESIVA`);
- cuadros depresivos activos (`CUADROS_DEPRESIVOS`).

Su análisis se considerará secundario o exploratorio y se controlará el riesgo de conclusiones selectivas derivado de múltiples comparaciones.

## 1.13. Decisiones que quedan pendientes

- Agrupación exacta de `NIVEST` en nivel bajo, medio y alto.
- Tratamiento de la categoría no clasificable de `CLASE_PR`.
- Elección de contrastes de tendencia para exposiciones ordinales.
- Forma funcional de la edad.
- Método para estimar varianzas teniendo en cuenta el diseño muestral con la información pública disponible.
- Umbral y tratamiento de consumo de alcohol; no se aplicarán límites de riesgo sin una fuente metodológica explícita.
- Estrategia ante valores perdidos: análisis completo, categorías explícitas o imputación, según patrón y magnitud.
- Definición final de interacciones y análisis estratificados.

Estas decisiones deben cerrarse en el plan de análisis antes de consultar resultados multivariables.

## 1.14. Trazabilidad y discrepancias documentales

- La página oficial de la ESdE informa de trabajo de campo entre agosto de 2023 y agosto de 2024.
- La metodología oficial, página 6, indica recogida entre septiembre de 2023 y agosto de 2024.
- Se conserva esta discrepancia sin resolver ni armonizar artificialmente. Para describir el conjunto se utilizará «recogida durante 2023–2024» y se citará la fuente concreta cuando se necesiten meses exactos.
- El paquete adulto utilizado es el vigente tras el aviso de revisión del IMC de 01/09/2025.
- El paquete de hogar utilizado es el vigente tras el aviso de actualización de ingresos de 16/04/2026.

## 1.15. Fuentes de referencia

- Ministerio de Sanidad. Encuesta de Salud de España 2023: https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/
- Ministerio de Sanidad. Banco de microdatos: https://www.sanidad.gob.es/estadisticas/microdatos.do
- Cuestionario oficial de adultos: `docs/official/ESdE23_ADULTO.pdf`.
- Metodología oficial: `docs/official/ESdE23_Metodologia.pdf`.
- Diseño de registro adulto: `data/extracted/adulto/dr_ESdEadulto_2023.xlsx`.
- Diseño de registro hogar: `data/extracted/hogar/dr_ESdEhogar_2023.xlsx`.
- Diccionario de trabajo: `outputs/01a03d6c-06a1-7f50-bf47-10ed54760d3c/diccionario_trabajo_ESdE2023.xlsx`.

## Registro de decisiones

| ID | Decisión | Justificación | Estado |
|---|---|---|---|
| D001 | Priorizar `C1` como resultado principal | Cobertura completa, interpretación clara y menor dependencia de variables derivadas | Fijada |
| D002 | Definir `C1` = 3–5 como salud menos que buena | Facilita prevalencias y comunicación; se conservará análisis ordinal | Fijada provisionalmente |
| D003 | Tratar educación, clase e ingresos como exposiciones separadas | Representan dimensiones socioeconómicas distintas | Fijada |
| D004 | Ajustar a priori por edad, sexo, origen y CCAA | Evita selección de covariables guiada por significación | Fijada |
| D005 | Aplicar `FACTORADULTO` | Necesario para inferencia poblacional | Fijada |
| D006 | Evitar interpretación causal | Diseño transversal | Fijada |
| D007 | Restringir análisis de IMC categórico a 18+ | Puntos de corte incluidos corresponden a adultos | Fijada |
| D008 | Mantener resultados secundarios separados | Reduce riesgo de cambiar el objetivo según los resultados | Fijada |
