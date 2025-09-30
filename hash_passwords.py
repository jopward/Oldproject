# reset_superadmin.py
from werkzeug.security import generate_password_hash
from db import get_db_connection, User

def reset_superadmin(username="superadmin", password="12345"):
    session = get_db_connection()
    try:
        # حذف أي مستخدم قديم
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            session.delete(existing)
            session.commit()
            print("🗑️ تم حذف السوبر أدمن القديم")

        # إنشاء مستخدم جديد
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, role="superadmin")
        session.add(user)
        session.commit()
        print(f"✅ تم إنشاء سوبر أدمن جديد:\n  المستخدم: {username}\n  كلمة المرور: {password}")
    finally:
        session.close()

if __name__ == "__main__":
    reset_superadmin(password="12345")  # غير الباسورد من هون لو بدك
