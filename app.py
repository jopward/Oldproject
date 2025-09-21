from flask import Flask, request, jsonify, session, redirect, url_for, flash, render_template
from auth import login_view, logout_view, login_required
import attendance
import students as students_module
import tracking
import reports as reports_module
import db  # ✅ استدعاء db.py
import teachers  # ملف teachers.py
import subjects  # ملف subjects.py

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
app.add_url_rule('/student/<int:student_id>', 'student_detail', reports_module.student_detail)

# teachers
app.add_url_rule('/teachers', 'teachers_page', teachers.teachers_page, methods=['GET'])
app.add_url_rule('/teachers/delete/<int:teacher_id>', 'delete_teacher', teachers.delete_teacher, methods=['POST'])
app.add_url_rule('/teachers/add', 'add_teacher', teachers.add_teacher, methods=['POST'])

# --- إدارة المواد (Subjects) ---
app.add_url_rule('/subjects', 'subjects_page', subjects.subjects_page, methods=['GET'])
app.add_url_rule('/subjects/add', 'add_subject', subjects.add_subject, methods=['POST'])
app.add_url_rule('/subjects/edit/<int:subject_id>', 'edit_subject', subjects.edit_subject, methods=['GET', 'POST'])
app.add_url_rule('/subjects/delete/<int:subject_id>', 'delete_subject', subjects.delete_subject, methods=['POST'])
app.add_url_rule('/subjects/remove_teacher/<int:st_id>', 'remove_teacher_from_subject', subjects.remove_teacher_from_subject, methods=['POST'])

# --- إضافة صفوف وشعب ---
@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if session.get("role") != "admin":
        flash("غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    teachers_list = conn.execute(
        "SELECT * FROM teachers WHERE school_id = ?", (session["school_id"],)
    ).fetchall()

    if request.method == "POST":
        class_name = request.form.get("class_name")
        section = request.form.get("section")
        period = request.form.get("period") or "صباحي"
        teacher_ids = request.form.getlist("teacher_ids")

        if class_name and section and teacher_ids:
            # ✅ إضافة school_id لكل صف
            cur = conn.execute(
                "INSERT INTO teacher_classes (class_name, section, period, school_id) VALUES (?, ?, ?, ?)",
                (class_name, section, period, session["school_id"])
            )
            class_id = cur.lastrowid
            for t_id in teacher_ids:
                conn.execute(
                    "INSERT INTO class_teachers (class_id, teacher_id) VALUES (?, ?)",
                    (class_id, t_id)
                )
            conn.commit()
            flash("✅ تم إضافة الصف والشعبة بنجاح")
            conn.close()
            return redirect(url_for("list_classes"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول واختيار المعلمين")

    conn.close()
    return render_template("add_class.html", teachers=teachers_list)

@app.route("/classes")
@login_required
def list_classes():
    conn = db.get_db_connection()
    rows = conn.execute("""
        SELECT tc.id, tc.class_name, tc.section, tc.period,
               GROUP_CONCAT(t.teacher_name, ', ') AS teacher_names
        FROM teacher_classes tc
        LEFT JOIN class_teachers ct ON tc.id = ct.class_id
        LEFT JOIN teachers t ON ct.teacher_id = t.id
        WHERE tc.school_id = ?
        GROUP BY tc.id
    """, (session["school_id"],)).fetchall()
    conn.close()
    return render_template("list_classes.html", classes=rows)

@app.route("/classes/edit/<int:class_id>", methods=["GET", "POST"])
@login_required
def edit_class(class_id):
    if session.get("role") != "admin":
        flash("غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    teachers_list = conn.execute(
        "SELECT * FROM teachers WHERE school_id = ?", (session["school_id"],)
    ).fetchall()

    class_row = conn.execute(
        "SELECT * FROM teacher_classes WHERE id = ? AND school_id = ?", (class_id, session["school_id"])
    ).fetchone()

    current_teachers = conn.execute(
        "SELECT teacher_id FROM class_teachers WHERE class_id = ?", (class_id,)
    ).fetchall()
    current_teacher_ids = [t['teacher_id'] for t in current_teachers]

    if not class_row:
        conn.close()
        flash("⚠️ الصف/الشعبة غير موجود")
        return redirect(url_for("list_classes"))

    if request.method == "POST":
        class_name = request.form.get("class_name")
        section = request.form.get("section")
        period = request.form.get("period") or "صباحي"
        teacher_ids = request.form.getlist("teacher_ids")

        if class_name and section and teacher_ids:
            conn.execute("""
                UPDATE teacher_classes
                SET class_name = ?, section = ?, period = ?
                WHERE id = ?
            """, (class_name, section, period, class_id))

            conn.execute("DELETE FROM class_teachers WHERE class_id = ?", (class_id,))
            for t_id in teacher_ids:
                conn.execute(
                    "INSERT INTO class_teachers (class_id, teacher_id) VALUES (?, ?)",
                    (class_id, t_id)
                )

            conn.commit()
            conn.close()
            flash("✅ تم تعديل الصف والشعبة بنجاح")
            return redirect(url_for("list_classes"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول واختيار المعلمين")

    conn.close()
    return render_template(
        "edit_class.html",
        class_data=class_row,
        teachers=teachers_list,
        current_teacher_ids=current_teacher_ids
    )

# --- إدارة المدارس (Superadmin) ---
@app.route("/schools")
@login_required
def list_schools():
    if session.get("role") != "superadmin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    schools = conn.execute("SELECT * FROM schools").fetchall()
    conn.close()
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
            conn = db.get_db_connection()
            conn.execute("""
                INSERT INTO schools (school_name, admin_username, admin_password)
                VALUES (?, ?, ?)
            """, (school_name, admin_username, admin_password))
            conn.commit()
            conn.close()
            flash("✅ تم إضافة المدرسة بنجاح")
            return redirect(url_for("list_schools"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول")

    return render_template("add_school.html")

@app.route("/schools/edit/<int:school_id>", methods=["GET", "POST"])
@login_required
def edit_school(school_id):
    if session.get("role") != "superadmin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    school = conn.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()

    if not school:
        flash("⚠️ المدرسة غير موجودة")
        return redirect(url_for("list_schools"))

    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        conn.execute("""
            UPDATE schools
            SET school_name = ?, admin_username = ?, admin_password = ?
            WHERE id = ?
        """, (school_name, admin_username, admin_password, school_id))
        conn.commit()
        conn.close()
        flash("✅ تم تعديل بيانات المدرسة")
        return redirect(url_for("list_schools"))

    conn.close()
    return render_template("edit_school.html", school=school)

@app.route("/schools/delete/<int:school_id>", methods=["POST"])
@login_required
def delete_school(school_id):
    if session.get("role") != "superadmin":
        flash("❌ غير مسموح")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    conn.execute("DELETE FROM schools WHERE id = ?", (school_id,))
    conn.commit()
    conn.close()
    flash("🗑️ تم حذف المدرسة بنجاح")
    return redirect(url_for("list_schools"))

# --- إنشاء الجداول الافتراضية ---
db.create_tables()
db.seed_data()

if __name__ == '__main__':
    app.run(debug=True)
