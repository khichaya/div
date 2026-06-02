import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# بيانات الدخول
EMAIL = "k.yahai"
PASSWORD = "Ghghjk.1611"

# رابط البداية
BASE_URL = "https://webonou.mesrs.dz/pages/onou/OnouCmLieusGerer?table-filters[residence]=5186280&table-filters[status]=699013&page="

# ملف الخرج
OUTPUT_FILE = r"D:\project\onou_all_pages.xlsx"

# إعداد المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 25)

# تسجيل الدخول مرة واحدة
driver.get("https://accounts.mesrs.dz/login")
wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "password").submit()
wait.until(EC.url_contains("accounts.mesrs.dz"))
print("✅ تم تسجيل الدخول بنجاح")

all_data = []
headers = []
total_rows = 0

# المرور على الصفحات من 1 إلى 50
for page in range(1, 103):
    url = BASE_URL + str(page)
    print(f"\n📄 تحميل الصفحة رقم {page} ...")
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "table-tbody")))
        time.sleep(2)

        # استخراج رؤوس الأعمدة مرة واحدة فقط من الصفحة الأولى
        if not headers:
            headers = [th.text.strip() for th in driver.find_elements(By.CSS_SELECTOR, "table thead th") if th.text.strip()]
            print("📋 الأعمدة:", headers)

        # استخراج الصفوف
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for r in rows:
            cols = [td.text.strip() for td in r.find_elements(By.TAG_NAME, "td")]
            if cols:
                all_data.append(cols)
        total_rows += len(rows)
        print(f"✅ تم استخراج {len(rows)} صفًا من الصفحة {page}")

    except Exception as e:
        print(f"⚠️ فشل تحميل الصفحة {page}: {e}")
        continue

# حفظ إلى Excel
df = pd.DataFrame(all_data, columns=headers)
df.to_excel(OUTPUT_FILE, index=False)

print(f"\n🎯 تم استخراج {total_rows} صفًا من 50 صفحة.")
print(f"💾 تم حفظ الملف في: {OUTPUT_FILE}")

driver.quit()
