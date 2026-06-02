# -*- coding: utf-8 -*-
import pandas as pd

# --- أسماء الملفات ---
file1 = "or1.xlsx"   # الملف الكبير (701 سطر)
file2 = "file02.xlsx"   # الملف الصغير (399 سطر)
output_file = "only_in_file1.xlsx"  # الناتج النهائي

# --- قراءة الملفين ---
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# --- تنظيف أسماء الأعمدة (إزالة الفراغات) ---
df1.columns = [c.strip() for c in df1.columns]
df2.columns = [c.strip() for c in df2.columns]

# --- تحديد الأعمدة المرجعية ---
key1 = "سنة  البكالوريا"
key2 = "رقم  التسجيل"

# --- التأكد من وجود الأعمدة ---
if key1 not in df1.columns or key2 not in df1.columns:
    raise ValueError(f"❌ الأعمدة '{key1}' و'{key2}' غير موجودة في الملف الأول")
if key1 not in df2.columns or key2 not in df2.columns:
    raise ValueError(f"❌ الأعمدة '{key1}' و'{key2}' غير موجودة في الملف الثاني")

# --- إنشاء مفتاح مشترك لكل صف (مزيج من العمودين) ---
df1["key"] = df1[key1].astype(str).str.strip() + "_" + df1[key2].astype(str).str.strip()
df2["key"] = df2[key1].astype(str).str.strip() + "_" + df2[key2].astype(str).str.strip()

# --- تحديد الصفوف غير الموجودة في الملف الثاني ---
df_diff = df1[~df1["key"].isin(df2["key"])].copy()

# --- حذف العمود المساعد ---
df_diff.drop(columns=["key"], inplace=True)

# --- حفظ النتيجة ---
df_diff.to_excel(output_file, index=False)

print(f"✅ تم إنشاء الملف '{output_file}' بعدد {len(df_diff)} سطر غير موجود في الملف الثاني.")
