# tracking.py
from flask import render_template, request, jsonify, session, redirect, url_for
from datetime import date
from db import SessionLocal  # SQLAlchemy session
from auth import login_required

@login_required
def tracking_page():
    school_id = session.get("school_id")
    if not school_id:
        return redirect(url_for("dashboard"))

    db_session = SessionLocal()
    today = date.today().isoformat()

    # الطلاب من نفس المدرسة
    students = db_session.execute(
        "SELECT * FROM students WHERE school_id=:school_id ORDER BY student_name",
        {"school_id": school_id}
    ).fetchall()

    # بيانات التتبع لليوم الحالي حسب المعلم أو لكل المعلمين إذا كان المدير
    if session.get("role") == "teacher":
        teacher_id = session['user']['id']
        rows = db_session.execute(
            "SELECT * FROM student_tracking WHERE date=:today AND school_id=:school_id AND teacher_id=:teacher_id",
            {"today": today, "school_id": school_id, "teacher_id": teacher_id}
        ).fetchall()
    else:
        rows = db_session.execute(
            "SELECT * FROM student_tracking WHERE date=:today AND school_id=:school_id",
            {"today": today, "school_id": school_id}
        ).fetchall()

    records = {r['student_id']: r for r in rows}

    # الصفوف والشعب لنفس المدرسة فقط
    classes = [row['class_name'] for row in db_session.execute(
        "SELECT DISTINCT class_name FROM students WHERE school_id=:school_id",
        {"school_id": school_id}
    ).fetchall()]
    sections = [row['section'] for row in db_session.execute(
        "SELECT DISTINCT section FROM students WHERE school_id=:school_id",
        {"school_id": school_id}
    ).fetchall()]

    db_session.close()

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

    db_session = SessionLocal()

    existing = db_session.execute(
        "SELECT id FROM student_tracking WHERE student_id=:student_id AND date=:today AND school_id=:school_id"
        + (" AND teacher_id=:teacher_id" if teacher_id else ""),
        {"student_id": student_id, "today": today, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
    ).fetchone()

    if existing:
        db_session.execute(
            f"UPDATE student_tracking SET {field}=:value WHERE student_id=:student_id AND date=:today AND school_id=:school_id"
            + (" AND teacher_id=:teacher_id" if teacher_id else ""),
            {"value": value, "student_id": student_id, "today": today, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
        )
    else:
        db_session.execute(
            f"INSERT INTO student_tracking (student_id, date, {field}, school_id"
            + (", teacher_id" if teacher_id else "") + ") VALUES (:student_id, :today, :value, :school_id"
            + (", :teacher_id" if teacher_id else "") + ")",
            {"student_id": student_id, "today": today, "value": value, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
        )

    db_session.commit()
    db_session.close()
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

    db_session = SessionLocal()

    existing = db_session.execute(
        "SELECT id FROM student_tracking WHERE student_id=:student_id AND date=:today AND school_id=:school_id"
        + (" AND teacher_id=:teacher_id" if teacher_id else ""),
        {"student_id": student_id, "today": today, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
    ).fetchone()

    if existing:
        db_session.execute(
            "UPDATE student_tracking SET note=:note WHERE student_id=:student_id AND date=:today AND school_id=:school_id"
            + (" AND teacher_id=:teacher_id" if teacher_id else ""),
            {"note": note, "student_id": student_id, "today": today, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
        )
    else:
        db_session.execute(
            "INSERT INTO student_tracking (student_id, date, note, school_id"
            + (", teacher_id" if teacher_id else "") + ") VALUES (:student_id, :today, :note, :school_id"
            + (", :teacher_id" if teacher_id else "") + ")",
            {"student_id": student_id, "today": today, "note": note, "school_id": school_id, **({"teacher_id": teacher_id} if teacher_id else {})}
        )

    db_session.commit()
    db_session.close()
    return jsonify({"status": "success"})
