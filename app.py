from flask import Flask, request, jsonify, session, redirect, url_for, flash, render_template
from auth import login_view, logout_view, login_required
import attendance
import students as students_module
import tracking
import reports as reports_module
import db  # ✅ استدعاء db.py
import teachers  # ملف teachers.py الجديد

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

# teachers
app.add_url_rule('/teachers', 'teachers_page', teachers.teachers_page, methods=['GET'])
app.add_url_rule('/teachers/delete/<int:teacher_id>', 'delete_teacher', teachers.delete_teacher, methods=['POST'])
app.add_url_rule('/teachers/add', 'add_teacher', teachers.add_teacher, methods=['POST'])

# --- ✅ إضافة صفوف وشعب ---
@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if session.get("role") != "admin":
        flash("غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    teachers = conn.execute(
        "SELECT * FROM teachers WHERE school_id = ?", (session["school_id"],)
    ).fetchall()

    if request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        class_name = request.form.get("class_name")
        section = request.form.get("section")

        if teacher_id and class_name and section:
            conn.execute(
                "INSERT INTO teacher_classes (teacher_id, class_name, section) VALUES (?, ?, ?)",
                (teacher_id, class_name, section),
            )
            conn.commit()
            flash("✅ تم إضافة الصف والشعبة بنجاح")
            conn.close()
            return redirect(url_for("list_classes"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول")

    conn.close()
    return render_template("add_class.html", teachers=teachers)


# --- ✅ عرض جميع الصفوف والشعب الخاصة بالمدرسة ---
@app.route("/classes")
@login_required
def list_classes():
    conn = db.get_db_connection()
    rows = conn.execute("""
        SELECT tc.id, tc.class_name, tc.section, t.teacher_name
        FROM teacher_classes tc
        JOIN teachers t ON tc.teacher_id = t.id
        WHERE t.school_id = ?
    """, (session["school_id"],)).fetchall()
    conn.close()
    return render_template("list_classes.html", classes=rows)


# --- ✅ حذف صف/شعبة ---
@app.route("/classes/delete/<int:class_id>", methods=["POST"])
@login_required
def delete_class(class_id):
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "غير مسموح"})

    conn = db.get_db_connection()
    conn.execute("DELETE FROM teacher_classes WHERE id = ?", (class_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "تم الحذف بنجاح"})


# --- ✅ تعديل صف/شعبة ---
@app.route("/classes/edit/<int:class_id>", methods=["GET", "POST"])
@login_required
def edit_class(class_id):
    if session.get("role") != "admin":
        flash("غير مسموح، هذه الصفحة خاصة بالمدير فقط")
        return redirect(url_for("dashboard"))

    conn = db.get_db_connection()
    teachers = conn.execute(
        "SELECT * FROM teachers WHERE school_id = ?", (session["school_id"],)
    ).fetchall()

    class_row = conn.execute(
        "SELECT * FROM teacher_classes WHERE id = ?", (class_id,)
    ).fetchone()

    if not class_row:
        conn.close()
        flash("⚠️ الصف/الشعبة غير موجود")
        return redirect(url_for("list_classes"))

    if request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        class_name = request.form.get("class_name")
        section = request.form.get("section")

        if teacher_id and class_name and section:
            conn.execute("""
                UPDATE teacher_classes
                SET teacher_id = ?, class_name = ?, section = ?
                WHERE id = ?
            """, (teacher_id, class_name, section, class_id))
            conn.commit()
            conn.close()
            flash("✅ تم تعديل الصف والشعبة بنجاح")
            return redirect(url_for("list_classes"))
        else:
            flash("⚠️ يرجى تعبئة جميع الحقول")

    conn.close()
    return render_template("edit_class.html", class_data=class_row, teachers=teachers)


# --- إنشاء الجداول ---
db.create_tables()
db.seed_data()

if __name__ == '__main__':
    app.run(debug=True)
