import os
import pandas as pd

# === 1️⃣ إعداد المسارات ===
folder_path = r"converted_jpg"   # ضع هنا مسار المجلد الذي فيه الصور
excel_file = r"filtered.xlsx"       # ضع هنا مسار ملف Excel

# === 2️⃣ قراءة ملف Excel ===
df = pd.read_excel(excel_file)

# التأكد من وجود العمود المطلوب
if "Code photo" not in df.columns:
    raise ValueError("❌ العمود 'Code photo' غير موجود في ملف Excel")

# === 3️⃣ استخراج القيم من العمود وحذف الصور ===
deleted_count = 0
not_found = []

for code in df["Code photo"].dropna().astype(str):
    # إذا كان الكود يحتوي على امتداد أو لا
    possible_names = [f"{code}.jpg", f"{code}.jpeg"]

    found = False
    for name in possible_names:
        file_path = os.path.join(folder_path, name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted: {name}")
            deleted_count += 1
            found = True
            break

    if not found:
        not_found.append(code)

# === 4️⃣ تقرير نهائي ===
print("\n=== SUMMARY ===")
print(f"✅ Deleted {deleted_count} file(s).")
if not_found:
    print(f"⚠️ Not found ({len(not_found)}): {', '.join(not_found[:10])}...")
else:
    print("🎯 All listed photos were found and deleted.")
