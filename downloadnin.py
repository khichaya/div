import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= CONFIG =================
EMAIL = "k.yahai"
PASSWORD = "Ghghjk.1611"

EXCEL_PATH = r"D:\project\000.xlsx"           # الملف الأصلي
OUTPUT_EXCEL = r"D:\project\000_with_nin.xlsx" # الملف الناتج
LOGIN_URL = "https://accounts.mesrs.dz/login"
TARGET_URL = "https://webonou.mesrs.dz/pages/onou/DossierInscriptionAdministrativeDemanderHebDou"
# ==========================================

# إعداد المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 25)

# تحميل البيانات
df = pd.read_excel(EXCEL_PATH)
if "NIN" not in df.columns:
    df["NIN"] = ""   # إنشاء العمود إذا غير موجود

print(f"🔢 Found {len(df)} records to process")

# تسجيل الدخول
driver.get(LOGIN_URL)
wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "password").submit()
wait.until(EC.url_contains("accounts.mesrs.dz"))

# فتح صفحة Dou
driver.get(TARGET_URL)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.defer='annee_bac']")))
print("✅ Logged in and opened Dou page directly")

# دالة انتظار بشرية بسيطة
def human_wait(a=2, b=5):
    time.sleep(random.uniform(a, b))

# الحلقة الرئيسية
for i in range(len(df)):
    year = str(df.at[i, "سنة  البكالوريا"]).strip()
    matricule = str(df.at[i, "رقم  التسجيل"]).strip()

    if not year or not matricule or year.lower() == "nan" or matricule.lower() == "nan":
        continue

    # إذا تمت معالجته مسبقًا
    if df.at[i, "NIN"] not in ("", "N/A", "ERROR"):
        continue

    print(f"\n[{i+1}/{len(df)}] 🔍 Searching for: {year}-{matricule}")

    try:
        # تعبئة سنة البكالوريا
        year_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.defer='annee_bac']"))
        )
        year_box.clear()
        year_box.send_keys(year)

        # تعبئة رقم التسجيل
        matricule_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.defer='matricule_bac']"))
        )
        matricule_box.clear()
        matricule_box.send_keys(matricule)

        # الضغط على زر البحث
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[wire\\:click='searchByYearMatricule']")
        driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(3)

        # استخراج رقم التعريف الوطني الصحيح فقط
        nin = "N/A"
        td_elements = driver.find_elements(By.CSS_SELECTOR, "td.py-1.px-6")
        for td in td_elements:
            text = td.text.strip()
            if text.isdigit() and 15 <= len(text) <= 20:
                nin = text
                break

        print(f"✅ NIN for {year}-{matricule}: {nin}")
        df.at[i, "NIN"] = nin

        # حفظ بعد كل عملية
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"💾 Saved progress ({i+1}/{len(df)})")

        human_wait(2, 4)

    except Exception as e:
        print(f"❌ Error for {year}-{matricule}: {e}")
        df.at[i, "NIN"] = "ERROR"
        df.to_excel(OUTPUT_EXCEL, index=False)
        driver.refresh()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[wire\\:model\\.defer='annee_bac']")))
        continue

# حفظ نهائي بعد الانتهاء
df.to_excel(OUTPUT_EXCEL, index=False)
print(f"\n🎯 Done! File saved successfully at:\n{OUTPUT_EXCEL}")
driver.quit()
