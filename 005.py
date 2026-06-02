# -*- coding: utf-8 -*-
import pandas as pd

# --- الملفات ---
fichier_original = "or1.xlsx"
fichier_csv = "result_all.csv"
fichier_csv_converti = "result_all_converted.csv"

# --- قراءة الملفين ---
df_orig = pd.read_excel(fichier_original)
df_csv = pd.read_csv(fichier_csv)

# استخراج مثال من التاريخ الأصلي لمعرفة التنسيق
sample_date = str(df_orig['تاريخ الميلاد'].dropna().iloc[0])
print(f"📘 نموذج من تاريخ الميلاد في Excel: {sample_date}")

# تحويل عمود التاريخ في CSV إلى datetime ثم إعادة تنسيقه
df_csv['date_de_naissance'] = pd.to_datetime(
    df_csv['date_de_naissance'], errors='coerce', dayfirst=True
)

# تحويل الصيغة لتكون مثل Excel (YYYY-MM-DD)
df_csv['date_de_naissance'] = df_csv['date_de_naissance'].dt.strftime("%Y-%m-%d")

# حفظ الملف الجديد
df_csv.to_csv(fichier_csv_converti, index=False, encoding='utf-8-sig')

print(f"✅ تم تحويل التواريخ وحفظها في '{fichier_csv_converti}'")
