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

# Columnas principales de IMPUESTO
COL_VIGENTE = "valor impuesto original"
COL_PROP2025 = "valor impuesto propuesta3"
COL_PROP_ANT = "valor impuesto propuesta anterior"

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
# 2. Carga y utilidades numéricas
# --------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def to_num(series: pd.Series) -> pd.Series:
    """
    Convierte una serie a numérico, soportando formato latino:
    1.234.567,89  -> 1234567.89
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    s = series.astype(str).str.replace(" ", "", regex=False)
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def safe_sum(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return np.nan
    return to_num(df[col]).fillna(0).sum()


# Cargar datos
try:
    df_raw = load_data(EXCEL_FILE)
except Exception as e:
    st.error(f"No se pudo cargar el archivo '{EXCEL_FILE}'. Detalle: {e}")
    st.stop()

df = df_raw.copy()


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
        'Actualización del esquema tarifario, impacto en el recaudo y distribución por actividad económica'
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
equivale a una disminución del 2,12%, evidenciando que la reforma no tiene un carácter recaudatorio sino 
redistributivo y correctivo.

Para la revisión tarifaria se analizaron las 530 actividades económicas del estatuto municipal, priorizando 
197 actividades donde se concentra la mayor parte de los contribuyentes activos. El nuevo esquema introduce 
tarifas diferenciadas según tamaño empresarial (micro, pequeña, mediana y gran empresa), lo que permite que 
los negocios con menor capacidad económica paguen proporcionalmente menos y que los aportes se ajusten a la 
magnitud real de cada operación económica.
"""

st.markdown(f'<p class="context-text">{contexto}</p>', unsafe_allow_html=True)


# --------------------------------------------------
# 4. Filtros laterales
# --------------------------------------------------
st.sidebar.title("Filtros")

mask = pd.Series(True, index=df.index)

if "AÑO" in df.columns:
    years = sorted(df["AÑO"].dropna().unique())
    selected_years = st.sidebar.multiselect("Año", years, default=years)
    mask &= df["AÑO"].isin(selected_years)

if "TIPO ACT" in df.columns:
    tipos = sorted(df["TIPO ACT"].dropna().unique())
    selected_tipo = st.sidebar.multiselect("Tipo actividad", tipos, default=tipos)
    mask &= df["TIPO ACT"].isin(selected_tipo)

if "TAMAÑO EMPRESA" in df.columns:
    tamanos = sorted(df["TAMAÑO EMPRESA"].dropna().unique())
    selected_tamano = st.sidebar.multiselect("Tamaño empresa", tamanos, default=tamanos)
    mask &= df["TAMAÑO EMPRESA"].isin(selected_tamano)

if "GRUPOS Y SUB" in df.columns:
    grupos = sorted(df["GRUPOS Y SUB"].dropna().unique())
    selected_grupo = st.sidebar.multiselect("Grupo CIIU", grupos, default=grupos)
    mask &= df["GRUPOS Y SUB"].isin(selected_grupo)

if "CONCLUSION" in df.columns:
    concs = sorted(df["CONCLUSION"].dropna().unique())
    selected_conc = st.sidebar.multiselect("Conclusión", concs, default=concs)
    mask &= df["CONCLUSION"].isin(selected_conc)

df_filt = df[mask].copy()

st.sidebar.markdown("---")
st.sidebar.write(f"Registros filtrados: **{df_filt.shape[0]}**")


# --------------------------------------------------
# 5. KPIs de IMPUESTO (solo impuesto, sin componentos)
# --------------------------------------------------
total_imp_vigente = safe_sum(df_filt, COL_VIGENTE)
total_imp_prop_2025 = safe_sum(df_filt, COL_PROP2025)
total_imp_prop_ant = safe_sum(df_filt, COL_PROP_ANT)

var_abs = total_imp_prop_2025 - total_imp_vigente
var_pct = (var_abs / total_imp_vigente * 100) if total_imp_vigente != 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Impuesto Vigente", f"${total_imp_vigente:,.0f}")

with col2:
    st.metric("Impuesto Propuesta 2025",
              f"${total_imp_prop_2025:,.0f}",
              delta=f"{var_pct:.2f} %",
              delta_color="inverse")

with col3:
    st.metric("Impuesto Propuesta Anterior", f"${total_imp_prop_ant:,.0f}")

with col4:
    if "CONCLUSION" in df_filt.columns:
        counts = df_filt["CONCLUSION"].value_counts()
        texto = " / ".join([f"{k}: {v}" for k, v in counts.items()])
        st.metric("Distribución Conclusión", f"{counts.sum()} registros", help=texto)


# --------------------------------------------------
# 6. Recaudo TOTAL (impuesto + avisos + sobretasa + sanciones + más)
# --------------------------------------------------
st.markdown("## Recaudo Total (todos los componentes del ingreso tributario)")

# Columnas de REC. vigente
columnas_recaudo_vig = [
    COL_VIGENTE,
    "AVISOS Y TABLEROS",
    "SOBRETASA BOMBERIL",
    "RETENCIONES",
    "AUTORETENCIONES",
    "SANCIONES",
    "VALOR A PAGAR",
]

col_v_exist = [c for c in columnas_recaudo_vig if c in df_filt.columns]

recaudo_total_vig = df_filt[col_v_exist].apply(to_num).fillna(0).sum().sum()

# Columnas propuesta 2025
columnas_recaudo_prop2025 = [
    COL_PROP2025,
    "AVISOS Y TABLEROS PROPUESTA2025",
    "SOBRETASA BOMBERIL PROPUESTA2025",
]

col_prop_exist = [c for c in columnas_recaudo_prop2025 if c in df_filt.columns]

recaudo_total_prop2025 = df_filt[col_prop_exist].apply(to_num).fillna(0).sum().sum()

colk1, colk2 = st.columns(2)
with colk1:
    st.metric("Recaudo Total Vigente", f"${recaudo_total_vig:,.0f}")
with colk2:
    st.metric("Recaudo Total Propuesta 2025", f"${recaudo_total_prop2025:,.0f}")


# --------------------------------------------------
# 7. Gráfico impuesto por escenario
# --------------------------------------------------
st.markdown("## Impuesto total por escenario")

df_plot = pd.DataFrame({
    "Escenario": ["Vigente", "Propuesta 2025", "Propuesta anterior"],
    "Impuesto": [total_imp_vigente, total_imp_prop_2025, total_imp_prop_ant]
})

fig = px.bar(df_plot, x="Escenario", y="Impuesto", text="Impuesto",
             title="Impuesto total (sin otros componentes)")
fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 8. Distribución conclusión
# --------------------------------------------------
if "CONCLUSION" in df_filt.columns:
    st.markdown("## Distribución de contribuyentes según variación")

    conclc = df_filt["CONCLUSION"].value_counts().reset_index()
    conclc.columns = ["CONCLUSION", "CONTRIBUYENTES"]

    fig_conc = px.bar(conclc, x="CONCLUSION", y="CONTRIBUYENTES",
                      text="CONTRIBUYENTES",
                      title="Cantidad de contribuyentes por conclusión")
    fig_conc.update_traces(textposition="outside")
    st.plotly_chart(fig_conc, use_container_width=True)


# --------------------------------------------------
# 9. Variación por actividad (top 15)
# --------------------------------------------------
st.markdown("## Actividades con mayor reducción del impuesto")

df_var = df_filt.copy()
df_var["DIF_IMP_ABS"] = to_num(df_var[COL_PROP2025]) - to_num(df_var[COL_VIGENTE])
df_var_top = df_var.sort_values("DIF_IMP_ABS").head(15)

df_var_top["Etiqueta"] = (
    df_var_top["CIIU"].astype(str) + " - " + df_var_top["DESCRIPCION"].astype(str)
)

fig_top = px.bar(
    df_var_top,
    x="DIF_IMP_ABS",
    y="Etiqueta",
    orientation="h",
    title="Top 15 actividades con mayor reducción",
)
st.plotly_chart(fig_top, use_container_width=True)


# --------------------------------------------------
# 10. Tarifas por tamaño empresarial
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
        value_name="Tarifa",
    )

    fig_t = px.bar(df_t_long, x="TAMAÑO EMPRESA", y="Tarifa", color="Escenario",
                   barmode="group", title="Tarifa promedio por tamaño empresarial")
    st.plotly_chart(fig_t, use_container_width=True)


# --------------------------------------------------
# 11. Tabla final
# --------------------------------------------------
st.markdown("## Tabla detallada")

cols_table = [
    "CIIU", "DESCRIPCION", "TAMAÑO EMPRESA", "RANGO UVT", "TIPO ACT",
    COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT,
    COL_VIGENTE, COL_PROP2025, COL_PROP_ANT,
    "CONCLUSION", "PORCENTAJE", "AÑO"
]

cols_present = [c for c in cols_table if c in df_filt.columns]

st.dataframe(df_filt[cols_present], use_container_width=True)
