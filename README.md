# Desigualdades socioeconómicas y salud en España | Encuesta de Salud de España 2023

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/francorte/desigualdades-salud-desde2023/blob/main/esde2023_desigualdades_salud.ipynb)
[![Fuente oficial](https://img.shields.io/badge/Datos-Ministerio%20de%20Sanidad-blue)](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE)

Análisis reproducible de las desigualdades socioeconómicas en salud autopercibida en España a partir de los microdatos de adultos de la Encuesta de Salud de España 2023 (ESdE 2023). El proyecto documenta la adquisición, limpieza y validación de los datos, aplica ponderaciones muestrales y estima asociaciones ajustadas mediante regresión y estandarización marginal.

*Reproducible analysis of socioeconomic inequalities in self-rated health in Spain using the 2023 Spanish Health Survey.*

## Artículo divulgativo

### [Leer el artículo divulgativo: «Tu posición social también se refleja en tu salud»](article/articulo_divulgativo.md)

Una versión accesible y visual de los principales resultados: qué muestran los datos sobre educación, clase social e ingresos, qué ocurre tras el ajuste estadístico y qué podemos —y qué no podemos— concluir sobre actividad física, apoyo social y desigualdad en salud.

## Resultado ejecutivo

La salud percibida presenta un gradiente social consistente. Tras ajustar por edad, sexo, país de nacimiento y comunidad autónoma, las diferencias se mantienen para educación, clase social e ingresos.

| Hallazgo | Resultado ajustado |
|---|---:|
| Prevalencia ponderada de salud menos que buena | 29,1 % |
| Educación baja frente a alta | +9,7 pp; RP 1,46 |
| Clase social VI frente a I | +12,2 pp; RP 1,57 |
| Ingresos más bajos frente a más altos | +9,6 pp; RP 1,39 |
| Registros adultos | 21.032 |
| Variables originales inspeccionadas | 432 |
| Ajustes puntuales convergentes | 30 de 30 |
| Réplicas bootstrap válidas por exposición | 1.000 de 1.000 |

## Interpretación

- El gradiente más amplio aparece entre los extremos de clase social ocupacional.
- Las diferencias persisten después del ajuste demográfico y territorial.
- La actividad física y el apoyo social atenúan parcialmente varias asociaciones.
- Los resultados describen asociaciones transversales; no identifican efectos causales ni prueban mediación.

## Pregunta de investigación

> ¿Existe un gradiente socioeconómico en la prevalencia de salud autopercibida regular, mala o muy mala entre la población adulta residente en España, y en qué medida se mantiene después de ajustar por edad, sexo, país de nacimiento y comunidad autónoma?

## Datos

- **Fuente:** Ministerio de Sanidad e Instituto Nacional de Estadística.
- **Encuesta:** ESdE 2023, recogida durante 2023–2024.
- **Unidad analítica:** persona seleccionada de 15 o más años residente en vivienda familiar.
- **Cobertura:** 21.032 adultos y 432 variables en el fichero original.
- **Ponderación:** `FACTORADULTO`.
- **Versiones:** fichero adulto vigente tras la revisión del IMC de 01/09/2025 y fichero de hogar vigente tras la actualización de ingresos de 16/04/2026.

Los microdatos no se incluyen en el repositorio. Deben descargarse desde el [banco oficial de microdatos](https://www.sanidad.gob.es/estadisticas/microdatos.do). Consulta [data/README.md](data/README.md) para conocer la ubicación esperada y reproducir el análisis.

## Método

1. Inspección del cuestionario, metodología y diseños de registro oficiales.
2. Construcción de un diccionario de trabajo y preespecificación de hipótesis.
3. Unión controlada de los ficheros adulto y hogar.
4. Validación de claves, rangos, códigos especiales y saltos del cuestionario.
5. EDA ponderada y diagnóstico de valores perdidos.
6. Estimación de prevalencias e intervalos mediante bootstrap estratificado aproximado.
7. Regresiones logísticas ponderadas secuenciales.
8. Estandarización marginal para obtener prevalencias, diferencias y razones ajustadas.

## Modelos

- **M0:** exposición sin ajuste.
- **M1:** edad, edad al cuadrado y sexo.
- **M2 principal:** M1 + país de nacimiento + comunidad autónoma.
- **M3:** M2 + actividad física en tiempo libre.
- **M4:** M3 + indicadores de apoyo social.

Cada indicador socioeconómico se analiza por separado. El resultado principal es `C1 = 3–5`: salud autopercibida regular, mala o muy mala.

## Estructura

```text
.
├── esde2023_desigualdades_salud.ipynb
├── article/
│   ├── articulo_divulgativo.md
│   └── figures/
├── data/
│   └── README.md
├── config/
│   └── variables_analisis.yml
├── docs/project/
├── outputs/
├── reports/
├── scripts/
├── requirements.txt
└── LICENSE
```

## Archivos principales

- [Artículo divulgativo](article/articulo_divulgativo.md)
- [Notebook completo](esde2023_desigualdades_salud.ipynb)
- [Resumen ejecutivo](reports/executive_summary.md)
- [Documentación de los datos](data/README.md)
- [Planteamiento e hipótesis](docs/project/01_planteamiento_pregunta_hipotesis.md)
- [Limpieza y operacionalización](docs/project/02_operacionalizacion_limpieza.md)
- [Varianzas e intervalos de confianza](docs/project/03_estimacion_varianzas_ic.md)
- [Regresiones ponderadas](docs/project/04_contrastes_regresiones_ponderadas.md)
- [Diccionario de trabajo](outputs/01a03d6c-06a1-7f50-bf47-10ed54760d3c/diccionario_trabajo_ESdE2023.xlsx)

## Reproducibilidad

```bash
git clone https://github.com/francorte/desigualdades-salud-desde2023.git
cd desigualdades-salud-desde2023
python -m venv .venv
pip install -r requirements.txt
jupyter notebook esde2023_desigualdades_salud.ipynb
```

Después de descargar los paquetes oficiales y colocarlos como indica `data/README.md`, ejecuta el notebook en orden. Los scripts también permiten reproducir cada etapa por separado.

## Limitaciones

- Diseño transversal: las asociaciones no deben interpretarse como causales.
- La población institucionalizada queda fuera del marco muestral.
- Los valores perdidos no son completamente aleatorios entre los grupos estudiados.
- El fichero público contiene estratos, pero no unidades primarias ni pesos replicados.
- Los intervalos usan bootstrap por estrato público y son aproximados; no reproducen el jackknife oficial por sección censal.
- Los análisis de actividad física y apoyo social son compatibles con atenuación, no demuestran mediación.

## Tecnologías

Python · Pandas · NumPy · SciPy · Statsmodels · Jupyter · Excel

## Autor

**Francisco de la Corte**  
Biólogo y analista de datos especializado en sostenibilidad, bioeconomía e IA aplicada.

## Licencias y fuente

El código y la documentación original del proyecto se publican bajo licencia [MIT](LICENSE). Los microdatos y documentos oficiales conservan sus condiciones de uso y no se redistribuyen en este repositorio.

> Ministerio de Sanidad e Instituto Nacional de Estadística. Encuesta de Salud de España 2023 (ESdE 2023).
