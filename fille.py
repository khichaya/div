import pandas as pd

# ملفاتك
file1 = r"D:\project\students_main.xlsx"      # الملف الرئيسي
file2 = r"D:\project\social_status.xlsx"      # ملف الضمان الاجتماعي
output = r"D:\project\students_final.xlsx"

# دالة توحيد التاريخ
def normalize_date(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    # إزالة الوقت الزائد مثل 00:00:00
    val = val.split()[0]
    # استبدال كل الفواصل بنقطة أو شرطة موحدة
    val = val.replace("/", "-").replace(".", "-")
    try:
        try:
            d = pd.to_datetime(val, errors="coerce", format="%Y-%m-%d")
        except:
            d = pd.to_datetime(val, errors="coerce", dayfirst=True)

        if pd.isna(d):
            return None
        return d.strftime("%Y-%m-%d")
    except Exception:
        return None

# قراءة الملفين
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# توحيد التاريخ
df1["date_norm"] = df1["تاريخ الميلاد"].apply(normalize_date)
df2["date_norm"] = df2["D_NAISS"].apply(normalize_date)

# معالجة الملف الثاني واختيار حالة واحدة لكل تاريخ
priority = {"Affilié": 3, "Doit Justifier sa situation": 2, "Non Affilié": 1, "منتمى": 3, "مسجل غير منتمي": 1}
df2["prio"] = df2["Lib_Rech"].map(priority).fillna(0)
df2_best = df2.sort_values(["date_norm", "prio"], ascending=[True, False]).drop_duplicates("date_norm")

# الدمج
merged = pd.merge(df1, df2_best[["date_norm", "Lib_Rech"]], on="date_norm", how="left")
merged.rename(columns={"Lib_Rech": "حالة الضمان الاجتماعي"}, inplace=True)
merged.drop(columns=["date_norm"], inplace=True)

# حفظ الملف
merged.to_excel(output, index=False)
print(f"✅ تم الدمج الكامل وحُفظ في:\n{output}")
