
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="LumiCity Dashboard",
    page_icon="🌃",
    layout="wide"
)

# =========================
# ESTILOS PERSONALIZADOS
# =========================
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #050816;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.main {
    padding: 2rem;
}

h1, h2, h3 {
    color: #7DF9FF;
}

[data-testid="stMetricValue"] {
    color: #7DF9FF;
}

.stTabs [data-baseweb="tab"] {
    color: white;
    font-size: 16px;
}

.stTabs [aria-selected="true"] {
    color: #7DF9FF;
    border-bottom: 2px solid #7DF9FF;
}

section[data-testid="stSidebar"] {
    background-color: #0A0F24;
}

.stAlert {
    border-radius: 10px;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("🌃 LumiCity Dashboard")
st.subheader("Sistema Inteligente de Monitoreo Lumínico Urbano")

st.markdown("""
Bienvenido a **LumiCity**, una plataforma interactiva de análisis ambiental desarrollada con tecnologías IoT.

Este sistema utiliza un sensor de luz conectado a un **ESP32** para capturar datos de iluminación ambiental en tiempo real desde un nodo urbano ubicado en la **Universidad EAFIT**.

La plataforma permite visualizar comportamientos lumínicos, identificar variaciones ambientales y analizar condiciones de iluminación en espacios urbanos y universitarios.
""")

# =========================
# MÉTRICAS SUPERIORES
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📡 Estado del Nodo", "Activo")

with col2:
    st.metric("💡 Sensor", "LDR / Luz")

with col3:
    st.metric("🛰 Dispositivo", "ESP32")

with col4:
    st.metric("📍 Ubicación", "EAFIT")

# =========================
# MAPA
# =========================
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783]
})

st.markdown("---")

st.subheader("📍 Nodo de Monitoreo Urbano")

st.markdown("""
El sensor principal se encuentra ubicado en la **Universidad EAFIT, Medellín**.

Este nodo recopila información lumínica del entorno para analizar variaciones de intensidad de luz en tiempo real dentro del campus universitario.
""")

st.map(eafit_location, zoom=15)

# =========================
# CARGA DE ARCHIVO
# =========================
st.markdown("---")

uploaded_file = st.file_uploader(
    "📂 Cargar archivo CSV del sensor",
    type=['csv']
)

# =========================
# PROCESAMIENTO DE DATOS
# =========================
if uploaded_file is not None:

    try:

        df1 = pd.read_csv(uploaded_file)

        # =========================
        # RENOMBRAR COLUMNA
        # =========================
        if 'Time' in df1.columns:

            other_columns = [col for col in df1.columns if col != 'Time']

            if len(other_columns) > 0:
                df1 = df1.rename(columns={
                    other_columns[0]: 'variable'
                })

        else:
            df1 = df1.rename(columns={
                df1.columns[0]: 'variable'
            })

        # =========================
        # FECHA
        # =========================
        if 'Time' in df1.columns:
            df1['Time'] = pd.to_datetime(df1['Time'])
            df1 = df1.set_index('Time')

        # =========================
        # TABS
        # =========================
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Visualización",
            "📊 Estadísticas",
            "🔍 Filtros",
            "🗺 Información del Nodo"
        ])

        # =====================================================
        # TAB 1
        # =====================================================
        with tab1:

            st.subheader("📈 Comportamiento Lumínico")

            st.markdown("""
            Visualización en tiempo real de la intensidad lumínica registrada por el sensor urbano.
            """)

            chart_type = st.selectbox(
                "Seleccione tipo de gráfico",
                ["Línea", "Área", "Barra"]
            )

            if chart_type == "Línea":
                st.line_chart(df1["variable"])

            elif chart_type == "Área":
                st.area_chart(df1["variable"])

            else:
                st.bar_chart(df1["variable"])

            # =========================
            # ESTADO DE LUZ
            # =========================
            promedio = df1["variable"].mean()

            st.markdown("---")

            if promedio < 300:
                st.error("🔴 Baja iluminación detectada")

            elif promedio < 700:
                st.warning("🟡 Iluminación media")

            else:
                st.success("🟢 Iluminación óptima")

            if st.checkbox("Mostrar datos crudos"):
                st.dataframe(df1)

        # =====================================================
        # TAB 2
        # =====================================================
        with tab2:

            st.subheader("📊 Análisis Estadístico del Sensor")

            stats_df = df1["variable"].describe()

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(stats_df)

            with col2:

                st.metric(
                    "💡 Intensidad Promedio",
                    f"{stats_df['mean']:.2f}"
                )

                st.metric(
                    "☀️ Valor Máximo",
                    f"{stats_df['max']:.2f}"
                )

                st.metric(
                    "🌑 Valor Mínimo",
                    f"{stats_df['min']:.2f}"
                )

                st.metric(
                    "📉 Variación",
                    f"{stats_df['std']:.2f}"
                )

        # =====================================================
        # TAB 3
        # =====================================================
        with tab3:

            st.subheader("🔍 Filtrado Inteligente de Datos")

            min_value = float(df1["variable"].min())
            max_value = float(df1["variable"].max())
            mean_value = float(df1["variable"].mean())

            if min_value == max_value:

                st.warning(
                    f"⚠️ Todos los registros tienen el mismo valor: {min_value:.2f}"
                )

                st.info(
                    "No es posible aplicar filtros porque no existe variación lumínica."
                )

                st.dataframe(df1)

            else:

                col1, col2 = st.columns(2)

                with col1:

                    min_val = st.slider(
                        'Nivel mínimo de iluminación',
                        min_value,
                        max_value,
                        mean_value,
                        key="min_val"
                    )

                    filtrado_df_min = df1[df1["variable"] > min_val]

                    st.write(
                        f"Registros superiores a {min_val:.2f}"
                    )

                    st.dataframe(filtrado_df_min)

                with col2:

                    max_val = st.slider(
                        'Nivel máximo de iluminación',
                        min_value,
                        max_value,
                        mean_value,
                        key="max_val"
                    )

                    filtrado_df_max = df1[df1["variable"] < max_val]

                    st.write(
                        f"Registros inferiores a {max_val:.2f}"
                    )

                    st.dataframe(filtrado_df_max)

                # =========================
                # DESCARGA
                # =========================
                csv = filtrado_df_min.to_csv().encode('utf-8')

                st.download_button(
                    label="📥 Descargar datos filtrados",
                    data=csv,
                    file_name='datos_filtrados_lumicity.csv',
                    mime='text/csv',
                )

        # =====================================================
        # TAB 4
        # =====================================================
        with tab4:

            st.subheader("🗺 Información del Nodo Urbano")

            col1, col2 = st.columns(2)

            with col1:

                st.write("### 📍 Ubicación")

                st.write("""
                **Universidad EAFIT — Medellín, Colombia**
                
                - Latitud: 6.2006  
                - Longitud: -75.5783  
                - Altitud: ~1,495 msnm  
                - Entorno: Campus universitario
                """)

            with col2:

                st.write("### 🛰 Detalles Técnicos")

                st.write("""
                - Dispositivo principal: ESP32  
                - Sensor conectado: Sensor de luz (LDR)  
                - Tipo de monitoreo: Intensidad lumínica ambiental  
                - Comunicación: IoT / Wokwi  
                - Plataforma de visualización: Streamlit  
                """)

    except Exception as e:

        st.error(f'❌ Error al procesar el archivo: {str(e)}')

        st.info(
            'Verifique que el archivo CSV tenga datos válidos.'
        )

# =========================
# MENSAJE INICIAL
# =========================
else:

    st.warning(
        '📂 Cargue un archivo CSV del sensor para comenzar el monitoreo.'
    )

# =========================
# FOOTER
# =========================
st.markdown("---")

st.markdown("""
### 🌃 LumiCity — Smart Urban Lighting Monitor

Sistema experimental de monitoreo lumínico urbano desarrollado con sensores IoT, ESP32 y visualización interactiva de datos.

📍 Universidad EAFIT — Medellín, Colombia
""")
```
