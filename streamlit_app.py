import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# 0. Configuración inicial
# --------------------------------------------------
st.set_page_config(
    page_title="Análisis ICA Segovia",
    layout="wide",
    initial_sidebar_state="expanded"
)

EXCEL_FILE = "MATRIZ_ICA_DEFINITIVA 22-11-2025.xlsx"  # AJUSTA SI CAMBIA EL NOMBRE

LOGO_LEGAL_PATH = "logo_legal.png"
LOGO_MUNICIPIO_PATH = "logo_segovia.png"

# Columnas del análisis técnico de impuesto (matriz completa priorizada)
COL_IMP_VIG_MAT = "VL IMPUESTO VIGENTE"
COL_IMP_PROP2025_MAT = "VALOR IMP PROPUESTA3"
COL_IMP_PROPANT_MAT = "VL IMPUESTO  PROPUESTA ANT"

# Columnas de impuesto según sistema de información
COL_IMP_VIG_SYS = "valor impuesto original"
COL_IMP_PROP2025_SYS = "valor impuesto propuesta3"
COL_IMP_PROPANT_SYS = "valor impuesto propuesta anterior"

# Columnas tarifarias
COL_TARIFA_ORIG = "TARIFA ORIGINAL"
COL_TARIFA_2025 = "PROPUESTA 2025"
COL_TARIFA_ANT = "PROPUESTA ANT"

# --------------------------------------------------
# 1. Estilos
# --------------------------------------------------
st.markdown(
    """
<style>
.header-container {
    text-align: center;
    padding-bottom: 20px;
}
.main-title {
    font-size: 2.4em;
    font-weight: bold;
    color: #004c99;
    margin-bottom: 0px;
}
.subtitle {
    font-size: 1.1em;
    color: #555555;
    margin-top: 5px;
}
.context-text {
    font-size: 0.95em;
    color: #333333;
    margin-top: 15px;
    margin-bottom: 30px;
    padding: 10px 0;
    border-top: 1px solid #dddddd;
    text-align: justify;
}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 2. Carga de datos y utilidades
# --------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def safe_sum(df: pd.DataFrame, col: str) -> float:
    """Suma una columna convirtiendo a numérico y manejando NaN."""
    if col not in df.columns:
        return np.nan
    return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()


# Cargar datos
try:
    df_raw = load_data(EXCEL_FILE)
except Exception as e:
    st.error(f"No se pudo cargar el archivo '{EXCEL_FILE}'. Detalle: {e}")
    st.stop()

df = df_raw.copy()

# Subconjunto base de análisis: solo filas con impuesto original (las 1053 válidas)
if COL_IMP_VIG_SYS in df.columns:
    df_base = df[df[COL_IMP_VIG_SYS].notna()].copy()
else:
    df_base = df.copy()


# --------------------------------------------------
# 3. Encabezado
# --------------------------------------------------
col_logo_legal, col_title, col_logo_mun = st.columns([1, 4, 1])

with col_logo_legal:
    try:
        st.image(LOGO_LEGAL_PATH, width=100)
    except:
        st.warning(f"Logo '{LOGO_LEGAL_PATH}' no encontrado.")

with col_title:
    st.markdown(
        '<div class="header-container"><p class="main-title">'
        'ANÁLISIS DEL IMPUESTO DE INDUSTRIA Y COMERCIO - SEGOVIA, ANTIOQUIA'
        '</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="header-container"><p class="subtitle">'
        'Actualización del esquema tarifario, impacto en el impuesto y en el recaudo'
        '</p></div>',
        unsafe_allow_html=True,
    )

with col_logo_mun:
    try:
        st.image(LOGO_MUNICIPIO_PATH, width=100)
    except:
        st.warning(f"Logo '{LOGO_MUNICIPIO_PATH}' no encontrado.")

contexto = """
La actualización del esquema tarifario del Impuesto de Industria y Comercio en el municipio de Segovia 
representa una reforma orientada a aliviar la carga tributaria, promover la formalización y ajustar las 
tarifas a la realidad económica del territorio. El análisis técnico demuestra que, en términos generales, 
el impuesto experimenta una reducción real: el valor total pasa de $8.668.859.820 a $8.492.448.621, lo que 
equivale a una disminución cercana al 2%, evidenciando que la reforma no tiene un carácter recaudatorio sino 
redistributivo y correctivo.

Para la revisión tarifaria se analizaron las actividades económicas del estatuto municipal, priorizando 
aquellas donde se concentran los contribuyentes activos. El nuevo esquema introduce tarifas diferenciadas 
según tamaño empresarial (micro, pequeña, mediana y gran empresa), lo que permite que los negocios con menor 
capacidad económica paguen proporcionalmente menos y que los aportes se ajusten a la magnitud real de cada 
operación económica.
"""

st.markdown(f'<p class="context-text">{contexto}</p>', unsafe_allow_html=True)


# --------------------------------------------------
# 4. Filtros laterales
# --------------------------------------------------
st.sidebar.title("Filtros")

mask = pd.Series(True, index=df_base.index)

if "AÑO" in df_base.columns:
    years = sorted(df_base["AÑO"].dropna().unique())
    selected_years = st.sidebar.multiselect("Año", years, default=years)
    mask &= df_base["AÑO"].isin(selected_years)

if "TIPO ACT" in df_base.columns:
    tipos = sorted(df_base["TIPO ACT"].dropna().unique())
    selected_tipo = st.sidebar.multiselect("Tipo actividad", tipos, default=tipos)
    mask &= df_base["TIPO ACT"].isin(selected_tipo)

if "TAMAÑO EMPRESA" in df_base.columns:
    tamanos = sorted(df_base["TAMAÑO EMPRESA"].dropna().unique())
    selected_tamano = st.sidebar.multiselect("Tamaño empresa", tamanos, default=tamanos)
    mask &= df_base["TAMAÑO EMPRESA"].isin(selected_tamano)

if "GRUPOS Y SUB" in df_base.columns:
    grupos = sorted(df_base["GRUPOS Y SUB"].dropna().unique())
    selected_grupo = st.sidebar.multiselect("Grupo CIIU", grupos, default=grupos)
    mask &= df_base["GRUPOS Y SUB"].isin(selected_grupo)

if "CONCLUSION" in df_base.columns:
    concs = sorted(df_base["CONCLUSION"].dropna().unique())
    selected_conc = st.sidebar.multiselect("Conclusión", concs, default=concs)
    mask &= df_base["CONCLUSION"].isin(selected_conc)

df_filt = df_base[mask].copy()

st.sidebar.markdown("---")
st.sidebar.write(f"Registros filtrados: **{df_filt.shape[0]}**")


# --------------------------------------------------
# 5. KPIs 1: Suma de valores de IMPUESTO (matriz técnica)
# --------------------------------------------------
imp_vig_mat = safe_sum(df_filt, COL_IMP_VIG_MAT)
imp_prop2025_mat = safe_sum(df_filt, COL_IMP_PROP2025_MAT)
imp_propant_mat = safe_sum(df_filt, COL_IMP_PROPANT_MAT)

var_abs_mat = imp_prop2025_mat - imp_vig_mat
var_pct_mat = (var_abs_mat / imp_vig_mat * 100) if imp_vig_mat != 0 else 0

st.markdown("### Suma de valores del impuesto (matriz técnica de escenarios)")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Impuesto Vigente (matriz)", f"${imp_vig_mat:,.0f}")

with c2:
    st.metric(
        "Impuesto Propuesta 2025 (matriz)",
        f"${imp_prop2025_mat:,.0f}",
        delta=f"{var_pct_mat:.2f} %",
        delta_color="inverse"
    )

with c3:
    st.metric("Impuesto Propuesta anterior (matriz)", f"${imp_propant_mat:,.0f}")

with c4:
    if "CONCLUSION" in df_filt.columns:
        counts = df_filt["CONCLUSION"].value_counts()
        texto = " / ".join([f"{k}: {v}" for k, v in counts.items()])
        st.metric("Distribución conclusión", f"{counts.sum()} registros", help=texto)


# --------------------------------------------------
# 6. KPIs 2: Impuesto según sistema + valor de recaudo (VALOR A PAGAR)
# --------------------------------------------------
st.markdown("### Impuesto según sistema de información y recaudo neto")

imp_vig_sys = safe_sum(df_filt, COL_IMP_VIG_SYS)
imp_prop2025_sys = safe_sum(df_filt, COL_IMP_PROP2025_SYS)
imp_propant_sys = safe_sum(df_filt, COL_IMP_PROPANT_SYS)
recaudo_vig = safe_sum(df_filt, "VALOR A PAGAR")

var_abs_sys = imp_prop2025_sys - imp_vig_sys
var_pct_sys = (var_abs_sys / imp_vig_sys * 100) if imp_vig_sys != 0 else 0

d1, d2, d3, d4 = st.columns(4)

with d1:
    st.metric("Impuesto Vigente (sistema)", f"${imp_vig_sys:,.0f}")

with d2:
    st.metric(
        "Impuesto Propuesta 2025 (sistema)",
        f"${imp_prop2025_sys:,.0f}",
        delta=f"{var_pct_sys:.2f} %",
        delta_color="inverse",
    )

with d3:
    st.metric("Impuesto Propuesta anterior (sistema)", f"${imp_propant_sys:,.0f}")

with d4:
    st.metric("Recaudo neto Vigente (VALOR A PAGAR)", f"${recaudo_vig:,.0f}")


# --------------------------------------------------
# 7. Gráfico impuesto por escenario (matriz técnica)
# --------------------------------------------------
st.markdown("## Impuesto total por escenario (matriz técnica)")

df_plot = pd.DataFrame({
    "Escenario": ["Vigente", "Propuesta 2025", "Propuesta anterior"],
    "Impuesto": [imp_vig_mat, imp_prop2025_mat, imp_propant_mat],
})

fig_imp = px.bar(
    df_plot,
    x="Escenario",
    y="Impuesto",
    text="Impuesto",
    title="Impuesto total por escenario",
)
fig_imp.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_imp, use_container_width=True)


# --------------------------------------------------
# 8. Distribución de conclusión
# --------------------------------------------------
if "CONCLUSION" in df_filt.columns:
    st.markdown("## Distribución de contribuyentes según variación del impuesto")

    conclc = df_filt["CONCLUSION"].value_counts().reset_index()
    conclc.columns = ["CONCLUSION", "CONTRIBUYENTES"]

    fig_conc = px.bar(
        conclc,
        x="CONCLUSION",
        y="CONTRIBUYENTES",
        text="CONTRIBUYENTES",
        title="Cantidad de contribuyentes por conclusión",
    )
    fig_conc.update_traces(textposition="outside")
    st.plotly_chart(fig_conc, use_container_width=True)


# --------------------------------------------------
# 9. Actividades con mayor reducción del impuesto (matriz)
# --------------------------------------------------
st.markdown("## Actividades con mayor reducción del impuesto (Propuesta 2025 vs Vigente)")

df_var = df_filt.copy()
df_var["DIF_IMP_ABS"] = pd.to_numeric(df_var[COL_IMP_PROP2025_MAT], errors="coerce") - \
                        pd.to_numeric(df_var[COL_IMP_VIG_MAT], errors="coerce")

df_var_top = df_var.sort_values("DIF_IMP_ABS").head(15)
df_var_top["Etiqueta"] = df_var_top["CIIU"].astype(str) + " - " + df_var_top["DESCRIPCION"].astype(str)

fig_top = px.bar(
    df_var_top,
    x="DIF_IMP_ABS",
    y="Etiqueta",
    orientation="h",
    title="Top 15 actividades con mayor reducción del impuesto",
    labels={"DIF_IMP_ABS": "Diferencia (Propuesta 2025 - Vigente)", "Etiqueta": "Actividad"},
)
st.plotly_chart(fig_top, use_container_width=True)


# --------------------------------------------------
# 10. Tarifas promedio por tamaño empresarial
# --------------------------------------------------
st.markdown("## Tarifas promedio por tamaño empresarial")

if all(c in df_filt.columns for c in [COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT, "TAMAÑO EMPRESA"]):
    df_t = df_filt.groupby("TAMAÑO EMPRESA")[
        [COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT]
    ].mean().reset_index()

    df_t_long = df_t.melt(
        id_vars="TAMAÑO EMPRESA",
        value_vars=[COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT],
        var_name="Escenario",
        value_name="Tarifa promedio",
    )

    fig_t = px.bar(
        df_t_long,
        x="TAMAÑO EMPRESA",
        y="Tarifa promedio",
        color="Escenario",
        barmode="group",
        title="Tarifa promedio por tamaño empresarial",
    )
    st.plotly_chart(fig_t, use_container_width=True)


# --------------------------------------------------
# 11. Tabla detallada
# --------------------------------------------------
st.markdown("## Detalle de actividades y escenarios")

cols_table = [
    "CIIU", "DESCRIPCION", "TAMAÑO EMPRESA", "RANGO UVT", "TIPO ACT",
    COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT,
    COL_IMP_VIG_MAT, COL_IMP_PROP2025_MAT, COL_IMP_PROPANT_MAT,
    COL_IMP_VIG_SYS, COL_IMP_PROP2025_SYS, COL_IMP_PROPANT_SYS,
    "VALOR A PAGAR", "CONCLUSION", "PORCENTAJE", "AÑO"
]

cols_present = [c for c in cols_table if c in df_filt.columns]

st.dataframe(df_filt[cols_present], use_container_width=True)
