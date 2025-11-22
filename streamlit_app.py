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

# Columnas principales de IMPUESTO (no recaudo total)
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


try:
    df_raw = load_data(EXCEL_FILE)
except Exception as e:
    st.error(
        f"No se pudo cargar el archivo '{EXCEL_FILE}'. "
        f"Verifica que el nombre y la ubicación sean correctos.\n\nDetalle: {e}"
    )
    st.stop()

df = df_raw.copy()

# --------------------------------------------------
# 3. Encabezado
# --------------------------------------------------
col_logo_legal, col_title, col_logo_mun = st.columns([1, 4, 1])

with col_logo_legal:
    try:
        st.image(LOGO_LEGAL_PATH, width=100)
    except Exception:
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
    except Exception:
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

if "AÑO" in df.columns:
    years = sorted(df["AÑO"].dropna().unique())
    selected_years = st.sidebar.multiselect("Año de declaración", years, default=years)
else:
    selected_years = None

if "TIPO ACT" in df.columns:
    tipos_act = sorted(df["TIPO ACT"].dropna().unique())
    selected_tipo = st.sidebar.multiselect("Tipo de actividad", tipos_act, default=tipos_act)
else:
    selected_tipo = None

if "TAMAÑO EMPRESA" in df.columns:
    tamanos = sorted(df["TAMAÑO EMPRESA"].dropna().unique())
    selected_tamano = st.sidebar.multiselect("Tamaño de empresa", tamanos, default=tamanos)
else:
    selected_tamano = None

if "GRUPOS Y SUB" in df.columns:
    grupos = sorted(df["GRUPOS Y SUB"].dropna().unique())
    selected_grupos = st.sidebar.multiselect("Grupo CIIU (primeros 2 dígitos)", grupos, default=grupos)
else:
    selected_grupos = None

if "CONCLUSION" in df.columns:
    conclusiones = sorted(df["CONCLUSION"].dropna().unique())
    selected_conclusion = st.sidebar.multiselect("Conclusión (aumenta/disminuye/igual)",
                                                 conclusiones, default=conclusiones)
else:
    selected_conclusion = None

mask = pd.Series(True, index=df.index)

if selected_years:
    mask &= df["AÑO"].isin(selected_years)
if selected_tipo:
    mask &= df["TIPO ACT"].isin(selected_tipo)
if selected_tamano:
    mask &= df["TAMAÑO EMPRESA"].isin(selected_tamano)
if selected_grupos:
    mask &= df["GRUPOS Y SUB"].isin(selected_grupos)
if selected_conclusion:
    mask &= df["CONCLUSION"].isin(selected_conclusion)

df_filt = df[mask].copy()
st.sidebar.markdown("---")
st.sidebar.write(f"Registros filtrados: **{df_filt.shape[0]}**")


# --------------------------------------------------
# 5. KPIs de IMPUESTO (solo valor de impuesto)
# --------------------------------------------------
total_imp_vigente = safe_sum(df_filt, COL_VIGENTE)
total_imp_prop_2025 = safe_sum(df_filt, COL_PROP2025)
total_imp_prop_ant = safe_sum(df_filt, COL_PROP_ANT)

var_abs = total_imp_prop_2025 - total_imp_vigente
var_pct = (var_abs / total_imp_vigente * 100) if total_imp_vigente != 0 else np.nan

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Recaudo de Impuesto Vigente", f"${total_imp_vigente:,.0f}")

with col2:
    st.metric("Recaudo de Impuesto Propuesta 2025",
              f"${total_imp_prop_2025:,.0f}",
              delta=f"{var_pct:.2f} %",
              delta_color="inverse")

with col3:
    st.metric("Recaudo de Impuesto Propuesta Anterior", f"${total_imp_prop_ant:,.0f}")

with col4:
    if "CONCLUSION" in df_filt.columns:
        counts = df_filt["CONCLUSION"].value_counts()
        total_reg = counts.sum()
        texto = " / ".join([f"{k}: {v}" for k, v in counts.items()])
        st.metric("Distribución conclusión", f"{total_reg} registros", help=texto)
    else:
        st.metric("Registros", df_filt.shape[0])


# --------------------------------------------------
# 6. Recaudo TOTAL (impuesto + otros componentes)
# --------------------------------------------------
st.markdown("## Recaudo Total Vigente y Propuesta 2025 (todos los componentes)")

# Columnas de recaudo vigente
columnas_recaudo_vigente = [
    COL_VIGENTE,
    "AVISOS Y TABLEROS",
    "SOBRETASA BOMBERIL",
    "RETENCIONES",
    "AUTORETENCIONES",
    "SANCIONES",
    "VALOR A PAGAR",
]

col_vig_exist = [c for c in columnas_recaudo_vigente if c in df_filt.columns]
recaudo_total_vigente = to_num(df_filt[col_vig_exist]).fillna(0).sum().sum()

# Columnas de recaudo propuesta 2025
columnas_recaudo_prop2025 = [
    COL_PROP2025,
    "AVISOS Y TABLEROS PROPUESTA2025",
    "SOBRETASA BOMBERIL PROPUESTA2025",
    # agrega aquí otras columnas de propuesta si las tienes (retenciones, etc.)
]

col_prop_exist = [c for c in columnas_recaudo_prop2025 if c in df_filt.columns]
recaudo_total_prop2025 = to_num(df_filt[col_prop_exist]).fillna(0).sum().sum()

colt1, colt2 = st.columns(2)
with colt1:
    st.metric("Recaudo Total Vigente", f"${recaudo_total_vigente:,.0f}")
with colt2:
    st.metric("Recaudo Total Propuesta 2025", f"${recaudo_total_prop2025:,.0f}")


# --------------------------------------------------
# 7. Gráfico de IMPUESTO por escenario
# --------------------------------------------------
st.markdown("## Comportamiento del impuesto por escenario")

df_escenarios = pd.DataFrame(
    {
        "Escenario": ["Vigente", "Propuesta 2025", "Propuesta anterior"],
        "Impuesto": [total_imp_vigente, total_imp_prop_2025, total_imp_prop_ant],
    }
)

fig_escenarios = px.bar(
    df_escenarios,
    x="Escenario",
    y="Impuesto",
    text="Impuesto",
    title="Impuesto total por escenario (sin otros componentes)",
)
fig_escenarios.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
fig_escenarios.update_layout(yaxis_title="Valor ($)", xaxis_title="")
st.plotly_chart(fig_escenarios, use_container_width=True)


# --------------------------------------------------
# 8. Distribución de aumento / disminución
# --------------------------------------------------
if "CONCLUSION" in df_filt.columns:
    st.markdown("## Distribución de contribuyentes según conclusión")

    concl_counts = df_filt["CONCLUSION"].value_counts().reset_index()
    concl_counts.columns = ["CONCLUSION", "CONTRIBUYENTES"]

    fig_concl = px.bar(
        concl_counts,
        x="CONCLUSION",
        y="CONTRIBUYENTES",
        text="CONTRIBUYENTES",
        title="Número de contribuyentes por tipo de variación del impuesto",
    )
    fig_concl.update_traces(textposition="outside")
    st.plotly_chart(fig_concl, use_container_width=True)


# --------------------------------------------------
# 9. Top actividades por variación del impuesto
# --------------------------------------------------
st.markdown("## Actividades con mayor variación del impuesto (Propuesta 2025 vs Vigente)")

if COL_VIGENTE in df_filt.columns and COL_PROP2025 in df_filt.columns:
    df_var = df_filt.copy()
    df_var["DIF_IMP_ABS"] = to_num(df_var[COL_PROP2025]) - to_num(df_var[COL_VIGENTE])

    df_var_top = df_var.sort_values("DIF_IMP_ABS").head(15)

    if "DESCRIPCION" in df_var_top.columns:
        df_var_top["Etiqueta"] = df_var_top["CIIU"].astype(str) + " - " + df_var_top["DESCRIPCION"].astype(str)
    else:
        df_var_top["Etiqueta"] = df_var_top["CIIU"].astype(str)

    fig_top = px.bar(
        df_var_top,
        x="DIF_IMP_ABS",
        y="Etiqueta",
        orientation="h",
        title="Top 15 actividades con mayor reducción del impuesto",
        labels={"DIF_IMP_ABS": "Diferencia (Propuesta 2025 - Vigente)", "Etiqueta": "Actividad"},
    )
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.info("No se encontraron las columnas necesarias para calcular la variación por actividad.")


# --------------------------------------------------
# 10. Esquema tarifario por tamaño empresarial
# --------------------------------------------------
st.markdown("## Esquema tarifario por tamaño empresarial")

if all(c in df_filt.columns for c in [COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT, "TAMAÑO EMPRESA"]):
    df_tarifas = df_filt.groupby("TAMAÑO EMPRESA")[
        [COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT]
    ].mean().reset_index()

    df_tarifas_long = df_tarifas.melt(
        id_vars="TAMAÑO EMPRESA",
        value_vars=[COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT],
        var_name="Escenario",
        value_name="Tarifa promedio",
    )

    fig_tarifas = px.bar(
        df_tarifas_long,
        x="TAMAÑO EMPRESA",
        y="Tarifa promedio",
        color="Escenario",
        barmode="group",
        title="Tarifa promedio por tamaño empresarial y escenario",
    )
    st.plotly_chart(fig_tarifas, use_container_width=True)
else:
    st.info("No se encontraron todas las columnas para analizar tarifas por tamaño empresarial.")


# --------------------------------------------------
# 11. Tabla de detalle
# --------------------------------------------------
st.markdown("## Detalle de actividades")

cols_tabla = []
for c in [
    "CIIU",
    "DESCRIPCION",
    "TAMAÑO EMPRESA",
    "RANGO UVT",
    "TIPO ACT",
    COL_TARIFA_ORIG,
    COL_TARIFA_2025,
    COL_TARIFA_ANT,
    COL_VIGENTE,
    COL_PROP2025,
    COL_PROP_ANT,
    "CONCLUSION",
    "PORCENTAJE",
    "AÑO",
]:
    if c in df_filt.columns:
        cols_tabla.append(c)

if cols_tabla:
    st.dataframe(
        df_filt[cols_tabla].sort_values(by=["AÑO", "CIIU"], ascending=True),
        use_container_width=True,
    )
else:
    st.info("No se encontraron columnas suficientes para mostrar la tabla de detalle.")


