# auth.py
from flask import Blueprint, session, redirect, url_for, flash, render_template, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import OperationalError
from functools import wraps
from db import get_db_connection, User, Teacher, School

# --- إنشاء الـ Blueprint ---
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- Decorator للتحقق من تسجيل الدخول ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- صفحة تسجيل الدخول ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("⚠️ الرجاء تعبئة اسم المستخدم وكلمة المرور.", "warning")
            return redirect(url_for('auth.login'))

        db_session = None
        try:
            db_session = get_db_connection()

            # 1) سوبرأدمن
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

            # 3) مدير مدرسة (admin)
            school = db_session.query(School).filter_by(admin_username=username).first()
            if school and check_password_hash(school.admin_password, password):
                session['user'] = {'id': school.id, 'name': username}
                session['school_id'] = school.id
                session['role'] = 'admin'
                return redirect(url_for('dashboard'))

            # فشل التوثيق
            flash('اسم المستخدم أو كلمة المرور خاطئة', 'danger')
            return redirect(url_for('auth.login'))

        except OperationalError:
            flash("خطأ في الاتصال بقاعدة البيانات. تأكد من إعدادات الاتصال.", "danger")
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"حدث خطأ داخلي: {str(e)}", "danger")
            return redirect(url_for('auth.login'))

        finally:
            if db_session:
                try:
                    db_session.close()
                except:
                    pass

    # GET
    return render_template('login.html')

# --- صفحة تسجيل الخروج ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
