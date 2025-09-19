# app.py
from flask import Flask, request, jsonify, session
from auth import login_view, logout_view, login_required
import attendance
import students as students_module
import tracking
import reports as reports_module
import db  # ✅ استدعاء db.py الذي أنشأنا فيه المدارس والمعلمين
import teachers  # ملف teachers.py الجديد

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- تسجيل المسارات كما في الكود الأصلي (نحافظ على أسماء endpoints) ---

# auth
app.add_url_rule('/login', 'login', login_view, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout_view)

# attendance / dashboard
app.add_url_rule('/', 'dashboard', attendance.dashboard)
app.add_url_rule('/update_attendance', 'update_attendance', attendance.update_attendance, methods=['POST'])

# students
app.add_url_rule('/students', 'students', students_module.students, methods=['GET', 'POST'])
app.add_url_rule('/edit_student/<int:student_id>', 'edit_student', students_module.edit_student, methods=['POST'])
app.add_url_rule('/delete_student/<int:student_id>', 'delete_student', students_module.delete_student, methods=['POST'])

# tracking
app.add_url_rule('/tracking', 'tracking_page', tracking.tracking_page)
app.add_url_rule('/update_tracking', 'update_tracking', tracking.update_tracking, methods=['POST'])
app.add_url_rule('/update_note', 'update_note', tracking.update_note, methods=['POST'])

# reports
app.add_url_rule('/reports', 'reports_page', reports_module.reports_page)
app.add_url_rule('/get_attendance_details/<int:student_id>/<status>', 'get_attendance_details', reports_module.get_attendance_details)
app.add_url_rule('/get_tracking_details/<int:student_id>/<field>', 'get_tracking_details', reports_module.get_tracking_details)

# --- مدارس ومعلمين ---
app.add_url_rule('/teachers', 'teachers_page', teachers.teachers_page, methods=['GET'])
app.add_url_rule('/teachers/delete/<int:teacher_id>', 'delete_teacher', teachers.delete_teacher, methods=['POST'])
app.add_url_rule('/teachers/add', 'add_teacher', teachers.add_teacher, methods=['POST'])  # ربط الدالة من teachers.py

# --- إنشاء الجداول الجديدة إذا لم تكن موجودة ---
db.create_tables()
db.seed_data()  # إضافة بيانات وهمية عند أول تشغيل

if __name__ == '__main__':
    app.run(debug=True)
