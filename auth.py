# auth.py
from functools import wraps
from flask import session, redirect, url_for, flash, render_template, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import OperationalError

# استدعي دوال وـModels من db.py
from db import get_db_connection, User, Teacher, School

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_view():
    """
    تسجيل الدخول:
    - superadmin   -> جدول users.role='superadmin'
    - admin        -> جدول schools (admin_username)
    - teacher      -> جدول teachers (username)
    يستخدم ORM (SQLAlchemy) وليس SQL النصّي
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # افتح جلسة SQLAlchemy
        try:
            db_session = get_db_connection()
        except OperationalError as e:
            # خطأ اتصال بقاعدة البيانات (Neon / Postgres) — أعرض رسالة للمستخدم ولوج مفيد للـ logs
            flash("خطأ في الاتصال بقاعدة البيانات. تأكد من إعدادات الاتصال.", "danger")
            # اظهر الخطأ في الخادم (لا تعرضه للمستخدم في الإنتاج)
            raise

        try:
            # 1) سوبرأدمن عبر جدول users (ORM)
            superadmin = db_session.query(User).filter_by(username=username, role='superadmin').first()
            if superadmin and check_password_hash(superadmin.password, password):
                session['user'] = {'id': superadmin.id, 'name': username}
                session['role'] = 'superadmin'
                return redirect(url_for('dashboard'))

            # 2) معلم
            teacher = db_session.query(Teacher).filter_by(username=username).first()
            if teacher and check_password_hash(teacher.password, password):
                session['user'] = {'id': teacher.id, 'name': teacher.teacher_name}
                session['school_id'] = teacher.school_id
                session['role'] = 'teacher'
                return redirect(url_for('dashboard'))

            # 3) مدير مدرسة (admin) عبر جدول schools
            school = db_session.query(School).filter_by(admin_username=username).first()
            if school and check_password_hash(school.admin_password, password):
                session['user'] = {'id': school.id, 'name': username}
                session['school_id'] = school.id
                session['role'] = 'admin'
                return redirect(url_for('dashboard'))

            # فشل التوثيق
            flash('اسم المستخدم أو كلمة المرور خاطئة', 'danger')
            return redirect(url_for('login'))

        finally:
            # تأكد من غلق الجلسة دائماً
            db_session.close()

    # GET
    return render_template('login.html')

def logout_view():
    session.clear()
    return redirect(url_for('login'))
