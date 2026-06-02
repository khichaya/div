# -*- coding: utf-8 -*-
import pandas as pd

# --- أسماء الملفات ---
file_clean = "clean.xlsx"       # الملف النقي (Nom, Prénom, Date de naissance)
file_full = "full.xlsx"         # الملف الكامل (تاريخ الميلاد، رقم التسجيل، الاسم، ...)
output_file = "merged_result23.xlsx"  # الناتج النهائي

# --- قراءة الملفات ---
df_clean = pd.read_excel(file_clean)
df_full = pd.read_excel(file_full)

# --- توحيد أسماء الأعمدة (لتفادي اختلافات في اللغة / الفراغات) ---
df_clean.columns = [c.strip().lower() for c in df_clean.columns]
df_full.columns = [c.strip().lower() for c in df_full.columns]

# --- تحويل التواريخ إلى صيغة موحدة ---
if 'date de naissance' in df_clean.columns:
    df_clean['date de naissance'] = pd.to_datetime(df_clean['date de naissance'], errors='coerce', dayfirst=True)

if 'تاريخ الميلاد' in df_full.columns:
    df_full['تاريخ الميلاد'] = pd.to_datetime(df_full['تاريخ الميلاد'], errors='coerce', dayfirst=True)

# --- الدمج حسب تاريخ الميلاد ---
df_merged = df_full.merge(
    df_clean,
    left_on='تاريخ الميلاد',
    right_on='date de naissance',
    how='inner'
)

# --- حفظ النتائج ---
df_merged.to_excel(output_file, index=False)

print(f"✅ تم إنشاء الملف '{output_file}' بعدد {len(df_merged)} صف مطابق حسب تاريخ الميلاد.")
