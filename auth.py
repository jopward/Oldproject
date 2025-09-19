# auth.py
from functools import wraps
from flask import session, redirect, url_for, flash, render_template, request
from db import get_db_connection
from werkzeug.security import check_password_hash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_view():
    """
    تسجيل الدخول: يتحقق من المدارس والمعلمين
    ويحدد دور المستخدم (admin أو teacher) ويحفظ school_id.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db_connection()

        # تحقق أولاً من المدرسين (Teachers)
        teacher = conn.execute(
            "SELECT * FROM teachers WHERE username = ?", (username,)
        ).fetchone()

        if teacher and check_password_hash(teacher['password'], password):
            # حفظ بيانات المعلم في الجلسة
            session['user'] = {'id': teacher['id'], 'name': teacher['teacher_name']}
            session['school_id'] = teacher['school_id']
            session['role'] = 'teacher'
            conn.close()
            return redirect(url_for('dashboard'))

        # تحقق من المدراء (Admins) في جدول schools
        school = conn.execute(
            "SELECT * FROM schools WHERE admin_username = ?", (username,)
        ).fetchone()

        if school and check_password_hash(school['admin_password'], password):
            session['user'] = {'id': school['id'], 'name': username}
            session['school_id'] = school['id']
            session['role'] = 'admin'
            conn.close()
            return redirect(url_for('dashboard'))

        conn.close()
        flash('اسم المستخدم أو كلمة المرور خاطئة')
        return redirect(url_for('login'))

    # GET
    return render_template('login.html')

def logout_view():
    session.clear()
    return redirect(url_for('login'))
