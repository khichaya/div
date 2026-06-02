# -*- coding: utf-8 -*-
import pandas as pd

# --- الملفات ---
fichier_original = "or.xlsx"       # الملف الأصلي
fichier_ocr = "result_all.csv"           # نتائج OCR من PDF
fichier_resultat = "filtered.xlsx"       # الملف الناتج النهائي

# --- قراءة الملفات ---
df_orig = pd.read_excel(fichier_original)
df_ocr = pd.read_csv(fichier_ocr)

# توحيد أسماء الأعمدة لتجنب الفراغات
df_orig.columns = [c.strip().lower() for c in df_orig.columns]
df_ocr.columns = [c.strip().lower() for c in df_ocr.columns]

# تنظيف القيم النصية لتوحد التنسيق
if 'تاريخ الميلاد' in df_orig.columns:
    df_orig['تاريخ الميلاد'] = df_orig['تاريخ الميلاد'].astype(str).str.strip().str.replace('/', '-')
if 'date_de_naissance' in df_ocr.columns:
    df_ocr['date_de_naissance'] = df_ocr['date_de_naissance'].astype(str).str.strip().str.replace('/', '-')

# --- الدمج حسب تاريخ الميلاد ---
df_merged = df_orig.merge(
    df_ocr,
    left_on='تاريخ الميلاد',
    right_on='date_de_naissance',
    how='inner'
)

# --- حفظ الملف الناتج ---
df_merged.to_excel(fichier_resultat, index=False)

print(f"✅ تم إنشاء الملف '{fichier_resultat}' بعدد {len(df_merged)} صف مطابق حسب تاريخ الميلاد فقط.")
