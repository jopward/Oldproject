# attendance.py
from flask import render_template, request, jsonify
from datetime import date
from auth import login_required
from db import get_db_connection

def dashboard():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute('''
        SELECT s.id, s.student_name, a.status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id AND a.date = ?
        ORDER BY s.student_name
    ''', (today,)).fetchall()
    conn.close()
    return render_template('dashboard.html', students=students, today=today)

def update_attendance():
    data = request.get_json()
    student_id = data['student_id']
    status = data['status']
    today = date.today().isoformat()
    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM attendance WHERE student_id=? AND date=?', (student_id, today)).fetchone()
    if existing:
        conn.execute('UPDATE attendance SET status=? WHERE student_id=? AND date=?', (status, student_id, today))
    else:
        conn.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, today, status))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
