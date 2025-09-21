# reports.py
from flask import render_template, jsonify, session, redirect, url_for
from datetime import date
from db import get_db_connection
from auth import login_required

@login_required
def reports_page():
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    if not school_id:
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    today = date.today().isoformat()
    
    # ✅ جلب الطلاب من نفس المدرسة
    # ✅ إذا كان المستخدم معلم، نحصر الحضور والملاحظات فقط له
    students = conn.execute('''
        SELECT s.id, s.student_name, s.class_name, s.section,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count,
               SUM(CASE WHEN t.teacher_id=? THEN t.homework ELSE 0 END) AS homework,
               SUM(CASE WHEN t.teacher_id=? THEN t.book ELSE 0 END) AS book,
               SUM(CASE WHEN t.teacher_id=? THEN t.participation ELSE 0 END) AS participation,
               SUM(CASE WHEN t.teacher_id=? THEN t.misbehavior ELSE 0 END) AS misbehavior,
               SUM(CASE WHEN t.teacher_id=? THEN t.note ELSE 0 END) AS note
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND (? IS NULL OR a.teacher_id=?)
        LEFT JOIN student_tracking t ON s.id = t.student_id AND t.date=? AND (? IS NULL OR t.teacher_id=?)
        WHERE s.school_id=?
        GROUP BY s.id
    ''', (teacher_id, teacher_id, teacher_id, teacher_id, teacher_id, teacher_id, teacher_id, today, teacher_id, teacher_id, school_id)).fetchall()

    # الصفوف والشعب
    classes = [row['class_name'] for row in conn.execute(
        "SELECT DISTINCT class_name FROM students WHERE school_id=?",
        (school_id,)
    ).fetchall()]

    sections = [row['section'] for row in conn.execute(
        "SELECT DISTINCT section FROM students WHERE school_id=?",
        (school_id,)
    ).fetchall()]

    conn.close()
    return render_template('reports.html', students=students, today=today, classes=classes, sections=sections)


@login_required
def student_detail(student_id):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    conn = get_db_connection()

    student = conn.execute('''
        SELECT s.id, s.student_name, s.class_name, s.section, sch.school_name,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count
        FROM students s
        LEFT JOIN schools sch ON s.school_id = sch.id
        LEFT JOIN attendance a ON s.id = a.student_id AND (? IS NULL OR a.teacher_id=?)
        WHERE s.id=? AND s.school_id=?
        GROUP BY s.id
    ''', (teacher_id, teacher_id, student_id, school_id)).fetchone()

    if not student:
        conn.close()
        return redirect(url_for("reports_page"))

    # جلب تفاصيل التتبع لكل طالب مع تصفية حسب المعلم إذا كان موجود
    rows = conn.execute('''
        SELECT sub.subject_name, st.tracking_date, st.homework, st.book,
               st.participation, st.misbehavior, st.note,
               COALESCE(a.status, 'غير محدد') AS attendance_status,
               t.teacher_name
        FROM student_tracking st
        LEFT JOIN class_subjects cs ON cs.class_id = st.class_id AND cs.teacher_id = st.teacher_id
        LEFT JOIN subjects sub ON cs.subject_id = sub.id
        LEFT JOIN teachers t ON st.teacher_id = t.id
        LEFT JOIN attendance a ON a.student_id = st.student_id AND a.date=st.tracking_date AND (? IS NULL OR a.teacher_id=?)
        WHERE st.student_id=? AND (? IS NULL OR st.teacher_id=?)
        ORDER BY sub.subject_name, st.tracking_date DESC
    ''', (teacher_id, teacher_id, student_id, teacher_id, teacher_id)).fetchall()
    
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
    
    conn.close()
    return render_template('student_detail.html', school_name=student['school_name'], student=student, tracking_data=tracking_data)


@login_required
def get_attendance_details(student_id, status):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT date FROM attendance WHERE student_id=? AND status=? AND school_id=? AND (? IS NULL OR teacher_id=?)",
        (student_id, status, school_id, teacher_id, teacher_id)
    ).fetchall()
    conn.close()
    dates = [r['date'] for r in rows]
    return jsonify(dates)


@login_required
def get_tracking_details(student_id, field):
    school_id = session.get("school_id")
    teacher_id = session.get("user", {}).get("id") if session.get("role") == "teacher" else None
    conn = get_db_connection()
    rows = conn.execute(
        f"SELECT date FROM student_tracking WHERE student_id=? AND {field}=1 AND school_id=? AND (? IS NULL OR teacher_id=?)",
        (student_id, school_id, teacher_id, teacher_id)
    ).fetchall()
    conn.close()
    dates = [r['date'] for r in rows]
    return jsonify(dates)
