# -------------------------------------------------------------------
# 0. LIBRERIAS
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.colors
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from datetime import datetime
from pandas.tseries.offsets import DateOffset

# -------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Bicing Insights",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# 2. PALETA DE COLORES (AURORA BOREAL + NEBULA)
# -------------------------------------------------------------------
aurora_palette = [
    "#00F5D4",  # 1. Turquesa (Original)
    "#00BBF9",  # 2. Azul brillante (Original)
    "#9B5DE5",  # 3. Violeta (Original)
    "#F15BB5",  # 4. Magenta (Original)
    "#00FF9F",  # 5. Verde aurora (Original)
    # --- Nuevos tonos complementarios ---
    "#70D6FF",  # 6. Celeste cielo
    "#FF70A6",  # 7. Rosa suave
    "#FF9770",  # 8. Coral neón
    "#FFEE93",  # 9. Amarillo pálido/crema
    "#8338EC"   # 10. Violeta eléctrico profundo
]
nebula_palette = [
    "#FEE440",  # amarillo canario (contrasta con el violeta)
    "#FF9100",  # naranja eléctrico
    "#FF006E",  # rosa intenso / punch
    "#8338EC",  # púrpura profundo
    "#3A86FF"   # azul real
]
base_colors = aurora_palette + nebula_palette

band_palette_base = [
    "#00F5D4",  # aurora
    "#00BBF9",
    "#9B5DE5",
    "#F15BB5",
    "#FEE440",  # nebula
    "#FF9100",
    "#3A86FF"
]

background_color = "#0E1117"

px.set_mapbox_access_token("######################################################################")

# CSS personalizado
st.markdown("""
<style>

/* ===== APP GLOBAL ===== */
.stApp {
    background-color: #0E1117;
    color: white;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #0E1117 !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ===== TEXTOS ===== */
h1, h2, h3, h4 {
    color: #00F5D4 !important;
}

/* ===== METRICS ===== */
[data-testid="stMetric"] {
    background-color: #151a28;
    border-radius: 10px;
    padding: 15px;
}

[data-testid="stMetricValue"] {
    color: white !important;
}

[data-testid="stMetricLabel"] {
    color: #00BBF9 !important;
}

/* ===== SELECTBOX ===== */
div[data-baseweb="select"] {
    background-color: #151a28 !important;
    color: white !important;
}

/* dropdown items */
div[data-baseweb="menu"] {
    background-color: #151a28 !important;
    color: white !important;
}

/* ===== Barra seleccionadora Buscar estación ===== */
div[data-baseweb="select"] {
    border: 2px solid #00F5D4 !important;  /* Borde verde */
    border-radius: 8px !important;         /* Bordes redondeados */
    padding: 5px !important;
}

/* ===== Barra seleccionadora Filtrar por tamaño ===== */
div[data-baseweb="select"] {
    border: 2px solid #00F5D4 !important;  /* Borde verde */
    border-radius: 8px !important;         /* Bordes redondeados */
    padding: 5px !important;
}

/* ===== Otras reglas de estilo del selectbox ===== */
div[data-baseweb="menu"] {
    background-color: #151a28 !important;
    color: white !important;
}

/* ===== Reforzar estilos de botones ya aplicados ===== */
.stButton > button {
    background-color: #151a28;
    color: white;
    border: 1px solid #00F5D4;
}

.stButton > button:hover {
    background-color: #00F5D4;
    color: #0E1117;
}            

/* ===== DATAFRAME ===== */
.stDataFrame {
    background-color: #0E1117 !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background-color: #151a28;
    color: white;
    border: 1px solid #00F5D4;
}

.stButton > button:hover {
    background-color: #00F5D4;
    color: #0E1117;
}

</style>
""", unsafe_allow_html=True)

# # -------------------------------------------------------------------
# # 3. TÍTULO
# # -------------------------------------------------------------------
# st.title("🚲DOS RUEDAS - MIL DATOS")
# st.subheader("Una exploracion de los patrones de uso, estaciones y movilidad del sistema de bicicletas de Barcelona")
# st.markdown("---")

# # -------------------------------------------------------------------
# # 4. INTRODUCCIÓN
# # -------------------------------------------------------------------
# st.markdown("""
# ### 📍 Sobre este proyecto

# **DOS RUEDAS - MIL DATOS** es un dashboard interactivo que analiza el sistema público de bicicletas compartidas de Barcelona.

# - **Objetivo:** Analizar y explorar los **patrones de uso**, la **distribución y comportamiento de las estaciones**, y la **movilidad general** dentro del sistema de bicicletas de Barcelona.**.
# - **Dataset:** El análisis utiliza datos históricos del sistema de estaciones entre **2019 y 2024**, con actualizaciones cada **4 minutos por estación**.
# - **Enriquecimiento:** Se incluyen datos de uso mensual y número de abonados, desde 2009, para profundizar el análisis.
# - **Fuentes:** 
#     - Portal de datos abiertos del Ayuntamiento de Barcelona.
#     - Dataset de Kaggle: "BCN Bike Sharing Dataset - Bicing Stations".
#     - Archivos CSV con datos históricos de uso y abonados de la empresa Bicing.
# """)

# -------------------------------------------------------------------
# 5. CONSTANTES Y RUTAS
# -------------------------------------------------------------------
BASE_PATH = r"C:\Users\ravin\Desktop\Proyecto"
OUTPUT_PATH = os.path.join(BASE_PATH, "datos_procesados")
INTERMEDIOS_PATH = os.path.join(OUTPUT_PATH, "intermedios")

# -------------------------------------------------------------------
# 6. CARGA DE DATOS (con caché)
# -------------------------------------------------------------------
@st.cache_resource
def cargar_datos():
    # Dataframes pequeños desde Excel y API
    df_usos = pd.read_parquet(os.path.join(INTERMEDIOS_PATH, "usos_mensuales.parquet"))
    df_abonados = pd.read_parquet(os.path.join(INTERMEDIOS_PATH, "abonados_mensuales.parquet"))
    df_tipo = pd.read_parquet(os.path.join(INTERMEDIOS_PATH, "usos_tipo.parquet"))
    df_inventario = pd.read_parquet(os.path.join(INTERMEDIOS_PATH, "inventario.parquet"))
    df_estaciones = pd.read_parquet(os.path.join(OUTPUT_PATH, "estaciones.parquet"))
    df_estaciones_historicas = pd.read_parquet(os.path.join(OUTPUT_PATH, "estaciones_historicas.parquet"))
    df_estaciones_historicas_2024 = df_estaciones_historicas[df_estaciones_historicas["año_snapshot"] == 2024].copy()

    # Datos agregados para análisis de estaciones
    AGREGADOS_PATH = os.path.join(OUTPUT_PATH, "agregados")

    df_resumen_diario = pd.read_parquet(os.path.join(AGREGADOS_PATH, "resumen_diario_estacion.parquet"))
    df_patron_horario = pd.read_parquet(os.path.join(AGREGADOS_PATH, "patron_horario_estacion.parquet"))
    df_patron_semanal = pd.read_parquet(os.path.join(AGREGADOS_PATH, "patron_semanal_estacion.parquet"))
    df_patron_mensual = pd.read_parquet(os.path.join(AGREGADOS_PATH, "patron_mensual_estacion.parquet"))
    df_patron_hora_dia = pd.read_parquet(os.path.join(AGREGADOS_PATH, "patron_hora_dia_semana.parquet"))
    df_top_vacias = pd.read_parquet(os.path.join(AGREGADOS_PATH, "top_estaciones_vacias.parquet"))
    df_top_llenas = pd.read_parquet(os.path.join(AGREGADOS_PATH, "top_estaciones_llenas.parquet"))
    df_top_criticas = pd.read_parquet(os.path.join(AGREGADOS_PATH, "top_estaciones_criticas.parquet"))
    df_top_rotacion = pd.read_parquet(os.path.join(AGREGADOS_PATH, "top_estaciones_rotacion.parquet"))
    df_ranking = pd.read_parquet(os.path.join(AGREGADOS_PATH, "ranking_estaciones_completo.parquet"))
    df_serie_temporal = pd.read_parquet(os.path.join(AGREGADOS_PATH, "serie_temporal_global.parquet"))
    df_evolucion_anual = pd.read_parquet(os.path.join(AGREGADOS_PATH, "evolucion_anual_estacion.parquet"))
    df_info_enriquecida = pd.read_parquet(os.path.join(AGREGADOS_PATH, "info_estaciones_enriquecida.parquet"))
    df_mapa = pd.read_parquet(os.path.join(AGREGADOS_PATH, "dataset_mapa.parquet"))
    df_mapa_animado = pd.read_parquet(os.path.join(AGREGADOS_PATH, "mapa_animado_horario.parquet"))

    # DataFrame de estaciones filtrado para análisis (solo las que tienen datos en agregados)
    estaciones_con_datos = df_resumen_diario['id_estacion'].unique()
    df_estaciones_filtrado = df_estaciones_historicas_2024[
        df_estaciones_historicas_2024['id_estacion'].isin(estaciones_con_datos)
    ].copy()

    return (df_usos, df_abonados, df_tipo, df_inventario, df_estaciones, df_estaciones_filtrado,
            df_resumen_diario, df_patron_horario, df_patron_semanal, df_patron_mensual,
            df_patron_hora_dia, df_top_vacias, df_top_llenas, df_top_criticas, df_top_rotacion,
            df_ranking, df_serie_temporal, df_evolucion_anual, df_info_enriquecida, df_mapa, df_estaciones_historicas , df_estaciones_historicas_2024, df_mapa_animado)

with st.spinner("Cargando datos..."):
            (df_usos, df_abonados, df_tipo, df_inventario, df_estaciones, df_estaciones_filtrado,
            df_resumen_diario, df_patron_horario, df_patron_semanal, df_patron_mensual,
            df_patron_hora_dia, df_top_vacias, df_top_llenas, df_top_criticas, df_top_rotacion,
            df_ranking, df_serie_temporal, df_evolucion_anual, df_info_enriquecida, df_mapa, df_estaciones_historicas , df_estaciones_historicas_2024, df_mapa_animado) = cargar_datos()
 

# -------------------------------------------------------------------
# 7. MENÚ DE NAVEGACIÓN EN SIDEBAR (reemplaza a los tabs)
# -------------------------------------------------------------------
with st.sidebar:
    st.header("🗂️ Navegación")
    pagina = st.radio(
        "Ir a:",
        [
            "📌 ¿Qué es Bicing?",
            "📈 Análisis histórico",
            "🗺️ Análisis espacial",
            "🚲 Análisis de estaciones",
            "⚡ Estado actual",
            "🔮 Predicción",
            "📊 Preguntas",
        ],
        index=0
    )

# -------------------------------------------------------------------
# 8. CONTENIDO SEGÚN LA PÁGINA SELECCIONADA
# -------------------------------------------------------------------

# ---------- PÁGINA 0: ¿QUÉ ES BICING? (nuevo contenido) ----------
if pagina == "📌 ¿Qué es Bicing?":
    #st.markdown("## 📌 ¿Qué es Bicing?")
    # -------------------------------------------------------------------
    # 3. TÍTULO
    # -------------------------------------------------------------------
    st.title("🚲DOS RUEDAS - MIL DATOS")
    st.subheader("Una exploracion de los patrones de uso, estaciones y movilidad del sistema de bicicletas de Barcelona")
    st.markdown("---")

    # -------------------------------------------------------------------
    # 4. INTRODUCCIÓN
    # -------------------------------------------------------------------
    st.markdown("""
    ### 📍 Sobre este proyecto

    **DOS RUEDAS - MIL DATOS** es un dashboard interactivo que analiza el sistema público de bicicletas compartidas de Barcelona.

    - **Objetivo:** Analizar y explorar los **patrones de uso**, la **distribución y comportamiento de las estaciones**, y la **movilidad general** dentro del sistema de bicicletas de Barcelona.**.
    - **Dataset:** El análisis utiliza datos históricos del sistema de estaciones entre **2019 y 2024**, con actualizaciones cada **4 minutos por estación**.
    - **Enriquecimiento:** Se incluyen datos de uso mensual y número de abonados, desde 2009, para profundizar el análisis.
    - **Fuentes:** 
        - Portal de datos abiertos del Ayuntamiento de Barcelona.
        - Dataset de Kaggle: "BCN Bike Sharing Dataset - Bicing Stations".
        - Archivos CSV con datos históricos de uso y abonados de la empresa Bicing.
    """)
    # Imagen de Bicing (ruta local)
    imagen_path = os.path.join(BASE_PATH, "bicing.jpg")
    if os.path.exists(imagen_path):
        st.image(imagen_path, caption="Estación Bicing en Barcelona", use_container_width=True)
    else:
        st.warning("Imagen no encontrada en la ruta especificada.")
    
    st.markdown("---")
    
    # Título con tooltip de información
    st.markdown("## 📌 ¿Qué es Bicing?", 
                help= "Bicing es el sistema público de bicicletas compartidas de Barcelona, operando desde 2007. Opera 24/7, con estaciones distribuidas por la ciudad y bicicletas mecánicas y eléctricas (de pedaleo asistido)"
    )

    st.markdown("---")

    # ------------------------------------------
    # DIMENSIÓN INICIAL (2018) vs AMPLIACIONES (2028)
    # ------------------------------------------
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("### 📐 Dimensión inicial del servicio (2018)")
        # KPIs 2018
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🚲 Mecánicas", "6.000")
        col_b.metric("⚡ Eléctricas", "1.000")
        col_c.metric("📊 Total bicis", "7.000")
        col_d, col_e = st.columns(2)
        col_d.metric("🔩 Anclajes/estación (media)", "27")
        col_e.metric("⚓ Total anclajes", "14.013")
        st.metric("⚖️ Proporción anclajes/bici", "2:1")

    with col_der:
        st.markdown("### 📈 Ampliaciones previstas (hasta 2028)")
        # KPIs ampliados con deltas
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🚲 Mecánicas", "0%")
        col_b.metric("⚡ Eléctricas", "100%")
        col_c.metric("📊 Total bicis", "8.000")
        col_d, col_e = st.columns(2)
        col_d.metric("🔩 Anclajes/estación (media)", "27")
        col_e.metric("⚓ Total anclajes", "16.000")
        st.metric("⚖️ Proporción anclajes/bici", "2:1 (se mantiene)")

    st.markdown("---")

    # ------------------------------------------
    # MODELO TARIFARIO (2018 vs ACTUAL)
    # ------------------------------------------

    st.markdown("### 💰 Modelo tarifario")

    st.markdown("---")

    # ------------------------------------------
    # TABLAS TARIFARIAS
    # ------------------------------------------

    col1, col2, col3 = st.columns(3)

    # ---------- 2018 ----------
    with col1:
        st.markdown("#### 🚲 2018")
        st.caption("Abono Mecánico (47,16 €) / Complemento Eléctrico (+14 €)")
        
        data_2018 = pd.DataFrame({
            "Periodo": ["0 – 30 min", "30 min – 2 h", "+2 h"],
            "Mecánicas": ["Gratis", "0,74 € / 30 min", "4,49 € / h"],
            "Eléctricas": ["0,45 €", "0,80 € / 30 min", "5,00 € / h"]
        })
        
        st.dataframe(data_2018, use_container_width=True, hide_index=True)


    # ---------- Tarifa Plana ----------
    with col2:
        st.markdown("#### 💳 Tarifa Plana 2026")
        st.caption("50 €/año")
        
        data_plana = pd.DataFrame({
            "Periodo": ["0 – 30 min", "30 min – 2 h", "+2 h"],
            "Mecánicas": ["Gratis", "0,81 € / 30 min", "5,75 € / h"],
            "Eléctricas": ["0,40 €", "1,04 € / 30 min", "5,75 € / h"]
        })
        
        st.dataframe(data_plana, use_container_width=True, hide_index=True)


    # ---------- Tarifa por Uso ----------
    with col3:
        st.markdown("#### 💳 Tarifa por Uso 2026")
        st.caption("35 €/año")
        
        data_uso = pd.DataFrame({
            "Periodo": ["0 – 30 min", "30 min – 2 h", "+2 h"],
            "Mecánicas": ["0,40 €", "0,81 € / 30 min", "5,75 € / h"],
            "Eléctricas": ["0,63 €", "1,04 € / 30 min", "5,75 € / h"]
        })
        
        st.dataframe(data_uso, use_container_width=True, hide_index=True)


# ---------- PÁGINA 1: ANÁLISIS HISTÓRICO ----------
elif pagina == "📈 Análisis histórico":
    st.markdown("## 📈 Análisis histórico del sistema")
    st.markdown("""
    En esta sección exploramos la evolución del sistema **Bicing** a lo largo del tiempo.
    Se analizan:
    - Evolución del número de **usos del sistema**
    - Crecimiento del número de **abonados**
    - Distribución de **bicicletas mecánicas vs eléctricas**
    - Cambios en el **inventario del sistema**
    """)
    st.markdown("---")
    # -------------------------------------------------------------------
    # 7. KPIs DEL SISTEMA
    # -------------------------------------------------------------------
    st.markdown("## 📊 KPIs del sistema")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🚲 Bicicletas", "8000")
    col2.metric("🔧 En reparación", "300")
    col3.metric("📍 Estaciones", df_estaciones.shape[0])

    # Suma de la columna capacidad
    total_anclajes = df_estaciones['capacidad'].sum()
    col4.metric("⚓ Número de anclajes", f"{total_anclajes:,}")

    # KPI Abonados (Corregido para ignorar ceros y ordenar cronológicamente)
    df_valido = df_abonados[df_abonados['abonados'] > 0].sort_values(['año', 'mes_num'])
    ultimo_dato = df_valido['abonados'].iloc[-1]
    col5.metric("👤 Abonados (último dato)", f"{ultimo_dato:,}")

    col6.metric("📊 Usos históricos", f"{df_usos['usos'].sum():,}")

    st.markdown("---")

    # ---------------------------------------------------------
    # Evolución histórica de usos del sistema
    # ---------------------------------------------------------
    st.markdown("### Evolución histórica del uso del sistema")
    st.markdown("""
    Este gráfico muestra la evolución del número de usos del sistema Bicing a lo largo del tiempo.
    Permite observar:
    - crecimiento del sistema
    - estacionalidad anual
    - impacto de eventos externos
    """)

    # Crear columna fecha para visualización temporal
    df_usos["fecha"] = pd.to_datetime(
        df_usos["año"].astype(str) + "-" + df_usos["mes_num"].astype(str) + "-01"
    )
    df_usos = df_usos.sort_values("fecha")

    # Crear gráfico
    fig_usos_line = px.line(
        df_usos,
        x="fecha",
        y="usos",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=[aurora_palette[0]]
    )
    fig_usos_line.update_traces(marker=dict(size=4))

    fig_usos_line.update_layout(
        template="plotly_dark",
        xaxis=dict(
            title="Fecha",
            color="white",
            showgrid=False,
            zeroline=False,
            showspikes=True,
            spikemode="across",
            spikecolor=aurora_palette[0],
            spikesnap="cursor",
            spikethickness=1,
        ),
        yaxis=dict(
            title="Número de usos",
            color=aurora_palette[0],
            showgrid=True,
            gridcolor='white',
        ),
        hovermode="x unified"
    )

    # Bandas sombreadas por año
    years = sorted(df_usos['fecha'].dt.year.unique())
    extended_bands = sample_colorscale(
        band_palette_base,
        [i / (len(years) - 1) for i in range(len(years))]
    )

    shapes = []
    for i, year in enumerate(years):
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year+1}-01-01")
        color = extended_bands[i]
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=start,
            x1=end,
            y0=0,
            y1=1,
            fillcolor=color,
            opacity=0.08,
            layer="below",
            line_width=0,
        ))
    fig_usos_line.update_layout(shapes=shapes)

    # Línea de cambio de concesión
    COLOR_HITO = nebula_palette[0]
    fig_usos_line.add_vline(x="2019-05-01", line_dash="dash", line_color=COLOR_HITO)
    fig_usos_line.add_annotation(
        x="2019-05-01",
        y=1,
        yref="paper",
        text="Inicio concesión Pedalem (2019)",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color=COLOR_HITO)
    )

    st.plotly_chart(fig_usos_line, use_container_width=True, key="fig_usos_line")

    # KPIs de usos
    uso_max = df_usos['usos'].max()
    mes_max = df_usos.loc[df_usos['usos'].idxmax(), 'fecha'].strftime("%B %Y")
    uso_min = df_usos['usos'].min()
    mes_min = df_usos.loc[df_usos['usos'].idxmin(), 'fecha'].strftime("%B %Y")
    ultimo_mes = df_usos['fecha'].max().strftime("%B %Y")
    uso_ultimo_mes = df_usos.loc[df_usos['fecha'] == df_usos['fecha'].max(), 'usos'].values[0]

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Mes de mayor uso ({mes_max})", f"{uso_max:,}")
    col2.metric(f"Mes de menor uso ({mes_min})", f"{uso_min:,}")
    col3.metric(f"Último mes registrado ({ultimo_mes})", f"{uso_ultimo_mes:,}")

    st.markdown("---")

    # ---------------------------------------------------------
    # Promedios históricos
    # ---------------------------------------------------------
    promedio_anual = df_usos.groupby('año')['usos'].mean().reset_index()
    promedio_mensual = df_usos.groupby('mes')['usos'].mean().reset_index()

    meses_ordenados = [
        'Enero','Febrero','Marzo','Abril','Mayo','Junio',
        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'
    ]
    promedio_mensual['mes'] = pd.Categorical(
        promedio_mensual['mes'],
        categories=meses_ordenados,
        ordered=True
    )
    promedio_mensual = promedio_mensual.sort_values('mes')

    col1, col2 = st.columns(2)

    color_anual = aurora_palette[1]
    color_mensual = aurora_palette[5]

    # Promedio anual
    fig_anual = px.bar(
        promedio_anual,
        x='usos',
        y='año',
        orientation='h',
        labels={'usos':'Promedio de usos','año':'Año'},
        title="Promedio anual de usos"
    )
    fig_anual.update_traces(marker_color=color_anual)
    fig_anual.update_layout(template="plotly_dark")
    with col1:
        st.plotly_chart(fig_anual, use_container_width=True, key="fig_anual")

    # Promedio mensual histórico
    fig_mensual = px.bar(
        promedio_mensual,
        x='usos',
        y='mes',
        orientation='h',
        labels={'usos':'Promedio de usos','mes':'Mes'},
        title="Promedio mensual histórico de usos"
    )
    fig_mensual.update_traces(marker_color=color_mensual)
    fig_mensual.update_layout(template="plotly_dark")
    with col2:
        st.plotly_chart(fig_mensual, use_container_width=True, key="fig_mensual")

    # ---------------------------------------------------------
    # Heatmap de estacionalidad (Año vs Mes)
    # ---------------------------------------------------------
    st.markdown("### Estacionalidad del sistema")
    st.markdown("""
    Este heatmap muestra cómo varía el uso del sistema Bicing según el **mes y el año**.
    Permite identificar:
    - meses con mayor demanda
    - patrones estacionales
    - cambios en el comportamiento del sistema a lo largo del tiempo
    """)

    heatmap_data = df_usos.pivot(index="año", columns="mes", values="usos")
    heatmap_data = heatmap_data[meses_ordenados]

    fig_heatmap = px.imshow(
        heatmap_data,
        color_continuous_scale=[aurora_palette[0], aurora_palette[3]],
        aspect="auto",
        labels=dict(x="Mes", y="Año", color="Usos")
    )
    fig_heatmap.update_layout(template="plotly_dark")
    st.plotly_chart(fig_heatmap, use_container_width=True, key="fig_heatmap")

    # ---------------------------------------------------------
    # Detección automática de estacionalidad
    # ---------------------------------------------------------
    st.markdown("### Detección automática de estacionalidad")
    promedio_mes = df_usos.groupby("mes")["usos"].mean().reset_index()
    mes_max = promedio_mes.loc[promedio_mes["usos"].idxmax()]
    mes_min = promedio_mes.loc[promedio_mes["usos"].idxmin()]

    col1, col2 = st.columns(2)
    col1.metric("📈 Mes con mayor uso promedio", mes_max["mes"])
    col2.metric("📉 Mes con menor uso promedio", mes_min["mes"])

    st.markdown("---")

    # ---------------------------------------------------------
    # Estacionalidad por estación del año
    # ---------------------------------------------------------
    st.markdown("### Uso promedio por estación del año",
                help="Estaciones: Invierno (Dic, Ene, Feb), Primavera (Mar, Abr, May), Verano (Jun, Jul, Ago), Otoño (Sep, Oct, Nov)")

    def asignar_estacion(mes):
        if mes in ["Diciembre","Enero","Febrero"]:
            return "Invierno"
        elif mes in ["Marzo","Abril","Mayo"]:
            return "Primavera"
        elif mes in ["Junio","Julio","Agosto"]:
            return "Verano"
        else:
            return "Otoño"

    df_usos["estacion"] = df_usos["mes"].apply(asignar_estacion)
    estacionalidad = df_usos.groupby("estacion")["usos"].mean().reset_index()
    orden_estaciones = ["Invierno","Primavera","Verano","Otoño"]
    estacionalidad["estacion"] = pd.Categorical(estacionalidad["estacion"], categories=orden_estaciones, ordered=True)
    estacionalidad = estacionalidad.sort_values("estacion")

    fig_estaciones = px.bar(
        estacionalidad,
        x="estacion",
        y="usos",
        labels={"estacion":"Estación del año", "usos":"Usos promedio"},
        title="Uso promedio del sistema por estación del año"
    )
    fig_estaciones.update_traces(marker_color=aurora_palette[6], marker_opacity=0.7)
    fig_estaciones.update_layout(template="plotly_dark", showlegend=False, yaxis=dict(gridcolor='white'))
    st.plotly_chart(fig_estaciones, use_container_width=True, key="fig_estaciones")

    # ---------------------------------------------------------
    # Evolución de abonados con bandas sombreadas por año
    # ---------------------------------------------------------
    st.markdown("### Evolución del número de abonados")
    st.markdown("""
    Este gráfico muestra la evolución del número de **abonados al sistema Bicing** a lo largo del tiempo.
    Permite analizar:
    - crecimiento de la base de usuarios
    - impacto de eventos externos
    - tendencias recientes de adopción del sistema
    """)

    df_abonados["fecha"] = pd.to_datetime(
        df_abonados["año"].astype(str) + "-" + df_abonados["mes_num"].astype(str) + "-01"
    )
    # El dato de diciembre 2025 ya está corregido en el parquet, no es necesario filtrar
    df_abonados = df_abonados.sort_values("fecha")

    # Bandas sombreadas
    shapes = []
    for i, year in enumerate(years):
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year+1}-01-01")
        color = extended_bands[i]
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=start,
            x1=end,
            y0=0,
            y1=1,
            fillcolor=color,
            opacity=0.08,
            layer="below",
            line_width=0,
        ))

    fig_abonados = px.line(
        df_abonados,
        x="fecha",
        y="abonados",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=[aurora_palette[1]]
    )
    fig_abonados.update_traces(marker=dict(size=4))
    fig_abonados.update_layout(
        template="plotly_dark",
        xaxis=dict(title="Fecha", color="white", showgrid=False),
        yaxis=dict(title="Número de abonados", color=aurora_palette[3], gridcolor='white'),
        hovermode="x unified",
        shapes=shapes
    )

    fig_abonados.add_vline(x="2019-05-01", line_dash="dash", line_color=COLOR_HITO)
    fig_abonados.add_annotation(
        x="2019-05-01",
        y=1,
        yref="paper",
        text="Inicio concesión Pedalem",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color=COLOR_HITO)
    )
    st.plotly_chart(fig_abonados, use_container_width=True, key="fig_abonados")

    # KPIs de abonados
    abonados_max = df_abonados["abonados"].max()
    fecha_max = df_abonados.loc[df_abonados["abonados"].idxmax(), "fecha"].strftime("%B %Y")
    abonados_min = df_abonados["abonados"].min()
    fecha_min = df_abonados.loc[df_abonados["abonados"].idxmin(), "fecha"].strftime("%B %Y")
    crecimiento_total = ((df_abonados["abonados"].iloc[-1] - df_abonados["abonados"].iloc[0]) / df_abonados["abonados"].iloc[0]) * 100

    inicio_pedalem = pd.Timestamp("2019-05-01")
    abonados_inicio = df_abonados[df_abonados['fecha'] == inicio_pedalem]['abonados'].values
    if len(abonados_inicio) == 0:
        abonados_inicio = df_abonados[df_abonados['fecha'] > inicio_pedalem].iloc[0]['abonados']
    else:
        abonados_inicio = abonados_inicio[0]
    abonados_actual = df_abonados['abonados'].max()
    incremento_abonados_pct = ((abonados_actual - abonados_inicio) / abonados_inicio) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Máximo de abonados ({fecha_max})", f"{abonados_max:,}")
    col2.metric(f"Mínimo de abonados ({fecha_min})", f"{abonados_min:,}")
    col3.metric("Crecimiento total del sistema", f"{crecimiento_total:.1f}%")
    col4.metric(f"Incremento abonados desde 05/2019", f"{incremento_abonados_pct:.1f} %")

    # ---------------------------------------------------------
    # Gráfico de dispersión: Usos vs Abonados
    # ---------------------------------------------------------
    st.markdown("### Relación entre usos y abonados")
    st.markdown("""
    Este gráfico muestra la relación entre **usos mensuales** y **abonados**.  
    - Cada punto representa un mes, coloreado según número de usos.  
    - La línea continua es la tendencia lineal global.  
    - Puntos alejados de la línea indican meses con comportamiento atípico.
    """)

    df_usos_temp = df_usos[['fecha', 'usos']].copy()
    df_abonados_temp = df_abonados[['fecha', 'abonados']].copy()
    df_relacion = pd.merge(df_usos_temp, df_abonados_temp, on='fecha', how='inner')

    fig_relacion = px.scatter(
        df_relacion,
        x='abonados',
        y='usos',
        trendline='ols',
        trendline_color_override='white',
        labels={'abonados': 'Número de abonados', 'usos': 'Usos mensuales'},
        title='Usos mensuales vs Abonados (2009-2025)'
    )
    fig_relacion.update_traces(
        marker=dict(size=6, color=aurora_palette[0], opacity=0.7),
        selector=dict(mode='markers')
    )
    fig_relacion.update_layout(
        template='plotly_dark',
        xaxis=dict(title='Número de abonados', color='white', showgrid=False),
        yaxis=dict(title='Usos mensuales', color='white', showgrid=True, gridcolor='white', gridwidth=1),
        hovermode='closest'
    )
    st.plotly_chart(fig_relacion, use_container_width=True, key='fig_relacion_corregido')

    # ---------------------------------------------------------
    # Usos por tipo de bicicleta y evolución del inventario
    # ---------------------------------------------------------
    st.markdown("### Usos por tipo de bicicleta y evolución del inventario")

    df_tipo['año'] = pd.to_numeric(df_tipo['año'], errors='coerce')
    df_tipo_plot = df_tipo[df_tipo['año'].between(2019, 2025)]
    df_tipo_grouped = df_tipo_plot.groupby(['año', 'tipo'])['usos'].sum().reset_index()

    fig_tipo = px.bar(
        df_tipo_grouped,
        x='año',
        y='usos',
        color='tipo',
        color_discrete_sequence=[aurora_palette[1], aurora_palette[2]],
        title="Usos por tipo de bicicleta",
        labels={'usos': 'Número de usos', 'año': 'Año', 'tipo': 'Tipo de bicicleta'}
    )
    fig_tipo.update_layout(template='plotly_dark', barmode='stack')

    df_inventario['año'] = pd.to_numeric(df_inventario['año'], errors='coerce')
    df_inventario_plot = df_inventario[df_inventario['año'].between(2019, 2024)]

    fig_inventario = go.Figure()
    fig_inventario.add_trace(go.Bar(
        x=df_inventario_plot['año'],
        y=df_inventario_plot['final_mec'],
        name="Mecánicas",
        marker_color=aurora_palette[2]
    ))
    fig_inventario.add_trace(go.Bar(
        x=df_inventario_plot['año'],
        y=df_inventario_plot['final_elec'],
        name="Eléctricas",
        marker_color=aurora_palette[1]
    ))
    fig_inventario.update_layout(
        template='plotly_dark',
        title="Evolución del inventario de bicicletas",
        xaxis_title="Año",
        yaxis_title="Número de bicicletas",
        barmode='stack',
        legend_title="Tipo de bicicleta"
    )

    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.plotly_chart(fig_tipo, use_container_width=True, key="fig_tipo")
    with col_graf2:
        st.plotly_chart(fig_inventario, use_container_width=True, key="fig_inventario")

    # KPIs
    inicio_2019 = df_tipo_grouped[df_tipo_grouped['año'] == 2019]
    fin_2025 = df_tipo_grouped[df_tipo_grouped['año'] == 2025]
    inicio_inv = df_inventario_plot[df_inventario_plot['año'] == 2019]
    fin_inv = df_inventario_plot[df_inventario_plot['año'] == 2024]

    kpi_col1, kpi_col2 = st.columns(2)

    if not inicio_2019.empty and not fin_2025.empty and not inicio_inv.empty and not fin_inv.empty:
        total_inicio = inicio_2019['usos'].sum()
        total_fin = fin_2025['usos'].sum()
        porc_inicio = (inicio_2019.set_index('tipo')['usos'] / total_inicio) * 100
        porc_fin = (fin_2025.set_index('tipo')['usos'] / total_fin) * 100
        elec_2019 = porc_inicio.get("Eléctrica", porc_inicio.get("Electrica"))
        elec_2025 = porc_fin.get("Eléctrica", porc_fin.get("Electrica"))
        mec_2019 = porc_inicio.get("Mecánica", porc_inicio.get("Mecanica"))
        mec_2025 = porc_fin.get("Mecánica", porc_fin.get("Mecanica"))

        total_inicio_inv = inicio_inv['final_mec'].values[0] + inicio_inv['final_elec'].values[0]
        total_fin_inv = fin_inv['final_mec'].values[0] + fin_inv['final_elec'].values[0]
        mec_inv_2019 = inicio_inv['final_mec'].values[0] / total_inicio_inv * 100
        mec_inv_2024 = fin_inv['final_mec'].values[0] / total_fin_inv * 100
        elec_inv_2019 = inicio_inv['final_elec'].values[0] / total_inicio_inv * 100
        elec_inv_2024 = fin_inv['final_elec'].values[0] / total_fin_inv * 100

        with kpi_col1:
            st.metric("% Eléctrica 2019 → 2025", f"{elec_2019:.1f}% → {elec_2025:.1f}%")
        with kpi_col2:
            st.metric("% Eléctricas 2019 → 2024", f"{elec_inv_2019:.1f}% → {elec_inv_2024:.1f}%")

        kpi_col3, kpi_col4 = st.columns(2)
        with kpi_col3:
            st.metric("% Mecánica 2019 → 2025", f"{mec_2019:.1f}% → {mec_2025:.1f}%")
        with kpi_col4:
            st.metric("% Mecánicas 2019 → 2024", f"{mec_inv_2019:.1f}% → {mec_inv_2024:.1f}%")
    else:
        st.warning("No hay datos suficientes para calcular los KPIs.")

# ---------- PÁGINA 2: ANÁLISIS ESPACIAL ----------
elif pagina == "🗺️ Análisis espacial":
    st.markdown("## 🗺️ Análisis espacial de estaciones")
    st.markdown("""
    Visualización geográfica de las estaciones de Bicing en Barcelona.
    Este análisis permitirá explorar:
    - Distribución de estaciones en la ciudad
    - Capacidad de cada estación
    - Altitud
    - Distancia entre estaciones
    """)
    st.markdown("---")
    st.markdown("### 📍 Mapa de estaciones Bicing")

    # -------------------------
    # Limpiar datos
    # -------------------------
    df_map = df_estaciones.dropna(subset=["latitud", "longitud"]).copy()

    df_map.rename(columns={
        "capacidad": "Capacidad",
        "altitud": "Altitud",
        "distancia_estacion_cercana": "Distancia + cercana"
    }, inplace=True)

    # -------------------------
    # Clasificación por tamaño
    # -------------------------
    def clasificar_capacidad(cap):
        if cap < 20:
            return "Pequeña"
        elif cap <= 35:
            return "Media"
        else:
            return "Grande"

    df_map["categoria"] = df_map["Capacidad"].apply(clasificar_capacidad)

    # -------------------------
    # Botones + selectores (MISMA FILA)
    # -------------------------
    col_btn1, col_btn2, col_btn3, col_extra1, col_extra2 = st.columns([1,1,1,3,3])

    # Botones de modo
    with col_btn1: modo_normal = st.button("Normal")
    with col_btn2: modo_altitud = st.button("Altitud")
    with col_btn3: modo_capacidad = st.button("Capacidad")

    # Selector de estación
    with col_extra1:
        estacion_sel = st.selectbox(
            "Buscar estación",
            ["Todas"] + sorted(df_map["nombre"].dropna().unique())
        )

    # Selector de categoría
    with col_extra2:
        categoria_sel = st.selectbox(
            "Filtrar por tamaño",
            ["Todas", "Pequeña", "Media", "Grande"]
        )

    # -------------------------
    # Determinar modo
    # -------------------------
    if modo_altitud:
        modo = "Altitud"
    elif modo_capacidad:
        modo = "Capacidad"
    else:
        modo = "Normal"

    # -------------------------
    # Filtrar por estación
    # -------------------------
    if estacion_sel != "Todas":
        df_map = df_map[df_map["nombre"] == estacion_sel]

    # -------------------------
    # Filtrar por categoría
    # -------------------------
    if categoria_sel != "Todas":
        df_map = df_map[df_map["categoria"] == categoria_sel]

    # -------------------------
    # Lógica de visualización
    # -------------------------
    color = None
    size = None
    color_scale = None
    range_color = None

    if modo == "Altitud":
        color = "Altitud"
        color_scale = "Plasma"

    elif modo == "Capacidad":
        size = "Capacidad"
        color = "Capacidad"
        color_scale = "Magma_r"
        range_color = (10, df_map["Capacidad"].max())

    elif modo == "Normal":
        pass

    # -------------------------
    # Crear mapa
    # -------------------------
    fig_map = px.scatter_mapbox(
        df_map,
        lat="latitud",
        lon="longitud",
        hover_name="nombre",
        custom_data=["Capacidad", "Altitud", "Distancia + cercana"],
        zoom=12,
        height=800,
        color=color,
        size=size,
        size_max=15,
        color_continuous_scale=color_scale,
        range_color=range_color
    )

    # -------------------------
    # Estilo del mapa
    # -------------------------
    fig_map.update_layout(
        mapbox_style="mapbox://styles/mapbox/dark-v10",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    if modo == "Normal":
        fig_map.update_traces(marker=dict(size=8))

    # -------------------------
    # Hover personalizado
    # -------------------------
    fig_map.update_traces(
        hovertemplate=
        "<b>%{hovertext}</b><br><br>" +
        "Capacidad: %{customdata[0]} anclajes<br>" +
        "Altitud: %{customdata[1]:.0f} m<br>" +
        "Distancia + cercana: %{customdata[2]:.0f} m<br>" +
        "<extra></extra>"
    )

    # -------------------------
    # Mostrar mapa
    # -------------------------
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("---")

    # -------------------------------------------------------------------
    # KPIs ANÁLISIS ESPACIAL
    # -------------------------------------------------------------------

    st.markdown("## 📊 KPIs del análisis espacial")

    # =========================
    # PREPARACIÓN DE DATOS
    # =========================
    df_kpi = df_estaciones.copy()

    # Filtrar capacidades válidas (>1)
    df_cap_valida = df_kpi[df_kpi["capacidad"] > 1]

    # =========================
    # 📊 BLOQUE 1: DIMENSIÓN DEL SISTEMA
    # =========================
    st.markdown("### 📊 Dimensión del sistema")

    total_estaciones = df_kpi.shape[0]

    cap_min = df_cap_valida["capacidad"].min()
    num_cap_min = df_cap_valida[df_cap_valida["capacidad"] == cap_min].shape[0]

    cap_media = df_cap_valida["capacidad"].mean()

    cap_max = df_cap_valida["capacidad"].max()
    num_cap_max = df_cap_valida[df_cap_valida["capacidad"] == cap_max].shape[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📍 Nº estaciones", total_estaciones)

    col2.metric(
        "🔻 Capacidad mínima",
        f"{cap_min}",
        f"{num_cap_min} estaciones"
    )

    col3.metric(
        "📊 Capacidad media",
        f"{cap_media:.1f}"
    )

    col4.metric(
        "🔺 Capacidad máxima",
        f"{cap_max}",
        f"{num_cap_max} estaciones"
    )

    st.markdown("---")

    # =========================
    # 🌍 BLOQUE 2: GEOGRAFÍA
    # =========================
    st.markdown("### 🌍 Geografía")

    # Estación más alta
    idx_max_alt = df_kpi["altitud"].idxmax()
    estacion_max_alt = df_kpi.loc[idx_max_alt, "nombre"]
    altitud_max = df_kpi.loc[idx_max_alt, "altitud"]

    # Estaciones a nivel del mar (<=5)
    nivel_mar = df_kpi[df_kpi["altitud"] <= 5].shape[0]

    # Altitud media
    altitud_media = df_kpi["altitud"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🏔️ Estación más alta",
        f"{altitud_max:.0f} m",
        estacion_max_alt
    )

    col2.metric(
        "🌊 Estaciones a nivel del mar",
        nivel_mar
    )

    col3.metric(
        "📏 Altitud media",
        f"{altitud_media:.1f} m"
    )

    # -------------------------
    # Relación Altitud vs Capacidad
    # -------------------------
    st.markdown("#### Relación entre altitud y capacidad")

    fig_rel_alt = px.scatter(
        df_cap_valida,
        x="altitud",
        y="capacidad",
        opacity=0.6,
        labels={
            "altitud": "Altitud (m)",
            "capacidad": "Capacidad (anclajes)"
        },
        title="Relación Altitud vs Capacidad"
    )

    fig_rel_alt.update_layout(template="plotly_dark")

    st.plotly_chart(fig_rel_alt, use_container_width=True)

    st.markdown("---")

    # =========================
    # 📍 BLOQUE 3: RED
    # =========================
    st.markdown("### 📍 Red de estaciones")

    # Distancia media
    dist_media = df_kpi["distancia_estacion_cercana"].mean()

    # Estación más aislada
    idx_aislada = df_kpi["distancia_estacion_cercana"].idxmax()
    estacion_aislada = df_kpi.loc[idx_aislada, "nombre"]
    dist_aislada = df_kpi.loc[idx_aislada, "distancia_estacion_cercana"]

    # Estación más cercana
    idx_cercana = df_kpi["distancia_estacion_cercana"].idxmin()
    estacion_cercana = df_kpi.loc[idx_cercana, "nombre"]
    dist_cercana = df_kpi.loc[idx_cercana, "distancia_estacion_cercana"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📏 Distancia media entre estaciones",
        f"{dist_media:.0f} m"
    )

    col2.metric(
        "📍 Estación más aislada",
        f"{dist_aislada:.0f} m",
        estacion_aislada
    )

    col3.metric(
        "📌 Estación más cercana",
        f"{dist_cercana:.0f} m",
        estacion_cercana
    )

    st.markdown("---")

    # =========================
    # ⚡ BLOQUE 4: INFRAESTRUCTURA
    # =========================
    st.markdown("### ⚡ Infraestructura")

    # % estaciones con cargador
    df_cargador_valido = df_kpi[df_kpi["capacidad"] > 1]
    pct_cargador = df_cargador_valido["es_cargador"].mean() * 100

    col1, col2 = st.columns(2)

    col1.metric(
        "⚡ % estaciones con cargador",
        f"{pct_cargador:.1f}%"
    )

    # -------------------------
    # Clasificación por tamaño
    # -------------------------
    def clasificar_capacidad(cap):
        if cap < 20:
            return "Pequeña"
        elif cap <= 35:
            return "Media"
        else:
            return "Grande"

    df_cap_valida["categoria"] = df_cap_valida["capacidad"].apply(clasificar_capacidad)

    dist_tamano = df_cap_valida["categoria"].value_counts(normalize=True) * 100

    pct_peq = dist_tamano.get("Pequeña", 0)
    pct_med = dist_tamano.get("Media", 0)
    pct_grande = dist_tamano.get("Grande", 0)

    col2.metric(
        "📊 % estaciones grandes",
        f"{pct_grande:.1f}%"
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "📉 % estaciones pequeñas",
        f"{pct_peq:.1f}%"
    )

    col4.metric(
        "📊 % estaciones medianas",
        f"{pct_med:.1f}%"
    )

    # -------------------------
    # Preparar datos correctamente
    # -------------------------
    df_tamano_plot = dist_tamano.reset_index()
    df_tamano_plot.columns = ["categoria", "porcentaje"]

    st.markdown("---")
    # -------------------------
    # Layout en columnas
    # -------------------------
    col_graf, col_info = st.columns([2, 1])  # puedes ajustar proporción

    # -------------------------
    # Gráfico distribución
    # -------------------------
    with col_graf:
        fig_tamano = px.pie(
            df_tamano_plot,
            names="categoria",
            values="porcentaje",
            title="Distribución de estaciones por tamaño",
            color="categoria",
            color_discrete_sequence=px.colors.sequential.Magma[4:8]
        )

        fig_tamano.update_traces(
            textinfo="percent+label",
            textfont_size=14,
            marker=dict(
                line=dict(color="rgba(0,0,0,0)", width=0)
            ),
            pull=[0.02, 0.02, 0.02]
        )

        fig_tamano.update_layout(
            template="plotly_dark",
            showlegend=True,
            legend=dict(
                orientation="v",
                y=0.5,
                yanchor="middle",
                x=0.85,
                xanchor="left",
                font=dict(size=12)
            ),
            margin=dict(t=50, b=20, l=20, r=20),
        )

        st.plotly_chart(fig_tamano, use_container_width=True)

    # -------------------------
    # Explicación de clasificación
    # -------------------------
    with col_info:
        st.info("""
            📌 Clasificación basada en la capacidad media de las estaciones Bicing:

            - **Pequeña (<20):** estaciones de baja demanda o zonas residenciales
            - **Media (20–35):** estándar del sistema
            - **Grande (>35):** zonas de alta demanda (centro, nodos de transporte)

            👉 Esta segmentación permite entender cómo está distribuida la infraestructura según la demanda esperada.
            """)

# ---------- PÁGINA 3: ANÁLISIS DE ESTACIONES ----------
elif pagina == "🚲 Análisis de estaciones":
    st.markdown("## 🚲 Análisis operativo de estaciones")
    st.markdown("""
    En esta sección se analiza el comportamiento de las estaciones a lo largo del tiempo (2019/03 - 2024/03).
    Se incluyen:
    - Visualización geoespacial interactiva con métricas operativas
    - Patrones de disponibilidad por hora y día
    - Estaciones críticas (más vacías, más llenas, mayor variabilidad)
    - Evolución temporal de estaciones individuales
    """)
    st.markdown("---")

    st.markdown("### 🗺️ Mapa operativo de estaciones")
    st.markdown("""
    Cada punto representa una estación Bicing. Selecciona una métrica para colorear el mapa
    y haz clic en una estación para ver su análisis detallado.
    """)
    st.markdown("---")

    # ── BOTONES DE MÉTRICA ───────────────────────────────────────────
    col_b1, col_b2, col_b3, col_b4, col_b5, col_b6, col_busq = st.columns([1,1,1,1,1,1,2])
    with col_b1: btn_todas     = st.button("🗺️ Estaciones",  help="Muestra todas las estaciones sin métrica de color.")
    with col_b2: btn_flujo     = st.button("↔️ Flujo neto",  help="Flujo neto histórico medio. Negativo = estación origen. Positivo = estación destino.")
    with col_b3: btn_ocupacion = st.button("📊 Ocupación",   help="% de anclajes ocupados por bicis en media.")
    with col_b4: btn_vacia     = st.button("🔵 % Vacía",     help="% del tiempo que la estación estuvo completamente sin bicis.")
    with col_b5: btn_llena     = st.button("🔴 % Llena",     help="% del tiempo que la estación estuvo completamente llena.")
    with col_b6: btn_bicis     = st.button("🚲 Bicis",       help="Número medio de bicis disponibles.")
    with col_busq:
        estacion_mapa_sel = st.selectbox(
            "🔍 Buscar estación",
            ["Todas"] + sorted(df_mapa['nombre'].dropna().unique().tolist()),
            key='selectbox_buscar_mapa',
            label_visibility='collapsed'
        )

    # ── DETERMINAR MÉTRICA ACTIVA ────────────────────────────────────
    if btn_vacia:
        metrica       = "pct_vacia"
        metrica_label = "% Tiempo vacía"
        color_scale   = "Blues"
        hover_extra   = "🔵% Vacía: %{customdata[1]:.1f}%"

    elif btn_llena:
        metrica       = "pct_llena"
        metrica_label = "% Tiempo llena"
        color_scale   = "Reds"
        hover_extra   = "🔴% Llena: %{customdata[1]:.1f}%"

    elif btn_bicis:
        metrica       = "bicis_media"
        metrica_label = "Bicis disponibles (media)"
        color_scale   = "Greens"
        hover_extra   = "🚲 Bicis media: %{customdata[1]:.1f}"

    elif btn_ocupacion:
        metrica           = "ocupacion_media"
        metrica_label     = "Ocupación media (%)"
        color_scale       = "RdBu_r"
        color_midpoint    = 50        # punto medio = 50% de anclajes ocupados
        hover_extra       = "📊 Ocupación media: %{customdata[1]:.1f}%"

    elif btn_flujo:
        metrica       = "flujo_neto_medio"
        metrica_label = "Flujo neto medio (bicis/intervalo)"
        color_scale   = "RdBu"
        hover_extra   = "↔️ Flujo neto medio: %{customdata[1]:.2f}"

    else:
        metrica       = None
        metrica_label = "Estaciones"
        color_scale   = None
        hover_extra   = None

    # ── PREPARAR DATOS ───────────────────────────────────────────────
    # 1. Filtrar solo estaciones con coordenadas válidas
    df_mapa_plot = df_mapa.dropna(subset=["latitud", "longitud"]).copy()

    # 2. Si hay métrica, filtrar estaciones que tienen ese dato
    if metrica is not None:
        df_mapa_plot = df_mapa_plot.dropna(subset=[metrica]).copy()
    else:
        # Modo "Estaciones": mostrar todas las que tienen al menos una métrica (las 514)
        # Para eso, filtramos donde ocupacion_media no sea nula (o cualquier métrica)
        df_mapa_plot = df_mapa_plot.dropna(subset=["pct_vacia"]).copy()

    
    # 3. Filtrar por estación seleccionada en el selectbox (si no es "Todas")
    estacion_mapa_sel = st.session_state.get('selectbox_buscar_mapa', 'Todas')
    if estacion_mapa_sel != "Todas":
        df_mapa_plot = df_mapa_plot[df_mapa_plot['nombre'] == estacion_mapa_sel]


    # ── CREAR MAPA ───────────────────────────────────────────────────
    fig_mapa_op = px.scatter_mapbox(
        df_mapa_plot,
        lat="latitud",
        lon="longitud",
        color=metrica,
        hover_name="nombre",
        custom_data=[
            "id_estacion",          
            metrica if metrica is not None else "ocupacion_media",  
        ],
        zoom=12,
        height=800,
        color_continuous_scale=color_scale,
        color_continuous_midpoint=50 if metrica == "ocupacion_media" else (0 if metrica == "flujo_neto_medio" else None),
    )

    fig_mapa_op.update_traces(
        marker=dict(size=8, opacity=0.85),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "🆔 ID: %{customdata[0]}<br>" +
            (hover_extra + "<br>" if hover_extra else "") +
            "<extra></extra>"
        )
    )

    fig_mapa_op.update_layout(
        mapbox_style="mapbox://styles/mapbox/dark-v10",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title={
                "text": metrica_label, 
                "font": {"color": "white"}  
            },
            tickfont=dict(color="white"),
            bgcolor="rgba(14,17,23,0.8)",
            bordercolor="rgba(0,245,212,0.3)",
        )
    )

    st.plotly_chart(fig_mapa_op, use_container_width=True, key="mapa_operativo")
    st.markdown("---")

    # ── SECCIÓN 2: KPIs GLOBALES ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 KPIs globales del sistema (2019–2024)")
    st.caption("""
    ℹ️ **Nota:** 'Ocupación' mide el % de anclajes ocupados por bicis en cada momento.
    Ocupación alta = estación llena de bicis = gente no está usando las bicis.
    Ocupación baja = estación vacía de bicis = gente está usando las bicis.
    """)

    # ── Constante reutilizada en el resto del script ──────────────────
    meses_es = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    # ── CÁLCULOS ──────────────────────────────────────────────────────
    n_estaciones     = df_ranking['id_estacion'].nunique()
    ocupacion_global = df_ranking['ocupacion_media'].mean()
    pct_vacia_global = df_ranking['pct_vacia'].mean()
    pct_llena_global = df_ranking['pct_llena'].mean()

    def buscar_nombre(id_est, df_2024, df_historico):
        resultado = df_2024[df_2024['id_estacion'] == id_est]['nombre'].values
        if len(resultado) > 0:
            return resultado[0]
        resultado = df_historico[df_historico['id_estacion'] == id_est]['nombre'].values
        return resultado[0] if len(resultado) > 0 else f"ID {id_est}"

    # Estación más crítica
    idx_critica         = df_ranking['pct_critico'].idxmax()
    val_critica         = df_ranking.loc[idx_critica, 'pct_critico']
    id_critica          = df_ranking.loc[idx_critica, 'id_estacion']
    nombre_critica      = buscar_nombre(id_critica,     df_estaciones_historicas_2024, df_estaciones_historicas)

    # Estación con más flujo negativo (mayor origen)
    idx_origen         = df_ranking['flujo_neto_medio'].idxmin()
    val_origen         = df_ranking.loc[idx_origen, 'flujo_neto_medio']
    id_origen          = df_ranking.loc[idx_origen, 'id_estacion']
    nombre_origen      = buscar_nombre(id_origen,      df_estaciones_historicas_2024, df_estaciones_historicas)

    # Estación con más flujo positivo (mayor destino)
    idx_destino         = df_ranking['flujo_neto_medio'].idxmax()
    val_destino         = df_ranking.loc[idx_destino, 'flujo_neto_medio']
    id_destino          = df_ranking.loc[idx_destino, 'id_estacion']
    nombre_destino      = buscar_nombre(id_destino,     df_estaciones_historicas_2024, df_estaciones_historicas)

    # Estación más equilibrada (flujo neto más cercano a cero)
    idx_equilibrada         = df_ranking['flujo_neto_medio'].abs().idxmin()
    val_equilibrada         = df_ranking.loc[idx_equilibrada, 'flujo_neto_medio']
    id_equilibrada          = df_ranking.loc[idx_equilibrada, 'id_estacion']
    nombre_equilibrada      = buscar_nombre(id_equilibrada, df_estaciones_historicas_2024, df_estaciones_historicas)

    # Mes con más y menos bicis aparcadas
    meses_es       = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    media_por_mes  = df_patron_mensual.groupby('mes_num')['ocupacion_mes'].mean()
    mes_max_num    = media_por_mes.idxmax()
    mes_min_num    = media_por_mes.idxmin()
    mes_max_nombre = meses_es[mes_max_num - 1]
    mes_min_nombre = meses_es[mes_min_num - 1]

    # Hora con menos y más bicis aparcadas
    media_por_hora = df_patron_horario.groupby('hora')['ocupacion_hora'].mean()
    hora_min_ocup  = media_por_hora.idxmin()
    hora_max_ocup  = media_por_hora.idxmax()

    # Hora con más salidas y más entradas (flujo neto)
    media_flujo_hora  = df_patron_horario.groupby('hora')['flujo_neto_hora'].mean()
    hora_max_salidas  = media_flujo_hora.idxmin()   # más negativo = más salidas
    hora_max_entradas = media_flujo_hora.idxmax()   # más positivo = más entradas

    # ── FILA 1: DIMENSIÓN DEL SISTEMA ────────────────────────────────
    st.markdown("##### Dimensión del sistema")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "📍 Número de estaciones",
        f"{n_estaciones}",
        help="Estaciones con datos suficientes para el análisis (período 2019–2024)"
    )
    col2.metric(
        "🚲 Ocupación media del sistema",
        f"{ocupacion_global:.1f}%",
        help="% medio de anclajes ocupados por bicis en el período 2019–2024"
    )
    col3.metric(
        "🔴 % Tiempo vacía (media)",
        f"{pct_vacia_global:.1f}%",
        help="% del tiempo que las estaciones estuvieron completamente sin bicis"
    )
    col4.metric(
        "🔵 % Tiempo llena (media)",
        f"{pct_llena_global:.1f}%",
        help="% del tiempo que las estaciones estuvieron completamente llenas de bicis"
    )

    # ── FILA 2: ESTACIONES DESTACADAS ────────────────────────────────
    st.markdown("##### Estaciones destacadas")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric(
        "⚠️ Estación más crítica",
        f"{val_critica:.1f}%",
        nombre_critica,
        help="Estación con mayor % de tiempo en estado crítico (vacía o llena)"
    )
    col6.metric(
        "🏠 Estación origen",
        f"{val_origen:.2f}",
        nombre_origen,
        help="Estación con flujo neto más negativo: la gente coge bicis aquí más de lo que las devuelve. "
             "Típica de zonas residenciales."
    )
    col7.metric(
        "🏢 Estación destino",
        f"{val_destino:.2f}",
        nombre_destino,
        help="Estación con flujo neto más positivo: la gente devuelve bicis aquí más de lo que las coge. "
             "Típica de zonas de oficinas o transporte."
    )
    col8.metric(
        "⚖️ Estación equilibrada",
        f"{abs(val_equilibrada):.2f}",
        nombre_equilibrada,
        help="Estación con flujo neto más cercano a cero: entradas y salidas de bicis están equilibradas. "
             "No tiene un rol claro de origen ni destino."
    )

    # ── FILA 3: PATRONES TEMPORALES ───────────────────────────────────
    st.markdown("##### Patrones temporales")
    col9, col10, col11, col12 = st.columns(4)
    col9.metric(
        "🕐 Hora de mayor uso",
        f"{hora_min_ocup}:00 h",
        help="Hora del día con menos bicis aparcadas = más bicis en circulación = mayor uso"
    )
    col10.metric(
        "🕐 Hora de menor uso",
        f"{hora_max_ocup}:00 h",
        help="Hora del día con más bicis aparcadas = menos bicis en circulación = menor uso"
    )
    col11.metric(
        "↗️ Hora con más salidas",
        f"{hora_max_salidas}:00 h",
        help="Hora del día en que más bicis salen de las estaciones (flujo neto más negativo)"
    )
    col12.metric(
        "↘️ Hora con más entradas",
        f"{hora_max_entradas}:00 h",
        help="Hora del día en que más bicis entran a las estaciones (flujo neto más positivo)"
    )

    # ── SECCIÓN 3: RANKINGS TOP 10 ───────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏆 Rankings: las estaciones más extremas")
    st.markdown("""
    Top 10 de estaciones según diferentes métricas operativas.
    Solo se incluyen estaciones con suficiente volumen de datos para garantizar representatividad.
    """)

    def enriquecer_top(df_top, col_metrica, unidad='%'):
        """
        Une el top con el histórico de estaciones para obtener nombres.
        Busca primero en el snapshot 2024 y, si no encuentra, en todo el histórico.
        """
        df_merge = df_top.merge(
            df_estaciones_historicas_2024[['id_estacion', 'nombre']],
            on='id_estacion', how='left'
        ).copy()

        # Para las que no tienen nombre en 2024, buscar en histórico completo
        sin_nombre = df_merge['nombre'].isna()
        if sin_nombre.any():
            fallback = df_merge.loc[sin_nombre, 'id_estacion'].map(
                df_estaciones_historicas.drop_duplicates('id_estacion')
                .set_index('id_estacion')['nombre']
            )
            df_merge.loc[sin_nombre, 'nombre'] = fallback

        # Solo eliminar si definitivamente no tiene nombre en ningún año
        df_merge = df_merge[df_merge['nombre'].notna()].copy()

        df_merge[col_metrica] = df_merge[col_metrica].round(2)
        label_col = f"{col_metrica.replace('_', ' ').title()} ({unidad})"
        df_merge = df_merge.rename(columns={
            'nombre':    'Estación',
            col_metrica: label_col
        })
        return df_merge[['Estación', label_col]].reset_index(drop=True)


    df_top_vacias_rich   = enriquecer_top(df_top_vacias,   'pct_vacia')
    df_top_llenas_rich   = enriquecer_top(df_top_llenas,   'pct_llena')
    df_top_criticas_rich = enriquecer_top(df_top_criticas, 'pct_critico')
    df_top_rotacion_rich = enriquecer_top(df_top_rotacion, 'rotacion_total_media', 'bicis/4min')

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        st.markdown(
            f"<h5 style='color:{aurora_palette[1]}'>🔵 Más vacías</h5>",
            unsafe_allow_html=True
        )
        st.caption("Estaciones que más tiempo pasan sin bicis disponibles")
        st.dataframe(df_top_vacias_rich,   use_container_width=True, hide_index=True)

    with col_r2:
        st.markdown(
            f"<h5 style='color:{aurora_palette[3]}'>🔴 Más llenas</h5>",
            unsafe_allow_html=True
        )
        st.caption("Estaciones que más tiempo pasan con todos los anclajes ocupados")
        st.dataframe(df_top_llenas_rich,   use_container_width=True, hide_index=True)

    with col_r3:
        st.markdown(
            f"<h5 style='color:{nebula_palette[1]}'>⚠️ Más críticas</h5>",
            unsafe_allow_html=True
        )
        st.caption("Estaciones que más tiempo pasan en estado extremo (vacía o llena)")
        st.dataframe(df_top_criticas_rich, use_container_width=True, hide_index=True)

    with col_r4:
        st.markdown(
            f"<h5 style='color:{aurora_palette[2]}'>🔄 Mayor rotación</h5>",
            unsafe_allow_html=True
        )
        st.caption("Cambio medio de bicis por intervalo de 4 minutos. Mayor valor = estación más activa.")
        st.dataframe(df_top_rotacion_rich, use_container_width=True, hide_index=True)

    # ── SECCIÓN 4: PATRONES GLOBALES ─────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 Patrones globales del sistema")
    st.caption("""
    ℹ️ Recuerda: en todas las gráficas de esta sección, el eje Y mide el **% de anclajes 
    ocupados por bicis**. Un valor alto significa muchas bicis aparcadas (la gente no las está usando). 
    Un valor bajo significa pocas bicis aparcadas (la gente las está usando).
    """)

    # ── 4.1 PATRÓN HORARIO GLOBAL ────────────────────────────────────
    st.markdown("#### 🕐 Bicis aparcadas por hora del día (media global)")
    st.markdown("""
    Muestra cuántas bicis hay aparcadas en media a cada hora del día.  
    - **Valores altos** (madrugada) → las bicis están aparcadas, el sistema descansa.  
    - **Valores bajos** (mediodía / tarde) → las bicis están en circulación, el sistema está siendo usado.
    """)

    patron_horario_global = (
        df_patron_horario
        .groupby('hora')['ocupacion_hora']
        .mean()
        .reset_index()
        .rename(columns={'ocupacion_hora': 'ocupacion_media'})
        .sort_values('hora')
    )

    fig_horario_global = px.line(
        patron_horario_global,
        x='hora',
        y='ocupacion_media',
        markers=True,
        line_shape='spline',
        labels={'hora': 'Hora del día', 'ocupacion_media': '% anclajes con bici'},
        title='% de anclajes ocupados por bicis — media por hora del día'
    )
    fig_horario_global.update_traces(
        line=dict(color=aurora_palette[4], width=2),
        marker=dict(size=6, color=aurora_palette[0])
    )
    fig_horario_global.update_layout(
        template='plotly_dark',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        yaxis=dict(gridcolor='white')
    )
    st.plotly_chart(fig_horario_global, use_container_width=True, key='fig_horario_global')


    dias_orden = [1, 2, 3, 4, 5, 6, 7]
    dias_nombres = {1:'Lunes', 2:'Martes', 3:'Miércoles',
                    4:'Jueves', 5:'Viernes', 6:'Sábado', 7:'Domingo'}
    

    # ── 4.3 HEATMAP HORA × DÍA DE LA SEMANA ─────────────────────────
    st.markdown("#### 🗓️ Heatmap: bicis aparcadas por hora × día")
    st.markdown("""
    - **Color turquesa intenso** → muchas bicis aparcadas → bajo uso del sistema  
    - **Color magenta/rosado** → pocas bicis aparcadas → alto uso del sistema  
    - El patrón rosado en las madrugadas de entre semana indica que las bicis se usan para ir al trabajo.
    """)

    heatmap_global = (
        df_patron_hora_dia
        .groupby(['hora', 'dia_semana'])['ocupacion_promedio']
        .mean()
        .reset_index()
    )
    heatmap_pivot = heatmap_global.pivot(
        index='dia_semana', columns='hora', values='ocupacion_promedio'
    )
    heatmap_pivot.index = [dias_nombres.get(d, str(d)) for d in heatmap_pivot.index]

    fig_heatmap_global = px.imshow(
        heatmap_pivot,
        color_continuous_scale=[aurora_palette[3], aurora_palette[0]],
        aspect='auto',
        labels=dict(x='Hora del día', y='Día de la semana', color='Ocupación (%)'),
        title='Ocupación media de anclajes por bicis: hora × día de la semana'
    )
    fig_heatmap_global.update_layout(template='plotly_dark')
    st.plotly_chart(fig_heatmap_global, use_container_width=True, key='fig_heatmap_global')

    # ── 4.3c OCUPACIÓN MEDIA POR AÑO Y MES ───────────────────────────
    st.markdown("#### 📅 Ocupación media por mes y año")
    st.markdown("""
    Estas visualizaciones muestran cómo varía la ocupación media del sistema a lo largo 
    de los meses en cada año del período 2019–2024.
    Permiten identificar:
    - **Patrones estacionales** repetidos año a año
    - **Anomalías** como el impacto del COVID-19 en 2020
    - **Huecos de cobertura** del dataset (celdas vacías o líneas interrumpidas)
    """)

    # Preparar datos: media ponderada por muestras para cada año × mes
    ocupacion_año_mes = (
        df_resumen_diario
        .assign(ocupacion_ponderada=lambda df: df['ocupacion_promedio'] * df['muestras_dia'])
        .groupby(['año', 'mes_num'])
        .agg(
            ocupacion_media=('ocupacion_ponderada', 'sum'),
            muestras_total=('muestras_dia', 'sum')
        )
        .reset_index()
    )
    ocupacion_año_mes['ocupacion_media'] = ocupacion_año_mes['ocupacion_media'] / ocupacion_año_mes['muestras_total']
    ocupacion_año_mes = ocupacion_año_mes.drop(columns='muestras_total')
    ocupacion_año_mes['mes_nombre'] = ocupacion_año_mes['mes_num'].apply(lambda x: meses_es[x - 1])

    # ── HEATMAP AÑO × MES ─────────────────────────────────────────────
    heatmap_año_mes = ocupacion_año_mes.pivot(
        index='año', columns='mes_nombre', values='ocupacion_media'
    )
    # Ordenar columnas por mes
    heatmap_año_mes = heatmap_año_mes[
        [m for m in meses_es if m in heatmap_año_mes.columns]
    ]

    fig_heatmap_año_mes = px.imshow(
        heatmap_año_mes,
        color_continuous_scale=[aurora_palette[3], aurora_palette[0]],
        aspect='auto',
        labels=dict(x='Mes', y='Año', color='Ocupación (%)'),
        title='Ocupación media por mes y año — huecos = días sin datos en el dataset'
    )
    fig_heatmap_año_mes.update_layout(
        template='plotly_dark',
        xaxis=dict(side='bottom'),
        coloraxis_colorbar=dict(
            title={"text": "Ocupación (%)", "font": {"color": "white"}},
            tickfont=dict(color="white")
        )
    )
    st.plotly_chart(fig_heatmap_año_mes, use_container_width=True, key='fig_heatmap_año_mes')

    # ── LÍNEA MÚLTIPLE AÑO × MES ──────────────────────────────────────
    años_disponibles = sorted(ocupacion_año_mes['año'].unique())
    colores_años = [
        aurora_palette[0], aurora_palette[1], aurora_palette[2],
        aurora_palette[3], aurora_palette[5], nebula_palette[1]
    ]

    fig_linea_años = go.Figure()

    for i, año in enumerate(años_disponibles):
        datos_año = (
            ocupacion_año_mes[ocupacion_año_mes['año'] == año]
            .sort_values('mes_num')
        )
        fig_linea_años.add_trace(go.Scatter(
            x=datos_año['mes_nombre'],
            y=datos_año['ocupacion_media'],
            mode='lines+markers',
            name=str(año),
            line=dict(color=colores_años[i % len(colores_años)], width=2),
            marker=dict(size=6),
            connectgaps=False    # los huecos quedan como interrupciones visibles
        ))

    fig_linea_años.update_layout(
        template='plotly_dark',
        title='Ocupación media mensual por año — interrupciones = huecos de datos',
        xaxis=dict(
            title='Mes',
            categoryorder='array',
            categoryarray=meses_es
        ),
        yaxis=dict(
            title='Ocupación media (%)',
            gridcolor='white'
        ),
        legend=dict(font=dict(color='white')),
        hovermode='x unified'
    )
    st.plotly_chart(fig_linea_años, use_container_width=True, key='fig_linea_años')

    # ── KPIs DE MES (con nota de sesgo) ───────────────────────────────
    # Calcular sobre datos ponderados (más robusto que la media simple)
    media_por_mes_ponderada = (
        ocupacion_año_mes
        .groupby('mes_num')['ocupacion_media']
        .mean()
    )
    mes_max_num    = media_por_mes_ponderada.idxmax()
    mes_min_num    = media_por_mes_ponderada.idxmin()
    mes_max_nombre = meses_es[mes_max_num - 1]
    mes_min_nombre = meses_es[mes_min_num - 1]

    col_mes1, col_mes2 = st.columns(2)
    col_mes1.metric(
        "📅 Mes con más bicis aparcadas",
        mes_max_nombre,
        help="Mes con mayor ocupación media de anclajes = menor uso del sistema"
    )
    col_mes2.metric(
        "📅 Mes con menos bicis aparcadas",
        mes_min_nombre,
        help="Mes con menor ocupación media de anclajes = mayor uso del sistema"
    )
    st.caption("""
    ⚠️ **Nota metodológica:** estos valores pueden estar influenciados por huecos de cobertura 
    en el dataset. En particular, marzo y abril de 2020 tienen muy pocos datos válidos debido 
    al confinamiento por COVID-19, y agosto-septiembre de 2023 tienen un incidente técnico 
    que redujo la cobertura. Las gráficas anteriores permiten visualizar estas anomalías.
    """)

    # ── 4.3b CURVA DE FLUJO NETO HORARIO GLOBAL ──────────────────────
    st.markdown("#### ↔️ Flujo neto por hora del día (media global)")
    st.markdown("""
    Muestra si en cada hora del día el sistema **pierde o gana bicis** en media.
    - **Valores negativos** (área roja) → las bicis salen de las estaciones: la gente las está cogiendo
    - **Valores positivos** (área azul) → las bicis entran a las estaciones: la gente las está devolviendo
    - El cruce por cero indica el momento de cambio entre hora de uso y hora de devolución
    """)

    flujo_horario_global = (
        df_patron_horario
        .groupby('hora')['flujo_neto_hora']
        .mean()
        .reset_index()
        .rename(columns={'flujo_neto_hora': 'flujo_neto_medio'})
        .sort_values('hora')
    )

    fig_flujo_global = go.Figure()

    # Área negativa — salidas (rojo)
    fig_flujo_global.add_trace(go.Scatter(
        x=flujo_horario_global['hora'],
        y=flujo_horario_global['flujo_neto_medio'].clip(upper=0),
        fill='tozeroy',
        mode='none',
        fillcolor='rgba(255,151,112,0.4)',
        name='Salidas (bicis cogidas)'
    ))

    # Área positiva — entradas (azul)
    fig_flujo_global.add_trace(go.Scatter(
        x=flujo_horario_global['hora'],
        y=flujo_horario_global['flujo_neto_medio'].clip(lower=0),
        fill='tozeroy',
        mode='none',
        fillcolor='rgba(58,134,255,0.4)',
        name='Entradas (bicis devueltas)'
    ))

    # Línea principal
    fig_flujo_global.add_trace(go.Scatter(
        x=flujo_horario_global['hora'],
        y=flujo_horario_global['flujo_neto_medio'],
        mode='lines+markers',
        line=dict(color='white', width=2),
        marker=dict(size=5, color='white'),
        name='Flujo neto medio'
    ))

    # Línea de cero
    fig_flujo_global.add_hline(
        y=0,
        line_dash='dash',
        line_color='rgba(255,255,255,0.4)',
        line_width=1
    )

    fig_flujo_global.update_layout(
        template='plotly_dark',
        title='Flujo neto medio por hora del día',
        xaxis=dict(
            title='Hora del día',
            tickmode='linear', tick0=0, dtick=1
        ),
        yaxis=dict(
            title='Flujo neto (bicis/intervalo)',
            gridcolor= 'white',
            zerolinecolor='rgba(255,255,255,0.3)'
        ),
        legend=dict(font=dict(color='white')),
        hovermode='x unified'
    )
    st.plotly_chart(fig_flujo_global, use_container_width=True, key='fig_flujo_global')

    # ── 4.4 SERIE TEMPORAL GLOBAL ─────────────────────────────────────
    st.markdown("#### 📆 Evolución temporal global (2019–2024)")
    st.markdown("""
    Cada punto es la media diaria de bicis aparcadas en todas las estaciones.  
    - **Picos altos** → días en que las bicis estuvieron paradas (festivos, mal tiempo, verano)  
    - **Valles** → días de alto uso (bicis en circulación)  
    - **Espacios en blanco** → días sin datos en el dataset original (limitación del dataset de Kaggle)  
    - **Caída en marzo 2020** → confinamiento COVID: bajísimo uso del sistema
    """)

    fig_serie = px.line(
        df_serie_temporal.sort_values('fecha'),
        x='fecha',
        y='ocupacion_global',
        line_shape='spline',
        labels={'fecha': 'Fecha', 'ocupacion_global': 'Ocupación global (%)'},
        title='Ocupación global diaria del sistema Bicing'
    )
    fig_serie.update_traces(
        line=dict(color=aurora_palette[1], width=1.5),
        connectgaps=False
    )
    fig_serie.update_layout(
        template='plotly_dark',
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='white'),
        hovermode='x unified'
    )

    # Línea COVID
    fig_serie.add_vline(x='2020-03-14', line_dash='dash', line_color=nebula_palette[0])
    fig_serie.add_annotation(
        x='2020-03-14', y=1, yref='paper',
        text='Inicio confinamiento (COVID)',
        showarrow=False, xanchor='left', yanchor='bottom',
        font=dict(color=nebula_palette[0])
    )
    st.plotly_chart(fig_serie, use_container_width=True, key='fig_serie_global')

    # ── SECCIÓN 5: ANÁLISIS INDIVIDUAL ───────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Análisis individual de estación")
    st.markdown("""
    Selecciona una estación para ver su comportamiento detallado:
    patrones horarios, semanales, mensuales y evolución histórica.
    """)

    # Selector de estación
    # Construir lista de opciones: "Nombre (ID)"
    opciones_estaciones = (
        df_estaciones_filtrado
        .sort_values('nombre')
        [['id_estacion', 'nombre']]
        .dropna(subset=['nombre'])
    )
    opciones_dict = {
        f"{row['nombre']} (ID {row['id_estacion']})": row['id_estacion']
        for _, row in opciones_estaciones.iterrows()
    }

    estacion_sel_label = st.selectbox(
        "Buscar estación",
        options=list(opciones_dict.keys()),
        key='selectbox_estacion_individual'
    )
    estacion_sel_id = opciones_dict[estacion_sel_label]

    # ── 5.1 FICHA RESUMEN ─────────────────────────────────────────────
    datos_estacion = df_ranking[df_ranking['id_estacion'] == estacion_sel_id]

    if datos_estacion.empty:
        st.warning("No hay datos suficientes para esta estación.")
    else:
        fila = datos_estacion.iloc[0]

        # Umbral dinámico para clasificación origen/destino
        # Se calcula aquí para que esté disponible también en el bloque de clasificación más abajo
        std_flujo = df_patron_horario['flujo_neto_hora'].std()
        umbral    = std_flujo * 0.5

        # Hora con más salidas y más entradas de esta estación
        flujo_est_horas = (
            df_patron_horario[df_patron_horario['id_estacion'] == estacion_sel_id]
            .groupby('hora')['flujo_neto_hora']
            .mean()
        )
        if not flujo_est_horas.empty:
            hora_salidas_est  = flujo_est_horas.idxmin()   # más negativo = más salidas
            hora_entradas_est = flujo_est_horas.idxmax()   # más positivo = más entradas
        else:
            hora_salidas_est  = "—"
            hora_entradas_est = "—"

        col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns(6)
        col_f1.metric(
            "📊 Ocupación media",
            f"{fila['ocupacion_media']:.1f}%",
            help="% medio de anclajes ocupados por bicis en esta estación"
        )
        col_f2.metric(
            "🔴 % Tiempo vacía",
            f"{fila['pct_vacia']:.1f}%",
            help="% del tiempo que la estación estuvo completamente sin bicis"
        )
        col_f3.metric(
            "🔵 % Tiempo llena",
            f"{fila['pct_llena']:.1f}%",
            help="% del tiempo que la estación estuvo completamente llena"
        )
        col_f4.metric(
            "↔️ Flujo neto medio",
            f"{fila['flujo_neto_medio']:.2f}",
            help="Flujo neto medio histórico. Negativo = estación origen. Positivo = estación destino."
        )
        col_f5.metric(
            "↗️ Hora más salidas",
            f"{hora_salidas_est}:00 h" if hora_salidas_est != "—" else "—",
            help="Hora del día en que más bicis salen de esta estación en media"
        )
        col_f6.metric(
            "↘️ Hora más entradas",
            f"{hora_entradas_est}:00 h" if hora_entradas_est != "—" else "—",
            help="Hora del día en que más bicis entran a esta estación en media"
        )

        # ── 5.2 PATRÓN HORARIO ────────────────────────────────────────
        st.markdown("#### 🕐 Patrón horario")

        horario_estacion = (
            df_patron_horario[df_patron_horario['id_estacion'] == estacion_sel_id]
            .groupby('hora')['ocupacion_hora']
            .mean()
            .reset_index()
            .rename(columns={'ocupacion_hora': 'ocupacion_media'})
            .sort_values('hora')
        )
        horario_global_ref = patron_horario_global.rename(
            columns={'ocupacion_media': 'media_global'}
        )

        fig_hor_est = px.line(
            horario_estacion,
            x='hora',
            y='ocupacion_media',
            markers=True,
            line_shape='spline',
            labels={'hora': 'Hora', 'ocupacion_media': 'Ocupación (%)'},
            title=f'Patrón horario — {estacion_sel_label}'
        )
        fig_hor_est.update_traces(
            line=dict(color=aurora_palette[1], width=2),
            marker=dict(size=5, color=aurora_palette[0]),
            name='Esta estación'
        )
        # Línea de referencia global (punteada)
        fig_hor_est.add_scatter(
            x=horario_global_ref['hora'],
            y=horario_global_ref['media_global'],
            mode='lines',
            line=dict(color='white', width=1, dash='dot'),
            name='Media global'
        )
        fig_hor_est.update_layout(
            template='plotly_dark',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            yaxis=dict(gridcolor='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig_hor_est, use_container_width=True, key='fig_horario_estacion')

        # ── 5.2b FLUJO NETO DE LA ESTACIÓN ───────────────────────────
        st.markdown("#### ↔️ Flujo neto por hora del día")
        st.markdown("""
        Compara el flujo neto de esta estación con la media global del sistema.
        - **Área roja** → la estación pierde bicis en esa hora (la gente las coge)
        - **Área azul** → la estación gana bicis en esa hora (la gente las devuelve)
        """)

        flujo_estacion = (
            df_patron_horario[df_patron_horario['id_estacion'] == estacion_sel_id]
            .groupby('hora')['flujo_neto_hora']
            .mean()
            .reset_index()
            .rename(columns={'flujo_neto_hora': 'flujo_neto'})
            .sort_values('hora')
        )

        flujo_global_ref = (
            df_patron_horario
            .groupby('hora')['flujo_neto_hora']
            .mean()
            .reset_index()
            .rename(columns={'flujo_neto_hora': 'flujo_neto_global'})
            .sort_values('hora')
        )

        if not flujo_estacion.empty:
            fig_flujo_est = go.Figure()

            # Área negativa — salidas
            fig_flujo_est.add_trace(go.Scatter(
                x=flujo_estacion['hora'],
                y=flujo_estacion['flujo_neto'].clip(upper=0),
                fill='tozeroy',
                mode='none',
                fillcolor='rgba(255,151,112,0.4)',   # aurora_palette[7]
                name='Salidas (bicis cogidas)'
            ))

            # Área positiva — entradas
            fig_flujo_est.add_trace(go.Scatter(
                x=flujo_estacion['hora'],
                y=flujo_estacion['flujo_neto'].clip(lower=0),
                fill='tozeroy',
                mode='none',
                fillcolor='rgba(58,134,255,0.4)',    # nebula_palette[4]
                name='Entradas (bicis devueltas)'
            ))

            # Línea de la estación
            fig_flujo_est.add_trace(go.Scatter(
                x=flujo_estacion['hora'],
                y=flujo_estacion['flujo_neto'],
                mode='lines+markers',
                line=dict(color=aurora_palette[1], width=2),
                marker=dict(size=5, color=aurora_palette[0]),
                name='Esta estación'
            ))

            # Línea de referencia global (punteada)
            fig_flujo_est.add_trace(go.Scatter(
                x=flujo_global_ref['hora'],
                y=flujo_global_ref['flujo_neto_global'],
                mode='lines',
                line=dict(color='white', width=1, dash='dot'),
                name='Media global'
            ))

            # Línea de cero
            fig_flujo_est.add_hline(
                y=0,
                line_dash='dash',
                line_color='rgba(255,255,255,0.4)',
                line_width=1
            )

            fig_flujo_est.update_layout(
                template='plotly_dark',
                title=f'Flujo neto por hora — {estacion_sel_label}',
                xaxis=dict(
                    title='Hora del día',
                    tickmode='linear', tick0=0, dtick=1
                ),
                yaxis=dict(
                    title='Flujo neto (bicis/intervalo)',
                    gridcolor='white',
                    zerolinecolor='rgba(255,255,255,0.3)'
                ),
                legend=dict(font=dict(color='white')),
                hovermode='x unified'
            )
            st.plotly_chart(fig_flujo_est, use_container_width=True, key='fig_flujo_estacion')


        # ── 5.3 PATRÓN SEMANAL ────────────────────────────────────────
        st.markdown("#### 📅 Patrón semanal")

        semanal_estacion = (
            df_patron_semanal[df_patron_semanal['id_estacion'] == estacion_sel_id]
            .groupby('dia_semana')['ocupacion_dia']
            .mean()
            .reset_index()
            .rename(columns={'ocupacion_dia': 'ocupacion_media'})
            .sort_values('dia_semana')
        )
        semanal_estacion['dia_nombre'] = semanal_estacion['dia_semana'].map(dias_nombres)
        semanal_estacion['es_finde'] = semanal_estacion['dia_semana'] >= 6

        semanal_estacion['color'] = semanal_estacion['es_finde'].map(
        {False: 'rgba(0,245,212,0.9)', True: 'rgba(0,245,212,0.9)'}
        )
        

        fig_sem_est = px.bar(
            semanal_estacion,
            x='dia_nombre',
            y='ocupacion_media',
            labels={'dia_nombre': 'Día', 'ocupacion_media': 'Ocupación (%)'},
            title=f'Patrón semanal — {estacion_sel_label}',
            category_orders={'dia_nombre': list(dias_nombres.values())}
        )
        fig_sem_est.update_traces(
            marker_color=semanal_estacion['color'].tolist()
        )
        
        fig_sem_est.update_layout(
            template='plotly_dark',
            showlegend=False,
            yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(fig_sem_est, use_container_width=True, key='fig_semanal_estacion')

        # ── 5.4 HEATMAP HORA × DÍA ────────────────────────────────────
        st.markdown("#### 🗓️ Heatmap: hora × día de la semana")

        heatmap_estacion = (
            df_patron_hora_dia[df_patron_hora_dia['id_estacion'] == estacion_sel_id]
            .groupby(['hora', 'dia_semana'])['ocupacion_promedio']
            .mean()
            .reset_index()
        )
        if not heatmap_estacion.empty:
            heatmap_est_pivot = heatmap_estacion.pivot(
                index='dia_semana', columns='hora', values='ocupacion_promedio'
            )
            heatmap_est_pivot.index = [dias_nombres.get(d, str(d)) for d in heatmap_est_pivot.index]

            fig_heat_est = px.imshow(
                heatmap_est_pivot,
                color_continuous_scale=[aurora_palette[3], aurora_palette[0]],
                aspect='auto',
                labels=dict(x='Hora', y='Día', color='Ocupación (%)'),
                title=f'Heatmap hora × día — {estacion_sel_label}'
            )
            fig_heat_est.update_layout(template='plotly_dark')
            st.plotly_chart(fig_heat_est, use_container_width=True, key='fig_heatmap_estacion')
        else:
            st.info("No hay datos de heatmap para esta estación.")

        # ── 5.5 PATRÓN MENSUAL ────────────────────────────────────────
        st.markdown("#### 📆 Patrón mensual")

        mensual_estacion = (
            df_patron_mensual[df_patron_mensual['id_estacion'] == estacion_sel_id]
            .groupby('mes_num')['ocupacion_mes']
            .mean()
            .reset_index()
            .rename(columns={'ocupacion_mes': 'ocupacion_media'})
            .sort_values('mes_num')
        )
        mensual_estacion['mes_nombre'] = mensual_estacion['mes_num'].apply(
            lambda x: meses_es[x - 1]
        )

        fig_men_est = px.bar(
            mensual_estacion,
            x='mes_nombre',
            y='ocupacion_media',
            labels={'mes_nombre': 'Mes', 'ocupacion_media': 'Ocupación (%)'},
            title=f'Patrón mensual — {estacion_sel_label}',
            category_orders={'mes_nombre': meses_es}
        )
        fig_men_est.update_traces(marker_color=aurora_palette[2], marker_opacity=0.8)
        fig_men_est.update_layout(
            template='plotly_dark',
            yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(fig_men_est, use_container_width=True, key='fig_mensual_estacion')

        # ── 5.6 EVOLUCIÓN ANUAL ───────────────────────────────────────
        st.markdown("#### 📊 Evolución anual")

        evolucion_estacion = (
            df_evolucion_anual[df_evolucion_anual['id_estacion'] == estacion_sel_id]
            .sort_values('año')
        )

        if not evolucion_estacion.empty:
            fig_evol_est = px.line(
                evolucion_estacion,
                x='año',
                y='ocupacion_media',
                markers=True,
                labels={'año': 'Año', 'ocupacion_media': 'Ocupación media (%)'},
                title=f'Evolución anual — {estacion_sel_label}'
            )
            fig_evol_est.update_traces(
                line=dict(color=aurora_palette[5], width=2),
                marker=dict(size=8, color=aurora_palette[5])
            )
            fig_evol_est.update_layout(
                template='plotly_dark',
                xaxis=dict(tickmode='linear'),
                yaxis=dict(gridcolor='white')
            )
            st.plotly_chart(fig_evol_est, use_container_width=True, key='fig_evolucion_estacion')
        else:
            st.info("No hay datos de evolución anual para esta estación.")

    # =============================================================================
    # SECCIÓN 6: COMPARADOR DE ESTACIONES
    # =============================================================================
    st.markdown("---")
    st.markdown("### ⚖️ Comparador de estaciones")
    st.markdown("""
    Selecciona entre 2 y 5 estaciones para comparar sus patrones operativos.
    Puedes usar el selector manual o hacer clic en una **categoría de zona** para cargar
    automáticamente 5 estaciones representativas de ese tipo.
    """)

    # ── DICCIONARIOS MANUALES (IDs verificados en datos históricos 2019–2024) ─────
    CATEGORIAS_IDS = {
        'playa':        [11, 12, 32, 170, 171],
        'hospital':     [113, 443, 279, 427, 40],
        'universidad':  [78, 79, 204, 46, 47],
        'oficinas':     [42, 143, 151, 152, 149],
        'comercial':    [36, 55, 57, 64, 23],
        'transporte':   [5, 6, 95, 97, 188],
        'industrial':   [179, 346, 343, 231, 39],
        'residencial':  [106, 107, 221, 277, 278],
    }

    # Nombres de las estaciones para mostrar en tooltip (verificados en 2024_INFO.csv)
    CATEGORIAS_NOMBRES = {
        'playa':       ["PG. MARITIM, 11", "PG. MARITIM, 23 (HOSPITAL DEL MAR)",
                        "LA BARCELONETA (CN BARCELONETA)", "AV. LITORAL, 40",
                        "AV. LITORAL, 172"],
        'hospital':    ["RONDA DE SANT PAU, 51", "C/ CASANOVA, 139",
                        "C/ MAS CASANOVAS, 137", "C/ DE SANT PAU, 119",
                        "C/ DOCTOR AIGUADER, 2"],
        'universidad': ["PL. UNIVERSITAT / ARIBAU", "PL. UNIVERSITAT",
                        "AV. DIAGONAL, 672", "C/ VILLENA, 1",
                        "C/ RAMON TRIAS FARGAS, 21"],
        'oficinas':    ["C/ CIUTAT DE GRANADA, 168", "C/ SANCHO DE ÁVILA, 170 / LLACUNA",
                        "C/ PALLARS, 182", "C/ PUJADES, 121",
                        "C/ PUJADES, 57B"],
        'comercial':   ["AV. DE LA CATEDRAL, 6", "LA RAMBLA, 80",
                        "LA RAMBLA, 2 (MUSEO DE CERA)", "PL. CATALUNYA, 10-11 (LA RAMBLA)",
                        "C/ BRUC, 45"],
        'transporte':  ["PG. LLUIS COMPANYS, 11 (ARC TRIOMF)", "PG. LLUIS COMPANYS, 18 (ARC TRIOMF)",
                        "C/ TARRAGONA, 103-115", "C/ TARRAGONA, 141",
                        "PG. SANT ANTONI / PL. SANTS"],
        'industrial':  ["PG. ZONA FRANCA, 244", "PG. ZONA FRANCA, 182",
                        "CAMPANA DE LA MAQUINISTA", "C/ PAU ALSINA, 54",
                        "PL. PAU VILA"],
        'residencial': ["PL. JOANIC / C/ BRUNIQUER, 59", "TRAV. DE GRÀCIA, 92 / VIA AUGUSTA",
                        "GRAN DE GRÀCIA, 155 (METRO FONTANA)", "TRAVESSERA DE GRÀCIA, 328",
                        "TRAVESSERA DE GRÀCIA, 368"],
    }

    COLORES_CATEGORIAS = {
        'playa':        aurora_palette[0],   # Turquesa
        'hospital':     nebula_palette[2],   # Rosa intenso
        'universidad':  aurora_palette[2],   # Violeta
        'oficinas':     nebula_palette[1],   # Naranja
        'comercial':    nebula_palette[0],   # Amarillo
        'transporte':   aurora_palette[1],   # Azul brillante
        'industrial':   '#6B7280',           # Gris neutro
        'residencial':  aurora_palette[5],   # Celeste
    }

    categorias_config = {
        "🏖️ Playa":       'playa',
        "🏥 Hospital":    'hospital',
        "🎓 Universidad": 'universidad',
        "💼 Oficinas":    'oficinas',
        "🛍️ Comercial":   'comercial',
        "🚇 Transporte":  'transporte',
        "🏭 Industrial":  'industrial',
        "🏠 Residencial": 'residencial',
    }

    # ── INICIALIZAR SESSION STATE ─────────────────────────────────────────────────
    if 'estaciones_comparar' not in st.session_state:
        st.session_state['estaciones_comparar'] = []
    if 'categoria_activa' not in st.session_state:
        st.session_state['categoria_activa'] = None

    # ── MAPA INVERSO: int(ID) → label ────────────────────────────────────────────
    # FIX CRÍTICO: opciones_dict tiene IDs como float (ej: 11.0) porque 2024_INFO.csv
    # tiene station_id como float64. Normalizamos a int para que el lookup funcione.
    id_a_label = {int(v): k for k, v in opciones_dict.items()}

    # ── BOTONES DE CATEGORÍA ──────────────────────────────────────────────────────
    #st.markdown("##### 📂 Seleccionar por categoría de zona")
    #st.caption("Haz clic en una categoría para cargar 5 estaciones representativas. Pasa el ratón por encima para ver qué estaciones incluye.")

    cols_cat = st.columns(8)
    for i, (label_cat, key_cat) in enumerate(categorias_config.items()):
        with cols_cat[i]:
            is_active = st.session_state['categoria_activa'] == key_cat

            # Construir tooltip con los nombres de las estaciones
            ids_cat    = CATEGORIAS_IDS[key_cat]
            nombres_cat = CATEGORIAS_NOMBRES[key_cat]
            tooltip = "\n".join(
                f"ID {sid}: {nom}" for sid, nom in zip(ids_cat, nombres_cat)
            )

            if st.button(
                label_cat,
                key=f'btn_cat_{key_cat}',
                type='primary' if is_active else 'secondary',
                help=tooltip          # ← aquí aparece el tooltip al hacer hover
            ):
                # Convertir IDs a labels usando el mapa inverso normalizado a int
                labels_cat = [id_a_label[sid] for sid in ids_cat if sid in id_a_label]

                if len(labels_cat) >= 2:
                    st.session_state['estaciones_comparar'] = labels_cat
                    st.session_state['categoria_activa']    = key_cat
                else:
                    st.warning(
                        f"Solo se encontraron {len(labels_cat)} estaciones con datos "
                        f"para '{label_cat}'. Puede que algunas no estén en el dataset histórico."
                    )


    # ── SELECTOR MANUAL ───────────────────────────────────────────────────────────
    st.markdown("##### ✏️ O selecciona estaciones manualmente")
    estaciones_comparar_labels = st.multiselect(
        "Estaciones a comparar (máx. 5)",
        options=list(opciones_dict.keys()),
        default=st.session_state.get('estaciones_comparar', []),
        max_selections=5,
        key='multiselect_comparador'
    )

    # Sincronizar: si el usuario toca el multiselect manualmente, desactivar categoría
    if estaciones_comparar_labels != st.session_state.get('estaciones_comparar', []):
        st.session_state['estaciones_comparar'] = estaciones_comparar_labels
        st.session_state['categoria_activa']    = None

    # ── GUARD ─────────────────────────────────────────────────────────────────────
    if len(estaciones_comparar_labels) < 2:
        st.info("ℹ️ Selecciona al menos **2 estaciones** para activar el comparador (máximo 5).")

    else:
        ids_comparar     = [int(opciones_dict[lbl]) for lbl in estaciones_comparar_labels]
        nombres_comparar = [lbl.split(' (ID')[0] for lbl in estaciones_comparar_labels]

        # ── PALETA DE COLORES ─────────────────────────────────────────────────────
        if st.session_state.get('categoria_activa'):
            import colorsys
            color_base = COLORES_CATEGORIAS[st.session_state['categoria_activa']]

            def ajustar_luminosidad(hex_color, factor):
                hex_color = hex_color.lstrip('#')
                r, g, b = tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
                h, l, s = colorsys.rgb_to_hls(r, g, b)
                l = max(0.15, min(0.92, l * factor))
                r, g, b = colorsys.hls_to_rgb(h, l, s)
                return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

            colores_comparar = [ajustar_luminosidad(color_base, f)
                                for f in [1.0, 0.75, 1.25, 0.55, 1.45]]
        else:
            colores_comparar = [
                aurora_palette[0], aurora_palette[3],
                aurora_palette[2], nebula_palette[1], aurora_palette[5]
            ]

        # ── 6.1 PATRÓN HORARIO — OCUPACIÓN ───────────────────────────────────────
        st.markdown("#### 🕐 Patrón horario comparado — Ocupación")

        fig_comp_hor = go.Figure()
        for i, est_id in enumerate(ids_comparar):
            datos_hor = (
                df_patron_horario[df_patron_horario['id_estacion'] == est_id]
                .groupby('hora')['ocupacion_hora'].mean()
                .reset_index().sort_values('hora')
            )
            if datos_hor.empty:
                continue
            fig_comp_hor.add_trace(go.Scatter(
                x=datos_hor['hora'],
                y=datos_hor['ocupacion_hora'],
                mode='lines+markers',
                name=nombres_comparar[i],
                line=dict(color=colores_comparar[i % len(colores_comparar)], width=2),
                marker=dict(size=5)
            ))
        fig_comp_hor.update_layout(
            template='plotly_dark',
            title='Ocupación media por hora del día',
            xaxis=dict(title='Hora del día', tickmode='linear', tick0=0, dtick=1),
            yaxis=dict(title='Ocupación media (%)', gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(font=dict(color='white')),
            hovermode='x unified'
        )
        st.plotly_chart(fig_comp_hor, use_container_width=True, key='fig_comp_horario')

        # ── 6.2 FLUJO NETO ────────────────────────────────────────────────────────
        st.markdown("#### ↔️ Patrón horario comparado — Flujo neto")
        st.markdown("""
        - **Valores negativos** → la estación pierde bicis (la gente las coge)
        - **Valores positivos** → la estación gana bicis (la gente las devuelve)
        """)

        fig_comp_flujo = go.Figure()
        for i, est_id in enumerate(ids_comparar):
            datos_flujo = (
                df_patron_horario[df_patron_horario['id_estacion'] == est_id]
                .groupby('hora')['flujo_neto_hora'].mean()
                .reset_index().sort_values('hora')
            )
            if datos_flujo.empty:
                continue
            fig_comp_flujo.add_trace(go.Scatter(
                x=datos_flujo['hora'],
                y=datos_flujo['flujo_neto_hora'],
                mode='lines+markers',
                name=nombres_comparar[i],
                line=dict(color=colores_comparar[i % len(colores_comparar)], width=2),
                marker=dict(size=5)
            ))
        fig_comp_flujo.add_hline(y=0, line_dash='dash',
                                  line_color='rgba(255,255,255,0.4)', line_width=1)
        fig_comp_flujo.update_layout(
            template='plotly_dark',
            title='Flujo neto por hora del día',
            xaxis=dict(title='Hora del día', tickmode='linear', tick0=0, dtick=1),
            yaxis=dict(title='Flujo neto (bicis/intervalo)',
                       gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(font=dict(color='white')),
            hovermode='x unified'
        )
        st.plotly_chart(fig_comp_flujo, use_container_width=True, key='fig_comp_flujo')

        # ── 6.3 RADAR ─────────────────────────────────────────────────────────────
        st.markdown("#### 🕸️ Perfil operativo comparado (radar)")
        st.markdown("""
        Cada eje va de 0 a 100, normalizado respecto al percentil 95 de todas las estaciones.
        - **Ocupación:** % de anclajes con bici. Alto = muchas bicis paradas.
        - **% Vacía / % Llena:** tiempo en estado extremo. Idealmente, ambos bajos.
        - **Rotación:** movimiento de bicis por intervalo. Alto = estación muy activa.
        - **Bicis media:** cantidad media de bicis disponibles.
        - **Flujo neto:** valor absoluto. Alto = estación muy direccional.
        """)

        metricas_radar  = ['ocupacion_media', 'pct_vacia', 'pct_llena',
                           'rotacion_total_media', 'bicis_media', 'flujo_neto_medio']
        etiquetas_radar = ['Ocupación', '% Vacía', '% Llena',
                           'Rotación', 'Bicis media', 'Flujo neto']

        df_ranking_radar = df_ranking.copy()
        df_ranking_radar['flujo_neto_medio'] = df_ranking_radar['flujo_neto_medio'].abs()
        # Normalizar id_estacion a int también en df_ranking por si acaso
        df_ranking_radar['id_estacion'] = df_ranking_radar['id_estacion'].astype(int)
        percentil_95 = {col: df_ranking_radar[col].quantile(0.95) for col in metricas_radar}

        fig_radar = go.Figure()
        for i, est_id in enumerate(ids_comparar):
            datos_radar = df_ranking_radar[df_ranking_radar['id_estacion'] == est_id]
            if datos_radar.empty:
                continue
            fila_radar = datos_radar.iloc[0]
            valores_norm = [
                min(
                    (fila_radar[col] / percentil_95[col] * 100)
                    if (pd.notna(fila_radar[col]) and percentil_95[col] > 0) else 0,
                    100
                )
                for col in metricas_radar
            ]
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_norm + [valores_norm[0]],
                theta=etiquetas_radar + [etiquetas_radar[0]],
                fill='toself',
                fillcolor=colores_comparar[i % len(colores_comparar)],
                opacity=0.35,
                line=dict(color=colores_comparar[i % len(colores_comparar)], width=2.5),
                name=nombres_comparar[i]
            ))
        fig_radar.update_layout(
            template='plotly_dark',
            height=550,
            polar=dict(
                bgcolor='rgba(14,17,23,0.8)',
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    tickvals=[20, 40, 60, 80, 100],
                    tickfont=dict(color='white', size=10),
                    gridcolor='rgba(255,255,255,0.15)',
                    linecolor='rgba(255,255,255,0.15)'
                ),
                angularaxis=dict(
                    tickfont=dict(color='white', size=13),
                    gridcolor='rgba(255,255,255,0.15)',
                    linecolor='rgba(255,255,255,0.15)'
                )
            ),
            legend=dict(
                font=dict(color='white', size=12),
                bgcolor='rgba(14,17,23,0.8)',
                bordercolor=aurora_palette[0],
                borderwidth=1
            ),
            title=dict(
                text='Perfil operativo comparado (normalizado al percentil 95)',
                font=dict(color='white')
            ),
            margin=dict(l=80, r=80, t=80, b=80)
        )
        st.plotly_chart(fig_radar, use_container_width=True, key='fig_radar_comparador')

    # ── SECCIÓN 7: MAPA ANIMADO ───────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎬 Mapa animado: comportamiento del sistema por hora")
    st.markdown("""
    Visualización hora a hora del comportamiento del sistema Bicing durante un día típico.
    Selecciona qué métrica quieres animar.
    - **Flujo neto:** rojo = estación perdiendo bicis (uso activo), azul = estación ganando bicis (devoluciones), blanco = sin cambio
    - **Ocupación:** intensidad del color según % de anclajes ocupados por bicis
    """)
    st.caption("""
    ℹ️ Los valores son medias históricas por hora del día, calculadas sobre todo el período 2019–2024.
    No representan un día concreto, sino el comportamiento **típico** del sistema.
    """)

    # Selector de métrica para la animación
    metrica_animacion = st.radio(
        "Métrica a animar",
        options=["Flujo neto", "Ocupación"],
        horizontal=True,
        key='radio_metrica_animacion'
    )

    # Preparar datos
    df_anim = df_mapa_animado.dropna(subset=["latitud", "longitud"]).copy()
    df_anim['hora'] = df_anim['hora'].astype(int)
    df_anim = df_anim.sort_values('hora')

    if metrica_animacion == "Flujo neto":
        col_anim        = "flujo_neto_hora"
        label_anim      = "Flujo neto (bicis/intervalo)"
        scale_anim      = "RdBu"
        midpoint_anim   = 0
        # Rango simétrico alrededor del cero
        val_abs_max     = df_anim[col_anim].abs().quantile(0.95)
        range_anim      = [-val_abs_max, val_abs_max]
    else:
        col_anim        = "ocupacion_hora"
        label_anim      = "Ocupación (% anclajes con bici)"
        scale_anim      = [[0, aurora_palette[3]], [1, aurora_palette[0]]]
        midpoint_anim   = None
        range_anim      = [
            df_anim[col_anim].quantile(0.05),
            df_anim[col_anim].quantile(0.95)
        ]

    # Filtrar filas con la métrica nula
    df_anim = df_anim.dropna(subset=[col_anim]).copy()

    # Crear mapa animado
    fig_animado = px.scatter_mapbox(
        df_anim,
        lat="latitud",
        lon="longitud",
        color=col_anim,
        animation_frame="hora",
        hover_name="nombre",
        custom_data=["id_estacion", col_anim],
        zoom=12,
        height=700,
        color_continuous_scale=scale_anim,
        color_continuous_midpoint=midpoint_anim,
        range_color=range_anim,
        labels={col_anim: label_anim}
    )

    fig_animado.update_traces(
        marker=dict(size=8, opacity=0.85),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "🆔 ID: %{customdata[0]}<br>"
            f"{label_anim}: " + "%{customdata[1]:.2f}<br>"
            "🚲 Bicis media: %{customdata[2]:.1f}<br>"
            "<extra></extra>"
        )
    )

    fig_animado.update_layout(
        mapbox_style="mapbox://styles/mapbox/dark-v10",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title={"text": label_anim, "font": {"color": "white"}},
            tickfont=dict(color="white"),
            bgcolor="rgba(14,17,23,0.8)",
            bordercolor="rgba(0,245,212,0.3)",
        ),
        # Configurar velocidad del slider
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "▶ Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 800, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 300}
                    }]
                },
                {
                    "label": "⏸ Pausa",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }
            ],
            "x": 0.1,
            "y": 0,
            "xanchor": "right",
            "yanchor": "top",
            "bgcolor": "#151a28",
            "font": {"color": "white"}
        }],
        sliders=[{
            "currentvalue": {
                "prefix": "Hora: ",
                "font": {"color": "white", "size": 14}
            },
            "font": {"color": "white"},
            "bgcolor": "#151a28",
            "bordercolor": aurora_palette[0],
        }]
    )

    st.plotly_chart(fig_animado, use_container_width=True, key='fig_mapa_animado')

    
# # ---------- PÁGINA 4: ESTADO ACTUAL ----------
# elif pagina == "⚡ Estado actual":
#     st.markdown("## ⚡ Estado actual del sistema")
#     st.markdown("""
#     Consulta del estado actual de las estaciones utilizando la API de datos abiertos de Barcelona.
#     Aquí se podrá:
#     - Seleccionar una estación
#     - Ver bicicletas disponibles
#     - Ver bicicletas eléctricas y mecánicas
#     - Ver anclajes libres
#     """)
#     # Aquí irá el código del estado actual (pendiente)

# ---------- PÁGINA 5: PREDICCIÓN ----------
elif pagina == "🔮 Predicción":
    st.markdown("## 🔮 Predicción de disponibilidad")
    st.markdown("""
    Modelo predictivo para estimar la disponibilidad futura de bicicletas en las estaciones.
    El modelo permitirá estimar:
    - Bicicletas disponibles en **5 minutos**
    - Bicicletas disponibles en **10 minutos**
    - Bicicletas disponibles en **15 minutos**
    """)
    # Aquí irá el código de predicción (pendiente)