# students.py
from flask import render_template, request, redirect, url_for, jsonify, session, flash
from db import SessionLocal  # ✅ استدعاء جلسة SQLAlchemy
from auth import login_required

@login_required
def students():
    db_session = SessionLocal()
    school_id = session.get("school_id")

    if not school_id:
        flash("⚠️ لم يتم تحديد المدرسة")
        db_session.close()
        return redirect(url_for("dashboard"))

    if request.method == 'POST':
        # الحقل في القالب اسمه student_names (يمكن أن يكون عدة أسطر)
        student_names = request.form.get('student_names') or request.form.get('student_name', '')
        class_name = request.form.get('class_name', '')
        section = request.form.get('section', '')

        # دعم إدخال أسماء متعددة (كل سطر اسم أو أكثر)
        for name in student_names.splitlines():
            name = name.strip()
            if name:
                db_session.execute(
                    'INSERT INTO students (student_name, class_name, section, school_id) '
                    'VALUES (:student_name, :class_name, :section, :school_id)',
                    {"student_name": name, "class_name": class_name, "section": section, "school_id": school_id}
                )
        db_session.commit()
        db_session.close()
        return redirect(url_for('students'))

    # GET → إظهار طلاب المدرسة الحالية فقط
    students_list = db_session.execute(
        'SELECT * FROM students WHERE school_id = :school_id ORDER BY student_name',
        {"school_id": school_id}
    ).fetchall()
    db_session.close()
    return render_template('students.html', students=students_list)

@login_required
def edit_student(student_id):
    data = request.get_json()
    student_name = data.get('student_name')
    class_name = data.get('class_name')
    section = data.get('section')

    db_session = SessionLocal()
    # تحديث بشرط school_id من السيشن
    db_session.execute('''
        UPDATE students
        SET student_name=:student_name, class_name=:class_name, section=:section
        WHERE id=:student_id AND school_id=:school_id
    ''', {
        "student_name": student_name,
        "class_name": class_name,
        "section": section,
        "student_id": student_id,
        "school_id": session.get("school_id")
    })
    db_session.commit()
    db_session.close()
    return jsonify({'success': True})

@login_required
def delete_student(student_id):
    db_session = SessionLocal()
    # حذف بشرط school_id كمان
    db_session.execute('DELETE FROM students WHERE id=:student_id AND school_id=:school_id',
                       {"student_id": student_id, "school_id": session.get("school_id")})
    db_session.commit()
    db_session.close()
    return jsonify({'success': True})
