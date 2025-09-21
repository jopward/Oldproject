# hash_passwords.py
import sqlite3
from werkzeug.security import generate_password_hash

DB = "attendance.db"  # غيّر إذا اسم قاعدة بياناتك مختلف

def is_hashed(pw: str) -> bool:
    if not pw:
        return True
    return pw.startswith("pbkdf2:") or pw.startswith("scrypt:")  # أكثر الصيغ شيوعاً

def hash_table_passwords(conn, table, id_col, pw_col, extra_select_cols=None, where_clause=""):
    cur = conn.cursor()
    select_cols = f"{id_col}, {pw_col}"
    if extra_select_cols:
        select_cols = select_cols + ", " + ", ".join(extra_select_cols)
    q = f"SELECT {select_cols} FROM {table} {where_clause}"
    rows = cur.execute(q).fetchall()

    updated = 0
    for row in rows:
        row = list(row)
        item_id = row[0]
        pw = row[1]
        if pw is None:
            continue
        if is_hashed(pw):
            continue
        new_pw = generate_password_hash(pw)
        cur.execute(f"UPDATE {table} SET {pw_col} = ? WHERE {id_col} = ?", (new_pw, item_id))
        updated += 1

    conn.commit()
    return updated

def main():
    print("🔐 بدء تحديث كلمات المرور (سيتم تجزئة كلمات المرور النصّية فقط)...")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    total = 0
    # جدول users (قد يحتوي على superadmin)
    try:
        n = hash_table_passwords(conn, "users", "id", "password")
        print(f"users: تم تعديل {n} كلمة مرور.")
        total += n
    except Exception as e:
        print("users: خطأ:", e)

    # جدول teachers
    try:
        n = hash_table_passwords(conn, "teachers", "id", "password")
        print(f"teachers: تم تعديل {n} كلمة مرور.")
        total += n
    except Exception as e:
        print("teachers: خطأ:", e)

    # جدول schools -> الحقل admin_password
    try:
        n = hash_table_passwords(conn, "schools", "id", "admin_password")
        print(f"schools (admin_password): تم تعديل {n} كلمة مرور.")
        total += n
    except Exception as e:
        print("schools: خطأ:", e)

    conn.close()
    print(f"✅ انتهى التحديث — إجمالي كلمات مرور تم تجزئتها: {total}")

if __name__ == "__main__":
    main()
