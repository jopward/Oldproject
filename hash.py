# set_superadmin.py
import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "attendance.db"
USERNAME = "superadmin"   # اسم المستخدم اللي عندك
NEW_PASSWORD = "1234"     # غيّر هنا لكلمة المرور اللي تريدها

def main():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    hashed = generate_password_hash(NEW_PASSWORD)

    # تأكد إذا فيه جدول users
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cur.fetchone():
        print("خطأ: ما في جدول users. تفقد هيكل DB أو اختر الخيار B لتعديل auth.py")
        conn.close()
        return

    # إذا موجود سجل للسوبر أدمن في users حدّثه، وإلا أدخله
    cur.execute("SELECT * FROM users WHERE username = ?", (USERNAME,))
    if cur.fetchone():
        cur.execute("UPDATE users SET password = ?, role = 'superadmin' WHERE username = ?", (hashed, USERNAME))
        print("✅ تم تحديث كلمة مرور السوبر أدمن في جدول users")
    else:
        # حاول الحصول على id فريد — id هو autoincrement عادةً
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (USERNAME, hashed, 'superadmin'))
        print("✅ تم إضافة السوبر أدمن إلى جدول users")

    conn.commit()
    conn.close()
    print("أعد تشغيل السيرفر (مثلاً: python app.py) وجرب تسجيل الدخول")

if __name__ == "__main__":
    main()
