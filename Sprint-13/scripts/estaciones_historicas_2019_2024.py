import polars as pl
import os

KAGGLE_PATH = r"C:\Users\ravin\Desktop\Proyecto\datos_procesados\intermedios\estaciones_kaggle"
OUTPUT_PATH = r"C:\Users\ravin\Desktop\Proyecto\datos_procesados"

años = [2019, 2020, 2021, 2022, 2023, 2024]         #"El análisis de atributos de estaciones se basa en los archivos INFO de Kaggle, 
snapshots = []                                      # que registran entre 411 (2019) y 513 (2022) estaciones con ficha completa por año."

for año in años:
    ruta = os.path.join(KAGGLE_PATH, f"{año}_INFO.csv")
    
    df = (
        pl.read_csv(ruta, infer_schema_length=0)
        .with_columns(pl.lit(año).alias("año_snapshot"))
        # Limpiar station_id: quitar decimales tipo "1.0" → "1"
        .with_columns(
            pl.col("station_id")
            .str.replace(r"\.0$", "")
            .cast(pl.Int64, strict=False)
            .alias("station_id")
        )
        .rename({
            "station_id": "id_estacion",
            "name": "nombre",
            "lat": "latitud",
            "lon": "longitud",
            "altitude": "altitud",
            "address": "direccion",
            "post_code": "codigo_postal",
            "capacity": "capacidad",
            "cross_street": "calle_cruce",
            "nearby_distance": "distancia_estacion_cercana",
        })
        # Convertir tipos
        .with_columns([
            pl.col("latitud").cast(pl.Float64, strict=False),
            pl.col("longitud").cast(pl.Float64, strict=False),
            pl.col("altitud").cast(pl.Float64, strict=False),
            pl.col("capacidad").cast(pl.Int64, strict=False),
            pl.col("distancia_estacion_cercana").cast(pl.Float64, strict=False),
        ])
        # Una fila por estación: el snapshot más reciente del año
        .sort("date", descending=True)
        .unique(subset=["id_estacion", "año_snapshot"], keep="first")
        # Solo columnas que existen en todos los años
        .select([
            "id_estacion", "año_snapshot", "nombre", "latitud", "longitud",
            "altitud", "direccion", "codigo_postal", "capacidad",
            "calle_cruce", "distancia_estacion_cercana", "physical_configuration"
        ])
    )
    
    snapshots.append(df)
    print(f"  {año}: {df.shape[0]} estaciones únicas")

df_historico = pl.concat(snapshots)

print(f"\nTotal registros: {df_historico.shape[0]}")
print(f"Estaciones únicas: {df_historico['id_estacion'].n_unique()}")

print("\nEstaciones por año:")
print(
    df_historico
    .group_by("año_snapshot")
    .agg(pl.len().alias("num_estaciones"))
    .sort("año_snapshot")
)

df_historico.write_parquet(os.path.join(OUTPUT_PATH, "estaciones_historicas.parquet"))
print("\n✅ estaciones_historicas.parquet guardado")