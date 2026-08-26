from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ADULT_PATH = ROOT / "data/extracted/adulto/CSV/ESdEadulto_2023.tab"
HOUSEHOLD_PATH = ROOT / "data/extracted/hogar/CSV/ESdEhogar_2023.tab"
OUT = ROOT / "data/processed"
REPORT = ROOT / "reports"

EXPECTED_ADULT_ROWS = 21_032
EXPECTED_ADULT_COLUMNS = 432


@dataclass
class Check:
    check_id: str
    severity: str
    description: str
    expected: str
    observed: str
    status: str


checks: list[Check] = []


def add_check(check_id, severity, description, expected, observed, passed):
    checks.append(Check(check_id, severity, description, str(expected), str(observed), "PASS" if passed else "FAIL"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid_or_missing(series: pd.Series, valid, missing=()):
    return set(series.dropna().unique()).issubset(set(valid) | set(missing))


def recode_with_missing(series: pd.Series, mapping: dict, missing: set[int]):
    clean = series.mask(series.isin(missing))
    return clean.map(mapping)


OUT.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)

adult = pd.read_csv(ADULT_PATH, sep="\t", low_memory=False)
household = pd.read_csv(HOUSEHOLD_PATH, sep="\t", low_memory=False)

add_check("C001", "critical", "Número de filas del fichero adulto", EXPECTED_ADULT_ROWS, len(adult), len(adult) == EXPECTED_ADULT_ROWS)
add_check("C002", "critical", "Número de columnas del fichero adulto", EXPECTED_ADULT_COLUMNS, len(adult.columns), len(adult.columns) == EXPECTED_ADULT_COLUMNS)
adult_key_unique = not adult.duplicated(["IDENTHOGAR", "NORDENa"]).any()
household_key_unique = not household.duplicated(["IDENTHOGAR", "NORDEN"]).any()
add_check("C003", "critical", "Clave adulta única", True, adult_key_unique, adult_key_unique)
add_check("C004", "critical", "Clave de miembros del hogar única", True, household_key_unique, household_key_unique)

merged = adult.merge(
    household[["IDENTHOGAR", "NORDEN", "ESTRATO", "A11", "INGRESOS"]],
    left_on=["IDENTHOGAR", "NORDENa"],
    right_on=["IDENTHOGAR", "NORDEN"],
    how="left",
    validate="one_to_one",
    indicator=True,
)
matched = int((merged["_merge"] == "both").sum())
add_check("C005", "critical", "Coincidencias adulto-hogar", EXPECTED_ADULT_ROWS, matched, matched == EXPECTED_ADULT_ROWS)
add_check("C006", "critical", "La unión no expande ni reduce filas", EXPECTED_ADULT_ROWS, len(merged), len(merged) == EXPECTED_ADULT_ROWS)
merged.drop(columns=["_merge", "NORDEN"], inplace=True)

domain_checks = {
    "C1": ({1, 2, 3, 4, 5}, set()),
    "SEXOa": ({1, 2}, set()),
    "CCAA": (set(range(1, 20)), set()),
    "A1a": ({1, 2}, {9}),
    "NIVEST": ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {99}),
    "CLASE_PR": ({1, 2, 3, 4, 5, 6}, {9}),
    "A11": ({1, 2, 3, 4, 5, 6, 7}, {9}),
    "INGRESOS": ({1, 2, 3, 4, 5}, {99}),
    "C2": ({1, 2}, {9}),
    "C3a": ({1, 2, 3}, {9}),
    "IMC": ({1, 2, 3, 4}, {9}),
    "SEVERIDAD_DEPRESIVA": ({1, 2, 3, 4, 5}, {9}),
    "CUADROS_DEPRESIVOS": ({1, 2, 3}, {9}),
    "O1": ({1, 2, 3, 4, 5}, {9}),
    "O2": ({1, 2, 3, 4}, {9}),
    "O7": (set(range(0, 8)), {9}),
    "Q1": ({1, 2, 3, 4}, {9}),
    "R1": (set(range(1, 10)), {99}),
    "S1": ({1, 2, 3, 4}, {9}),
    "S2": ({1, 2, 3, 4, 5}, {9}),
    "S3": ({1, 2, 3, 4, 5}, {9}),
}
for i, (var, (valid, missing)) in enumerate(domain_checks.items(), start=7):
    observed = sorted(merged[var].dropna().unique().tolist())
    ok = valid_or_missing(merged[var], valid, missing)
    add_check(f"C{i:03d}", "critical", f"Dominio oficial de {var}", f"válidos={sorted(valid)}; especiales={sorted(missing)}", observed, ok)

age_ok = (merged["EDADa"].between(15, 120) | merged["EDADa"].eq(999)).all()
add_check("C028", "critical", "Rango de edad", "15–120 o 999", f"{merged.EDADa.min()}–{merged.EDADa.max()}", age_ok)
weight_ok = merged["FACTORADULTO"].notna().all() and merged["FACTORADULTO"].gt(0).all()
add_check("C029", "critical", "Ponderación adulta positiva y completa", True, weight_ok, weight_ok)
wellbeing_ok = merged["INDICE_BIENESTAR"].isin([999]).where(merged["INDICE_BIENESTAR"].eq(999), merged["INDICE_BIENESTAR"].between(0, 100)).all()
add_check("C030", "critical", "Rango del índice de bienestar", "0–100 o 999", f"{merged.INDICE_BIENESTAR.min()}–{merged.INDICE_BIENESTAR.max()}", wellbeing_ok)
alcohol_ok = merged["CMD1"].eq(999).where(merged["CMD1"].eq(999), merged["CMD1"].between(0, 300)).all()
add_check("C031", "critical", "Rango de consumo medio diario", "0–300 o 999", f"{merged.CMD1.min()}–{merged.CMD1.max()}", alcohol_ok)

failed_critical = [c for c in checks if c.severity == "critical" and c.status == "FAIL"]
if failed_critical:
    pd.DataFrame(asdict(c) for c in checks).to_csv(REPORT / "validacion_controles.csv", index=False, encoding="utf-8-sig")
    raise RuntimeError("Fallaron controles críticos: " + ", ".join(c.check_id for c in failed_critical))

raw_vars = [
    "IDENTHOGAR", "NORDENa", "C1", "NIVEST", "CLASE_PR", "A11", "INGRESOS",
    "ESTRATO", "EDADa", "SEXOa", "A1a", "CCAA", "FACTORADULTO", "C2", "C3a", "IMC",
    "INDICE_BIENESTAR", "SEVERIDAD_DEPRESIVA", "CUADROS_DEPRESIVOS", "O1", "O2",
    "O7", "Q1", "R1", "CMD1", "S1", "S2", "S3",
]
analytic = merged[raw_vars].copy()

analytic["salud_menos_que_buena"] = merged["C1"].map({1: 0, 2: 0, 3: 1, 4: 1, 5: 1}).astype("Int8")
analytic["educacion_3"] = recode_with_missing(
    merged["NIVEST"],
    {2: "bajo", 3: "bajo", 4: "bajo", 5: "bajo", 6: "medio", 7: "medio", 8: "medio", 9: "alto"},
    {99},
)
analytic["educacion_ordinal"] = analytic["educacion_3"].map({"bajo": 1, "medio": 2, "alto": 3}).astype("Int8")
analytic["educacion_missing"] = merged["NIVEST"].eq(99).astype("Int8")
analytic["clase_social_1_6"] = merged["CLASE_PR"].mask(merged["CLASE_PR"].eq(9)).astype("Int8")
analytic["clase_social_missing"] = merged["CLASE_PR"].eq(9).astype("Int8")
analytic["ingresos_5"] = merged["INGRESOS"].mask(merged["INGRESOS"].eq(99)).astype("Int8")
analytic["ingresos_missing"] = merged["INGRESOS"].eq(99).astype("Int8")
analytic["situacion_laboral"] = recode_with_missing(
    merged["A11"],
    {1: "trabajando", 2: "desempleo", 3: "jubilacion_prejubilacion", 4: "estudiando", 5: "incapacidad", 6: "labores_hogar", 7: "otros"},
    {9},
)
analytic["situacion_laboral_missing"] = merged["A11"].eq(9).astype("Int8")
analytic["edad"] = merged["EDADa"].mask(merged["EDADa"].eq(999)).astype("Int16")
analytic["grupo_edad_4"] = pd.cut(analytic["edad"], bins=[14, 24, 44, 64, np.inf], labels=["15-24", "25-44", "45-64", "65+"])
analytic["sexo"] = merged["SEXOa"].map({1: "hombre", 2: "mujer"})
analytic["nacido_extranjero"] = merged["A1a"].mask(merged["A1a"].eq(9)).map({1: 0, 2: 1}).astype("Int8")
analytic["ccaa"] = merged["CCAA"].astype("Int8")
analytic["peso_adulto"] = merged["FACTORADULTO"].astype(float)
analytic["estrato_publico"] = merged["ESTRATO"].astype("Int8")
analytic["problema_cronico"] = merged["C2"].mask(merged["C2"].eq(9)).map({1: 1, 2: 0}).astype("Int8")
analytic["limitacion_salud"] = merged["C3a"].mask(merged["C3a"].eq(9)).map({1: 1, 2: 1, 3: 0}).astype("Int8")
analytic["imc_categoria"] = merged["IMC"].mask(merged["IMC"].eq(9)).astype("Int8")
analytic["incluir_imc_18plus"] = analytic["edad"].ge(18).astype("Int8")
analytic["bienestar_0_100"] = merged["INDICE_BIENESTAR"].mask(merged["INDICE_BIENESTAR"].eq(999)).astype(float)
analytic["severidad_depresiva"] = merged["SEVERIDAD_DEPRESIVA"].mask(merged["SEVERIDAD_DEPRESIVA"].eq(9)).astype("Int8")
analytic["cuadro_depresivo_bin"] = merged["CUADROS_DEPRESIVOS"].mask(merged["CUADROS_DEPRESIVOS"].eq(9)).map({1: 1, 2: 1, 3: 0}).astype("Int8")
analytic["actividad_principal"] = merged["O1"].mask(merged["O1"].eq(9)).astype("Int8")
analytic["ocio_sedentario"] = merged["O2"].mask(merged["O2"].eq(9)).map({1: 1, 2: 0, 3: 0, 4: 0}).astype("Int8")
analytic["deporte_dias"] = merged["O7"].mask(merged["O7"].eq(9)).astype("Int8")
analytic["deporte_3omas_dias"] = analytic["deporte_dias"].ge(3).where(analytic["deporte_dias"].notna()).astype("Int8")
analytic["fumador_actual"] = merged["Q1"].mask(merged["Q1"].eq(9)).map({1: 1, 2: 1, 3: 0, 4: 0}).astype("Int8")
analytic["alcohol_frecuencia"] = merged["R1"].mask(merged["R1"].eq(99)).astype("Int8")
analytic["alcohol_media_diaria"] = merged["CMD1"].mask(merged["CMD1"].eq(999)).astype(float)
analytic["apoyo_personas"] = merged["S1"].mask(merged["S1"].eq(9)).astype("Int8")
analytic["interes_otros"] = merged["S2"].mask(merged["S2"].eq(9)).astype("Int8")
analytic["ayuda_vecinal"] = merged["S3"].mask(merged["S3"].eq(9)).astype("Int8")

add_check("C032", "critical", "Filas tras las derivaciones", EXPECTED_ADULT_ROWS, len(analytic), len(analytic) == EXPECTED_ADULT_ROWS)
add_check("C033", "critical", "Resultado primario derivado completo", EXPECTED_ADULT_ROWS, analytic["salud_menos_que_buena"].notna().sum(), analytic["salud_menos_que_buena"].notna().sum() == EXPECTED_ADULT_ROWS)
add_check("C034", "critical", "Claves conservadas y únicas", True, not analytic.duplicated(["IDENTHOGAR", "NORDENa"]).any(), not analytic.duplicated(["IDENTHOGAR", "NORDENa"]).any())
stratum_ok = merged["ESTRATO"].notna().all() and merged["ESTRATO"].isin(range(0, 7)).all()
add_check("C035", "critical", "Estrato público completo y en dominio 0–6", True, stratum_ok, stratum_ok)

missing_specs = {
    "C1": ("C1", set()), "NIVEST": ("NIVEST", {99}), "CLASE_PR": ("CLASE_PR", {9}),
    "A11": ("A11", {9}), "INGRESOS": ("INGRESOS", {99}), "EDADa": ("EDADa", {999}),
    "SEXOa": ("SEXOa", set()), "A1a": ("A1a", {9}), "CCAA": ("CCAA", set()),
    "FACTORADULTO": ("FACTORADULTO", set()), "C2": ("C2", {9}), "C3a": ("C3a", {9}),
    "IMC": ("IMC", {9}), "INDICE_BIENESTAR": ("INDICE_BIENESTAR", {999}),
    "SEVERIDAD_DEPRESIVA": ("SEVERIDAD_DEPRESIVA", {9}), "CUADROS_DEPRESIVOS": ("CUADROS_DEPRESIVOS", {9}),
    "O1": ("O1", {9}), "O2": ("O2", {9}), "O7": ("O7", {9}), "Q1": ("Q1", {9}),
    "R1": ("R1", {99}), "CMD1": ("CMD1", {999}), "S1": ("S1", {9}), "S2": ("S2", {9}), "S3": ("S3", {9}),
}
total_weight = merged["FACTORADULTO"].sum()
missing_rows = []
for label, (var, special) in missing_specs.items():
    mask = merged[var].isna() | merged[var].isin(special)
    n = int(mask.sum())
    missing_rows.append({
        "variable": label,
        "n_total": len(merged),
        "n_ausente": n,
        "pct_ausente_no_ponderado": n / len(merged),
        "peso_total": total_weight,
        "peso_ausente": merged.loc[mask, "FACTORADULTO"].sum(),
        "pct_ausente_ponderado": merged.loc[mask, "FACTORADULTO"].sum() / total_weight,
        "codigos_especiales": ", ".join(str(x) for x in sorted(special)) or "ninguno",
    })
missing_df = pd.DataFrame(missing_rows).sort_values(["pct_ausente_no_ponderado", "variable"], ascending=[False, True])

base_required = ["salud_menos_que_buena", "edad", "sexo", "nacido_extranjero", "ccaa", "peso_adulto"]
exposure_sets = {
    "educacion": "educacion_3", "clase_social": "clase_social_1_6",
    "ingresos": "ingresos_5", "situacion_laboral": "situacion_laboral",
}
exclusion_rows = []
for analysis_name, exposure in exposure_sets.items():
    current = pd.Series(True, index=analytic.index)
    exclusion_rows.append({"analisis": analysis_name, "paso": "Registros iniciales", "n_excluidos_paso": 0, "n_restantes": int(current.sum())})
    for label, field in [("Resultado ausente", "salud_menos_que_buena"), ("Exposición ausente", exposure), ("Covariables/diseño ausentes", None)]:
        if field:
            drop = current & analytic[field].isna()
        else:
            covars = [x for x in base_required if x != "salud_menos_que_buena"]
            drop = current & analytic[covars].isna().any(axis=1)
        current &= ~drop
        exclusion_rows.append({"analisis": analysis_name, "paso": label, "n_excluidos_paso": int(drop.sum()), "n_restantes": int(current.sum())})
exclusions = pd.DataFrame(exclusion_rows)

analytic_path = OUT / "esde2023_adultos_analitica.csv.gz"
analytic.to_csv(analytic_path, index=False, encoding="utf-8", compression="gzip")
missing_path = REPORT / "valores_perdidos.csv"
missing_df.to_csv(missing_path, index=False, encoding="utf-8-sig", float_format="%.6f")
exclusion_path = REPORT / "registro_exclusiones.csv"
exclusions.to_csv(exclusion_path, index=False, encoding="utf-8-sig")
checks_path = REPORT / "validacion_controles.csv"
checks_df = pd.DataFrame(asdict(c) for c in checks)
checks_df.to_csv(checks_path, index=False, encoding="utf-8-sig")

metadata = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "script": "scripts/clean_esde2023.py",
    "adult_source": str(ADULT_PATH.relative_to(ROOT)),
    "household_source": str(HOUSEHOLD_PATH.relative_to(ROOT)),
    "adult_source_sha256": sha256(ADULT_PATH),
    "household_source_sha256": sha256(HOUSEHOLD_PATH),
    "output": str(analytic_path.relative_to(ROOT)),
    "output_sha256": sha256(analytic_path),
    "rows": len(analytic),
    "columns": len(analytic.columns),
    "critical_checks_passed": int((checks_df.query("severity == 'critical'").status == "PASS").sum()),
    "critical_checks_failed": int((checks_df.query("severity == 'critical'").status == "FAIL").sum()),
}
(OUT / "esde2023_adultos_analitica.metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

worst = missing_df.head(10)
report_lines = [
    "# Informe de validación y valores perdidos",
    "",
    f"**Generado:** {metadata['created_utc']}  ",
    f"**Tabla analítica:** `{metadata['output']}`  ",
    f"**Dimensión:** {metadata['rows']:,} filas × {metadata['columns']} columnas  ".replace(",", "."),
    "",
    "## Resultado ejecutivo",
    "",
    f"- Controles críticos superados: {metadata['critical_checks_passed']}.",
    f"- Controles críticos fallidos: {metadata['critical_checks_failed']}.",
    f"- Coincidencias en la unión adulto-hogar: {matched:,} de {len(adult):,}.".replace(",", "."),
    "- La tabla conserva las 21.032 filas adultas; las exclusiones se aplican solo al construir cada muestra de análisis.",
    "- Los originales y las variables derivadas conviven en la tabla para facilitar auditoría.",
    "",
    "## Variables con mayor ausencia",
    "",
    "| Variable | n ausente | % no ponderado | % ponderado |",
    "|---|---:|---:|---:|",
]
for _, row in worst.iterrows():
    report_lines.append(f"| `{row.variable}` | {int(row.n_ausente):,} | {row.pct_ausente_no_ponderado:.2%} | {row.pct_ausente_ponderado:.2%} |".replace(",", "."))
report_lines += [
    "",
    "Los porcentajes ponderados utilizan `FACTORADULTO`. Los códigos especiales se contabilizan como ausencia analítica; `O1 = 5` permanece como categoría estructural no aplicable.",
    "",
    "## Muestras completas previstas",
    "",
    "| Exposición | Registros finales | Exclusiones |",
    "|---|---:|---:|",
]
for analysis_name in exposure_sets:
    final_n = int(exclusions.query("analisis == @analysis_name").iloc[-1].n_restantes)
    report_lines.append(f"| {analysis_name} | {final_n:,} | {len(analytic)-final_n:,} |".replace(",", "."))
report_lines += [
    "",
    "Estas cifras corresponden al resultado primario y a las covariables preespecificadas. Pueden cambiar en modelos que incorporen actividad física o apoyo social.",
    "",
    "## Archivos de auditoría",
    "",
    "- `reports/validacion_controles.csv`: resultado de cada control.",
    "- `reports/valores_perdidos.csv`: ausencia no ponderada y ponderada.",
    "- `reports/registro_exclusiones.csv`: flujo de exclusiones por exposición.",
    "- `data/processed/esde2023_adultos_analitica.metadata.json`: fuentes, huellas y dimensión.",
    "",
    "## Interpretación",
    "",
    "El proceso de limpieza es reproducible y no altera los archivos oficiales. La ausencia más importante se concentra previsiblemente en educación, ingresos, IMC, clase social y variables de depresión. No se ha realizado imputación. Antes de modelizar se comparará el perfil de las personas incluidas y excluidas.",
]
(REPORT / "informe_validacion_valores_perdidos.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

print(json.dumps(metadata, ensure_ascii=False, indent=2))
print("\nValores perdidos principales:\n", worst[["variable", "n_ausente", "pct_ausente_no_ponderado", "pct_ausente_ponderado"]].to_string(index=False))
print("\nExclusiones:\n", exclusions.to_string(index=False))
