# encrypt_all_passwords.py
from werkzeug.security import generate_password_hash
from db import get_db_connection

def encrypt_passwords():
    conn = get_db_connection()

    # --- Superadmin users ---
    superadmins = conn.execute("SELECT id, password FROM users WHERE role='superadmin'").fetchall()
    for user in superadmins:
        pw = user['password']
        if not pw.startswith('pbkdf2:sha256:'):
            hashed_pw = generate_password_hash(pw)
            conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user['id']))
            print(f"✅ Superadmin ID={user['id']} تم تشفير كلمة المرور")

    # --- Admins (schools) ---
    schools = conn.execute("SELECT id, admin_password FROM schools").fetchall()
    for school in schools:
        pw = school['admin_password']
        if not pw.startswith('pbkdf2:sha256:'):
            hashed_pw = generate_password_hash(pw)
            conn.execute("UPDATE schools SET admin_password = ? WHERE id = ?", (hashed_pw, school['id']))
            print(f"✅ Admin (School) ID={school['id']} تم تشفير كلمة المرور")

    # --- Teachers ---
    teachers = conn.execute("SELECT id, password FROM teachers").fetchall()
    for teacher in teachers:
        pw = teacher['password']
        if not pw.startswith('pbkdf2:sha256:'):
            hashed_pw = generate_password_hash(pw)
            conn.execute("UPDATE teachers SET password = ? WHERE id = ?", (hashed_pw, teacher['id']))
            print(f"✅ Teacher ID={teacher['id']} تم تشفير كلمة المرور")

    conn.commit()
    conn.close()
    print("✅ تم تشفير كل كلمات المرور بنجاح")

if __name__ == "__main__":
    encrypt_passwords()
