from pathlib import Path
import json
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/esde2023_adultos_analitica.csv.gz"
OUT = ROOT / "reports/modelos"
OUT.mkdir(parents=True, exist_ok=True)

B = 1000
SEED = 20230826
EPS = 1e-9

d = pd.read_csv(DATA)

EXPOSURES = {
    "educacion": {"field": "educacion_3", "levels": ["alto", "medio", "bajo"], "reference": "alto"},
    "clase_social": {"field": "clase_social_1_6", "levels": [1, 2, 3, 4, 5, 6], "reference": 1},
    "ingresos": {"field": "ingresos_5", "levels": [5, 4, 3, 2, 1], "reference": 5},
}

MODELS = {
    "M0_bruto": [],
    "M1_edad_sexo": ["age_poly", "sexo"],
    "M2_principal": ["age_poly", "sexo", "origen", "ccaa"],
    "M3_actividad": ["age_poly", "sexo", "origen", "ccaa", "actividad"],
    "M4_apoyo": ["age_poly", "sexo", "origen", "ccaa", "actividad", "apoyo"],
}


def dummy_block(series, levels, reference, prefix):
    arrays, names = [], []
    for level in levels:
        if level == reference:
            continue
        arrays.append(series.eq(level).to_numpy(float))
        names.append(f"{prefix}[{level}]")
    return arrays, names


def build_matrix(df, spec, covariates, forced_exposure=None):
    n = len(df)
    arrays = [np.ones(n)]
    names = ["Intercepto"]
    exposure_series = df[spec["field"]] if forced_exposure is None else pd.Series(forced_exposure, index=df.index)
    a, nm = dummy_block(exposure_series, spec["levels"], spec["reference"], spec["field"])
    arrays += a; names += nm
    if "age_poly" in covariates:
        age10 = (df.edad.to_numpy(float) - 50) / 10
        arrays += [age10, age10**2]; names += ["edad_centrada_10", "edad_centrada_10_sq"]
    if "sexo" in covariates:
        arrays.append(df.SEXOa.eq(2).to_numpy(float)); names.append("mujer")
    if "origen" in covariates:
        arrays.append(df.nacido_extranjero.to_numpy(float)); names.append("nacido_extranjero")
    if "ccaa" in covariates:
        a, nm = dummy_block(df.ccaa, list(range(1,20)), 1, "ccaa")
        arrays += a; names += nm
    if "actividad" in covariates:
        a, nm = dummy_block(df.O2, [1,2,3,4], 1, "actividad_ocio")
        arrays += a; names += nm
    if "apoyo" in covariates:
        for field, levels, reference in [("S1",[1,2,3,4],4),("S2",[1,2,3,4,5],1),("S3",[1,2,3,4,5],1)]:
            a, nm = dummy_block(df[field], levels, reference, field)
            arrays += a; names += nm
    return np.column_stack(arrays), names


def expit(x):
    out = np.empty_like(x, dtype=float)
    pos = x >= 0
    out[pos] = 1 / (1 + np.exp(-x[pos]))
    ex = np.exp(x[~pos]); out[~pos] = ex / (1 + ex)
    return out


def fit_logit(X, y, weights, max_iter=80, tol=1e-9):
    beta = np.zeros(X.shape[1])
    weights = weights / np.mean(weights[weights > 0])
    converged = False
    for iteration in range(1, max_iter + 1):
        p = np.clip(expit(X @ beta), EPS, 1-EPS)
        score = X.T @ (weights * (y-p))
        h = X.T @ ((weights*p*(1-p))[:,None] * X)
        h.flat[::h.shape[0]+1] += 1e-8
        step = np.linalg.solve(h, score)
        beta_new = beta + step
        if np.max(np.abs(step)) < tol:
            beta = beta_new; converged = True; break
        beta = beta_new
    p = np.clip(expit(X @ beta), EPS, 1-EPS)
    loglik = float(np.sum(weights * (y*np.log(p)+(1-y)*np.log(1-p))))
    return beta, converged, iteration, loglik


def marginal_prevalences(df, spec, covariates, beta, standard_weights):
    result = {}
    sw = standard_weights / standard_weights.sum()
    for level in spec["levels"]:
        Xcf, _ = build_matrix(df, spec, covariates, forced_exposure=level)
        result[str(level)] = float(np.sum(sw * expit(Xcf @ beta)))
    return result


def required_fields(spec, model):
    fields = ["salud_menos_que_buena", "peso_adulto", "estrato_publico", spec["field"]]
    covars = MODELS[model]
    if "age_poly" in covars: fields += ["edad"]
    if "sexo" in covars: fields += ["SEXOa"]
    if "origen" in covars: fields += ["nacido_extranjero"]
    if "ccaa" in covars: fields += ["ccaa"]
    if "actividad" in covars: fields += ["O2"]
    if "apoyo" in covars: fields += ["S1","S2","S3"]
    return list(dict.fromkeys(fields))


model_rows, marginal_rows = [], []
fit_cache = {}
for exposure, spec in EXPOSURES.items():
    common_fields = required_fields(spec, "M4_apoyo")
    common_mask = d[common_fields].notna().all(axis=1) & ~d.O2.eq(9) & ~d.S1.eq(9) & ~d.S2.eq(9) & ~d.S3.eq(9)
    for model, covars in MODELS.items():
        fields = required_fields(spec, model)
        mask = d[fields].notna().all(axis=1)
        if "actividad" in covars: mask &= ~d.O2.eq(9)
        if "apoyo" in covars: mask &= ~d.S1.eq(9) & ~d.S2.eq(9) & ~d.S3.eq(9)
        # M0-M4 also fitted on a common sample to make attenuation interpretable.
        samples = [("disponible", mask)]
        if model in MODELS:
            samples.append(("comun_M0_M4", common_mask))
        for sample_name, smask in samples:
            df = d.loc[smask].copy()
            X, names = build_matrix(df, spec, covars)
            y = df.salud_menos_que_buena.to_numpy(float)
            weights = df.peso_adulto.to_numpy(float)
            beta, converged, iterations, loglik = fit_logit(X,y,weights)
            model_rows.append({"exposicion":exposure,"modelo":model,"muestra":sample_name,"n":len(df),"p":X.shape[1],"converge":converged,"iteraciones":iterations,"loglik_ponderada_normalizada":loglik})
            prev = marginal_prevalences(df,spec,covars,beta,weights)
            ref = str(spec["reference"]); pref=prev[ref]
            for level in spec["levels"]:
                lev=str(level); plev=prev[lev]
                marginal_rows.append({"exposicion":exposure,"modelo":model,"muestra":sample_name,"categoria":lev,"referencia":ref,"n":len(df),"prevalencia_ajustada":plev,"diferencia_vs_ref":plev-pref,"razon_vs_ref":plev/pref})
            if model == "M2_principal" and sample_name == "disponible":
                fit_cache[exposure] = (df, X, beta, covars, spec, weights)

models = pd.DataFrame(model_rows)
marginals = pd.DataFrame(marginal_rows)
models.to_csv(OUT/"diagnostico_modelos.csv",index=False,encoding="utf-8-sig")
marginals.to_csv(OUT/"prevalencias_marginales_modelos.csv",index=False,encoding="utf-8-sig",float_format="%.8f")

# Bootstrap estratificado con refit completo del modelo principal M2.
rng = np.random.default_rng(SEED)
boot_rows=[]
for exposure,(df,X,beta,covars,spec,base_weights) in fit_cache.items():
    y=df.salud_menos_que_buena.to_numpy(float); strata=df.estrato_publico.to_numpy(int)
    stratum_indices=[np.flatnonzero(strata==h) for h in sorted(np.unique(strata))]
    cf={str(level):build_matrix(df,spec,covars,forced_exposure=level)[0] for level in spec["levels"]}
    ref=str(spec["reference"])
    for b in range(B):
        counts=np.zeros(len(df),dtype=float)
        for idx in stratum_indices:
            counts[idx]=rng.multinomial(len(idx),np.full(len(idx),1/len(idx)))
        wb=base_weights*counts
        try:
            bb,conv,it,ll=fit_logit(X,y,wb,max_iter=60,tol=1e-8)
            if not conv: continue
            sw=wb/wb.sum()
            prev={lev:float(np.sum(sw*expit(mat@bb))) for lev,mat in cf.items()}
            pref=prev[ref]
            for lev,pv in prev.items():
                boot_rows.append({"exposicion":exposure,"replica":b,"categoria":lev,"prevalencia":pv,"diferencia_vs_ref":pv-pref,"razon_vs_ref":pv/pref})
        except np.linalg.LinAlgError:
            continue

boot=pd.DataFrame(boot_rows)
boot.to_csv(OUT/"bootstrap_m2_replicas.csv.gz",index=False,compression="gzip",encoding="utf-8")

primary=marginals.query("modelo=='M2_principal' and muestra=='disponible'").copy()
final=[]
for _,r in primary.iterrows():
    b=boot[(boot.exposicion==r.exposicion)&(boot.categoria.astype(str)==str(r.categoria))]
    final.append({
        **r.to_dict(),
        "replicas_validas":b.replica.nunique(),
        "prev_ic95_inf":b.prevalencia.quantile(.025),"prev_ic95_sup":b.prevalencia.quantile(.975),
        "dp_ic95_inf":b.diferencia_vs_ref.quantile(.025),"dp_ic95_sup":b.diferencia_vs_ref.quantile(.975),
        "rp_ic95_inf":b.razon_vs_ref.quantile(.025),"rp_ic95_sup":b.razon_vs_ref.quantile(.975),
    })
final=pd.DataFrame(final)
final.to_csv(OUT/"contrastes_ajustados_m2.csv",index=False,encoding="utf-8-sig",float_format="%.8f")

# Quantify attenuation on a common sample using extreme categories.
extremes={"educacion":("bajo","alto"),"clase_social":("6","1"),"ingresos":("1","5")}
atten=[]
for exposure,(adverse,reference) in extremes.items():
    for model in MODELS:
        t=marginals.query("exposicion==@exposure and modelo==@model and muestra=='comun_M0_M4'").set_index("categoria")
        pa=t.loc[adverse,"prevalencia_ajustada"]; pr=t.loc[reference,"prevalencia_ajustada"]
        atten.append({"exposicion":exposure,"modelo":model,"n":int(t.iloc[0].n),"prevalencia_desfavorecida":pa,"prevalencia_referencia":pr,"diferencia_prevalencias":pa-pr,"razon_prevalencias":pa/pr})
atten=pd.DataFrame(atten)
atten.to_csv(OUT/"atenuacion_modelos_muestra_comun.csv",index=False,encoding="utf-8-sig",float_format="%.8f")

failed=int((~models.converge).sum())
summary={"bootstrap_requested":B,"seed":SEED,"model_fits":len(models),"failed_point_fits":failed,"bootstrap_valid_by_exposure":boot.groupby('exposicion').replica.nunique().to_dict()}
(OUT/"modelos_metadata.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

lines=[
"# Contrastes ajustados y regresiones ponderadas","",
"**Resultado:** salud autopercibida regular, mala o muy mala.  ",
"**Modelo principal:** regresión logística ponderada, estandarización marginal y bootstrap estratificado aproximado.  ",
"**Advertencia:** los IC no incorporan la sección censal y no equivalen a los errores oficiales.","",
"## Especificación","",
"- M0: exposición sin ajuste.",
"- M1: edad (término lineal y cuadrático) y sexo.",
"- M2 principal: M1 + país de nacimiento + comunidad autónoma.",
"- M3: M2 + actividad física en tiempo libre.",
"- M4: M3 + tres indicadores de apoyo social.",
"- Cada exposición se ajusta en un modelo separado.",
"- La atenuación M0–M4 se calcula sobre una muestra común por exposición.","",
"## Resultados principales M2","",
"| Exposición | Categoría | n | Prevalencia ajustada (IC95%) | Diferencia vs referencia, pp (IC95%) | Razón vs referencia (IC95%) |",
"|---|---|---:|---:|---:|---:|",
]
def fmt_n(value): return f"{int(value):,}".replace(",", ".")
for _,r in final.iterrows():
    if str(r.categoria)==str(r.referencia):
        dp="Referencia"; rp="Referencia"
    else:
        dp=f"{100*r.diferencia_vs_ref:.1f} ({100*r.dp_ic95_inf:.1f}, {100*r.dp_ic95_sup:.1f})"
        rp=f"{r.razon_vs_ref:.2f} ({r.rp_ic95_inf:.2f}, {r.rp_ic95_sup:.2f})"
    lines.append(f"| {r.exposicion} | {r.categoria} | {fmt_n(r.n)} | {r.prevalencia_ajustada:.1%} ({r.prev_ic95_inf:.1%}, {r.prev_ic95_sup:.1%}) | {dp} | {rp} |")
lines += ["","## Atenuación en muestra común","","| Exposición | Modelo | n | Diferencia extremos, pp | Razón extremos |","|---|---|---:|---:|---:|"]
for _,r in atten.iterrows(): lines.append(f"| {r.exposicion} | {r.modelo} | {fmt_n(r.n)} | {100*r.diferencia_prevalencias:.1f} | {r.razon_prevalencias:.2f} |")
lines += ["","## Interpretación","",
"Los resultados M2 son asociaciones ajustadas, no efectos causales. La estandarización traduce los modelos a prevalencias comparables y evita depender exclusivamente de odds ratios. Los cambios entre M2, M3 y M4 son compatibles con atenuación por actividad física o apoyo social, pero no demuestran mediación.","",
"## Diagnóstico","",f"- Ajustes puntuales: {len(models)}.",f"- Ajustes puntuales sin convergencia: {failed}."]
for exposure,nrep in summary["bootstrap_valid_by_exposure"].items(): lines.append(f"- Réplicas bootstrap M2 válidas para {exposure}: {nrep} de {B}.")
(OUT/"informe_regresiones_ponderadas.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

print(json.dumps(summary,ensure_ascii=False,indent=2))
print(final.to_string(index=False))
print(atten.to_string(index=False))
