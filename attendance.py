# attendance.py
from flask import render_template, request, jsonify
from datetime import date
from auth import login_required
from db import get_db_connection

@login_required
def dashboard():
    conn = get_db_connection()
    today = date.today().isoformat()

    # نجلب الطلاب مع الصف والشعبة وحالة الحضور
    students = conn.execute('''
        SELECT s.id, s.student_name, s.class_name, s.section, a.status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id AND a.date = ?
        ORDER BY s.student_name
    ''', (today,)).fetchall()

    # نبني قائمة الصفوف والشُعب (مميزة)
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

def update_attendance():
    data = request.get_json()
    student_id = data['student_id']
    status = data['status']
    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM attendance WHERE student_id=? AND date=?',
        (student_id, today)
    ).fetchone()

    if existing:
        conn.execute(
            'UPDATE attendance SET status=? WHERE student_id=? AND date=?',
            (status, student_id, today)
        )
    else:
        conn.execute(
            'INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
            (student_id, today, status)
        )

    conn.commit()
    conn.close()

    return jsonify({'success': True})
