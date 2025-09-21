# teachers.py
from flask import render_template, session, redirect, url_for, jsonify, request
from auth import login_required
from db import get_db_connection
from werkzeug.security import generate_password_hash

@login_required
def teachers_page():
    """
    عرض صفحة المعلمين الخاصة بالمدرسة.
    المدير (admin) يرى جميع المعلمين في مدرسته.
    المعلم العادي يرى نفسه فقط.
    """
    user = session.get('user')
    school_id = session.get('school_id')  # معرف المدرسة من السيشن
    role = session.get('role', 'teacher')  # 'admin' أو 'teacher'

    if not school_id:
        return redirect(url_for('dashboard'))

    conn = get_db_connection()

    if role == 'admin':
        # الأدمن يرى كل المعلمين في المدرسة
        teachers = conn.execute(
            "SELECT * FROM teachers WHERE school_id = ? ORDER BY teacher_name",
            (school_id,)
        ).fetchall()
    else:
        # المعلم العادي يرى نفسه فقط
        teachers = conn.execute(
            "SELECT * FROM teachers WHERE id = ? AND school_id = ?",
            (user['id'], school_id)
        ).fetchall()

    conn.close()
    return render_template("teachers.html", teachers=teachers)


@login_required
def add_teacher():
    """
    إضافة معلم جديد ضمن المدرسة الحالية.
    فقط الأدمن يستطيع الإضافة.
    """
    role = session.get('role', 'teacher')
    school_id = session.get('school_id')

    if role != 'admin' or not school_id:
        return jsonify({"success": False, "message": "غير مسموح"})

    data = request.form
    teacher_name = data.get('teacher_name')
    username = data.get('username')
    password = data.get('password')

    if not all([teacher_name, username, password]):
        return jsonify({"success": False, "message": "جميع الحقول مطلوبة"})

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO teachers (teacher_name, username, password, school_id) VALUES (?, ?, ?, ?)",
        (teacher_name, username, hashed_pw, school_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "تم إضافة المعلم بنجاح"})


@login_required
def delete_teacher(teacher_id):
    """
    حذف معلم إذا كان ضمن نفس المدرسة.
    فقط الأدمن يستطيع الحذف.
    """
    user = session.get('user')
    school_id = session.get('school_id')
    role = session.get('role', 'teacher')

    if role != 'admin' or not school_id:
        return jsonify({"success": False, "message": "غير مسموح"})

    conn = get_db_connection()
    # التحقق من أن المعلم ينتمي لنفس المدرسة
    teacher = conn.execute(
        "SELECT * FROM teachers WHERE id = ? AND school_id = ?",
        (teacher_id, school_id)
    ).fetchone()

    if not teacher:
        conn.close()
        return jsonify({"success": False, "message": "المعلم غير موجود أو ليس ضمن مدرستك"})

    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "تم الحذف بنجاح"})
