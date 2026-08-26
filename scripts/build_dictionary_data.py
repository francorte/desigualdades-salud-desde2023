from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AD = ROOT / "data/extracted/adulto"
HH = ROOT / "data/extracted/hogar"
OUT = ROOT / "outputs/01a03d6c-06a1-7f50-bf47-10ed54760d3c"


def design(path):
    d = pd.read_excel(path, sheet_name="Diseño", header=1)
    return d[d["Variable"].notna()].set_index("Variable")


def dictionaries(path):
    x = pd.ExcelFile(path)
    result = {}
    for sheet in [s for s in x.sheet_names if s.startswith("Tablas")]:
        raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
        for i in range(len(raw) - 2):
            name = raw.iat[i, 0]
            if pd.isna(name) or str(raw.iat[i + 1, 0]).strip() != "Código":
                continue
            items = []
            j = i + 2
            while j < len(raw) and not pd.isna(raw.iat[j, 0]):
                code = raw.iat[j, 0]
                label = raw.iat[j, 1]
                if not pd.isna(label):
                    if isinstance(code, float) and code.is_integer():
                        code = int(code)
                    items.append((str(code), str(label).strip()))
                j += 1
            result[str(name).strip()] = items
    return result


ad_design = design(AD / "dr_ESdEadulto_2023.xlsx")
hh_design = design(HH / "dr_ESdEhogar_2023.xlsx")
ad_dict = dictionaries(AD / "dr_ESdEadulto_2023.xlsx")
hh_dict = dictionaries(HH / "dr_ESdEhogar_2023.xlsx")
ad = pd.read_csv(AD / "CSV/ESdEadulto_2023.tab", sep="\t", low_memory=False)
hh = pd.read_csv(HH / "CSV/ESdEhogar_2023.tab", sep="\t", low_memory=False)

selected = [
    ("adulto", "CCAA", "Controles y diseño", "control"),
    ("adulto", "SEXOa", "Controles y diseño", "control"),
    ("adulto", "EDADa", "Controles y diseño", "control"),
    ("adulto", "A1a", "Controles y diseño", "control"),
    ("adulto", "FACTORADULTO", "Controles y diseño", "diseño"),
    ("adulto", "NIVEST", "Socioeconómico", "exposición"),
    ("hogar", "A11", "Socioeconómico", "exposición"),
    ("hogar", "INGRESOS", "Socioeconómico", "exposición"),
    ("adulto", "CLASE_PR", "Socioeconómico", "exposición"),
    ("adulto", "C1", "Resultados de salud", "resultado"),
    ("adulto", "C2", "Resultados de salud", "resultado"),
    ("adulto", "C3a", "Resultados de salud", "resultado"),
    ("adulto", "IMC", "Resultados de salud", "resultado"),
    ("adulto", "INDICE_BIENESTAR", "Resultados de salud", "resultado"),
    ("adulto", "SEVERIDAD_DEPRESIVA", "Resultados de salud", "resultado"),
    ("adulto", "CUADROS_DEPRESIVOS", "Resultados de salud", "resultado"),
    ("adulto", "O1", "Hábitos y determinantes", "exposición"),
    ("adulto", "O2", "Hábitos y determinantes", "exposición"),
    ("adulto", "O7", "Hábitos y determinantes", "exposición"),
    ("adulto", "Q1", "Hábitos y determinantes", "exposición"),
    ("adulto", "R1", "Hábitos y determinantes", "exposición"),
    ("adulto", "CMD1", "Hábitos y determinantes", "exposición"),
    ("adulto", "S1", "Hábitos y determinantes", "exposición"),
    ("adulto", "S2", "Hábitos y determinantes", "exposición"),
    ("adulto", "S3", "Hábitos y determinantes", "exposición"),
]

transform = {
    "CCAA": "Usar como factor; considerar efectos fijos autonómicos.",
    "SEXOa": "Usar como factor; estratificar o probar interacción si procede.",
    "EDADa": "Excluir 999; usar continua y explorar no linealidad o grupos etarios.",
    "A1a": "Recodificar España/extranjero; 9 como perdido.",
    "FACTORADULTO": "Aplicar como ponderación muestral; no tratar como predictor.",
    "NIVEST": "Agrupar en bajo/medio/alto con una regla documentada; 99 como perdido.",
    "A11": "Recodificar categorías laborales; 9 como perdido.",
    "INGRESOS": "Tratar como ordinal; enlazar por IDENTHOGAR y NORDENa=NORDEN; códigos especiales como perdidos.",
    "CLASE_PR": "Usar como ordinal/categórica; mantener 'no clasificable' separado o como perdido según análisis.",
    "C1": "Resultado ordinal; alternativa binaria: mala/regular (3–5) frente a buena (1–2).",
    "C2": "Resultado binario; 9 como perdido.",
    "C3a": "Resultado ordinal; alternativa binaria: cualquier limitación (1–2) frente a ninguna (3); 9 perdido.",
    "IMC": "Usar categorías oficiales; restringir a 18+ si se interpreta con puntos de corte adultos.",
    "INDICE_BIENESTAR": "Usar continua; 999 como perdido; comprobar rango y distribución.",
    "SEVERIDAD_DEPRESIVA": "Usar ordinal; conservar categorías oficiales y tratar especiales como perdidos.",
    "CUADROS_DEPRESIVOS": "Usar categórica/binaria según códigos oficiales; tratar especiales como perdidos.",
    "O1": "Usar como ordinal/categórica; 9 como perdido.",
    "O2": "Usar como ordinal/categórica; 9 como perdido.",
    "O7": "Días/semana (0–7); 9 como perdido; considerar binaria ≥3 días.",
    "Q1": "Recodificar nunca/exfumador/ocasional/diario según categorías oficiales; 9 perdido.",
    "R1": "Usar ordinal; distinguir abstinencia de consumo infrecuente; 99 perdido.",
    "CMD1": "Usar continua; 999 como perdido; explorar asimetría y categorías de riesgo solo con umbral documentado.",
    "S1": "Usar ordinal; 9 como perdido.",
    "S2": "Usar ordinal; 9 como perdido.",
    "S3": "Usar ordinal; 9 como perdido.",
}

rows = []
for source, var, block, role in selected:
    des = ad_design if source == "adulto" else hh_design
    dic = ad_dict if source == "adulto" else hh_dict
    data = ad if source == "adulto" else hh
    meta = des.loc[var]
    dict_name = meta["Diccionario de la variable"]
    cats = dic.get(str(dict_name).strip(), []) if pd.notna(dict_name) else []
    codes = "; ".join(f"{c} = {lab}" for c, lab in cats)
    series = data[var]
    observed = sorted(series.dropna().unique().tolist())
    observed_text = ", ".join(str(int(v)) if isinstance(v, float) and v.is_integer() else str(v) for v in observed[:40])
    if len(observed) > 40:
        observed_text += f" … ({len(observed)} valores únicos)"
    special = [f"{c} = {lab}" for c, lab in cats if any(k in lab.lower() for k in ["no contesta", "no sabe /", "no sabe/", "no consta", "no clasific"])]
    rows.append({
        "fuente_fichero": source,
        "nombre_original": var,
        "etiqueta_definicion_oficial": str(meta["Descripción"]).strip(),
        "tipo_oficial": "numérico" if meta["Tipo"] == "N" else "código alfanumérico",
        "decimales": "" if pd.isna(meta["Decimales"]) else int(meta["Decimales"]),
        "codigos_categorias_oficiales": codes or "No aplica; variable numérica o identificador.",
        "valores_perdidos_especiales": "; ".join(special) or "No consta código especial en el diccionario; los blancos del CSV son ausencias por filtro/no aplicable cuando corresponda.",
        "bloque_tematico": block,
        "papel_analitico_sugerido": role,
        "transformacion_sugerida": transform[var],
        "observaciones": ("Variable procedente del fichero hogar actualizado 16/04/2026. " if source == "hogar" else "") + (str(meta["Observaciones"]).strip() if pd.notna(meta["Observaciones"]) else ""),
        "n_registros_fuente": len(data),
        "n_no_nulos_csv": int(series.notna().sum()),
        "n_nulos_csv": int(series.isna().sum()),
        "valores_observados_csv": observed_text,
        "diccionario_oficial": "" if pd.isna(dict_name) else str(dict_name),
    })

df = pd.DataFrame(rows)
OUT.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT / "diccionario_trabajo_ESdE2023.csv", index=False, encoding="utf-8-sig")
(OUT / "diccionario_trabajo_ESdE2023.json").write_text(
    df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8"
)

join = ad[["IDENTHOGAR", "NORDENa"]].merge(
    hh[["IDENTHOGAR", "NORDEN", "A11", "INGRESOS"]],
    left_on=["IDENTHOGAR", "NORDENa"], right_on=["IDENTHOGAR", "NORDEN"],
    how="left", validate="one_to_one"
)
summary = {
    "adult_rows": len(ad), "adult_columns": len(ad.columns),
    "adult_int_columns": int((ad.dtypes == "int64").sum()),
    "adult_float_columns": int((ad.dtypes == "float64").sum()),
    "household_member_rows": len(hh), "household_columns": len(hh.columns),
    "join_rows": len(join), "join_income_non_null": int(join["INGRESOS"].notna().sum()),
    "join_work_status_non_null": int(join["A11"].notna().sum()),
    "selected_variables": len(df),
}
(OUT / "inspection_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(df[["nombre_original", "diccionario_oficial", "n_no_nulos_csv", "valores_perdidos_especiales"]].to_string(index=False))
