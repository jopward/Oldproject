# db.py
import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "attendance.db"  # قاعدة البيانات الحالية

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ✅ إنشاء الجداول الأساسية ---
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

    # جدول الصفوف
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        section TEXT,
        period TEXT DEFAULT 'صباحي'
    )
    """)

    # جدول وسيط لربط الصفوف بالمعلمين (دعم أكثر من معلم لكل صف)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY(class_id) REFERENCES teacher_classes(id) ON DELETE CASCADE,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE(class_id, teacher_id)
    )
    """)

    # إضافة عمود school_id إلى جدول الطلاب إذا لم يكن موجود
    cur.execute("PRAGMA table_info(students)")
    columns = [col['name'] for col in cur.fetchall()]
    if 'school_id' not in columns:
        cur.execute("ALTER TABLE students ADD COLUMN school_id INTEGER REFERENCES schools(id)")

    conn.commit()
    conn.close()


# --- ✅ إضافة بيانات وهمية (Seed) ---
def seed_data():
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

    # جلب المدارس
    cur.execute("SELECT * FROM schools")
    school_rows = cur.fetchall()

    # معلمين وهميين
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

    # إضافة صفوف
    classes = [
        {"class_name": "الصف السابع", "section": "أ", "period": "صباحي"},
        {"class_name": "الصف الثامن", "section": "ب", "period": "صباحي"},
        {"class_name": "الصف السابع", "section": "ب", "period": "صباحي"},
        {"class_name": "الصف التاسع", "section": "أ", "period": "صباحي"},
        {"class_name": "الصف التاسع", "section": "ب", "period": "صباحي"}
    ]
    for c in classes:
        cur.execute("""
        INSERT OR IGNORE INTO teacher_classes (class_name, section, period)
        VALUES (?, ?, ?)
        """, (c['class_name'], c['section'], c['period']))

    # ربط الصفوف بالمعلمين في جدول class_teachers
    cur.execute("SELECT * FROM teacher_classes")
    class_rows = cur.fetchall()
    cur.execute("SELECT * FROM teachers")
    teacher_rows = cur.fetchall()

    class_teacher_links = [
        {"class_id": class_rows[0]['id'], "teacher_id": teacher_rows[0]['id']},
        {"class_id": class_rows[1]['id'], "teacher_id": teacher_rows[0]['id']},
        {"class_id": class_rows[2]['id'], "teacher_id": teacher_rows[1]['id']},
        {"class_id": class_rows[3]['id'], "teacher_id": teacher_rows[2]['id']},
        {"class_id": class_rows[4]['id'], "teacher_id": teacher_rows[3]['id']}
    ]
    for link in class_teacher_links:
        cur.execute("""
        INSERT OR IGNORE INTO class_teachers (class_id, teacher_id)
        VALUES (?, ?)
        """, (link['class_id'], link['teacher_id']))

    conn.commit()
    conn.close()
    print("✅ تم إنشاء الجداول وإضافة بيانات وهمية بنجاح")


# --- ✅ إضافة مدرسة جديدة مع المعلمين ---
def add_school(school_name, admin_username, admin_password, teachers_list=None):
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

    add_school(
        "مدرسة الربيع",
        "admin_rabea",
        "1234",
        teachers_list=[
            {"teacher_name": "ليلى", "username": "leila", "password": "123"},
            {"teacher_name": "علي", "username": "ali", "password": "123"}
        ]
    )
