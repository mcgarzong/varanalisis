import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from influxdb_client import InfluxDBClient
from streamlit_autorefresh import st_autorefresh
import time

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Sistema de Monitoreo Lumínico IoT",
    page_icon="📡",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=2000, key="refresh")

# =========================================================
# ESTILOS CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #050816;
    color: #E6F1FF;
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background-color: #050816;
}

h1, h2, h3 {
    color: #00D1FF;
}

[data-testid="metric-container"] {
    background-color: rgba(0, 209, 255, 0.08);
    border: 1px solid rgba(0,209,255,0.2);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 0px 12px rgba(0,209,255,0.2);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #0B1120;
    border-radius: 12px;
    padding: 10px 20px;
    color: white;
}

.stTabs [aria-selected="true"] {
    background-color: #00D1FF;
    color: black;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATOS DE INFLUXDB
# =========================================================

INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = "TU_TOKEN"
INFLUXDB_ORG = "Garzon"
INFLUXDB_BUCKET = "FINAL"

# =========================================================
# CONEXIÓN A INFLUXDB
# =========================================================

client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

query_api = client.query_api()

# =========================================================
# CONSULTA DE DATOS
# =========================================================

query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "Sensor 1")
  |> filter(fn: (r) => r["_field"] == "luminusidad")
'''

result = query_api.query_data_frame(query)

# =========================================================
# LIMPIEZA DE DATOS
# =========================================================

if isinstance(result, list):
    df = pd.concat(result)
else:
    df = result

if not df.empty:

    df = df[["_time", "_value"]]
    df.columns = ["Tiempo", "Lux"]

    ultimo_lux = float(df["Lux"].iloc[-1])

else:
    ultimo_lux = 0

# =========================================================
# HEADER
# =========================================================

st.title("📡 Sistema de Monitoreo Lumínico IoT")

st.caption(
    "Visualización en tiempo real de datos capturados por un ESP32 y almacenados en InfluxDB Cloud."
)

# =========================================================
# KPIs
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "💡 Luminosidad",
    f"{ultimo_lux:.2f} lx"
)

col2.metric(
    "📶 Estado ESP32",
    "Conectado"
)

col3.metric(
    "⏱ Frecuencia",
    "2s"
)

st.divider()

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📡 Tiempo Real",
    "📈 Histórico",
    "🧠 Estado del Sistema",
    "⚙ Configuración"
])

# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader("Monitoreo de Luminosidad")

    # MAPA
    mapa = pd.DataFrame({
        'lat': [6.2006],
        'lon': [-75.5783]
    })

    st.map(mapa, zoom=15)

    st.markdown("### 📍 Nodo Sensorial")

    st.write("""
    **Ubicación:** Universidad EAFIT  
    **Microcontrolador:** ESP32  
    **Sensor:** Fotoresistor LDR  
    **Conectividad:** WiFi  
    **Base de datos:** InfluxDB Cloud  
    """)

    # ESTADO DE LUZ
    st.markdown("### 🌗 Estado Lumínico")

    if ultimo_lux < 50:
        st.warning("🌑 Oscuridad detectada")

    elif ultimo_lux < 300:
        st.info("🌤 Iluminación moderada")

    else:
        st.success("☀ Alta iluminación")

# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.subheader("📈 Histórico de Datos")

    if not df.empty:

        fig = px.line(
            df,
            x="Tiempo",
            y="Lux",
            template="plotly_dark"
        )

        fig.update_traces(
            line=dict(width=3)
        )

        fig.update_layout(
            paper_bgcolor="#050816",
            plot_bgcolor="#050816",
            font_color="white",
            xaxis_title="Tiempo",
            yaxis_title="Lux"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No hay datos disponibles.")

# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.subheader("🧠 Estado del Sistema")

    st.success("✅ ESP32 conectado")

    st.success("✅ InfluxDB sincronizado")

    st.success("✅ Captura de datos activa")

    st.markdown("### ⚙ Información Técnica")

    st.write("""
    - Microcontrolador: ESP32
    - Sensor: Fotoresistor LDR
    - Variable medida: Luminosidad (Lux)
    - Intervalo de lectura: 2 segundos
    - Comunicación: WiFi
    - Almacenamiento: InfluxDB Cloud
    """)

# =========================================================
# TAB 4
# =========================================================

with tab4:

    st.subheader("⚙ Configuración")

    st.code(f"""
WIFI_SSID = "Wokwi-GUEST"

INFLUXDB_ORG = "{INFLUXDB_ORG}"

INFLUXDB_BUCKET = "{INFLUXDB_BUCKET}"

MEASUREMENT = "Sensor 1"

FIELD = "luminusidad"
""")

    st.warning(
        "Recuerda reemplazar el token de InfluxDB antes de subir el proyecto a GitHub."
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Desarrollado para monitoreo ambiental IoT • ESP32 + InfluxDB + Streamlit"
)
