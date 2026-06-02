import pandas as pd

# تحميل الملفات
results = pd.read_excel("results.xlsx")        # يحتوي: page, registration_number
students = pd.read_excel("saoudibachir.xlsx")  # يحتوي: full_name, em_code, photo

# نتأكد أن الأعمدة نصوص (لتفادي مشاكل الصفر البادئ)
results["registration_number"] = results["registration_number"].astype(str)
students["em_code"] = students["em_code"].astype(str)

# استخراج آخر 8 أرقام من رقم التسجيل
results["last8"] = results["registration_number"].str[-8:]

# الدمج بين الملفين على أساس آخر 8 أرقام ↔ em_code
merged = pd.merge(
    students,
    results[["last8", "page"]],
    left_on="em_code",
    right_on="last8",
    how="inner"   # فقط المتواجدين في كلا الملفين
)

# حذف عمود last8 (غير ضروري)
merged.drop(columns=["last8"], inplace=True)

# حفظ النتيجة في ملف جديد
merged.to_excel("merged_results.xlsx", index=False)

print("✅ تم إنشاء الملف merged_results.xlsx ويحتوي فقط الطلبة الموجودين في كلا الملفين مع رقم الصفحة.")
