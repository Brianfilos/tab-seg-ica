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

EXCEL_FILE = "MATRIZ_ICA_DEFINITIVA 22-11-2025.xlsx"

LOGO_LEGAL_PATH = "logo_legal.png"
LOGO_MUNICIPIO_PATH = "logo_segovia.png"

# Columnas del análisis técnico de impuesto
COL_IMP_VIG_MAT = "VL IMPUESTO VIGENTE"
COL_IMP_PROP2025_MAT = "VALOR IMP PROPUESTA3"
COL_IMP_PROPANT_MAT = "VL IMPUESTO  PROPUESTA ANT"

# Columnas del sistema
COL_IMP_VIG_SYS = "valor impuesto original"
COL_IMP_PROP2025_SYS = "valor impuesto propuesta3"
COL_IMP_PROPANT_SYS = "valor impuesto propuesta anterior"

# Columnas tarifarias
COL_TARIFA_ORIG = "TARIFA ORIGINAL"
COL_TARIFA_2025 = "PROPUESTA 2025"
COL_TARIFA_ANT = "PROPUESTA ANT"

# --------------------------------------------------
# Funciones
# --------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data(path):
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    return df

def safe_sum(df, col):
    if col not in df.columns:
        return 0
    return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()


# --------------------------------------------------
# 1. Cargar datos
# --------------------------------------------------
try:
    df = load_data(EXCEL_FILE)
except Exception as e:
    st.error(f"Error cargando archivo: {e}")
    st.stop()

# Subconjunto base de análisis → filas con impuesto original (1053 filas)
df_base = df[df[COL_IMP_VIG_SYS].notna()].copy()


# --------------------------------------------------
# 2. Encabezado
# --------------------------------------------------
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    try:
        st.image(LOGO_LEGAL_PATH, width=100)
    except:
        pass

with col2:
    st.markdown(
        '<h1 style="text-align:center;color:#004c99;">ANÁLISIS DEL IMPUESTO DE INDUSTRIA Y COMERCIO – SEGOVIA</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="text-align:center;font-size:18px;color:#555;">Impacto del nuevo esquema tarifario y comportamiento del recaudo</p>',
        unsafe_allow_html=True
    )

with col3:
    try:
        st.image(LOGO_MUNICIPIO_PATH, width=100)
    except:
        pass


# --------------------------------------------------
# 3. KPIs – SUMAS EXACTAS DEL EXCEL
# --------------------------------------------------

st.markdown("## 🔵 Suma total de valores del impuesto (Matriz técnica)")

imp_vig = safe_sum(df_base, COL_IMP_VIG_MAT)
imp_prop2025 = safe_sum(df_base, COL_IMP_PROP2025_MAT)
imp_propant = safe_sum(df_base, COL_IMP_PROPANT_MAT)

var_abs = imp_prop2025 - imp_vig
var_pct = (var_abs / imp_vig * 100) if imp_vig != 0 else 0

k1, k2, k3, k4 = st.columns(4)

k1.metric("Vigente", f"${imp_vig:,.0f}")
k2.metric("Propuesta 2025", f"${imp_prop2025:,.0f}", delta=f"{var_pct:.2f}%", delta_color="inverse")
k3.metric("Propuesta anterior", f"${imp_propant:,.0f}")
k4.metric("Variación absoluta", f"${var_abs:,.0f}")


# --------------------------------------------------
# 4. KPIs – Impuesto del sistema + Recaudo real
# --------------------------------------------------

st.markdown("## 🟢 Impuesto según sistema + Recaudo")

imp_vig_sys = safe_sum(df_base, COL_IMP_VIG_SYS)
imp_prop2025_sys = safe_sum(df_base, COL_IMP_PROP2025_SYS)
imp_propant_sys = safe_sum(df_base, COL_IMP_PROPANT_SYS)
recaudo_vig = safe_sum(df_base, "VALOR A PAGAR")

v1, v2, v3, v4 = st.columns(4)

v1.metric("Impuesto Vigente (sistema)", f"${imp_vig_sys:,.0f}")
v2.metric("Propuesta 2025 (sistema)", f"${imp_prop2025_sys:,.0f}")
v3.metric("Propuesta anterior (sistema)", f"${imp_propant_sys:,.0f}")
v4.metric("Recaudo Vigente (VALOR A PAGAR)", f"${recaudo_vig:,.0f}")


# --------------------------------------------------
# 5. Gráfico de impuestos
# --------------------------------------------------

st.markdown("## 📊 Impuesto total por escenario (matriz técnica)")

df_plot = pd.DataFrame({
    "Escenario": ["Vigente", "Propuesta 2025", "Propuesta anterior"],
    "Impuesto": [imp_vig, imp_prop2025, imp_propant]
})

fig = px.bar(df_plot, x="Escenario", y="Impuesto", text="Impuesto",
             title="Comparación del impuesto total por escenario")
fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 6. Top actividades con mayor reducción
# --------------------------------------------------

st.markdown("## 🔻 Actividades con mayor reducción del impuesto (matriz)")

df_var = df_base.copy()
df_var["DIF_IMP_ABS"] = (
    pd.to_numeric(df_var[COL_IMP_PROP2025_MAT], errors="coerce") -
    pd.to_numeric(df_var[COL_IMP_VIG_MAT], errors="coerce")
)

df_var_top = df_var.sort_values("DIF_IMP_ABS").head(15)

df_var_top["Etiqueta"] = (
    df_var_top["CIIU"].astype(str) + " - " + df_var_top["DESCRIPCION"].astype(str)
)

fig2 = px.bar(
    df_var_top,
    x="DIF_IMP_ABS",
    y="Etiqueta",
    orientation="h",
    title="Top 15 actividades con mayor reducción del impuesto"
)
st.plotly_chart(fig2, use_container_width=True)


# --------------------------------------------------
# 7. Tabla final
# --------------------------------------------------

st.markdown("## 📋 Tabla de actividades")

cols_table = [
    "CIIU", "DESCRIPCION", "TAMAÑO EMPRESA", "RANGO UVT", "TIPO ACT",
    COL_TARIFA_ORIG, COL_TARIFA_2025, COL_TARIFA_ANT,
    COL_IMP_VIG_MAT, COL_IMP_PROP2025_MAT, COL_IMP_PROPANT_MAT,
    COL_IMP_VIG_SYS, COL_IMP_PROP2025_SYS, COL_IMP_PROPANT_SYS,
    "VALOR A PAGAR", "CONCLUSION", "PORCENTAJE", "AÑO"
]

cols_presentes = [c for c in cols_table if c in df_base.columns]

st.dataframe(df_base[cols_presentes], use_container_width=True)
