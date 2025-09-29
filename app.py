from flask import Flask, request, jsonify, session, redirect, url_for, flash, render_template
from auth import login_view, logout_view, login_required
import attendance
import students as students_module
import tracking
import reports as reports_module
import db  # ✅ استدعاء db.py
import teachers  # ملف teachers.py
import subjects  # ملف subjects.py
from werkzeug.security import generate_password_hash  # ✅ إضافة التشفير
from sqlalchemy.orm import joinedload

# --- تعريف التطبيق ---
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- تسجيل المسارات ---

# auth
app.add_url_rule('/login', 'login', login_view, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout_view)

# attendance / dashboard
app.add_url_rule('/', 'dashboard', attendance.dashboard)
app.add_url_rule('/update_attendance', 'update_attendance', attendance.update_attendance, methods=['POST'])

# students (خاص بالمدير فقط)
@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    if session.get("role") != "admin":
        flash("❌ غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))
    return students_module.students()

@app.route('/get_students', methods=['GET'])
@login_required
def get_students():
    if session.get("role") != "admin":
        return jsonify({"error": "❌ غير مسموح"}), 403
    return students_module.get_students()

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    if session.get("role") != "admin":
        return jsonify({"error": "❌ غير مسموح"}), 403
    return students_module.add_student()

@app.route('/edit_student/<int:student_id>', methods=['POST'])
@login_required
def edit_student(student_id):
    if session.get("role") != "admin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))
    return students_module.edit_student(student_id)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if session.get("role") != "admin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))
    return students_module.delete_student(student_id)

# tracking
app.add_url_rule('/tracking', 'tracking_page', tracking.tracking_page)
app.add_url_rule('/update_tracking', 'update_tracking', tracking.update_tracking, methods=['POST'])
app.add_url_rule('/update_note', 'update_note', tracking.update_note, methods=['POST'])

# reports
app.add_url_rule('/reports', 'reports_page', reports_module.reports_page)
app.add_url_rule('/get_attendance_details/<int:student_id>/<status>', 'get_attendance_details', reports_module.get_attendance_details)
app.add_url_rule('/get_tracking_details/<int:student_id>/<field>', 'get_tracking_details', reports_module.get_tracking_details)
app.add_url_rule('/student/<int:student_id>', 'student_detail', reports_module.student_detail)

# teachers
app.add_url_rule('/teachers', 'teachers_page', teachers.teachers_page, methods=['GET'])
app.add_url_rule('/teachers/delete/<int:teacher_id>', 'delete_teacher', teachers.delete_teacher, methods=['POST'])
app.add_url_rule('/teachers/add', 'add_teacher', teachers.add_teacher, methods=['POST'])

# subjects
app.add_url_rule('/subjects', 'subjects_page', subjects.subjects_page, methods=['GET'])
app.add_url_rule('/subjects/add', 'add_subject', subjects.add_subject, methods=['POST'])
app.add_url_rule('/subjects/edit/<int:subject_id>', 'edit_subject', subjects.edit_subject, methods=['GET', 'POST'])
app.add_url_rule('/subjects/delete/<int:subject_id>', 'delete_subject', subjects.delete_subject, methods=['POST'])
app.add_url_rule('/subjects/remove_teacher/<int:st_id>', 'remove_teacher_from_subject', subjects.remove_teacher_from_subject, methods=['POST'])

# --- إدارة الصفوف ---
@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if session.get("role") != "admin":
        flash("غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))

    session_db = db.get_db_connection()
    try:
        teachers_list = session_db.query(db.Teacher).filter_by(school_id=session["school_id"]).all()

        if request.method == "POST":
            class_name = request.form.get("class_name")
            section = request.form.get("section")
            period = request.form.get("period") or "صباحي"
            teacher_ids = request.form.getlist("teacher_ids")

            if class_name and section and teacher_ids:
                new_class = db.TeacherClass(class_name=class_name, section=section, period=period)
                session_db.add(new_class)
                session_db.commit()  # لازم commit حتى يحصل على id
                for t_id in teacher_ids:
                    ct = db.ClassTeacher(class_id=new_class.id, teacher_id=int(t_id))
                    session_db.add(ct)
                session_db.commit()
                flash("✅ تم إضافة الصف والشعبة بنجاح")
                return redirect(url_for("list_classes"))
            else:
                flash("⚠️ يرجى تعبئة جميع الحقول واختيار المعلمين")
    finally:
        session_db.close()

    return render_template("add_class.html", teachers=teachers_list)

@app.route("/classes")
@login_required
def list_classes():
    session_db = db.get_db_connection()
    try:
        classes = session_db.query(db.TeacherClass).all()
    finally:
        session_db.close()
    return render_template("list_classes.html", classes=classes)

# --- إدارة المدارس (Superadmin) ---
@app.route("/schools")
@login_required
def list_schools():
    if session.get("role") != "superadmin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))

    session_db = db.get_db_connection()
    try:
        schools = session_db.query(db.School).all()
    finally:
        session_db.close()
    return render_template("list_schools.html", schools=schools)

@app.route("/schools/add", methods=["GET", "POST"])
@login_required
def add_school():
    if session.get("role") != "superadmin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        if school_name and admin_username and admin_password:
            db.add_school(school_name, admin_username, admin_password)
            flash("✅ تم إضافة المدرسة بنجاح")
            return redirect(url_for("list_schools"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول")

    return render_template("add_school.html")

# --- إنشاء الجداول الافتراضية ---
db.init_db()
db.create_superadmin()

if __name__ == '__main__':
    app.run(debug=True)
