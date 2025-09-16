import sqlite3

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# جداول المشروع المطلوبة
required_tables = ['students', 'attendance', 'student_tracking']

# جلب الجداول الموجودة
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
existing_tables = [row[0] for row in cursor.fetchall()]

# التحقق من كل جدول
for table in required_tables:
    if table in existing_tables:
        print(f"[✓] الجدول موجود: {table}")
    else:
        print(f"[✗] الجدول مفقود: {table}")

# التحقق من أعمدة كل جدول
print("\nتفاصيل الجداول:")
for table in required_tables:
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    print(f"\n{table}:")
    for col in columns:
        print(f" - {col[1]} ({col[2]})")

conn.close()
