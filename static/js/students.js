from flask import request, jsonify, render_template, session
import db

# 📌 صفحة واجهة الطلاب (HTML + JS)
def students():
    return render_template("students.html")

# 📌 جلب الطلاب (مع البحث + الصف والشعبة)
def get_students():
    search = request.args.get("search", "").strip()
    conn = db.get_db_connection()

    if search:
        rows = conn.execute("""
            SELECT s.id, s.student_name, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.school_id = ? AND s.student_name LIKE ?
            ORDER BY s.id DESC
        """, (session["school_id"], f"%{search}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT s.id, s.student_name, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.school_id = ?
            ORDER BY s.id DESC
        """, (session["school_id"],)).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

# 📌 إضافة طالب
def add_student():
    data = request.get_json()
    name = data.get("student_name")
    class_name = data.get("class_name")
    section = data.get("section")

    if not name or not class_name or not section:
        return jsonify({"error": "⚠️ يرجى إدخال جميع البيانات"}), 400

    conn = db.get_db_connection()

    # التحقق من وجود الصف والشعبة
    class_row = conn.execute("""
        SELECT id FROM teacher_classes
        WHERE class_name = ? AND section = ? AND school_id = ?
    """, (class_name, section, session["school_id"])).fetchone()

    if class_row:
        class_id = class_row["id"]
    else:
        cur = conn.execute("""
            INSERT INTO teacher_classes (class_name, section, period, school_id)
            VALUES (?, ?, 'صباحي', ?)
        """, (class_name, section, session["school_id"]))
        class_id = cur.lastrowid

    conn.execute("""
        INSERT INTO students (student_name, class_id, school_id)
        VALUES (?, ?, ?)
    """, (name, class_id, session["school_id"]))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

# 📌 تعديل طالب
def edit_student(student_id):
    data = request.get_json()
    new_name = data.get("student_name")
    new_class = data.get("class_name")
    new_section = data.get("section")

    if not new_name or not new_class or not new_section:
        return jsonify({"error": "⚠️ يرجى إدخال جميع البيانات"}), 400

    conn = db.get_db_connection()

    # التحقق من وجود الصف والشعبة الجديدة
    class_row = conn.execute("""
        SELECT id FROM teacher_classes
        WHERE class_name = ? AND section = ? AND school_id = ?
    """, (new_class, new_section, session["school_id"])).fetchone()

    if class_row:
        class_id = class_row["id"]
    else:
        cur = conn.execute("""
            INSERT INTO teacher_classes (class_name, section, period, school_id)
            VALUES (?, ?, 'صباحي', ?)
        """, (new_class, new_section, session["school_id"]))
        class_id = cur.lastrowid

    conn.execute("""
        UPDATE students
        SET student_name = ?, class_id = ?
        WHERE id = ?
    """, (new_name, class_id, student_id))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

# 📌 حذف طالب
def delete_student(student_id):
    conn = db.get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})
