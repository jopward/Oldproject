from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# ----------------------------
# دالة مساعدة لفتح اتصال قاعدة البيانات
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------
# لوحة الحضور والغياب
# ----------------------------
@app.route('/')
def dashboard():
    conn = get_db_connection()
    today = date.today().isoformat()
    
    students = conn.execute('''
        SELECT s.id, s.student_name, 
               a.status 
        FROM students s
        LEFT JOIN attendance a 
        ON s.id = a.student_id AND a.date = ?
    ''', (today,)).fetchall()

    conn.close()
    return render_template('dashboard.html', students=students, today=today)

@app.route('/update_attendance', methods=['POST'])
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
def students():
    conn = get_db_connection()
    if request.method == 'POST':
        student_name = request.form['student_name']
        class_name = request.form['class_name']
        section = request.form['section']
        conn.execute('INSERT INTO students (student_name, class_name, section) VALUES (?, ?, ?)',
                     (student_name, class_name, section))
        conn.commit()
        return redirect(url_for('students'))
    students_list = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('students.html', students=students_list)

# ----------------------------
# صفحة المتابعة اليومية للطلاب
# ----------------------------
@app.route("/tracking")
def tracking():
    conn = get_db_connection()
    today = date.today().isoformat()

    # جلب الطلاب
    students = conn.execute("SELECT id, student_name, class_name, section FROM students").fetchall()

    # جلب سجلات اليوم
    rows = conn.execute("SELECT * FROM student_tracking WHERE date=?", (today,)).fetchall()
    records = {r['student_id']: r for r in rows}

    conn.close()
    return render_template("tracking.html", students=students, records=records, today=today)

@app.route("/update_tracking", methods=["POST"])
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
# صفحة التقارير: حضور + متابعة + ملاحظات
# ----------------------------
@app.route('/reports')
def reports():
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
def get_attendance_details(student_id, status):
    conn = get_db_connection()
    rows = conn.execute('SELECT date FROM attendance WHERE student_id=? AND status=?', (student_id, status)).fetchall()
    dates = [r['date'] for r in rows]
    conn.close()
    return jsonify(dates)

@app.route('/get_tracking_details/<int:student_id>/<field>')
def get_tracking_details(student_id, field):
    conn = get_db_connection()
    today = date.today().isoformat()
    rows = conn.execute(f'SELECT date FROM student_tracking WHERE student_id=? AND {field}=1', (student_id,)).fetchall()
    dates = [r['date'] for r in rows]
    conn.close()
    return jsonify(dates)

@app.route('/get_note_details/<int:student_id>')
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
