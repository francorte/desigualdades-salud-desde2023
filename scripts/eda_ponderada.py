from pathlib import Path
import json
import numpy as np
import pandas as pd
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/esde2023_adultos_analitica.csv.gz"
OUT = ROOT / "reports/eda"
FIG = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

d = pd.read_csv(DATA)
w = d["peso_adulto"]


def wmean(x, weights):
    mask = x.notna() & weights.notna()
    return np.average(x[mask], weights=weights[mask]) if mask.any() else np.nan


def weighted_group(df, group, outcome="salud_menos_que_buena"):
    rows = []
    for value, g in df[df[group].notna()].groupby(group, observed=True):
        rows.append({
            "variable": group,
            "categoria": str(value),
            "n_no_ponderado": len(g),
            "peso_poblacional": g.peso_adulto.sum(),
            "proporcion_muestra": len(g) / len(df),
            "proporcion_ponderada": g.peso_adulto.sum() / df.loc[df[group].notna(), "peso_adulto"].sum(),
            "prevalencia_salud_menos_buena": wmean(g[outcome], g.peso_adulto),
        })
    return pd.DataFrame(rows)


group_vars = ["educacion_3", "clase_social_1_6", "ingresos_5", "situacion_laboral", "sexo", "grupo_edad_4", "nacido_extranjero", "ccaa"]
tables = pd.concat([weighted_group(d, v) for v in group_vars], ignore_index=True)
tables.to_csv(OUT / "prevalencia_ponderada_por_grupos.csv", index=False, encoding="utf-8-sig", float_format="%.6f")

overall = pd.DataFrame([
    {"indicador": "salud_menos_que_buena", "n_validos": d.salud_menos_que_buena.notna().sum(), "estimacion_ponderada": wmean(d.salud_menos_que_buena, w)},
    {"indicador": "problema_cronico", "n_validos": d.problema_cronico.notna().sum(), "estimacion_ponderada": wmean(d.problema_cronico, w)},
    {"indicador": "limitacion_salud", "n_validos": d.limitacion_salud.notna().sum(), "estimacion_ponderada": wmean(d.limitacion_salud, w)},
    {"indicador": "fumador_actual", "n_validos": d.fumador_actual.notna().sum(), "estimacion_ponderada": wmean(d.fumador_actual, w)},
    {"indicador": "ocio_sedentario", "n_validos": d.ocio_sedentario.notna().sum(), "estimacion_ponderada": wmean(d.ocio_sedentario, w)},
    {"indicador": "cuadro_depresivo_bin", "n_validos": d.cuadro_depresivo_bin.notna().sum(), "estimacion_ponderada": wmean(d.cuadro_depresivo_bin, w)},
    {"indicador": "edad_media", "n_validos": d.edad.notna().sum(), "estimacion_ponderada": wmean(d.edad, w)},
    {"indicador": "bienestar_medio", "n_validos": d.bienestar_0_100.notna().sum(), "estimacion_ponderada": wmean(d.bienestar_0_100, w)},
])
overall.to_csv(OUT / "indicadores_ponderados_generales.csv", index=False, encoding="utf-8-sig", float_format="%.6f")

missing_exposures = {
    "educacion": "educacion_3",
    "clase_social": "clase_social_1_6",
    "ingresos": "ingresos_5",
}
selectivity = []
for label, field in missing_exposures.items():
    for state, mask in [("observado", d[field].notna()), ("ausente", d[field].isna())]:
        g = d[mask]
        selectivity.append({
            "exposicion": label,
            "estado": state,
            "n": len(g),
            "porcentaje_muestra": len(g) / len(d),
            "porcentaje_ponderado": g.peso_adulto.sum() / d.peso_adulto.sum(),
            "edad_media_ponderada": wmean(g.edad, g.peso_adulto),
            "porcentaje_mujeres_ponderado": wmean(g.SEXOa.eq(2).astype(int), g.peso_adulto),
            "porcentaje_nacido_extranjero_ponderado": wmean(g.nacido_extranjero, g.peso_adulto),
            "prevalencia_salud_menos_buena": wmean(g.salud_menos_que_buena, g.peso_adulto),
            "prevalencia_problema_cronico": wmean(g.problema_cronico, g.peso_adulto),
        })
selectivity = pd.DataFrame(selectivity)
selectivity.to_csv(OUT / "selectividad_valores_perdidos.csv", index=False, encoding="utf-8-sig", float_format="%.6f")

orders = {
    "educacion_3": ["bajo", "medio", "alto"],
    "clase_social_1_6": ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0"],
    "ingresos_5": ["1.0", "2.0", "3.0", "4.0", "5.0"],
}
labels = {
    "educacion_3": {"bajo": "Bajo", "medio": "Medio", "alto": "Alto"},
    "clase_social_1_6": {str(float(i)): str(i) for i in range(1, 7)},
    "ingresos_5": {str(float(i)): str(i) for i in range(1, 6)},
}
titles = {"educacion_3": "Nivel educativo", "clase_social_1_6": "Clase social", "ingresos_5": "Ingresos del hogar"}
colors = ["#9C3D54", "#2B6F8A", "#397A63"]


def svg_text(x, y, text, size=12, anchor="middle", weight="normal", fill="#172B3A"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(str(text))}</text>'


def socioeconomic_svg():
    width, height = 1200, 400
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>']
    pieces.append(svg_text(width/2, 28, "Salud autopercibida regular, mala o muy mala", 18, weight="bold"))
    for panel, ((var, order), color) in enumerate(zip(orders.items(), colors)):
        px = 55 + panel * 390; py = 70; pw = 340; ph = 260
        t = tables[tables.variable.eq(var)].copy().set_index("categoria").reindex(order).dropna(subset=["prevalencia_salud_menos_buena"])
        vals = (t.prevalencia_salud_menos_buena * 100).tolist(); cats = [labels[var].get(i, i) for i in t.index]
        ymax = max(50, np.ceil((max(vals)+5)/10)*10)
        for tick in np.linspace(0, ymax, 6):
            yy = py + ph - tick/ymax*ph
            pieces.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}" stroke="#D9E1E8"/>')
            if panel == 0: pieces.append(svg_text(px-8, yy+4, f"{tick:.0f}", 10, anchor="end", fill="#526270"))
        bw = min(55, pw/(len(vals)*1.5)); gap = pw/len(vals)
        for i, (cat, val) in enumerate(zip(cats, vals)):
            cx = px + gap*(i+.5); bh = val/ymax*ph; y = py+ph-bh
            pieces.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}"/>')
            pieces.append(svg_text(cx, y-6, f"{val:.1f}%", 11, weight="bold"))
            pieces.append(svg_text(cx, py+ph+20, cat, 11))
        pieces.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="#8A98A5"/>')
        pieces.append(svg_text(px+pw/2, py-15, titles[var], 14, weight="bold"))
    pieces.append(svg_text(18, 200, "Prevalencia ponderada (%)", 12, anchor="middle"))
    pieces.append('</svg>')
    return "".join(pieces)


def missingness_svg():
    width, height = 850, 430; px, py, pw, ph = 85, 70, 700, 280
    pivot = selectivity.pivot(index="exposicion", columns="estado", values="prevalencia_salud_menos_buena").loc[["educacion", "clase_social", "ingresos"]] * 100
    ymax = np.ceil((pivot.max().max()+5)/10)*10
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', svg_text(width/2, 28, "Salud menos que buena según disponibilidad de la exposición", 17, weight="bold")]
    for tick in np.linspace(0, ymax, 6):
        yy = py+ph-tick/ymax*ph; pieces.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}" stroke="#D9E1E8"/>'); pieces.append(svg_text(px-9, yy+4, f"{tick:.0f}", 10, anchor="end"))
    cats = [("educacion","Educación"),("clase_social","Clase social"),("ingresos","Ingresos")]
    group_gap = pw/3; bw = 52
    for i,(key,lab) in enumerate(cats):
        cx=px+group_gap*(i+.5)
        for offset,state,color in [(-bw/2,"observado","#2B6F8A"),(bw/2,"ausente","#C47A3A")]:
            val=pivot.loc[key,state]; bh=val/ymax*ph; y=py+ph-bh
            pieces.append(f'<rect x="{cx+offset-bw/2:.1f}" y="{y:.1f}" width="{bw}" height="{bh:.1f}" fill="{color}"/>'); pieces.append(svg_text(cx+offset,y-6,f"{val:.1f}%",11,weight="bold"))
        pieces.append(svg_text(cx,py+ph+22,lab,12))
    pieces.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="#8A98A5"/>')
    pieces.append(f'<rect x="275" y="390" width="14" height="14" fill="#2B6F8A"/>{svg_text(295,401,"Dato observado",11,anchor="start")}')
    pieces.append(f'<rect x="440" y="390" width="14" height="14" fill="#C47A3A"/>{svg_text(460,401,"Dato ausente",11,anchor="start")}')
    pieces.append('</svg>'); return "".join(pieces)


(FIG / "prevalencia_gradiente_socioeconomico.svg").write_text(socioeconomic_svg(), encoding="utf-8")
(FIG / "selectividad_ausencia.svg").write_text(missingness_svg(), encoding="utf-8")

def get_rows(var, desired):
    t = tables[tables.variable.eq(var)].copy()
    t["categoria"] = t.categoria.astype(str)
    return t.set_index("categoria").reindex(desired)

edu = get_rows("educacion_3", orders["educacion_3"])
cls = get_rows("clase_social_1_6", orders["clase_social_1_6"])
inc = get_rows("ingresos_5", orders["ingresos_5"])
sex = get_rows("sexo", ["hombre", "mujer"])
age = get_rows("grupo_edad_4", ["15-24", "25-44", "45-64", "65+"])

def md_table(t, label_map=None):
    lines = ["| Categoría | n | Distribución ponderada | Salud menos que buena |", "|---|---:|---:|---:|"]
    for idx, row in t.iterrows():
        lab = label_map.get(idx, idx) if label_map else idx
        lines.append(f"| {lab} | {int(row.n_no_ponderado):,} | {row.proporcion_ponderada:.1%} | {row.prevalencia_salud_menos_buena:.1%} |".replace(",", "."))
    return lines

lines = [
    "# EDA ponderada y diagnóstico de ausencia",
    "",
    "**Estado:** análisis descriptivo; no incluye todavía contrastes confirmatorios ni modelos ajustados.  ",
    "**Ponderación:** `FACTORADULTO`.  ",
    "**Resultado:** `salud_menos_que_buena` (`C1` = 3–5).",
    "",
    "## Resumen general",
    "",
]
for _, r in overall.iterrows():
    if r.indicador in {"edad_media", "bienestar_medio"}:
        lines.append(f"- {r.indicador.replace('_',' ')}: {r.estimacion_ponderada:.1f}.")
    else:
        lines.append(f"- {r.indicador.replace('_',' ')}: {r.estimacion_ponderada:.1%}.")
lines += ["", "## Gradiente por educación", ""] + md_table(edu, labels["educacion_3"])
lines += ["", "## Gradiente por clase social", ""] + md_table(cls, labels["clase_social_1_6"])
lines += ["", "## Gradiente por ingresos", ""] + md_table(inc, labels["ingresos_5"])
lines += ["", "## Distribución por sexo", ""] + md_table(sex)
lines += ["", "## Distribución por edad", ""] + md_table(age)
lines += [
    "", "## Diagnóstico de ausencia", "",
    "| Exposición | Estado | n | Peso poblacional | Edad media | Mujeres | Nacido extranjero | Salud menos que buena |",
    "|---|---|---:|---:|---:|---:|---:|---:|",
]
for _, r in selectivity.iterrows():
    lines.append(f"| {r.exposicion} | {r.estado} | {int(r.n):,} | {r.porcentaje_ponderado:.1%} | {r.edad_media_ponderada:.1f} | {r.porcentaje_mujeres_ponderado:.1%} | {r.porcentaje_nacido_extranjero_ponderado:.1%} | {r.prevalencia_salud_menos_buena:.1%} |".replace(",", "."))
lines += [
    "", "## Lectura provisional", "",
    "- Los tres indicadores muestran un patrón social amplio: la salud menos que buena es más frecuente en las posiciones menos favorecidas. El descenso es claro por educación y entre los extremos de clase e ingresos, pero no es estrictamente monotónico en todas las categorías intermedias.",
    "- Las diferencias son asociaciones brutas y pueden reflejar en gran medida la estructura de edad y otras variables de confusión.",
    "- La ausencia no es completamente neutra: los grupos con información ausente presentan perfiles de edad, origen y salud distintos según la exposición.",
    "- Por ello, el análisis de casos completos deberá acompañarse de una comparación explícita de incluidos y excluidos y de análisis de sensibilidad.",
    "", "## Límites", "",
    "Las estimaciones son descriptivas y ponderadas. No se presentan todavía intervalos de confianza porque antes debe cerrarse el método de estimación de varianza compatible con la información pública del diseño muestral. No deben interpretarse como efectos causales ni como resultados ajustados.",
]
(OUT / "informe_eda_ponderada.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

summary = {
    "n": len(d),
    "weighted_primary_prevalence": wmean(d.salud_menos_que_buena, w),
    "education_low": float(edu.loc["bajo", "prevalencia_salud_menos_buena"]),
    "education_high": float(edu.loc["alto", "prevalencia_salud_menos_buena"]),
    "income_1": float(inc.loc["1.0", "prevalencia_salud_menos_buena"]),
    "income_5": float(inc.loc["5.0", "prevalencia_salud_menos_buena"]),
}
(OUT / "eda_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(selectivity.to_string(index=False))
