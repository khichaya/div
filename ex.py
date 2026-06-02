import fitz  # PyMuPDF
from PIL import Image
import pandas as pd
import os

# 📂 مسارات الملفات
pdf_path = r"d:\project\badges_UN3901-1.pdf"
output_folder = r"d:\project\student_photos"
excel_path = r"d:\project\merged_results.xlsx"
output_excel = r"d:\project\merged_with_photos.xlsx"

os.makedirs(output_folder, exist_ok=True)

# 📄 قراءة ملف Excel
df = pd.read_excel(excel_path)

# نتأكد أن فيه أعمدة page و em_code
if not {"page", "em_code"}.issubset(df.columns):
    raise ValueError("⚠️ ملف merged_results.xlsx يجب أن يحتوي أعمدة: page و em_code")

# افتح PDF
doc = fitz.open(pdf_path)

# قائمة لحفظ المسارات
photo_paths = []

for idx, row in df.iterrows():
    page_num = int(row["page"]) - 1  # صفحات PDF تبدأ من 0
    em_code = str(row["em_code"])

    if page_num < 0 or page_num >= len(doc):
        print(f"⚠️ الصفحة {page_num+1} غير موجودة في PDF")
        photo_paths.append(None)
        continue

    page = doc[page_num]
    face_saved = False
    photo_path = os.path.join(output_folder, f"{em_code}.jpg")

    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        # فلترة: فقط صور الوجه (Portrait وكبيرة)
        if pix.width > 150 and pix.height > 200 and pix.height > pix.width:
            try:
                # احفظ مباشرة JPG
                temp_path = photo_path.replace(".jpg", "_temp.png")
                pix.save(temp_path)

                img_pil = Image.open(temp_path).convert("RGB")
                img_pil.save(photo_path, "JPEG")
                os.remove(temp_path)

                print(f"[OK] Saved {photo_path}")
                face_saved = True
                break  # نحفظ صورة واحدة فقط (أول وجه)

            except Exception as e:
                print(f"⚠️ خطأ مع {em_code}: {e}")
                img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_pil.save(photo_path, "JPEG")
                face_saved = True
                break

        pix = None

    if face_saved:
        photo_paths.append(photo_path)
    else:
        photo_paths.append(None)

# ➕ نضيف العمود photo للإكسل
df["photo"] = photo_paths

# 💾 نحفظ ملف جديد
df.to_excel(output_excel, index=False)

print("✅ تم استخراج الصور وحفظها بأسماء em_code وتحديث ملف إكسل بالمسارات!")
