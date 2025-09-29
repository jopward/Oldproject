# attendance.py
from flask import render_template, request, jsonify, session, redirect, url_for
from datetime import date
from auth import login_required
from db import SessionLocal  # ✅ استخدام SQLAlchemy
from sqlalchemy import text  # ✅ إضافة text

@login_required
def dashboard():
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id")  # المعلم الحالي
    if not school_id or not teacher_id:
        return redirect(url_for("login"))

    db_session = SessionLocal()
    today = date.today().isoformat()

    # الطلاب من نفس المدرسة فقط + الحضور مرتبط بالمعلم
    students = db_session.execute(text('''
        SELECT s.id, s.student_name, s.class_name, s.section, a.status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id AND a.date = :today AND a.school_id = :school_id AND a.teacher_id = :teacher_id
        WHERE s.school_id = :school_id
        ORDER BY s.student_name
    '''), {"today": today, "school_id": school_id, "teacher_id": teacher_id}).fetchall()

    # الصفوف والشعب ضمن نفس المدرسة فقط
    classes = sorted(set([row["class_name"] for row in students if row["class_name"]]))
    sections = sorted(set([row["section"] for row in students if row["section"]]))

    db_session.close()

    return render_template(
        'dashboard.html',
        students=students,
        today=today,
        classes=classes,
        sections=sections
    )

@login_required
def update_attendance():
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id")
    if not school_id or not teacher_id:
        return jsonify({'success': False, 'message': 'مدرسة أو معلم غير معروف'})

    data = request.get_json()
    student_id = data['student_id']
    status = data['status']
    today = date.today().isoformat()

    db_session = SessionLocal()
    
    existing = db_session.execute(
        text('SELECT * FROM attendance WHERE student_id = :student_id AND date = :today AND school_id = :school_id AND teacher_id = :teacher_id'),
        {"student_id": student_id, "today": today, "school_id": school_id, "teacher_id": teacher_id}
    ).fetchone()

    if existing:
        db_session.execute(
            text('UPDATE attendance SET status = :status WHERE student_id = :student_id AND date = :today AND school_id = :school_id AND teacher_id = :teacher_id'),
            {"status": status, "student_id": student_id, "today": today, "school_id": school_id, "teacher_id": teacher_id}
        )
    else:
        db_session.execute(
            text('INSERT INTO attendance (student_id, date, status, school_id, teacher_id) VALUES (:student_id, :today, :status, :school_id, :teacher_id)'),
            {"student_id": student_id, "today": today, "status": status, "school_id": school_id, "teacher_id": teacher_id}
        )

    db_session.commit()
    db_session.close()

    return jsonify({'success': True})
