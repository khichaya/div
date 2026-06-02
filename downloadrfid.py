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

EXCEL_PATH = r"D:\project\00.xlsx"
OUTPUT_EXCEL = r"D:\project\00_with_rfid.xlsx"
LOGIN_URL = "https://accounts.mesrs.dz/login"
TARGET_URL = "https://webonou.mesrs.dz/pages/onou/DossierInscriptionAdministrativeHebC"
# ==========================================

# إعداد المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 25)

# تحميل البيانات
df = pd.read_excel(EXCEL_PATH)
if "RFID Code" not in df.columns:
    df["RFID Code"] = ""   # إنشاء العمود إذا غير موجود

print(f"🔢 Found {len(df)} records to process")

# تسجيل الدخول
driver.get(LOGIN_URL)
wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "password").submit()
wait.until(EC.url_contains("accounts.mesrs.dz"))

# فتح صفحة Hébergement مباشرة
driver.get(TARGET_URL)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
print("✅ Logged in and opened Hébergement page directly")

# دالة انتظار بشرية بسيطة
def human_wait(a=2, b=5):
    time.sleep(random.uniform(a, b))

# الحلقة الرئيسية
for i in range(len(df)):
    raw_code = str(df.at[i, "Matricule de Bac"]).strip()
    if raw_code.endswith(".0"):
        code = raw_code[:-2]
    else:
        code = raw_code

    if not code or code.lower() == "nan":
        continue

    # إذا هذا الصف تمت معالجته مسبقًا نتخطاه
    if df.at[i, "RFID Code"] not in ("", "N/A", "ERROR"):
        continue

    print(f"\n[{i+1}/{len(df)}] 🔍 Searching for: {code}")

    try:
        # البحث في المربع
        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.live='search']"))
        )
        search_box.clear()
        search_box.send_keys(code)
        time.sleep(1.5)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2.5)

        # انتظار ظهور الصف
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr[id^='table-row-']")
        if not rows:
            print(f"⚠️ No result for {code}, skipping...")
            df.at[i, "RFID Code"] = "N/A"
            continue

        row_el = rows[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_el)
        time.sleep(0.5)
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", row_el
        )
        print("🖱️ Clicked on the first result successfully")

        # انتظار تفاصيل الطالب
        wait.until(EC.presence_of_element_located((By.ID, "details")))
        time.sleep(1.5)

        # استخراج كود RFID
        try:
            rfid_el = driver.find_element(
                By.XPATH,
                "//th[contains(normalize-space(text()), 'RFID Number')]/following-sibling::td"
            )
            rfid_code = rfid_el.text.strip()
            if not rfid_code:
                rfid_code = "N/A"
        except Exception:
            rfid_code = "N/A"

        print(f"✅ RFID for {code}: {rfid_code}")
        df.at[i, "RFID Code"] = rfid_code

        # 🔹 نحفظ مباشرة بعد كل عملية
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"💾 Saved progress ({i+1}/{len(df)})")

        human_wait(3, 6)

    except Exception as e:
        print(f"❌ Error for {code}: {e}")
        df.at[i, "RFID Code"] = "ERROR"
        df.to_excel(OUTPUT_EXCEL, index=False)
        driver.refresh()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
        continue

# حفظ نهائي بعد الانتهاء
df.to_excel(OUTPUT_EXCEL, index=False)
print(f"\n🎯 Done! File saved successfully at:\n{OUTPUT_EXCEL}")
driver.quit()
