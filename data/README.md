# Datos

Los microdatos de la ESdE 2023 no se distribuyen en este repositorio. Se conservan localmente, separados del código, y están excluidos mediante `.gitignore`.

## Fuente oficial

- [Encuesta de Salud de España 2023](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/)
- [Banco de microdatos del Ministerio de Sanidad](https://www.sanidad.gob.es/estadisticas/microdatos.do)

Descarga los paquetes CSV de **Adulto** y **Hogar** correspondientes a 2023. Para reproducir este análisis deben utilizarse las versiones oficiales vigentes:

- Adulto: revisión del IMC publicada el 01/09/2025.
- Hogar: actualización de ingresos publicada el 16/04/2026.

## Estructura local esperada

```text
data/
├── raw/
│   ├── ESdEadulto_2023.zip
│   └── ESdEhogar_2023.zip
├── extracted/
│   ├── adulto/
│   └── hogar/
└── processed/
    └── esde2023_adultos_analitica.csv.gz
```

`raw/` conserva las descargas sin modificar; `extracted/`, los archivos oficiales descomprimidos; y `processed/`, la tabla analítica generada por el proceso de limpieza.

## Cobertura comprobada

- Fichero adulto: 21.032 filas y 432 columnas.
- Fichero hogar: empleado para incorporar ingresos y situación laboral mediante las claves oficiales.
- Tabla analítica: 21.032 filas y 62 columnas.
- Ponderación principal: `FACTORADULTO`.

## Documentación

El cuestionario, la metodología y los diseños de registro deben obtenerse de la misma fuente oficial. El diccionario de trabajo producido por el proyecto se encuentra en `outputs/`.

Los scripts nunca sobrescriben los originales: leen de `raw/` o `extracted/` y escriben productos derivados en `processed/` y `reports/`.
