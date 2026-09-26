import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuración de página (debe ser la primera orden de Streamlit)
st.set_page_config(
    page_title="Dashboard Ejecutivo de Capturas",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚔 Dashboard Ejecutivo de Capturas (2022–2026)")
st.markdown("---")


@st.cache_data
def cargar_datos():
    df = pd.read_csv("resumen_ejecutivo_capturas.csv")
    df = df.dropna(subset=["AÑO", "MES_NUM"])
    df["AÑO"] = df["AÑO"].astype(int)
    df["MES_NUM"] = df["MES_NUM"].astype(int)
    return df


try:
    df = cargar_datos()

    # Panel lateral
    st.sidebar.header("⚙️ Filtros de Control")

    años_disponibles = sorted(list(df["AÑO"].unique()))
    años_sel = st.sidebar.multiselect(
        "Años a incluir",
        options=años_disponibles,
        default=años_disponibles,
    )

    deptos = ["TODOS"] + sorted(
        [str(d) for d in df["DEPARTAMENTO"].dropna().unique()]
    )
    depto_sel = st.sidebar.selectbox("Departamento", deptos)

    # Filtrado
    df_f = df[df["AÑO"].isin(años_sel)]
    if depto_sel != "TODOS":
        df_f = df_f[df_f["DEPARTAMENTO"] == depto_sel]

    if df_f.empty:
        st.warning(
            "No hay datos para la combinación de filtros seleccionada.",
            icon="⚠️",
        )
    else:
        # --- FILA 1: CUADRANTES SUPERIORES ---
        col_top1, col_top2 = st.columns(2)

        with col_top1:
            st.subheader("Evolución Anual de Capturas")
            df_anual = df_f.groupby("AÑO")["CAPTURAS"].sum().reset_index()
            df_anual["AÑO"] = df_anual["AÑO"].astype(str)

            fig_anual = px.bar(
                df_anual,
                x="AÑO",
                y="CAPTURAS",
                text="CAPTURAS",
                template="plotly_dark",
                color_discrete_sequence=["#1f77b4"],
            )
            fig_anual.update_traces(
                texttemplate="%{text:,}", textposition="outside"
            )
            fig_anual.update_layout(
                xaxis_title="Año", yaxis_title="Total Capturas", height=380
            )
            st.plotly_chart(fig_anual, use_container_width=True)

        with col_top2:
            st.subheader("Participación por Top Delitos")
            df_delito = (
                df_f.groupby("DELITO")["CAPTURAS"]
                .sum()
                .reset_index()
                .sort_values("CAPTURAS", ascending=False)
            )

            top_delitos = df_delito.head(7).copy()
            otros_cant = df_delito.iloc[7:]["CAPTURAS"].sum()
            if otros_cant > 0:
                top_delitos = pd.concat(
                    [
                        top_delitos,
                        pd.DataFrame(
                            [
                                {
                                    "DELITO": "OTROS DELITOS",
                                    "CAPTURAS": otros_cant,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

            fig_donut = px.pie(
                top_delitos,
                values="CAPTURAS",
                names="DELITO",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_donut.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            fig_donut.update_layout(height=380)
            st.plotly_chart(fig_donut, use_container_width=True)

        # --- FILA 2: CUADRANTES INFERIORES ---
        col_bot1, col_bot2 = st.columns(2)

        with col_bot1:
            st.subheader("Top 10 Departamentos")
            df_dept_top = (
                df_f.groupby("DEPARTAMENTO")["CAPTURAS"]
                .sum()
                .reset_index()
                .sort_values("CAPTURAS", ascending=True)
                .tail(10)
            )

            fig_dept = px.bar(
                df_dept_top,
                x="CAPTURAS",
                y="DEPARTAMENTO",
                orientation="h",
                text="CAPTURAS",
                template="plotly_dark",
                color_discrete_sequence=["#2ca02c"],
            )
            fig_dept.update_traces(
                texttemplate="%{text:,}", textposition="outside"
            )
            fig_dept.update_layout(
                xaxis_title="Capturas", yaxis_title="Departamento", height=380
            )
            st.plotly_chart(fig_dept, use_container_width=True)

        with col_bot2:
            st.subheader("Distribución Mensual Comparativa")
            nombres_meses = {
                1: "Ene",
                2: "Feb",
                3: "Mar",
                4: "Abr",
                5: "May",
                6: "Jun",
                7: "Jul",
                8: "Ago",
                9: "Sep",
                10: "Oct",
                11: "Nov",
                12: "Dic",
            }
            df_mes = (
                df_f.groupby(["AÑO", "MES_NUM"])["CAPTURAS"].sum().reset_index()
            )
            df_mes["MES"] = df_mes["MES_NUM"].map(nombres_meses)
            df_mes["AÑO"] = df_mes["AÑO"].astype(str)

            fig_mes = px.line(
                df_mes,
                x="MES",
                y="CAPTURAS",
                color="AÑO",
                markers=True,
                template="plotly_dark",
            )
            fig_mes.update_layout(
                xaxis_title="Mes", yaxis_title="Total Capturas", height=380
            )
            st.plotly_chart(fig_mes, use_container_width=True)

except FileNotFoundError:
    st.error(
        "❌ **No se encontró el archivo 'resumen_ejecutivo_capturas.csv' en GitHub.** "
        "Por favor, sube este archivo a tu repositorio."
    )
except Exception as e:
    st.error(f"❌ **Error al cargar la aplicación:** {e}")