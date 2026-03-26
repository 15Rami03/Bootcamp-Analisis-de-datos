# ------------------------------------------------------------------- #
# PIPELINE BICING COMPLETO
# ------------------------------------------------------------------- #

import polars as pl
import os
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# ------------------------------------------------------------------- #
# RUTAS
# ------------------------------------------------------------------- #
BASE_PATH = r"C:\Users\ravin\Desktop\Proyecto"
OUTPUT_PATH = os.path.join(BASE_PATH, "datos_procesados")
PARTITIONED_PATH = os.path.join(OUTPUT_PATH, "bicing_particionado")
AGREGADOS_PATH = os.path.join(OUTPUT_PATH, "agregados")
HISTORICAS_PATH = os.path.join(OUTPUT_PATH, "estaciones_historicas.parquet")


# ------------------------------------------------------------------- #
# FUNCIÓN DE PROCESAMIENTO POR FECHA
# ------------------------------------------------------------------- #
def procesar_fecha(fecha):
    año = int(str(fecha)[:4])  # extraer año de la fecha

    df_estaciones = (
        pl.read_parquet(os.path.join(OUTPUT_PATH, "estaciones_historicas.parquet"))
        .filter(pl.col("año_snapshot") == año)
        .select([
            "id_estacion",
            "nombre",
            pl.col("capacidad").alias("capacidad_estacion_actual"),
            "latitud", "longitud"
        ])
    )

    ruta_fecha = os.path.join(PARTITIONED_PATH, f"fecha={fecha}")
    if not os.path.exists(ruta_fecha):
        return None, None, None, None, None

    df_lazy = (
        pl.scan_parquet(ruta_fecha)
        .join(df_estaciones.lazy(), on="id_estacion", how="left")
        .filter(
            (pl.col("dato_valido_bicis") == True) &
            (pl.col("estado") == "IN_SERVICE") &

            #  CLAVE 1: eliminar estaciones sin info (como 532)
            pl.col("latitud").is_not_null() &

            #  CLAVE 2: bbox
            (pl.col("latitud") >= 41.32) &
            (pl.col("latitud") <= 41.47) &
            (pl.col("longitud") >= 2.05) &
            (pl.col("longitud") <= 2.23) &

            #  CLAVE 3: nombre (robusto: smartcity / smart city)
            ~pl.col("nombre")
                .str.to_lowercase()
                .str.contains("prueba|test|smart\\s*city|copa america|copa américa|temporal|demo|taller") &
            (pl.col("bicis_disponibles") + pl.col("anclajes_libres")) > 0
        )
        .with_columns([
            pl.col("bicis_disponibles")
                .diff()
                .over("id_estacion")
                .alias("diff_bicis_signo"),        # con signo, sin abs()

            pl.col("bicis_disponibles")
                .diff()
                .over("id_estacion")
                .abs()
                .alias("diff_bicis"),              # sin signo, para rotación total
        ])
        .with_columns([
            pl.col("diff_bicis").alias("rotacion_total"),
            pl.col("diff_bicis_signo").alias("flujo_neto"),   # negativo=salidas, positivo=entradas

            (pl.col("estacion_vacia") | pl.col("estacion_llena"))
                .cast(pl.Int8)
                .alias("estado_critico")
        ])
    )

    # ── RESUMEN DIARIO ──────────────────────────────────────────────
    resumen_dia = (
        df_lazy.group_by(["id_estacion", "fecha"]).agg([
            # Ocupación
            pl.mean("tasa_ocupacion").alias("ocupacion_promedio"),
            pl.std("tasa_ocupacion").alias("ocupacion_std"),

            # Flujo neto
            pl.mean("flujo_neto").alias("flujo_neto_dia"),
            pl.col("flujo_neto").clip(upper_bound=0).sum().alias("salidas_dia"),    # solo negativos
            pl.col("flujo_neto").clip(lower_bound=0).sum().alias("entradas_dia"),   # solo positivos

            # Bicis
            pl.mean("bicis_disponibles").alias("bicis_promedio"),
            pl.std("bicis_disponibles").alias("bicis_std"),
            pl.quantile("bicis_disponibles", 0.25).alias("bicis_p25"),
            pl.quantile("bicis_disponibles", 0.75).alias("bicis_p75"),

            # Mecánicas y eléctricas
            pl.mean("mecanicas_disponibles").alias("mecanicas_promedio"),
            pl.mean("electricas_disponibles").alias("electricas_promedio"),

            # Anclajes
            pl.mean("anclajes_libres").alias("anclajes_promedio"),
            pl.std("anclajes_libres").alias("anclajes_std"),

            # Estados
            (pl.col("estacion_vacia").sum() / pl.len() * 100).alias("pct_vacia"),
            (pl.col("estacion_llena").sum() / pl.len() * 100).alias("pct_llena"),
            (pl.col("casi_vacia").sum() / pl.len() * 100).alias("pct_casi_vacia"),
            (pl.col("casi_llena").sum() / pl.len() * 100).alias("pct_casi_llena"),
            (pl.col("estado_critico").sum() / pl.len() * 100).alias("pct_critico"),

            # Rotación
            pl.mean("rotacion_total").alias("rotacion_total_media"),
            #pl.mean("rotacion_filtrada").alias("rotacion_filtrada_media"),

            # Temporal
            pl.first("año").alias("año"),
            pl.first("mes_num").alias("mes_num"),
            pl.len().alias("muestras_dia")
        ])
        .filter(pl.col("muestras_dia") > 20)    # Solo días con suficiente data para evitar ruido en el resumen diario, 
        .collect()                              # el número 20 es arbitrario y puede ajustarse según el dataset y el nivel de confianza deseado
    )

    # ── PATRÓN HORARIO ──────────────────────────────────────────────
    patron_horario = (
        df_lazy.group_by(["id_estacion", "hora"]).agg([
            # Ocupación
            pl.mean("tasa_ocupacion").alias("ocupacion_hora"),
            pl.std("tasa_ocupacion").alias("ocupacion_std"),

            # Flujo neto
            pl.mean("flujo_neto").alias("flujo_neto_hora"),
            pl.col("flujo_neto").clip(upper_bound=0).sum().alias("salidas_hora"),    # solo negativos
            pl.col("flujo_neto").clip(lower_bound=0).sum().alias("entradas_hora"),   # solo positivos

            # Bicis
            pl.mean("bicis_disponibles").alias("bicis_promedio"),
            pl.std("bicis_disponibles").alias("bicis_std"),

            # Mecánicas y eléctricas
            pl.mean("mecanicas_disponibles").alias("mecanicas_promedio"),
            pl.mean("electricas_disponibles").alias("electricas_promedio"),

            # Anclajes
            pl.mean("anclajes_libres").alias("anclajes_promedio"),

            # Estados
            (pl.col("estacion_vacia").sum() / pl.len() * 100).alias("pct_vacia_hora"),
            (pl.col("estacion_llena").sum() / pl.len() * 100).alias("pct_llena_hora"),
            (pl.col("casi_vacia").sum() / pl.len() * 100).alias("pct_casi_vacia"),
            (pl.col("casi_llena").sum() / pl.len() * 100).alias("pct_casi_llena"),

            # Rotación
            pl.mean("rotacion_total").alias("rotacion_total_hora"),
            #pl.mean("rotacion_filtrada").alias("rotacion_filtrada_hora"),

            pl.len().alias("muestras")
        ])
        .collect()
    )

    # ── PATRÓN SEMANAL ──────────────────────────────────────────────
    patron_semanal = (
        df_lazy.group_by(["id_estacion", "dia_semana", "es_fin_semana"]).agg([
            # Ocupación
            pl.mean("tasa_ocupacion").alias("ocupacion_dia"),
            pl.std("tasa_ocupacion").alias("ocupacion_std"),

            # Flujo neto
            pl.mean("flujo_neto").alias("flujo_neto_dia"),
            pl.col("flujo_neto").clip(upper_bound=0).sum().alias("salidas_dia"),    # solo negativos
            pl.col("flujo_neto").clip(lower_bound=0).sum().alias("entradas_dia"),   # solo positivos

            # Bicis
            pl.mean("bicis_disponibles").alias("bicis_promedio"),
            pl.std("bicis_disponibles").alias("bicis_std"),

            # Mecánicas y eléctricas
            pl.mean("mecanicas_disponibles").alias("mecanicas_promedio"),
            pl.mean("electricas_disponibles").alias("electricas_promedio"),

            # Anclajes
            pl.mean("anclajes_libres").alias("anclajes_promedio"),

            # Estados
            (pl.col("estacion_vacia").sum() / pl.len() * 100).alias("pct_vacia"),
            (pl.col("estacion_llena").sum() / pl.len() * 100).alias("pct_llena"),
            (pl.col("casi_vacia").sum() / pl.len() * 100).alias("pct_casi_vacia"),
            (pl.col("casi_llena").sum() / pl.len() * 100).alias("pct_casi_llena"),

            # Rotación
            pl.mean("rotacion_total").alias("rotacion_total"),
            #pl.mean("rotacion_filtrada").alias("rotacion_filtrada"),

            pl.len().alias("muestras")
        ])
        .collect()
    )

    # ── PATRÓN MENSUAL ──────────────────────────────────────────────
    patron_mensual = (
        df_lazy.group_by(["id_estacion", "mes_num"]).agg([
            # Ocupación
            pl.mean("tasa_ocupacion").alias("ocupacion_mes"),
            pl.std("tasa_ocupacion").alias("ocupacion_std"),

            # Flujo neto
            pl.mean("flujo_neto").alias("flujo_neto_mes"),
            pl.col("flujo_neto").clip(upper_bound=0).sum().alias("salidas_mes"),    # solo negativos
            pl.col("flujo_neto").clip(lower_bound=0).sum().alias("entradas_mes"),   # solo positivos

            # Bicis
            pl.mean("bicis_disponibles").alias("bicis_promedio"),
            pl.std("bicis_disponibles").alias("bicis_std"),

            # Mecánicas y eléctricas
            pl.mean("mecanicas_disponibles").alias("mecanicas_promedio"),
            pl.mean("electricas_disponibles").alias("electricas_promedio"),

            # Anclajes
            pl.mean("anclajes_libres").alias("anclajes_promedio"),

            # Estados
            (pl.col("estado_critico").sum() / pl.len() * 100).alias("pct_critico"),
            (pl.col("estacion_vacia").sum() / pl.len() * 100).alias("pct_vacia"),
            (pl.col("estacion_llena").sum() / pl.len() * 100).alias("pct_llena"),
            (pl.col("casi_vacia").sum() / pl.len() * 100).alias("pct_casi_vacia"),
            (pl.col("casi_llena").sum() / pl.len() * 100).alias("pct_casi_llena"),

            # Rotación
            pl.mean("rotacion_total").alias("rotacion_total_mes"),
            #pl.mean("rotacion_filtrada").alias("rotacion_filtrada_mes"),

            pl.len().alias("muestras")
        ])
        .collect()
    )

    # ── PATRÓN HORA × DÍA SEMANA (heatmap) ─────────────────────────
    patron_hora_dia = (
        df_lazy.group_by(["id_estacion", "hora", "dia_semana"]).agg([
            # Ocupación
            pl.mean("tasa_ocupacion").alias("ocupacion_promedio"),
            pl.std("tasa_ocupacion").alias("ocupacion_std"),

            # Flujo neto
            pl.mean("flujo_neto").alias("flujo_neto_promedio"),
            pl.col("flujo_neto").clip(upper_bound=0).sum().alias("salidas_promedio"),    # solo negativos
            pl.col("flujo_neto").clip(lower_bound=0).sum().alias("entradas_promedio"),   # solo positivos

            # Bicis
            pl.mean("bicis_disponibles").alias("bicis_promedio"),

            # Mecánicas y eléctricas
            pl.mean("mecanicas_disponibles").alias("mecanicas_promedio"),
            pl.mean("electricas_disponibles").alias("electricas_promedio"),

            # Anclajes
            pl.mean("anclajes_libres").alias("anclajes_promedio"),

            # Estados
            (pl.col("estacion_vacia").sum() / pl.len() * 100).alias("pct_vacia"),
            (pl.col("estacion_llena").sum() / pl.len() * 100).alias("pct_llena"),
            (pl.col("casi_vacia").sum() / pl.len() * 100).alias("pct_casi_vacia"),
            (pl.col("casi_llena").sum() / pl.len() * 100).alias("pct_casi_llena"),

            pl.len().alias("muestras")
        ])
        .collect()
    )

    return resumen_dia, patron_horario, patron_semanal, patron_mensual, patron_hora_dia


# ------------------------------------------------------------------- #
# MAIN
# ------------------------------------------------------------------- #
if __name__ == "__main__":

    os.makedirs(AGREGADOS_PATH, exist_ok=True)

    # 1. Info estaciones
    print("\n1. Cargando info de estaciones...")
    df_estaciones = (pl.read_parquet(HISTORICAS_PATH).filter(pl.col("año_snapshot") == 2024))


    # 2. Fechas únicas
    print("\n2. Extrayendo fechas únicas...")
    fechas = (
        pl.scan_parquet(PARTITIONED_PATH)
        .select("fecha")
        .filter(pl.col("fecha").is_not_null())
        .unique()
        .sort("fecha")
        .collect()
        ["fecha"].to_list()
    )
    print(f"   Fechas encontradas: {len(fechas)}")

    # 3. Procesar en paralelo
    print("\n3. Procesando fechas en paralelo...")
    resumen_list, horario_list, semanal_list, mensual_list, hora_dia_list = [], [], [], [], []

    with ProcessPoolExecutor() as executor:
        for resultado in tqdm(executor.map(procesar_fecha, fechas), total=len(fechas)):
            r, h, s, m, hd = resultado
            if r is not None:
                resumen_list.append(r)
                horario_list.append(h)
                semanal_list.append(s)
                mensual_list.append(m)
                hora_dia_list.append(hd)

    # 4. Guardar agregados base
    print("\n4. Guardando agregados base...")
    
    # Resumen diario (no necesita reagregación, cada fila es un día único)
    pl.concat(resumen_list).write_parquet(
        os.path.join(AGREGADOS_PATH, "resumen_diario_estacion.parquet"))

    # Patrón horario (reagregamos para colapsar los días en una media por hora)
    (
        pl.concat(horario_list)
        .group_by(["id_estacion", "hora"])
        .agg([
            pl.mean("ocupacion_hora"),
            pl.mean("ocupacion_std"),
            pl.mean("flujo_neto_hora"),
            pl.sum("salidas_hora"),
            pl.sum("entradas_hora"),
            pl.mean("bicis_promedio"),
            pl.mean("bicis_std"),
            pl.mean("mecanicas_promedio"),
            pl.mean("electricas_promedio"),
            pl.mean("anclajes_promedio"),
            pl.mean("pct_vacia_hora"),
            pl.mean("pct_llena_hora"),
            pl.mean("pct_casi_vacia"),
            pl.mean("pct_casi_llena"),
            pl.mean("rotacion_total_hora"),
            pl.sum("muestras"),
        ])
        .sort(["id_estacion", "hora"])
        .write_parquet(os.path.join(AGREGADOS_PATH, "patron_horario_estacion.parquet"))
    )

    # Patrón semanal
    pl.concat(semanal_list).write_parquet(
        os.path.join(AGREGADOS_PATH, "patron_semanal_estacion.parquet"))

    # Patrón mensual
    pl.concat(mensual_list).write_parquet(
        os.path.join(AGREGADOS_PATH, "patron_mensual_estacion.parquet"))

    # Patrón hora x día semana (reagregamos igual que el horario)
    (
        pl.concat(hora_dia_list)
        .group_by(["id_estacion", "hora", "dia_semana"])
        .agg([
            pl.mean("ocupacion_promedio"),
            pl.mean("ocupacion_std"),
            pl.mean("flujo_neto_promedio"),
            pl.sum("salidas_promedio"),
            pl.sum("entradas_promedio"),
            pl.mean("bicis_promedio"),
            pl.mean("mecanicas_promedio"),
            pl.mean("electricas_promedio"),
            pl.mean("anclajes_promedio"),
            pl.mean("pct_vacia"),
            pl.mean("pct_llena"),
            pl.mean("pct_casi_vacia"),
            pl.mean("pct_casi_llena"),
            pl.sum("muestras"),
        ])
        .sort(["id_estacion", "dia_semana", "hora"])
        .write_parquet(os.path.join(AGREGADOS_PATH, "patron_hora_dia_semana.parquet"))
    )

    # 5. Rankings y tops
    print("\n5. Calculando rankings...")
    ranking = (
        pl.scan_parquet(os.path.join(AGREGADOS_PATH, "resumen_diario_estacion.parquet"))
        .group_by("id_estacion")
        .agg([
            pl.mean("pct_critico").alias("pct_critico"),
            pl.mean("pct_vacia").alias("pct_vacia"),
            pl.mean("pct_llena").alias("pct_llena"),
            pl.mean("pct_casi_vacia").alias("pct_casi_vacia"),
            pl.mean("pct_casi_llena").alias("pct_casi_llena"),
            pl.mean("ocupacion_promedio").alias("ocupacion_media"),
            pl.mean("bicis_promedio").alias("bicis_media"),
            pl.mean("mecanicas_promedio").alias("mecanicas_media"),
            pl.mean("electricas_promedio").alias("electricas_media"),
            pl.mean("anclajes_promedio").alias("anclajes_media"),
            pl.mean("rotacion_total_media").alias("rotacion_total_media"),
            #pl.mean("rotacion_filtrada_media").alias("rotacion_filtrada_media"),
            pl.mean("flujo_neto_dia").alias("flujo_neto_medio"),
            pl.sum("muestras_dia").alias("muestras")
        ])
        .filter(pl.col("muestras") > 100)   # Solo estaciones con suficiente data para evitar ruido en el ranking, 
        .collect()                          # El número 100 es arbitrario y puede ajustarse según el dataset y el nivel de confianza deseado
    )                                       # El filtro de 100 reduce la visualización de estaciones con muy poca data, que podrían tener porcentajes extremos por falta de representatividad

    ranking.write_parquet(
        os.path.join(AGREGADOS_PATH, "ranking_estaciones_completo.parquet"))

    # Tops derivados del ranking (sin scripts separados)
    ranking.sort("pct_critico", descending=True).head(10).write_parquet(
        os.path.join(AGREGADOS_PATH, "top_estaciones_criticas.parquet"))
    ranking.sort("pct_vacia", descending=True).head(10).write_parquet(
        os.path.join(AGREGADOS_PATH, "top_estaciones_vacias.parquet"))
    ranking.sort("pct_llena", descending=True).head(10).write_parquet(
        os.path.join(AGREGADOS_PATH, "top_estaciones_llenas.parquet"))
    ranking.sort("rotacion_total_media", descending=True).head(10).write_parquet(
        os.path.join(AGREGADOS_PATH, "top_estaciones_rotacion.parquet"))
    
    # 5b. Agregado para mapa animado (flujo neto por estación y hora)
    print("\n5b. Generando agregado para mapa animado...")
    (
        pl.scan_parquet(os.path.join(AGREGADOS_PATH, "patron_horario_estacion.parquet"))
        # DESPUÉS — usamos el snapshot más reciente disponible (2024)
        .join(
            pl.scan_parquet(os.path.join(OUTPUT_PATH, "estaciones_historicas.parquet"))
            .filter(pl.col("año_snapshot") == 2024)
            .select(["id_estacion", "nombre", "latitud", "longitud"]),
            on="id_estacion",
            how="left"
        )
        .filter(
            pl.col("latitud").is_not_null() &
            pl.col("longitud").is_not_null()
        )
        .select([
            "id_estacion", "nombre", "latitud", "longitud",
            "hora",
            "flujo_neto_hora",
            "ocupacion_hora",
        ])
        .collect()
        .write_parquet(os.path.join(AGREGADOS_PATH, "mapa_animado_horario.parquet"))
    )

    # 6. Evolución anual por estación
    print("\n6. Generando evolución anual...")
    (
        pl.scan_parquet(os.path.join(AGREGADOS_PATH, "resumen_diario_estacion.parquet"))
        .group_by(["id_estacion", "año"])
        .agg([
            # Ocupación
            pl.mean("ocupacion_promedio").alias("ocupacion_media"),

            # Bicis
            pl.mean("bicis_promedio").alias("bicis_media"),
            pl.mean("mecanicas_promedio").alias("mecanicas_media"),
            pl.mean("electricas_promedio").alias("electricas_media"),

            # Anclajes
            pl.mean("anclajes_promedio").alias("anclajes_media"),

            # Estados
            pl.mean("pct_vacia").alias("pct_vacia"),
            pl.mean("pct_llena").alias("pct_llena"),
            pl.mean("pct_casi_vacia").alias("pct_casi_vacia"),
            pl.mean("pct_casi_llena").alias("pct_casi_llena"),
            pl.mean("pct_critico").alias("pct_critico"),

            # Rotación
            pl.mean("rotacion_total_media").alias("rotacion_media"),

            pl.sum("muestras_dia").alias("muestras")
        ])
        .sort(["id_estacion", "año"])
        .collect()
        .write_parquet(os.path.join(AGREGADOS_PATH, "evolucion_anual_estacion.parquet"))
    )

    # 7. Serie temporal global
    print("\n7. Generando serie temporal global...")
    (
        pl.scan_parquet(os.path.join(AGREGADOS_PATH, "resumen_diario_estacion.parquet"))
        .group_by(["fecha"])
        .agg([
            # Ocupación
            pl.mean("ocupacion_promedio").alias("ocupacion_global"),
            pl.std("ocupacion_promedio").alias("ocupacion_std_global"),

            # Bicis
            pl.mean("bicis_promedio").alias("bicis_global"),
            pl.mean("mecanicas_promedio").alias("mecanicas_global"),
            pl.mean("electricas_promedio").alias("electricas_global"),

            # Anclajes
            pl.mean("anclajes_promedio").alias("anclajes_global"),

            # Estados
            pl.mean("pct_vacia").alias("ratio_vacias"),
            pl.mean("pct_llena").alias("ratio_llenas"),
            pl.mean("pct_casi_vacia").alias("ratio_casi_vacias"),
            pl.mean("pct_casi_llena").alias("ratio_casi_llenas"),
            pl.mean("pct_critico").alias("ratio_critico"),

            # Rotación
            pl.mean("rotacion_total_media").alias("rotacion_total_global"),
            #pl.mean("rotacion_filtrada_media").alias("rotacion_filtrada_global"),

            # Control
            pl.sum("muestras_dia").alias("num_registros"),
            pl.n_unique("id_estacion").alias("num_estaciones")
        ])
        .sort("fecha")
        .collect()
        .write_parquet(os.path.join(AGREGADOS_PATH, "serie_temporal_global.parquet"))
    )

    # 8. Info estaciones enriquecida (NUEVO)
    print("\n8. Generando info estaciones enriquecida...")
    (
        df_estaciones
        .select(["id_estacion", "nombre", "latitud", "longitud",
                "altitud", "capacidad",
                "codigo_postal"])
        .join(ranking, on="id_estacion", how="left")
        .write_parquet(os.path.join(AGREGADOS_PATH, "info_estaciones_enriquecida.parquet"))
    )

    # 9. Dataset para mapa
    print("\n9. Generando dataset para mapa...")
    (
        pl.read_parquet(os.path.join(AGREGADOS_PATH, "info_estaciones_enriquecida.parquet"))
        .select([
            "id_estacion", "nombre", "latitud", "longitud",
            "ocupacion_media", "pct_critico", "pct_vacia", "pct_llena",
            "pct_casi_vacia", "pct_casi_llena",
            "bicis_media", "mecanicas_media", "electricas_media", "anclajes_media",
            "rotacion_total_media", "flujo_neto_medio",  #"rotacion_filtrada_media", 
        ])
        .write_parquet(os.path.join(AGREGADOS_PATH, "dataset_mapa.parquet"))
    )

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETADO ✅")
    print(f"Archivos generados en: {AGREGADOS_PATH}")
    print("\nArchivos:")
    for f in sorted(os.listdir(AGREGADOS_PATH)):
        size_mb = os.path.getsize(os.path.join(AGREGADOS_PATH, f)) / 1024 / 1024
        print(f"  {f:<45} {size_mb:.1f} MB")
 