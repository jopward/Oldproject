# update_superadmin_password.py
import sqlite3
from auth import hash_password  # استدعاء دالة تشفير كلمات السر من auth.py

# ضع هنا كلمة السر الجديدة
new_password = "12345"

# تشفير كلمة السر بالطريقة نفسها المستخدمة في المشروع
hashed_password = hash_password(new_password)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('attendance.db')
cur = conn.cursor()

# تحديث كلمة السر للـ superadmin
cur.execute("UPDATE users SET password=? WHERE username='superadmin'", (hashed_password,))
conn.commit()
conn.close()

print("✅ تم تحديث كلمة سر superadmin بنجاح")
