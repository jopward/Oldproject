# app.py
from flask import Flask
from auth import login_view, logout_view, login_required
import attendance
import students as students_module
import tracking
import reports as reports_module

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- تسجيل المسارات كما في الكود الأصلي (نحافظ على أسماء endpoints) ---

# auth
app.add_url_rule('/login', 'login', login_view, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout_view)

# attendance / dashboard
# عرض لوحة الحضور (function name: dashboard)
app.add_url_rule('/', 'dashboard', attendance.dashboard)
# تحديث حضور (POST)
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

if __name__ == '__main__':
    app.run(debug=True)
