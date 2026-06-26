from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "cases.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# 1. Hitung missing value tiap kolom
missing_report = pd.DataFrame({
    "column": df.columns,
    "missing_count": df.isna().sum().values,
    "missing_percentage": (df.isna().sum().values / len(df) * 100).round(2)
})

missing_report.to_csv(
    OUTPUT_DIR / "missing_value_report.csv",
    index=False,
    encoding="utf-8-sig"
)

# 2. Tangani missing value tekstual
text_columns = [
    "no_perkara",
    "tanggal_putus",
    "pengadilan",
    "jenis_perkara",
    "kategori",
    "terdakwa",
    "terdakwa_anon",
    "penuntut_umum",
    "hakim_ketua",
    "pasal",
    "pasal_utama",
    "jenis_narkotika",
    "label_perbuatan",
    "dakwaan",
    "barang_bukti",
    "amar_putusan",
    "pidana_penjara",
    "denda",
    "ringkasan_fakta",
    "argumen_hukum_utama",
    "text_full"
]

for col in text_columns:
    if col in df.columns:
        df[col] = df[col].fillna("Tidak ditemukan di sumber HTML")

# 3. Tangani missing value numerik
if "length_words" in df.columns:
    df["length_words"] = df["length_words"].fillna(0)

# 4. Simpan versi bersih
df.to_csv(
    OUTPUT_DIR / "cases_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Missing value check selesai.")
print("Output:")
print("- data/processed/missing_value_report.csv")
print("- data/processed/cases_cleaned.csv")
print()
print(missing_report)