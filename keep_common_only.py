# -*- coding: utf-8 -*-
import pandas as pd

# --- الملفات ---
excel_file = "or.xlsx"   # الملف الأصلي
csv_file = "result_all.csv"    # ملف الـ CSV
output_file = "filtered_only_common.xlsx"  # الناتج الجديد

# --- قراءة الملفين ---
# نحدد اسم الورقة الأولى والثانية إذا موجودة داخل نفس الملف
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names
print("📄 الأوراق الموجودة:", sheet_names)

# Sheet1 = الأصلية، Sheet2 = فيها csv (كما قلت)
df_orig = pd.read_excel(xls, sheet_name='Sheet1')
df_csv = pd.read_excel(xls, sheet_name='Sheet2')

# --- تنظيف الأعمدة ---
df_orig['تاريخ الميلاد'] = pd.to_datetime(df_orig['تاريخ الميلاد'], errors='coerce', dayfirst=True)
df_csv['date_de_naissance'] = pd.to_datetime(df_csv['date_de_naissance'], errors='coerce', dayfirst=True)

# --- استخراج التواريخ المشتركة ---
dates_csv = set(df_csv['date_de_naissance'].dropna().unique())

# --- الاحتفاظ فقط بالمشتركين ---
df_filtered = df_orig[df_orig['تاريخ الميلاد'].isin(dates_csv)].copy()

# --- حفظ الملف الناتج ---
df_filtered.to_excel(output_file, index=False)

print(f"✅ تم حفظ الملف '{output_file}' بعدد {len(df_filtered)} صف (الأشخاص المشتركين فقط).")
