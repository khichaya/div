# -*- coding: utf-8 -*-
import pandas as pd

# --- Files ---
file_csv = "result_all.csv"       # CSV file (from PDF)
file_excel = "or1.xlsx"      # Excel file (original)
output_file = "filtered_common.xlsx"  # output file

# --- Load data ---
df_csv = pd.read_csv(file_csv)
df_excel = pd.read_excel(file_excel)

# --- Display columns for checking ---
print("🧾 Columns in Excel file:")
for c in df_excel.columns:
    print(f"- {c}")

print("\n🧾 Columns in CSV file:")
for c in df_csv.columns:
    print(f"- {c}")

# --- Normalize column names (remove spaces / lowercase) ---
df_csv.columns = [c.strip().lower() for c in df_csv.columns]
df_excel.columns = [c.strip() for c in df_excel.columns]

# --- Detect birthdate column automatically in Excel ---
birth_col_candidates = [c for c in df_excel.columns if "ميلاد" in c]
if not birth_col_candidates:
    raise Exception("❌ No column containing 'ميلاد' found in Excel file.")
birth_col = birth_col_candidates[0]
print(f"\n📅 Using Excel birthdate column: {birth_col}")

# --- Convert dates to consistent format ---
df_csv["date_de_naissance"] = pd.to_datetime(
    df_csv["date_de_naissance"], errors="coerce", dayfirst=True
)
df_excel[birth_col] = pd.to_datetime(
    df_excel[birth_col], errors="coerce", dayfirst=True
)

# --- Filter only common birthdates ---
dates_csv = set(df_csv["date_de_naissance"].dropna().unique())
df_filtered = df_excel[df_excel[birth_col].isin(dates_csv)].copy()

# --- Save output with all original columns ---
df_filtered.to_excel(output_file, index=False)

print(f"\n✅ Created '{output_file}' with {len(df_filtered)} matching rows.")
