# attendance.py
from flask import render_template, request, jsonify, session, redirect, url_for
from datetime import date
from auth import login_required
from db import get_db_connection

@login_required
def dashboard():
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id")  # ✅ نستخدم id المعلم من الجلسة
    if not school_id or not teacher_id:
        return redirect(url_for("login"))

    conn = get_db_connection()
    today = date.today().isoformat()

    # ✅ الطلاب من نفس المدرسة فقط + الحضور مرتبط بالمعلم
    students = conn.execute('''
        SELECT s.id, s.student_name, s.class_name, s.section, a.status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id AND a.date = ? AND a.school_id=? AND a.teacher_id=?
        WHERE s.school_id=?
        ORDER BY s.student_name
    ''', (today, school_id, teacher_id, school_id)).fetchall()

    # ✅ الصفوف والشعب ضمن نفس المدرسة فقط
    classes = sorted(set([row["class_name"] for row in students if row["class_name"]]))
    sections = sorted(set([row["section"] for row in students if row["section"]]))

    conn.close()

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
    teacher_id = session.get("user", {}).get("id")  # ✅ المعلم الحالي
    if not school_id or not teacher_id:
        return jsonify({'success': False, 'message': 'مدرسة أو معلم غير معروف'})

    data = request.get_json()
    student_id = data['student_id']
    status = data['status']
    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM attendance WHERE student_id=? AND date=? AND school_id=? AND teacher_id=?',
        (student_id, today, school_id, teacher_id)
    ).fetchone()

    if existing:
        conn.execute(
            'UPDATE attendance SET status=? WHERE student_id=? AND date=? AND school_id=? AND teacher_id=?',
            (status, student_id, today, school_id, teacher_id)
        )
    else:
        conn.execute(
            'INSERT INTO attendance (student_id, date, status, school_id, teacher_id) VALUES (?, ?, ?, ?, ?)',
            (student_id, today, status, school_id, teacher_id)
        )

    conn.commit()
    conn.close()

    return jsonify({'success': True})
