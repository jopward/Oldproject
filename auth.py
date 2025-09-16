# auth.py
from functools import wraps
from flask import session, redirect, url_for, flash, render_template, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# دوال العرض (ستُسجل لاحقاً في app.py)
def login_view():
    # GET or POST handled by app.add_url_rule -> view function will be called with request context
    from flask import request
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'admin' and password == '1234':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور خاطئة')
            return redirect(url_for('login'))
    return render_template('login.html')

def logout_view():
    session.pop('user', None)
    return redirect(url_for('login'))
