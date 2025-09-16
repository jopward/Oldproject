# tracking.py
from flask import render_template, request, jsonify
from datetime import date
from db import get_db_connection
from auth import login_required

def tracking_page():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute("SELECT * FROM students ORDER BY student_name").fetchall()
    rows = conn.execute("SELECT * FROM student_tracking WHERE date=?", (today,)).fetchall()
    records = {r['student_id']: r for r in rows}
    conn.close()
    return render_template("tracking.html", students=students, records=records, today=today)

def update_tracking():
    data = request.get_json()
    student_id = data.get("student_id")
    field = data.get("field")
    value = data.get("value")
    today = date.today().isoformat()
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM student_tracking WHERE student_id=? AND date=?", (student_id, today)).fetchone()
    if existing:
        conn.execute(f"UPDATE student_tracking SET {field}=? WHERE student_id=? AND date=?", (value, student_id, today))
    else:
        conn.execute(f"INSERT INTO student_tracking (student_id, date, {field}) VALUES (?, ?, ?)", (student_id, today, value))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

def update_note():
    data = request.get_json()
    student_id = data.get("student_id")
    note = data.get("note")
    today = date.today().isoformat()
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM student_tracking WHERE student_id=? AND date=?", (student_id, today)).fetchone()
    if existing:
        conn.execute("UPDATE student_tracking SET note=? WHERE student_id=? AND date=?", (note, student_id, today))
    else:
        conn.execute("INSERT INTO student_tracking (student_id, date, note) VALUES (?, ?, ?)", (student_id, today, note))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
