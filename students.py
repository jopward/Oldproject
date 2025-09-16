# students.py
from flask import render_template, request, redirect, url_for, jsonify
from db import get_db_connection
from auth import login_required

def students():
    conn = get_db_connection()
    if request.method == 'POST':
        # الآن الحقل في القالب اسمه student_names (يمكن أن يكون عدة أسطر)
        student_names = request.form.get('student_names') or request.form.get('student_name', '')
        class_name = request.form.get('class_name', '')
        section = request.form.get('section', '')
        # دعم إدخال أسماء متعددة (كل سطر اسم أو أكثر)
        for name in student_names.splitlines():
            name = name.strip()
            if name:
                conn.execute('INSERT INTO students (student_name, class_name, section) VALUES (?, ?, ?)',
                             (name, class_name, section))
        conn.commit()
        conn.close()
        return redirect(url_for('students'))
    # GET
    students_list = conn.execute('SELECT * FROM students ORDER BY student_name').fetchall()
    conn.close()
    return render_template('students.html', students=students_list)

def edit_student(student_id):
    data = request.get_json()
    student_name = data.get('student_name')
    class_name = data.get('class_name')
    section = data.get('section')
    conn = get_db_connection()
    conn.execute('UPDATE students SET student_name=?, class_name=?, section=? WHERE id=?',
                 (student_name, class_name, section, student_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

def delete_student(student_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id=?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
