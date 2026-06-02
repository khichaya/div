#!/usr/bin/env python3
"""
clicker.py
نقرة تلقائية بالفأرة (يسار) كل فترة زمنية.
استخدام:
  python clicker.py                # ينقر في موقع الماوس الحالي كل 10 ثواني إلى أن تضغط Ctrl+C
  python clicker.py --interval 5   # ينقر كل 5 ثواني
  python clicker.py --x 800 --y 400 --count 10  # ينقر 10 مرات عند (800,400)
"""

import time
import argparse
import pyautogui
import sys

# ميزة أمان: حرك الماوس إلى الزاوية العلوية اليسرى لإيقاف البرنامج فورًا
pyautogui.FAILSAFE = True

def parse_args():
    p = argparse.ArgumentParser(description="Auto mouse clicker (left) every N seconds.")
    p.add_argument("--interval", "-i", type=float, default=10.0,
                   help="الفاصل الزمني بين النقرات بالثواني (الافتراضي 10s)")
    p.add_argument("--x", type=int, default=None, help="إحداثي X للنقرة (إذا لم يعطَ يستخدم موقع الماوس الحالي)")
    p.add_argument("--y", type=int, default=None, help="إحداثي Y للنقرة (إذا لم يعطَ يستخدم موقع الماوس الحالي)")
    p.add_argument("--count", "-c", type=int, default=0,
                   help="عدد النقرات المراد تنفيذها. 0 يعني إلى ما لا نهاية (افتراضي)")
    p.add_argument("--delay", "-d", type=float, default=5.0,
                   help="مهلة قبل البدء بالسكلربت لإعطائك وقت وضع الماوس (بالثواني).")
    return p.parse_args()

def main():
    args = parse_args()
    interval = args.interval
    count = args.count
    x = args.x
    y = args.y
    delay = args.delay

    print("Auto clicker — يبدأ بعد مهلة بسيطة.")
    print(f"الفاصل: {interval}s | إحداثيات ثابتة: {('غير مستخدمة' if x is None else f'({x},{y})')} | عدد النقرات: {('غير محدود' if count==0 else count)}")
    print(f"حرك المؤشر إلى الزاوية العليا اليسرى لإيقاف Failsafe أو اضغط Ctrl+C.")

    try:
        # وقت تحضيري لتضع الماوس أو تجهز الشاشات
        for t in range(int(delay), 0, -1):
            sys.stdout.write(f"\rابدأ خلال {t} ثانية... ")
            sys.stdout.flush()
            time.sleep(1)
        print("\nانطلاق الآن!")

        clicks_done = 0
        while True:
            if count and clicks_done >= count:
                print("اكتمل عدد النقرات المطلوب.")
                break

            if x is None or y is None:
                # استخدم موقع الماوس الحالي
                cx, cy = pyautogui.position()
            else:
                cx, cy = x, y

            # تنفيذ نقرة يسار
            try:
                pyautogui.click(cx, cy, button="left")
                clicks_done += 1
                print(f"[{clicks_done}] نقرة في ({cx},{cy}) — انتظار {interval} ثانية...")
            except pyautogui.FailSafeException:
                print("\n✋ تم إيقاف البرنامج عبر Failsafe (حرّكت الماوس إلى الزاوية العليا اليسرى).")
                break
            except Exception as e:
                print(f"⚠️ حصل خطأ أثناء النقر: {e}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n✋ تم إيقاف البرنامج بيد المستخدم (Ctrl+C).")

if __name__ == "__main__":
    main()
