# auth.py
from flask import Blueprint, session, redirect, url_for, flash, render_template, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import OperationalError
from functools import wraps
from db import get_db_connection, User, Teacher, School
import logging

# إعداد logging بسيط
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

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
                logging.info(f"✅ سوبرأدمن '{username}' سجل الدخول")
                return redirect(url_for('attendance.dashboard'))

            # 2) معلم
            teacher = db_session.query(Teacher).filter_by(username=username).first()
            if teacher and check_password_hash(teacher.password, password):
                session['user'] = {'id': teacher.id, 'name': teacher.teacher_name}  # ✅ أغلق القاموس
                session['school_id'] = teacher.school_id
                session['role'] = 'teacher'
                logging.info(f"✅ المعلم '{username}' سجل الدخول")
                return redirect(url_for('attendance.dashboard'))

            # 3) مدير مدرسة (admin)
            school = db_session.query(School).filter_by(admin_username=username).first()
            if school and check_password_hash(school.admin_password, password):
                session['user'] = {'id': school.id, 'name': username}
                session['school_id'] = school.id
                session['role'] = 'admin'
                logging.info(f"✅ مدير المدرسة '{username}' سجل الدخول")
                return redirect(url_for('attendance.dashboard'))

            # فشل التوثيق
            flash('اسم المستخدم أو كلمة المرور خاطئة', 'danger')
            logging.warning(f"❌ فشل تسجيل الدخول للمستخدم '{username}'")
            return redirect(url_for('auth.login'))

        except OperationalError:
            flash("خطأ في الاتصال بقاعدة البيانات. تأكد من إعدادات الاتصال.", "danger")
            logging.error("❌ خطأ في الاتصال بقاعدة البيانات")
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"حدث خطأ داخلي: {str(e)}", "danger")
            logging.exception("❌ حدث خطأ داخلي أثناء تسجيل الدخول")
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
    user_name = session.get('user', {}).get('name', 'غير معروف')
    logging.info(f"✅ المستخدم '{user_name}' قام بتسجيل الخروج")
    session.clear()
    return redirect(url_for('auth.login'))
