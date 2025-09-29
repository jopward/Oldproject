# reports.py
from flask import render_template, jsonify, session, redirect, url_for
from datetime import date
from db import SessionLocal  # استخدام SQLAlchemy
from auth import login_required
from sqlalchemy import text  # ✅ إضافة text

@login_required
def reports_page():
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    if not school_id:
        return redirect(url_for("dashboard"))

    db_session = SessionLocal()
    today = date.today().isoformat()

    students = db_session.execute(
        text('''
        SELECT s.id, s.student_name, s.class_name, s.section,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count,
               SUM(CASE WHEN t.teacher_id=:teacher_id THEN t.homework ELSE 0 END) AS homework,
               SUM(CASE WHEN t.teacher_id=:teacher_id THEN t.book ELSE 0 END) AS book,
               SUM(CASE WHEN t.teacher_id=:teacher_id THEN t.participation ELSE 0 END) AS participation,
               SUM(CASE WHEN t.teacher_id=:teacher_id THEN t.misbehavior ELSE 0 END) AS misbehavior,
               SUM(CASE WHEN t.teacher_id=:teacher_id THEN t.note ELSE 0 END) AS note
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND (:teacher_id IS NULL OR a.teacher_id=:teacher_id)
        LEFT JOIN student_tracking t ON s.id = t.student_id AND t.tracking_date=:today AND (:teacher_id IS NULL OR t.teacher_id=:teacher_id)
        WHERE s.school_id=:school_id
        GROUP BY s.id
        '''), {"teacher_id": teacher_id, "today": today, "school_id": school_id}
    ).fetchall()

    # الصفوف والشعب
    classes = [row['class_name'] for row in db_session.execute(
        text("SELECT DISTINCT class_name FROM students WHERE school_id=:school_id"),
        {"school_id": school_id}
    ).fetchall()]

    sections = [row['section'] for row in db_session.execute(
        text("SELECT DISTINCT section FROM students WHERE school_id=:school_id"),
        {"school_id": school_id}
    ).fetchall()]

    db_session.close()
    return render_template('reports.html', students=students, today=today, classes=classes, sections=sections)


@login_required
def student_detail(student_id):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    db_session = SessionLocal()

    student = db_session.execute(
        text('''
        SELECT s.id, s.student_name, s.class_name, s.section, sch.school_name,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count
        FROM students s
        LEFT JOIN schools sch ON s.school_id = sch.id
        LEFT JOIN attendance a ON s.id = a.student_id AND (:teacher_id IS NULL OR a.teacher_id=:teacher_id)
        WHERE s.id=:student_id AND s.school_id=:school_id
        GROUP BY s.id, sch.school_name
        '''), {"teacher_id": teacher_id, "student_id": student_id, "school_id": school_id}
    ).fetchone()

    if not student:
        db_session.close()
        return redirect(url_for("reports_page"))

    # تفاصيل التتبع لكل طالب
    rows = db_session.execute(
        text('''
        SELECT sub.subject_name, st.tracking_date, st.homework, st.book,
               st.participation, st.misbehavior, st.note,
               COALESCE(a.status, 'غير محدد') AS attendance_status,
               t.teacher_name
        FROM student_tracking st
        LEFT JOIN class_subjects cs ON cs.class_id = st.class_id AND cs.teacher_id = st.teacher_id
        LEFT JOIN subjects sub ON cs.subject_id = sub.id
        LEFT JOIN teachers t ON st.teacher_id = t.id
        LEFT JOIN attendance a ON a.student_id = st.student_id AND a.date = st.tracking_date AND (:teacher_id IS NULL OR a.teacher_id=:teacher_id)
        WHERE st.student_id=:student_id AND (:teacher_id IS NULL OR st.teacher_id=:teacher_id)
        ORDER BY sub.subject_name, st.tracking_date DESC
        '''), {"teacher_id": teacher_id, "student_id": student_id}
    ).fetchall()

    tracking_data = {}
    for r in rows:
        subject = r['subject_name']
        if subject not in tracking_data:
            tracking_data[subject] = []
        tracking_data[subject].append({
            'tracking_date': r['tracking_date'],
            'homework': r['homework'],
            'book': r['book'],
            'participation': r['participation'],
            'misbehavior': r['misbehavior'],
            'note': r['note'],
            'attendance_status': r['attendance_status'],
            'teacher_name': r['teacher_name']
        })

    db_session.close()
    return render_template('student_detail.html', school_name=student['school_name'], student=student, tracking_data=tracking_data)


@login_required
def get_attendance_details(student_id, status):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    db_session = SessionLocal()

    rows = db_session.execute(
        text("SELECT date FROM attendance WHERE student_id=:student_id AND status=:status AND school_id=:school_id AND (:teacher_id IS NULL OR teacher_id=:teacher_id)"),
        {"student_id": student_id, "status": status, "school_id": school_id, "teacher_id": teacher_id}
    ).fetchall()

    db_session.close()
    dates = [r['date'] for r in rows]
    return jsonify(dates)


@login_required
def get_tracking_details(student_id, field):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    db_session = SessionLocal()

    # ✅ استخدام text للـ SQL مع f-string
    rows = db_session.execute(
        text(f"SELECT tracking_date FROM student_tracking WHERE student_id=:student_id AND {field}=1 AND school_id=:school_id AND (:teacher_id IS NULL OR teacher_id=:teacher_id)"),
        {"student_id": student_id, "school_id": school_id, "teacher_id": teacher_id}
    ).fetchall()

    db_session.close()
    dates = [r['tracking_date'] for r in rows]
    return jsonify(dates)
