import re
import fitz  # pymupdf
import pandas as pd
from PIL import Image
import io
import os

# اختياري - فقط اذا استخدمت OCR
import pytesseract

# ====== إعدادات قابلة للتغيير ======
PDF_PATH = r"badges_UN3901.pdf"   # غيّر لمسار ملف الـ PDF عندك
OUTPUT_XLSX = "results.xlsx"
# نمط عام لأرقام التسجيل: هنا نأخذ أي سلسلة من الأرقام طولها بين 8 و 20 (عدّل حسب حاجتك)
REGEX_PATTERN = re.compile(r"\b\d{8,20}\b")

# إذا كنت على Windows و tesseract غير في PATH ضع المسار الكامل، مثال:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# وإلاّ احذف/عطِّل السطر أعلاه.
# ===================================

def extract_from_text_blocks(page):
    """
    يستعمل بلوكات النص مع إحداثياتها ليختار الرقم الأقرب للأسفل (biggest y1).
    يرجع None إن لم يجد.
    """
    blocks = page.get_text("blocks")  # كل بلوك: (x0, y0, x1, y1, "text", block_no)
    candidates = []
    for b in blocks:
        x0, y0, x1, y1, text, _ = b[:6]
        if not text:
            continue
        # نبحث عن أرقام تماثل النمط داخل نفس البلوك
        for m in REGEX_PATTERN.finditer(text):
            val = m.group(0)
            # نخزن القيمة مع إحداثي الأسفل للبلوك (y1)
            candidates.append((val, y1, text.strip()))
    if not candidates:
        return None
    # نختار المرشح ذو أكبر y1 (أي الأقرب لأسفل الصفحة)
    candidates.sort(key=lambda t: t[1], reverse=True)
    chosen = candidates[0]
    return {"reg": chosen[0], "y_bottom": chosen[1], "block_text": chosen[2]}

def ocr_page(page, zoom=2):
    """
    يعمل صورة من الصفحة ثم يطبق pytesseract للبحث عن أرقام.
    zoom: كثافة الصورة لزيادة دقة الـ OCR
    """
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    ocr_text = pytesseract.image_to_string(img, lang='eng+ara')  # أضف 'ara' لو نص عربي مفيد
    # نبحث بالأرقام
    m = REGEX_PATTERN.search(ocr_text)
    if m:
        return {"reg": m.group(0), "ocr_text_preview": ocr_text[:200]}
    return None

def main():
    # تأكد من وجود الملف
    if not os.path.exists(PDF_PATH):
        print("ملف PDF غير موجود:", PDF_PATH)
        return

    doc = fitz.open(PDF_PATH)
    results = []
    total_pages = doc.page_count
    print(f"فتح الملف، عدد الصفحات = {total_pages}")

    for page_index in range(total_pages):
        page = doc.load_page(page_index)
        page_no = page_index + 1

        # تجربة الاستخراج من النص (المطلوب عادة)
        res = extract_from_text_blocks(page)
        method = None
        if res:
            method = "text_blocks"
            reg = res["reg"]
        else:
            # محاولة OCR كبديل
            try:
                res_ocr = ocr_page(page, zoom=2)
            except Exception as e:
                res_ocr = None
                print(f"خطأ OCR في صفحة {page_no}: {e}")

            if res_ocr:
                method = "ocr"
                reg = res_ocr["reg"]
            else:
                method = "not_found"
                reg = None

        print(f"صفحة {page_no}: {reg}  ({method})")
        results.append({
            "page": page_no,
            "registration_number": reg,
            "method": method
        })

    # حفظ إلى اكسل
    df = pd.DataFrame(results)
    df.to_excel(OUTPUT_XLSX, index=False)
    print("تم الحفظ في:", OUTPUT_XLSX)

if __name__ == "__main__":
    main()
