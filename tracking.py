# tracking.py
from flask import render_template, request, jsonify, session, redirect, url_for
from datetime import date
from db import get_db_connection
from auth import login_required

@login_required
def tracking_page():
    school_id = session.get("school_id")
    if not school_id:
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    today = date.today().isoformat()

    # ✅ الطلاب من نفس المدرسة فقط
    students = conn.execute(
        "SELECT * FROM students WHERE school_id=? ORDER BY student_name",
        (school_id,)
    ).fetchall()

    # ✅ بيانات التتبع لليوم الحالي حسب المعلم أو لجميع المعلمين إذا كان المدير
    if session.get("role") == "teacher":
        teacher_id = session['user']['id']
        rows = conn.execute(
            "SELECT * FROM student_tracking WHERE date=? AND school_id=? AND teacher_id=?",
            (today, school_id, teacher_id)
        ).fetchall()
    else:
        # المدير يرى كل البيانات
        rows = conn.execute(
            "SELECT * FROM student_tracking WHERE date=? AND school_id=?",
            (today, school_id)
        ).fetchall()

    records = {r['student_id']: r for r in rows}

    # ✅ الصفوف والشعب لنفس المدرسة فقط
    classes = [row['class_name'] for row in conn.execute(
        "SELECT DISTINCT class_name FROM students WHERE school_id=?",
        (school_id,)
    ).fetchall()]
    sections = [row['section'] for row in conn.execute(
        "SELECT DISTINCT section FROM students WHERE school_id=?",
        (school_id,)
    ).fetchall()]

    conn.close()

    return render_template(
        "tracking.html",
        students=students,
        records=records,
        today=today,
        classes=classes,
        sections=sections
    )


@login_required
def update_tracking():
    school_id = session.get("school_id")
    if not school_id:
        return jsonify({"status": "error", "message": "مدرسة غير معروفة"})

    data = request.get_json()
    student_id = data.get("student_id")
    field = data.get("field")
    value = data.get("value")
    today = date.today().isoformat()

    teacher_id = session['user']['id'] if session.get("role") == "teacher" else None

    conn = get_db_connection()
    existing = conn.execute(
        "SELECT id FROM student_tracking WHERE student_id=? AND date=? AND school_id=?"
        + (" AND teacher_id=?" if teacher_id else ""),
        (student_id, today, school_id) + ((teacher_id,) if teacher_id else ())
    ).fetchone()

    if existing:
        conn.execute(
            f"UPDATE student_tracking SET {field}=? WHERE student_id=? AND date=? AND school_id=?"
            + (" AND teacher_id=?" if teacher_id else ""),
            (value, student_id, today, school_id) + ((teacher_id,) if teacher_id else ())
        )
    else:
        conn.execute(
            f"INSERT INTO student_tracking (student_id, date, {field}, school_id"
            + (", teacher_id" if teacher_id else "") + ") VALUES (?, ?, ?, ?"
            + (", ?" if teacher_id else "") + ")",
            (student_id, today, value, school_id) + ((teacher_id,) if teacher_id else ())
        )

    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@login_required
def update_note():
    school_id = session.get("school_id")
    if not school_id:
        return jsonify({"status": "error", "message": "مدرسة غير معروفة"})

    data = request.get_json()
    student_id = data.get("student_id")
    note = data.get("note")
    today = date.today().isoformat()

    teacher_id = session['user']['id'] if session.get("role") == "teacher" else None

    conn = get_db_connection()
    existing = conn.execute(
        "SELECT id FROM student_tracking WHERE student_id=? AND date=? AND school_id=?"
        + (" AND teacher_id=?" if teacher_id else ""),
        (student_id, today, school_id) + ((teacher_id,) if teacher_id else ())
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE student_tracking SET note=? WHERE student_id=? AND date=? AND school_id=?"
            + (" AND teacher_id=?" if teacher_id else ""),
            (note, student_id, today, school_id) + ((teacher_id,) if teacher_id else ())
        )
    else:
        conn.execute(
            "INSERT INTO student_tracking (student_id, date, note, school_id"
            + (", teacher_id" if teacher_id else "") + ") VALUES (?, ?, ?, ?"
            + (", ?" if teacher_id else "") + ")",
            (student_id, today, note, school_id) + ((teacher_id,) if teacher_id else ())
        )

    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
