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

    # جدول وسيط لربط الصفوف بالمعلمين
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

    # --- ✅ الجداول الجديدة للمواد ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        UNIQUE (teacher_id, subject_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY (class_id) REFERENCES teacher_classes(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE(class_id, subject_id, teacher_id)
    )
    """)

    # --- ✅ جدول تتبع الطلاب ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        school_id INTEGER NOT NULL,
        tracking_date TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(class_id) REFERENCES teacher_classes(id) ON DELETE CASCADE,
        FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
    )
    """)

    # إضافة عمود school_id إلى جدول الطلاب إذا لم يكن موجود
    cur.execute("PRAGMA table_info(students)")
    columns = [col['name'] for col in cur.fetchall()]
    if 'school_id' not in columns:
        cur.execute("ALTER TABLE students ADD COLUMN school_id INTEGER REFERENCES schools(id)")

    # --- ✅ إنشاء جدول السوبر أدمن (users) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# --- ✅ إضافة سوبر أدمن ---
def create_superadmin(username="superadmin", password="12345"):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)

    exists = cur.execute("SELECT * FROM users WHERE username = ? AND role = 'superadmin'", (username,)).fetchone()
    if exists:
        cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, exists['id']))
        print(f"✅ تم تحديث كلمة مرور السوبر أدمن '{username}'")
    else:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'superadmin')", (username, hashed_pw))
        print(f"✅ تم إنشاء السوبر أدمن '{username}' بكلمة مرور جديدة")

    conn.commit()
    conn.close()

# --- ✅ بقية الداتا الوهمية والمدارس والمعلمين كما هي ---
def seed_data():
    conn = get_db_connection()
    cur = conn.cursor()
    # مدارس وهمية
    schools = [
        {"school_name": "مدرسة النور", "admin_username": "admin_nour", "admin_password": generate_password_hash("1234")},
        {"school_name": "مدرسة الأمل", "admin_username": "admin_amal", "admin_password": generate_password_hash("1234")}
    ]
    for s in schools:
        cur.execute("INSERT OR IGNORE INTO schools (school_name, admin_username, admin_password) VALUES (?, ?, ?)",
                    (s['school_name'], s['admin_username'], s['admin_password']))
    cur.execute("SELECT * FROM schools")
    school_rows = cur.fetchall()

    teachers = [
        {"teacher_name": "أحمد", "username": "ahmed", "password": generate_password_hash("123"), "school_id": school_rows[0]['id']},
        {"teacher_name": "سعاد", "username": "suad", "password": generate_password_hash("123"), "school_id": school_rows[0]['id']},
        {"teacher_name": "محمود", "username": "mahmoud", "password": generate_password_hash("123"), "school_id": school_rows[1]['id']},
        {"teacher_name": "منى", "username": "mona", "password": generate_password_hash("123"), "school_id": school_rows[1]['id']}
    ]
    for t in teachers:
        cur.execute("INSERT OR IGNORE INTO teachers (teacher_name, username, password, school_id) VALUES (?, ?, ?, ?)",
                    (t['teacher_name'], t['username'], t['password'], t['school_id']))

    conn.commit()
    conn.close()
    print("✅ تم إنشاء الجداول وإضافة بيانات وهمية بنجاح")

# --- ✅ إضافة مدرسة جديدة ---
def add_school(school_name, admin_username, admin_password, teachers_list=None):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_admin_pw = generate_password_hash(admin_password)
    cur.execute("INSERT INTO schools (school_name, admin_username, admin_password) VALUES (?, ?, ?)",
                (school_name, admin_username, hashed_admin_pw))
    school_id = cur.lastrowid

    if teachers_list:
        for t in teachers_list:
            hashed_pw = generate_password_hash(t['password'])
            cur.execute("INSERT INTO teachers (teacher_name, username, password, school_id) VALUES (?, ?, ?, ?)",
                        (t['teacher_name'], t['username'], hashed_pw, school_id))
    conn.commit()
    conn.close()
    print(f"✅ تم إضافة المدرسة '{school_name}' بنجاح")

# --- التنفيذ عند تشغيل الملف مباشرة ---
if __name__ == "__main__":
    create_tables()
    seed_data()
    create_superadmin()  # إنشاء أو تحديث السوبر أدمن
