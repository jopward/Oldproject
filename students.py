# students.py
from flask import render_template, request, redirect, url_for, jsonify, session, flash
from db import get_db_connection
from auth import login_required

@login_required
def students():
    conn = get_db_connection()
    school_id = session.get("school_id")

    if not school_id:
        flash("⚠️ لم يتم تحديد المدرسة")
        conn.close()
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
                conn.execute(
                    'INSERT INTO students (student_name, class_name, section, school_id) VALUES (?, ?, ?, ?)',
                    (name, class_name, section, school_id)
                )
        conn.commit()
        conn.close()
        return redirect(url_for('students'))

    # GET → إظهار طلاب المدرسة الحالية فقط
    students_list = conn.execute(
        'SELECT * FROM students WHERE school_id = ? ORDER BY student_name',
        (school_id,)
    ).fetchall()
    conn.close()
    return render_template('students.html', students=students_list)

@login_required
def edit_student(student_id):
    data = request.get_json()
    student_name = data.get('student_name')
    class_name = data.get('class_name')
    section = data.get('section')

    conn = get_db_connection()
    # تحديث بشرط school_id من السيشن (عشان ما يقدر مدير يعدل طلاب مدرسة تانية)
    conn.execute('''
        UPDATE students
        SET student_name=?, class_name=?, section=?
        WHERE id=? AND school_id=?
    ''', (student_name, class_name, section, student_id, session.get("school_id")))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@login_required
def delete_student(student_id):
    conn = get_db_connection()
    # حذف بشرط school_id كمان
    conn.execute('DELETE FROM students WHERE id=? AND school_id=?',
                 (student_id, session.get("school_id")))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
