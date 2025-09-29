# teachers.py
from flask import render_template, session, redirect, url_for, jsonify, request
from auth import login_required
from db import SessionLocal  # ✅ استدعاء جلسة SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import text  # ✅ إضافة text

@login_required
def teachers_page():
    """
    عرض صفحة المعلمين الخاصة بالمدرسة.
    المدير (admin) يرى جميع المعلمين في مدرسته.
    المعلم العادي يرى نفسه فقط.
    """
    user = session.get('user')
    school_id = session.get('school_id')
    role = session.get('role', 'teacher')

    if not school_id:
        return redirect(url_for('dashboard'))

    db_session = SessionLocal()

    if role == 'admin':
        teachers = db_session.execute(
            text("SELECT * FROM teachers WHERE school_id = :school_id ORDER BY teacher_name"),
            {"school_id": school_id}
        ).fetchall()
    else:
        teachers = db_session.execute(
            text("SELECT * FROM teachers WHERE id = :teacher_id AND school_id = :school_id"),
            {"teacher_id": user['id'], "school_id": school_id}
        ).fetchall()

    db_session.close()
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

    db_session = SessionLocal()
    db_session.execute(
        text("INSERT INTO teachers (teacher_name, username, password, school_id) "
             "VALUES (:teacher_name, :username, :password, :school_id)"),
        {"teacher_name": teacher_name, "username": username, "password": hashed_pw, "school_id": school_id}
    )
    db_session.commit()
    db_session.close()
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

    db_session = SessionLocal()
    teacher = db_session.execute(
        text("SELECT * FROM teachers WHERE id = :teacher_id AND school_id = :school_id"),
        {"teacher_id": teacher_id, "school_id": school_id}
    ).fetchone()

    if not teacher:
        db_session.close()
        return jsonify({"success": False, "message": "المعلم غير موجود أو ليس ضمن مدرستك"})

    db_session.execute(
        text("DELETE FROM teachers WHERE id = :teacher_id"),
        {"teacher_id": teacher_id}
    )
    db_session.commit()
    db_session.close()
    return jsonify({"success": True, "message": "تم الحذف بنجاح"})
