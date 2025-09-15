from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # ضروري للجلسة

# ----------------------------
# دالة مساعدة لفتح اتصال قاعدة البيانات
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------
# دالة حماية الصفحات
# ----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------
# صفحة تسجيل الدخول
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # تحقق من المستخدم (يمكن تعديل للتحقق من قاعدة بيانات حقيقية)
        if username == 'admin' and password == '1234':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور خاطئة')
            return redirect(url_for('login'))

    return render_template('login.html')

# ----------------------------
# تسجيل الخروج
# ----------------------------
@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ----------------------------
# لوحة الحضور والغياب
# ----------------------------
@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute('''
        SELECT s.id, s.student_name, a.status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id AND a.date = ?
    ''', (today,)).fetchall()
    conn.close()
    return render_template('dashboard.html', students=students, today=today)

@app.route('/update_attendance', methods=['POST'])
@login_required
def update_attendance():
    data = request.get_json()
    student_id = data['student_id']
    status = data['status']
    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM attendance WHERE student_id=? AND date=?', (student_id, today)).fetchone()
    if existing:
        conn.execute('UPDATE attendance SET status=? WHERE student_id=? AND date=?', (status, student_id, today))
    else:
        conn.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, today, status))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ----------------------------
# صفحة الطلاب
# ----------------------------
@app.route('/students', methods=['GET', 'POST'])
@login_required
def students_page():
    conn = get_db_connection()
    if request.method == 'POST':
        student_name = request.form['student_name']
        class_name = request.form['class_name']
        section = request.form['section']
        conn.execute('INSERT INTO students (student_name, class_name, section) VALUES (?, ?, ?)',
                     (student_name, class_name, section))
        conn.commit()
        return redirect(url_for('students_page'))
    students_list = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('students.html', students=students_list)

# ----------------------------
# صفحة المتابعة اليومية للطلاب
# ----------------------------
@app.route("/tracking")
@login_required
def tracking_page():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute("SELECT * FROM students").fetchall()
    rows = conn.execute("SELECT * FROM student_tracking WHERE date=?", (today,)).fetchall()
    records = {r['student_id']: r for r in rows}
    conn.close()
    return render_template("tracking.html", students=students, records=records, today=today)

@app.route("/update_tracking", methods=["POST"])
@login_required
def update_tracking():
    data = request.get_json()
    student_id = data.get("student_id")
    field = data.get("field")
    value = data.get("value")
    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM student_tracking WHERE student_id=? AND date=?", (student_id, today)).fetchone()

    if existing:
        conn.execute(f"UPDATE student_tracking SET {field}=? WHERE student_id=? AND date=?", (value, student_id, today))
    else:
        conn.execute(f"INSERT INTO student_tracking (student_id, date, {field}) VALUES (?, ?, ?)", (student_id, today, value))

    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/update_note", methods=["POST"])
@login_required
def update_note():
    data = request.get_json()
    student_id = data.get("student_id")
    note = data.get("note")
    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM student_tracking WHERE student_id=? AND date=?", (student_id, today)).fetchone()

    if existing:
        conn.execute("UPDATE student_tracking SET note=? WHERE student_id=? AND date=?", (note, student_id, today))
    else:
        conn.execute("INSERT INTO student_tracking (student_id, date, note) VALUES (?, ?, ?)", (student_id, today, note))

    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# ----------------------------
# صفحة التقارير
# ----------------------------
@app.route('/reports')
@login_required
def reports_page():
    conn = get_db_connection()
    today = date.today().isoformat()
    students = conn.execute('''
        SELECT s.id, s.student_name,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late_count,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent_count,
               t.homework, t.book, t.participation, t.misbehavior, t.note
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN student_tracking t ON s.id = t.student_id AND t.date=?
        GROUP BY s.id
    ''', (today,)).fetchall()
    conn.close()
    return render_template('reports.html', students=students, today=today)

@app.route('/get_attendance_details/<int:student_id>/<status>')
@login_required
def get_attendance_details(student_id, status):
    conn = get_db_connection()
    rows = conn.execute('SELECT date FROM attendance WHERE student_id=? AND status=?', (student_id, status)).fetchall()
    dates = [r['date'] for r in rows]
    conn.close()
    return jsonify(dates)

@app.route('/get_tracking_details/<int:student_id>/<field>')
@login_required
def get_tracking_details(student_id, field):
    conn = get_db_connection()
    rows = conn.execute(f'SELECT date FROM student_tracking WHERE student_id=? AND {field}=1', (student_id,)).fetchall()
    dates = [r['date'] for r in rows]
    conn.close()
    return jsonify(dates)

@app.route('/get_note_details/<int:student_id>')
@login_required
def get_note_details(student_id):
    conn = get_db_connection()
    today = date.today().isoformat()
    row = conn.execute('SELECT note FROM student_tracking WHERE student_id=? AND date=?', (student_id, today)).fetchone()
    note = row['note'] if row else ""
    conn.close()
    return jsonify({"note": note})

# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
