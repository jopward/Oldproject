# db.py
import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "attendance.db"  # قاعدة البيانات الحالية

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # جدول المدارس
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_name TEXT NOT NULL,
        admin_username TEXT NOT NULL,
        admin_password TEXT NOT NULL
    )
    """)

    # جدول المعلمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        school_id INTEGER NOT NULL,
        FOREIGN KEY(school_id) REFERENCES schools(id)
    )
    """)

    # جدول شعب المعلمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        section TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id)
    )
    """)

    # إضافة عمود school_id إلى جدول الطلاب إذا لم يكن موجود
    cur.execute("PRAGMA table_info(students)")
    columns = [col['name'] for col in cur.fetchall()]
    if 'school_id' not in columns:
        cur.execute("ALTER TABLE students ADD COLUMN school_id INTEGER REFERENCES schools(id)")

    conn.commit()
    conn.close()

def seed_data():
    """
    إضافة بيانات وهمية: مدارس، معلمين، وشعب
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # مدارس وهمية
    schools = [
        {"school_name": "مدرسة النور", "admin_username": "admin_nour", "admin_password": generate_password_hash("1234")},
        {"school_name": "مدرسة الأمل", "admin_username": "admin_amal", "admin_password": generate_password_hash("1234")}
    ]
    for s in schools:
        cur.execute("""
        INSERT OR IGNORE INTO schools (school_name, admin_username, admin_password)
        VALUES (?, ?, ?)
        """, (s['school_name'], s['admin_username'], s['admin_password']))

    # المعلمين لكل مدرسة
    cur.execute("SELECT * FROM schools")
    school_rows = cur.fetchall()

    teachers = [
        {"teacher_name": "أحمد", "username": "ahmed", "password": generate_password_hash("123"), "school_id": school_rows[0]['id']},
        {"teacher_name": "سعاد", "username": "suad", "password": generate_password_hash("123"), "school_id": school_rows[0]['id']},
        {"teacher_name": "محمود", "username": "mahmoud", "password": generate_password_hash("123"), "school_id": school_rows[1]['id']},
        {"teacher_name": "منى", "username": "mona", "password": generate_password_hash("123"), "school_id": school_rows[1]['id']}
    ]
    for t in teachers:
        cur.execute("""
        INSERT OR IGNORE INTO teachers (teacher_name, username, password, school_id)
        VALUES (?, ?, ?, ?)
        """, (t['teacher_name'], t['username'], t['password'], t['school_id']))

    # إضافة شعب لكل معلم
    cur.execute("SELECT * FROM teachers")
    teacher_rows = cur.fetchall()

    classes = [
        {"teacher_id": teacher_rows[0]['id'], "class_name": "الصف السابع", "section": "أ"},
        {"teacher_id": teacher_rows[0]['id'], "class_name": "الصف الثامن", "section": "ب"},
        {"teacher_id": teacher_rows[1]['id'], "class_name": "الصف السابع", "section": "ب"},
        {"teacher_id": teacher_rows[2]['id'], "class_name": "الصف التاسع", "section": "أ"},
        {"teacher_id": teacher_rows[3]['id'], "class_name": "الصف التاسع", "section": "ب"}
    ]
    for c in classes:
        cur.execute("""
        INSERT OR IGNORE INTO teacher_classes (teacher_id, class_name, section)
        VALUES (?, ?, ?)
        """, (c['teacher_id'], c['class_name'], c['section']))

    conn.commit()
    conn.close()
    print("✅ تم إنشاء الجداول وإضافة بيانات وهمية بنجاح")

def add_school(school_name, admin_username, admin_password, teachers_list=None):
    """
    إضافة مدرسة جديدة مع مديرها وأي معلمين.
    teachers_list = [
        {"teacher_name": "...", "username": "...", "password": "..."}
    ]
    """
    conn = get_db_connection()
    cur = conn.cursor()

    hashed_admin_pw = generate_password_hash(admin_password)
    cur.execute("""
        INSERT INTO schools (school_name, admin_username, admin_password)
        VALUES (?, ?, ?)
    """, (school_name, admin_username, hashed_admin_pw))
    school_id = cur.lastrowid

    if teachers_list:
        for t in teachers_list:
            hashed_pw = generate_password_hash(t['password'])
            cur.execute("""
                INSERT INTO teachers (teacher_name, username, password, school_id)
                VALUES (?, ?, ?, ?)
            """, (t['teacher_name'], t['username'], hashed_pw, school_id))

    conn.commit()
    conn.close()
    print(f"✅ تم إضافة المدرسة '{school_name}' بنجاح")

# --- التنفيذ عند تشغيل الملف مباشرة ---
if __name__ == "__main__":
    create_tables()
    seed_data()

    # إضافة مدرسة جديدة بأدمن ومعلمين
    add_school(
        "مدرسة الربيع",
        "admin_rabea",
        "1234",
        teachers_list=[
            {"teacher_name": "ليلى", "username": "leila", "password": "123"},
            {"teacher_name": "علي", "username": "ali", "password": "123"}
        ]
    )
