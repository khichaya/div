import threading
import time, os, re, requests, pandas as pd, pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================
# ⚙️ إعدادات عامة
# ========================
EMAIL = "f.ben bourdi"
PASSWORD = "cxaPyKBj"
EXCEL_FILE = "rumoussaoi.xlsx"
LOGIN_URL = "https://accounts.mesrs.dz/login"
DASHBOARD_URL = "https://webonou.mesrs.dz/dashboard"
BASE_URL = "https://webonou.mesrs.dz/pages/onou/DossierInscriptionAdministrativeHebC?table-search="

output_folder = "downloaded_images"
os.makedirs(output_folder, exist_ok=True)

# ========================
# 🧹 دوال مساعدة
# ========================
def clean_filename(name):
    return re.sub(r'\s+', '_', re.sub(r'[\\/*?:"<>|]', '', str(name).strip()))

def download_image(session, src, filename):
    """تحميل الصورة من الرابط وحفظها"""
    try:
        r = session.get(src, timeout=20)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"✅ {os.path.basename(filename)}")
    except Exception as e:
        print(f"⚠️ تحميل فشل {filename}: {e}")

# ========================
# 🖱️ كود الضغط الآلي (يعمل في خيط منفصل)
# ========================
def auto_clicker(interval=6):
    """ينقر بالزر الأيسر كل interval ثانية"""
    pyautogui.FAILSAFE = True
    print(f"🖱️ Auto Clicker بدأ العمل (كل {interval} ثواني). حرك الماوس إلى زاوية الشاشة لإيقافه.")
    try:
        while True:
            pyautogui.click(button='left')
            print(f"🖱️ نقرة أوتوماتيكية...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("⛔ تم إيقاف Auto Clicker يدوياً.")
    except pyautogui.FailSafeException:
        print("⛔ تم إيقاف Auto Clicker (ميزة Failsafe).")

# تشغيل النقر التلقائي في خيط مستقل
click_thread = threading.Thread(target=auto_clicker, args=(10,), daemon=True)
click_thread.start()

# ========================
# 🚀 تسجيل الدخول وبدء تحميل الصور
# ========================
opt = webdriver.ChromeOptions()
opt.add_argument("--no-sandbox")
opt.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=opt)
wait = WebDriverWait(driver, 25)

try:
    # تسجيل الدخول
    driver.get(LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password").submit()
    wait.until(EC.url_contains("accounts.mesrs.dz"))
    driver.get(DASHBOARD_URL)
    print("✅ تسجيل الدخول تم")

    # إعداد جلسة Requests
    session = requests.Session()
    for c in driver.get_cookies():
        session.cookies.set(c["name"], c["value"], domain=c["domain"])

    df = pd.read_excel(EXCEL_FILE)
    print(f"📘 عدد الطلاب: {len(df)}")

    for i, row in df.iterrows():
        matricule = str(row["Matricule de Bac"]).strip()
        code_photo = clean_filename(row["Code photo"])
        print(f"\n({i+1}/{len(df)}) 🔍 {matricule}")

        driver.get(f"{BASE_URL}{matricule}")

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
            time.sleep(1)

            # العثور على الصف القابل للنقر
            row_el = driver.find_element(By.CSS_SELECTOR, "table tbody tr")

            # تنفيذ نقرة JS مؤكدة
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)
            driver.execute_script("arguments[0].click();", row_el)
            print("🖱️ تم الضغط على الصف")

            # الانتظار لظهور الصورة (حتى 10 ثواني)
            img_src = None
            for sec in range(10):
                try:
                    img_el = driver.find_element(By.CSS_SELECTOR, "div.md\\:w-1\\/6 img")
                    src = img_el.get_attribute("src")
                    if src and "photos" in src:
                        img_src = src
                        break
                except Exception:
                    pass
                time.sleep(1)

            if not img_src:
                print("⚠️ لم تظهر الصورة بعد، تجاوز الطالب.")
                continue

            path = os.path.join(output_folder, f"{code_photo}.jpg")
            download_image(session, img_src, path)

        except Exception as e:
            print(f"❌ خطأ عند {matricule}: {e}")
            continue

    print("\n🎯 اكتمل التحميل بنجاح")

finally:
    driver.quit()
