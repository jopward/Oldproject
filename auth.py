from flask import Blueprint, session, redirect, url_for, flash, render_template, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import OperationalError
from functools import wraps
import logging
from db import get_db_connection, User, Teacher, School

# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ========================
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

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

            # سوبرأدمن
            superadmin = db_session.query(User).filter_by(username=username, role='superadmin').first()
            if superadmin and check_password_hash(superadmin.password, password):
                session['user'] = {'id': superadmin.id, 'name': username}
                session['role'] = 'superadmin'
                logging.info(f"✅ سوبر أدمن '{username}' سجل الدخول")
                return redirect(url_for('dashboard'))

            # معلم
            teacher = db_session.query(Teacher).filter_by(username=username).first()
            if teacher and check_password_hash(teacher.password, password):
                session['user'] = {'id': teacher.id, 'name':
