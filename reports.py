# reports.py
from flask import render_template, jsonify
from datetime import date
from db import get_db_connection
from auth import login_required

def reports_page():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute('''
        SELECT s.id, s.student_name, s.class_name, s.section,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count,
               t.homework, t.book, t.participation, t.misbehavior, t.note
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN student_tracking t ON s.id = t.student_id AND t.date=?
        GROUP BY s.id
    ''', (today,)).fetchall()
    classes = [row['class_name'] for row in conn.execute("SELECT DISTINCT class_name FROM students").fetchall()]
    sections = [row['section'] for row in conn.execute("SELECT DISTINCT section FROM students").fetchall()]
    conn.close()
    return render_template('reports.html', students=students, today=today, classes=classes, sections=sections)

def get_attendance_details(student_id, status):
    conn = get_db_connection()
    rows = conn.execute("SELECT date FROM attendance WHERE student_id=? AND status=?", (student_id, status)).fetchall()
    conn.close()
    dates = [r['date'] for r in rows]
    return jsonify(dates)

def get_tracking_details(student_id, field):
    conn = get_db_connection()
    rows = conn.execute(f"SELECT date FROM student_tracking WHERE student_id=? AND {field}=1", (student_id,)).fetchall()
    conn.close()
    dates = [r['date'] for r in rows]
    return jsonify(dates)
