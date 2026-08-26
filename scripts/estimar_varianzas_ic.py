from pathlib import Path
import json
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/esde2023_adultos_analitica.csv.gz"
OUT = ROOT / "reports/inferencia"
OUT.mkdir(parents=True, exist_ok=True)

B = 1000
SEED = 20230826
Z = 1.959963984540054

d = pd.read_csv(DATA)
y = d.salud_menos_que_buena.to_numpy(float)
w = d.peso_adulto.to_numpy(float)
strata = d.estrato_publico.to_numpy(int)

estimands = [
    ("total", np.ones(len(d), dtype=bool)),
    ("educacion_bajo", d.educacion_3.eq("bajo").to_numpy()),
    ("educacion_medio", d.educacion_3.eq("medio").to_numpy()),
    ("educacion_alto", d.educacion_3.eq("alto").to_numpy()),
    ("clase_1", d.clase_social_1_6.eq(1).to_numpy()),
    ("clase_2", d.clase_social_1_6.eq(2).to_numpy()),
    ("clase_3", d.clase_social_1_6.eq(3).to_numpy()),
    ("clase_4", d.clase_social_1_6.eq(4).to_numpy()),
    ("clase_5", d.clase_social_1_6.eq(5).to_numpy()),
    ("clase_6", d.clase_social_1_6.eq(6).to_numpy()),
    ("ingresos_1", d.ingresos_5.eq(1).to_numpy()),
    ("ingresos_2", d.ingresos_5.eq(2).to_numpy()),
    ("ingresos_3", d.ingresos_5.eq(3).to_numpy()),
    ("ingresos_4", d.ingresos_5.eq(4).to_numpy()),
    ("ingresos_5", d.ingresos_5.eq(5).to_numpy()),
]
names = [x[0] for x in estimands]
M = np.column_stack([x[1].astype(float) for x in estimands])


def estimate(weights):
    den = M.T @ weights
    num = M.T @ (weights * y)
    return num / den


point = estimate(w)
rng = np.random.default_rng(SEED)
stratum_indices = [np.flatnonzero(strata == h) for h in sorted(np.unique(strata))]
boot = np.empty((B, len(names)))
for b in range(B):
    counts = np.zeros(len(d), dtype=float)
    for idx in stratum_indices:
        counts[idx] = rng.multinomial(len(idx), np.full(len(idx), 1 / len(idx)))
    boot[b] = estimate(w * counts)


def wilson(p, n_eff):
    den = 1 + Z**2 / n_eff
    center = (p + Z**2/(2*n_eff)) / den
    half = Z * math.sqrt(p*(1-p)/n_eff + Z**2/(4*n_eff**2)) / den
    return max(0, center-half), min(1, center+half)


rows = []
for j, (name, mask) in enumerate(estimands):
    wg = w[mask]
    n_eff = wg.sum()**2 / np.square(wg).sum()
    kw_lo, kw_hi = wilson(point[j], n_eff)
    bs_lo, bs_hi = np.quantile(boot[:, j], [0.025, 0.975])
    rows.append({
        "estimando": name,
        "n_no_ponderado": int(mask.sum()),
        "n_efectivo_kish": n_eff,
        "estimacion": point[j],
        "bootstrap_se": boot[:, j].std(ddof=1),
        "bootstrap_ic95_inf": bs_lo,
        "bootstrap_ic95_sup": bs_hi,
        "kish_wilson_ic95_inf": kw_lo,
        "kish_wilson_ic95_sup": kw_hi,
        "replicas_bootstrap": B,
        "semilla": SEED,
    })
ci = pd.DataFrame(rows)
ci.to_csv(OUT / "intervalos_prevalencia_aproximados.csv", index=False, encoding="utf-8-sig", float_format="%.8f")

contrasts = [
    ("educacion_bajo_vs_alto", "educacion_bajo", "educacion_alto"),
    ("clase_6_vs_1", "clase_6", "clase_1"),
    ("ingresos_1_vs_5", "ingresos_1", "ingresos_5"),
]
contrast_rows = []
for label, adverse, reference in contrasts:
    ia, ir = names.index(adverse), names.index(reference)
    rd = point[ia] - point[ir]
    pr = point[ia] / point[ir]
    rd_boot = boot[:, ia] - boot[:, ir]
    pr_boot = boot[:, ia] / boot[:, ir]
    contrast_rows.append({
        "contraste": label,
        "prevalencia_expuesto": point[ia],
        "prevalencia_referencia": point[ir],
        "diferencia_prevalencias": rd,
        "dp_ic95_inf": np.quantile(rd_boot, .025),
        "dp_ic95_sup": np.quantile(rd_boot, .975),
        "razon_prevalencias": pr,
        "rp_ic95_inf": np.quantile(pr_boot, .025),
        "rp_ic95_sup": np.quantile(pr_boot, .975),
    })
contrast_df = pd.DataFrame(contrast_rows)
contrast_df.to_csv(OUT / "contrastes_brutos_aproximados.csv", index=False, encoding="utf-8-sig", float_format="%.8f")

meta = {
    "method_primary": "bootstrap estratificado por ESTRATO público, remuestreo individual dentro de estrato",
    "method_sensitivity": "Kish-Wilson basado en tamaño muestral efectivo por pesos",
    "replicates": B,
    "seed": SEED,
    "public_strata": sorted(np.unique(strata).tolist()),
    "n_by_stratum": {str(int(h)): int((strata == h).sum()) for h in np.unique(strata)},
    "official_method": "jackknife delete-one census section within stratum",
    "official_method_reproducible": False,
    "reason": "el microdato público no incluye identificador de sección censal ni pesos replicados",
}
(OUT / "metodo_varianza.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

overall = ci.iloc[0]
lines = [
    "# Intervalos de confianza aproximados",
    "",
    "**Importante:** estos intervalos no reproducen los errores oficiales de Sanidad. El método oficial elimina secciones censales mediante jackknife; el microdato público no contiene el identificador de sección ni pesos replicados.",
    "",
    "## Método adoptado",
    "",
    f"- Método principal exploratorio: bootstrap estratificado por `ESTRATO`, con {B:,} réplicas y remuestreo de personas dentro de cada estrato.".replace(f"{B:,}", f"{B:,}".replace(",", ".")),
    "- Sensibilidad: intervalo Wilson usando el tamaño muestral efectivo de Kish.",
    "- Ambos métodos incorporan la desigualdad de pesos; el bootstrap conserva el tamaño de cada estrato público.",
    "- Ninguno incorpora la correlación dentro de secciones censales. Si esta correlación es positiva, los intervalos pueden ser demasiado estrechos.",
    "- Los intervalos se usarán para análisis exploratorio y portfolio, no como equivalentes a la inferencia oficial del INE/MS.",
    "",
    "## Prevalencia total",
    "",
    f"Salud regular/mala/muy mala: **{overall.estimacion:.1%}**; IC95% bootstrap aproximado **{overall.bootstrap_ic95_inf:.1%}–{overall.bootstrap_ic95_sup:.1%}**; IC95% Kish–Wilson **{overall.kish_wilson_ic95_inf:.1%}–{overall.kish_wilson_ic95_sup:.1%}**.",
    "",
    "## Contrastes brutos entre extremos",
    "",
    "| Contraste | Prevalencias | Diferencia, puntos porcentuales (IC95%) | Razón de prevalencias (IC95%) |",
    "|---|---:|---:|---:|",
]
for _, r in contrast_df.iterrows():
    lines.append(f"| {r.contraste} | {r.prevalencia_expuesto:.1%} vs {r.prevalencia_referencia:.1%} | {100*r.diferencia_prevalencias:.1f} ({100*r.dp_ic95_inf:.1f}, {100*r.dp_ic95_sup:.1f}) | {r.razon_prevalencias:.2f} ({r.rp_ic95_inf:.2f}, {r.rp_ic95_sup:.2f}) |")
lines += [
    "",
    "## Decisión para las regresiones",
    "",
    "1. Ajustar modelos ponderados con `FACTORADULTO`.",
    "2. Presentar efectos ajustados mediante prevalencias marginales, diferencias y razones de prevalencia cuando sean estimables.",
    "3. Calcular incertidumbre principal mediante el mismo bootstrap estratificado, reajustando el modelo en cada réplica.",
    "4. Usar una covarianza sándwich ponderada a nivel individual como comprobación secundaria, no como corrección completa del diseño.",
    "5. No interpretar valores p aislados; priorizar magnitud, dirección, intervalos y consistencia entre especificaciones.",
    "6. Reetiquetar todo el bloque inferencial como aproximado hasta disponer de PSU o pesos replicados oficiales.",
    "",
    "## Qué permitiría inferencia completa",
    "",
    "Sería necesario obtener al menos uno de estos elementos: identificador anonimizado de sección censal, pesos jackknife/replicados o un servicio oficial que calcule errores para estimandos personalizados. Con cualquiera de ellos se sustituirá esta aproximación.",
]
(OUT / "informe_intervalos_aproximados.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

print(ci.to_string(index=False))
print("\n", contrast_df.to_string(index=False))
