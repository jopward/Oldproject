import sqlite3
from datetime import date

DATABASE = "attendance.db"

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# ----------------------------
# جدول الطلاب
# ----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL
)
""")

# بيانات تجريبية للطلاب
students_data = [
    ("أحمد علي", "العاشر", "أ"),
    ("سارة محمد", "العاشر", "ب"),
    ("خالد يوسف", "التاسع", "ج"),
    ("ليلى حسن", "التاسع", "د")
]

cur.executemany("INSERT INTO students (student_name, class_name, section) VALUES (?, ?, ?)", students_data)

# ----------------------------
# جدول الحضور والغياب
# ----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

# ----------------------------
# جدول المتابعة اليومية
# ----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS student_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    homework INTEGER DEFAULT 0,
    book INTEGER DEFAULT 0,
    participation INTEGER DEFAULT 0,
    misbehavior INTEGER DEFAULT 0,
    note TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()
conn.close()

print("تم إنشاء جميع الجداول الضرورية وإضافة بيانات تجريبية.")
