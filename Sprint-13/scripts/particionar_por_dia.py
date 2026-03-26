import polars as pl
import os
from tqdm import tqdm

# -----------------------------
# 1. RUTAS
# -----------------------------
BASE_PATH = r"C:\Users\ravin\Desktop\Proyecto\datos_procesados"
RAW_PATH = os.path.join(BASE_PATH, "raw")
PARTITIONED_PATH = os.path.join(BASE_PATH, "bicing_particionado")

# Crear carpetas si no existen
os.makedirs(RAW_PATH, exist_ok=True)
os.makedirs(PARTITIONED_PATH, exist_ok=True)

# Archivo original
INPUT_FILE = os.path.join(RAW_PATH, "bicing_limpio.parquet")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"No se encontró {INPUT_FILE}. Mueve tu parquet original a 'raw/'")

# -----------------------------
# 2. ESCANEAR EL PARQUET (LAZY)
# -----------------------------
print("Escaneando parquet original (lazy, sin cargar en RAM)...")
df_lazy = pl.scan_parquet(INPUT_FILE).with_columns([
    pl.col("fecha").cast(pl.Date)  # Asegura que 'fecha' sea tipo Date
])

# -----------------------------
# 3. OBTENER FECHAS ÚNICAS
# -----------------------------
fechas = df_lazy.select("fecha").unique().collect().to_series().to_list()
print(f"Fechas encontradas: {len(fechas)}")

# -----------------------------
# 4. PARTICIONAR POR DÍA
# -----------------------------
print("Particionando parquet por día...")
for fecha in tqdm(fechas, desc="Particionando por día"):
    # Filtra solo filas de esa fecha y recolecta
    df_fecha = df_lazy.filter(pl.col("fecha") == fecha).collect()
    
    # Carpeta de salida para ese día
    out_dir = os.path.join(PARTITIONED_PATH, f"fecha={fecha}")
    os.makedirs(out_dir, exist_ok=True)
    
    # Guardar parquet
    df_fecha.write_parquet(os.path.join(out_dir, "part-0.parquet"))

print("\n✅ Particionado completado")
print(f"Datos particionados guardados en: {PARTITIONED_PATH}")