import os
import time
import random
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= CONFIG =================
EMAIL = "m.lammamra"
PASSWORD = "radEUtSh"

EXCEL_PATH = r"D:\project\saoudibachir1.xlsx"
OUTPUT_DIR = r"D:\project\downloaded_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🚨 اسم العمود الذي تريد استخدامه لتسمية الصورة
PHOTO_CODE_COLUMN = "Code photo"
# ==========================================

LOGIN_URL = "https://accounts.mesrs.dz/login"
DASHBOARD_URL = "https://webonou.mesrs.dz/dashboard"

# Chrome setup
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 25)

# ---------------- تحميل الأكواد من Excel ----------------
df = pd.read_excel(EXCEL_PATH)

# قراءة عمودي البحث (Matricule de Bac) والتسمية (Code photo)
data_rows = df[["Matricule de Bac", PHOTO_CODE_COLUMN]].dropna().to_dict('records')

print(f"🔢 Found {len(data_rows)} records with registration and photo codes")

# ---------------- تسجيل الدخول ----------------
driver.get(LOGIN_URL)
wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "password").submit()
wait.until(EC.url_contains("accounts.mesrs.dz"))
driver.get(DASHBOARD_URL)
print("✅ Logged in successfully")

# ---------------- الذهاب إلى صفحة Hébergement ----------------
heberg = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Hébergement')]")))
heberg.click()
time.sleep(1)

demandes = wait.until(EC.element_to_be_clickable(
 (By.XPATH, "//a[contains(@href,'/pages/onou/DossierInscriptionAdministrativeHebC')]")
))
driver.execute_script("arguments[0].click();", demandes)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
print("✅ Accommodation page ready")

# ---------------- إعداد جلسة Requests بنفس الكوكيز ----------------
session = requests.Session()
for c in driver.get_cookies():
 session.cookies.set(c['name'], c['value'], domain=c.get('domain'))

# ---------------- وظائف مساعدة ----------------
def human_wait(a=2, b=5):
 """انتظار عشوائي طبيعي"""
 time.sleep(random.uniform(a, b))

def wait_for_loading_to_finish():
 """ينتظر حتى تختفي عبارة loading بعد الضغط على الصف"""
 try:
  print("⌛ Waiting for details to load...")
  WebDriverWait(driver, 8).until(
   EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'loading') or contains(text(),'Loading')]"))
  )
  WebDriverWait(driver, 20).until_not(
   EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'loading') or contains(text(),'Loading')]"))
  )
  print("✅ Details loaded.")
 except:
  print("⚠️ No explicit loading detected — maybe loaded instantly.")

# ---------------- الحلقة الرئيسية ----------------
downloaded_codes = {os.path.splitext(f)[0] for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".jpg")}
log_path = os.path.join(OUTPUT_DIR, "download_log.txt")

for i, row_data in enumerate(data_rows, start=1):
 # كود البحث (Matricule de Bac)
 code = str(row_data["Matricule de Bac"])
 # كود التسمية (Code photo)
 photo_code = str(row_data[PHOTO_CODE_COLUMN])

 if photo_code in downloaded_codes:
  print(f"⏭️ Already downloaded: {photo_code}")
  continue

 print(f"\n[{i}/{len(data_rows)}] 🔍 Searching for {code} (Photo Name: {photo_code})...")

 try:
  # 1️⃣ إدخال الرقم في مربع البحث
  search_box = wait.until(EC.presence_of_element_located(
   (By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
  search_box.clear()
  search_box.send_keys(code)
  time.sleep(1.5)
  search_box.send_keys(Keys.ENTER)
  time.sleep(2.5)

  # 2️⃣ انتظار الصف في الجدول (تعديل: ننتظر أن يكون الصف قابلاً للنقر)
  try:
   row = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "table tbody tr"))
   )
  except:
   print(f"⚠️ No row found for {code} after search. Refreshing page...")
   # تحديث الصفحة للمحاولة مجدداً
   driver.refresh()
   wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
   continue

  # 3️⃣ الضغط على الصف والانتظار حتى تظهر التفاصيل
  # التأكد من رؤية الصف قبل النقر (Scroll into view)
  driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
  row.click()
  print("🖱️ Successfully clicked on the row.")
  wait_for_loading_to_finish()

  # ⏳ 4️⃣ فاصل إضافي (5 ثوانٍ) للسماح بعرض الصورة
  print("🕒 Waiting 5 seconds for the image to display...")
  time.sleep(5) 

  # 5️⃣ انتظار الصورة الجديدة 
  try:
   img_el = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.md\\:w-1\\/6 img"))
   )
   img_src = img_el.get_attribute("src")
  except:
   print(f"⚠️ No image appeared for {code}.")
   continue

  if not img_src or "photos" not in img_src:
   print("⚠️ Invalid image URL, skipping.")
   continue

  # 6️⃣ تحميل الصورة
  print("📥 Downloading image...")
  r = session.get(img_src, timeout=15)
  img_data = r.content

  # تحقق من صلاحية الصورة
  if len(img_data) < 10000:
   print(f"⚠️ Image too small ({len(img_data)} bytes) — skipping.")
   continue

  try:
   img = Image.open(BytesIO(img_data))
   w, h = img.size
   if w < 100 or h < 100:
    print(f"⚠️ Image dimensions too small ({w}x{h}) — skipping.")
    continue
  except Exception as e:
   print(f"⚠️ Error opening image: {e}")
   continue

  # 7️⃣ حفظ الصورة باستخدام Photo Code
  filename = os.path.join(OUTPUT_DIR, f"{photo_code}.jpg")
  with open(filename, "wb") as f:
   f.write(img_data)
  print(f"✅ Saved image: {filename} ({w}x{h})")

  # نستخدم كود التسمية (photo_code) في السجل أيضاً
  with open(log_path, "a", encoding="utf-8") as log:
   log.write(f"{photo_code}\tOK\t{w}x{h}\n")

  # 🕒 8️⃣ فاصل إضافي بعد كل عملية (للسماح بالتبديل بين الصور)
  delay = random.uniform(5, 9)
  print(f"🕒 Waiting {delay:.1f}s before next code...")
  time.sleep(delay)

 except Exception as e:
  print(f"❌ Error for {code}: {e}")
  # نستخدم كود التسمية (photo_code) في السجل أيضاً
  with open(log_path, "a", encoding="utf-8") as log:
   log.write(f"{photo_code}\tERROR\t{e}\n")
  # إعادة تحميل الصفحة في حالة حدوث خطأ كبير لمنع التعطل التام
  driver.refresh()
  wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[wire\\:model\\.live='search']")))
  continue

print("\n🎯 Done! All valid photos downloaded successfully.")
driver.quit()
