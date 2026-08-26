# Estrategia de estimación de varianzas e intervalos de confianza

**Versión:** 1.0  
**Fecha:** 2026-08-26  
**Estado:** decisión cerrada para los análisis exploratorios y modelos posteriores

## Diseño oficial

La ESdE 2023 emplea muestreo trietápico. Las unidades de primera etapa son secciones censales, estratificadas por tamaño municipal; después se seleccionan viviendas y, dentro del hogar, una persona adulta.

La metodología oficial calcula errores mediante jackknife: elimina sucesivamente cada sección censal dentro de su estrato y reajusta los pesos de las restantes secciones del estrato. Los coeficientes de variación publicados por Sanidad proceden de ese procedimiento.

## Información disponible en los microdatos

El fichero de hogar aporta `ESTRATO`, enlazable uno-a-uno con los adultos. En la muestra adulta aparecen siete códigos, 0–6, sin valores perdidos.

No se publican:

- identificadores de sección censal;
- pesos replicados jackknife;
- identificadores de provincia suficientemente detallados para reconstruir estratos completos;
- covarianzas entre categorías de las tablas oficiales.

`IDENTHOGAR` es un identificador de hogar y no se utilizará para inferir una sección. Tampoco se crearán pseudo-PSU a partir de fragmentos del identificador.

## Consecuencia

La varianza oficial no es reproducible exactamente con el fichero público. Usar cada persona como si fuera una unidad primaria puede ignorar correlación intrasección y producir intervalos demasiado estrechos. Los coeficientes de variación oficiales no permiten reconstruir el error del resultado binario personalizado `C1 = 3–5`, porque faltan las covarianzas entre las tres categorías agregadas.

## Decisión adoptada

### Estimaciones puntuales

Se utilizará el estimador ponderado de razón:

```text
p̂ = Σ(wᵢ yᵢ) / Σ(wᵢ)
```

con `wᵢ = FACTORADULTO`.

### Intervalo principal aproximado

Bootstrap estratificado por el `ESTRATO` público:

1. mantener el número observado de personas en cada estrato;
2. remuestrear personas con reemplazo dentro de cada estrato;
3. conservar su peso original;
4. recalcular el estimando en cada réplica;
5. utilizar los percentiles 2,5 y 97,5 de 1.000 réplicas;
6. fijar la semilla en 20230826.

Este método refleja variabilidad individual, estratificación pública y dispersión de pesos, pero no la agrupación por sección censal.

### Comprobación de sensibilidad

Se calculará el tamaño muestral efectivo de Kish:

```text
n_eff = (Σwᵢ)² / Σwᵢ²
```

y un intervalo Wilson para proporciones basado en `n_eff`. La proximidad entre ambos intervalos se usará como control numérico, no como validación del diseño.

## Regresiones

- Los modelos serán ponderados.
- La incertidumbre principal procederá de reajustar el modelo en cada réplica del bootstrap estratificado.
- Una covarianza sándwich ponderada a nivel individual servirá como sensibilidad.
- Los resultados se presentarán preferentemente como prevalencias marginales, diferencias de prevalencia y razones de prevalencia ajustadas.
- Los valores p serán secundarios y nunca se describirán como exactos respecto del diseño oficial.

## Lenguaje obligatorio en resultados

> Intervalos aproximados obtenidos mediante bootstrap estratificado por el estrato público. No incorporan la agrupación por sección censal porque el microdato anonimizado no publica PSU ni pesos replicados; no equivalen a los errores oficiales del Ministerio de Sanidad y el INE.

## Criterio para sustituir el método

La estrategia se reemplazará si se obtienen identificadores anonimizados de sección, pesos replicados oficiales o un mecanismo oficial para calcular errores de estimandos personalizados.

## Fuentes

- Metodología ESdE 2023, apartados 4.1 y 4.6: `docs/official/ESdE23_Metodologia.pdf`, páginas 6 y 12–13.
- Errores de muestreo oficiales: https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/ESdE2023/ESdE23_erroresMuestreo.pdf

## Registro de decisiones

| ID | Decisión | Estado |
|---|---|---|
| D017 | No reconstruir ni inventar PSU | Fijada |
| D018 | Bootstrap estratificado individual como IC aproximado principal | Fijada |
| D019 | Kish–Wilson como sensibilidad | Fijada |
| D020 | Reajustar modelos en cada réplica bootstrap | Fijada |
| D021 | Etiquetar la inferencia como aproximada | Fijada |
| D022 | Sustituir el método si se obtienen PSU o pesos replicados | Fijada |
