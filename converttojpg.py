import os
from PIL import Image

# مسار المجلد الذي يحتوي الصور
input_folder = r"RUMOUSSAOI"   # غيّر هذا إلى مسار مجلدك

# إنشاء مجلد للإخراج (اختياري)
output_folder = os.path.join(input_folder, "convertedRUMOUSSAOI_jpg")
os.makedirs(output_folder, exist_ok=True)

# المرور على كل الملفات في المجلد
for filename in os.listdir(input_folder):
    # التأكد أن الملف صورة
    if filename.lower().endswith(('.jpeg', '.jpg')):
        file_path = os.path.join(input_folder, filename)

        # فتح الصورة
        try:
            with Image.open(file_path) as img:
                # تحويلها إلى RGB (لتجنب مشاكل بعض الصيغ)
                rgb_img = img.convert("RGB")

                # استخراج اسم الملف بدون الامتداد
                base_name = os.path.splitext(filename)[0]

                # حفظها بصيغة JPG في مجلد الإخراج
                output_path = os.path.join(output_folder, f"{base_name}.jpg")
                rgb_img.save(output_path, "JPEG")

                print(f"✅ تم تحويل: {filename} → {base_name}.jpg")

        except Exception as e:
            print(f"❌ فشل تحويل {filename}: {e}")

print("\n🎯 تم تحويل جميع الصور بنجاح!")
