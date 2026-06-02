# -*- coding: utf-8 -*-
import re
from pdf2image import convert_from_path
import pytesseract
import pandas as pd

# --- الإعدادات ---
PDF_FILE = "liste.pdf"          # اسم ملف الـ PDF
OUTPUT_XLSX = "resultats.xlsx"  # ملف الإخراج Excel
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- تعريف الـ Regex ---
re_nom = re.compile(r"Nom\s*[:\-]?\s*([A-ZÀ-ÖØ-öø-ÿ'\- ]+)", re.IGNORECASE)
re_prenom = re.compile(r"Pr[eé]nom\s*[:\-]?\s*([A-ZÀ-ÖØ-öø-ÿ'\- ]+)", re.IGNORECASE)
re_date = re.compile(r"(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})")

# --- تحويل PDF إلى نص ---
def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=250)
    text_total = ""
    for i, page in enumerate(pages, start=1):
        print(f"🔍 Lecture OCR page {i}/{len(pages)} ...")
        text = pytesseract.image_to_string(page, lang="fra+eng+ara", config="--psm 6")
        text_total += text + "\n"
    return text_total

# --- استخراج المعلومات ---
def extract_info(text):
    pattern = re.compile(r"([A-ZÀ-ÖØ-öø-ÿ'\- ]+)\s+([A-ZÀ-ÖØ-öø-ÿ'\- ]+)\s+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})")
    matches = pattern.findall(text)
    results = []
    for match in matches:
        nom = match[0].strip().title()
        prenom = match[1].strip().title()
        date_naissance = match[2].replace('.', '-').replace('/', '-')
        results.append((nom, prenom, date_naissance))
    return results

# --- التنفيذ ---
print("📄 Lecture du fichier PDF ...")
text = extract_text_from_pdf(PDF_FILE)
data = extract_info(text)

# --- حفظ النتائج في Excel ---
df = pd.DataFrame(data, columns=["Nom", "Prénom", "Date de naissance"])
df.to_excel(OUTPUT_XLSX, index=False)

print(f"✅ تم استخراج {len(df)} شخص وحفظهم في '{OUTPUT_XLSX}'.")
