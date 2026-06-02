import pandas as pd
import subprocess
import time

file_path = "listofaccepted.xlsx"
df = pd.read_excel(file_path)

if "Status" not in df.columns:
    df["Status"] = ""

package = "khicha.dr.smsapp/.MainActivity"
package_name = "khicha.dr.smsapp"

for i, row in df.iterrows():
    phone = str(row.get("رقم الهاتف", "")).strip()
    name = str(row.get("الإسم", "")).strip()
    lastname = str(row.get("اللقب", "")).strip()
    status = str(row.get("Status", "")).strip()

    if not phone:
        continue

    if not phone.startswith("0") and not phone.startswith("+213"):
        phone = "0" + phone
    phone = phone.replace(" ", "").replace("-", "")

    if status != "Sent":
        # ✅ الرسالة في سطر واحد لتجنب الخطأ
        msg_template = (
            f"لقد تم قبول طلبكم للحصول على الايواء 🏡. "
            f"الاسم: {name} {lastname}. "
            "الرجاء تسديد الحقوق قبل غلق الموقع: "
            "https://progres.mesrs.dz/epaiement/epaiementH.xhtml . "
            "ثم التوجه إلى الإقامة لاستلام المفتاح. Dou El Oued."
        )

        # ✅ نستخدم اقتباسات آمنة
        command = f'adb shell am start -n "{package}" --es phone "{phone}" --es message "{msg_template}"'

        print(f"🚀 Sending SMS to {name} {lastname} ({phone})...")
        process = subprocess.Popen(
            ["cmd.exe", "/C", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        time.sleep(3)

        subprocess.run(["adb", "shell", "am", "force-stop", package_name], shell=True)
        print("✅ Message sent and app closed.\n")

        # ✅ نحول العمود إلى نص لتفادي تحذير dtype
        df["Status"] = df["Status"].astype(str)
        df.at[i, "Status"] = "Sent"
        df.to_excel(file_path, index=False)

print("✅ جميع الرسائل أُرسلت بنجاح!")
