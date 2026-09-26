import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuración de página
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

    # Mapeo oficial de meses
    nombres_meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    df["MES"] = df["MES_NUM"].map(nombres_meses)
    return df, nombres_meses


try:
    df, dict_meses = cargar_datos()

    # --- PANEL LATERAL DE FILTROS ---
    st.sidebar.header("⚙️ Filtros de Control")

    # 1. Filtro de Años
    años_disponibles = sorted(list(df["AÑO"].unique()))
    años_sel = st.sidebar.multiselect(
        "1. Años a incluir",
        options=años_disponibles,
        default=años_disponibles,
    )

    # 2. Filtro de Departamento
    deptos = ["TODOS"] + sorted(
        [str(d) for d in df["DEPARTAMENTO"].dropna().unique()]
    )
    depto_sel = st.sidebar.selectbox("2. Departamento / Zona", deptos)

    # 3. Filtro de Meses
    lista_meses = list(dict_meses.values())
    meses_sel = st.sidebar.multiselect(
        "3. Meses a incluir",
        options=lista_meses,
        default=lista_meses,
        help="Selecciona uno o varios meses para filtrar las métricas",
    )

    # --- APLICACIÓN DE FILTROS ---
    df_f = df[(df["AÑO"].isin(años_sel)) & (df["MES"].isin(meses_sel))]
    if depto_sel != "TODOS":
        df_f = df_f[df_f["DEPARTAMENTO"] == depto_sel]

    if df_f.empty:
        st.warning(
            "⚠️ No hay datos disponibles para la combinación de filtros seleccionada."
        )
    else:
        # --- FILA 1 DE GRÁFICOS (SUPERIOR) ---
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

            top_delitos = df_delito.head(6).copy()
            otros_cant = df_delito.iloc[6:]["CAPTURAS"].sum()
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
                hole=0.45,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_donut.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            fig_donut.update_layout(
                height=380, legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # --- FILA 2 DE GRÁFICOS (INFERIOR) ---
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
            df_mes = (
                df_f.groupby(["AÑO", "MES_NUM", "MES"])["CAPTURAS"]
                .sum()
                .reset_index()
            )
            df_mes = df_mes.sort_values("MES_NUM")
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

        # --- FILA 3: SECCIÓN TABLA DE DATOS (DATASET) ---
        st.markdown("---")
        st.subheader("📋 Dataset Filtrado y Detalle de Registros")

        col_tbl1, col_tbl2 = st.columns([3, 1])
        with col_tbl1:
            st.caption(
                f"Mostrando **{len(df_f):,}** filas agregadas correspondientes a los filtros activos."
            )
        with col_tbl2:
            # Botón para descargar los datos filtrados en CSV
            csv_data = df_f.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Dataset (CSV)",
                data=csv_data,
                file_name="dataset_capturas_filtrado.csv",
                mime="text/csv",
            )

        # Muestra la tabla interactiva
        df_display = df_f[
            ["AÑO", "MES", "DEPARTAMENTO", "DELITO", "CAPTURAS"]
        ].sort_values(by=["AÑO", "MES"], ascending=[False, True])

        st.dataframe(
            df_display,
            use_container_width=True,
            height=300,
            hide_index=True,
        )

except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")