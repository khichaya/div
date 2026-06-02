# -*- coding: utf-8 -*-
import pandas as pd

# --- الملفات ---
fichier_original = "or.xlsx"
fichier_csv = "result_all.csv"  # أو result_all_converted.csv إذا حولت الصيغ

# --- قراءة الملفات ---
df_orig = pd.read_excel(fichier_original)
df_csv = pd.read_csv(fichier_csv)

# --- تنظيف الأعمدة ---
df_orig.columns = [c.strip().lower() for c in df_orig.columns]
df_csv.columns = [c.strip().lower() for c in df_csv.columns]

# --- تحويل التواريخ إلى نفس الشكل ---
df_orig['تاريخ الميلاد'] = pd.to_datetime(df_orig['تاريخ الميلاد'], errors='coerce', dayfirst=True)
df_csv['date_de_naissance'] = pd.to_datetime(df_csv['date_de_naissance'], errors='coerce', dayfirst=True)

# --- حذف التكرارات والفراغات ---
dates_orig = df_orig['تاريخ الميلاد'].dropna().unique()
dates_csv = df_csv['date_de_naissance'].dropna().unique()

# --- حساب الأعداد ---
total_csv = len(dates_csv)
total_orig = len(dates_orig)

# عدد المشتركين
common_dates = set(dates_csv).intersection(set(dates_orig))
common_count = len(common_dates)

# --- عرض النتائج ---
print("📊 نتائج المقارنة:")
print(f"عدد التواريخ المختلفة في ملف CSV: {total_csv}")
print(f"عدد التواريخ المختلفة في ملف Excel: {total_orig}")
print(f"عدد التواريخ المشتركة بين الملفين: {common_count}")
print("\n✅ الأشخاص المشتركون (حسب تاريخ الميلاد):")
for d in sorted(common_dates):
    print(" -", d.strftime("%Y-%m-%d"))
