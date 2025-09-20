from flask import render_template, request, redirect, url_for, flash
from db import get_db_connection
from auth import login_required

@login_required
def subjects_page():
    conn = get_db_connection()
    subjects = conn.execute("SELECT * FROM subjects").fetchall()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    subject_teachers = conn.execute("""
        SELECT st.id, s.id AS subject_id, s.subject_name, t.teacher_name
        FROM subject_teachers st
        JOIN subjects s ON st.subject_id = s.id
        JOIN teachers t ON st.teacher_id = t.id
        ORDER BY s.subject_name, t.teacher_name
    """).fetchall()
    conn.close()
    return render_template("subjects.html", subjects=subjects, teachers=teachers, subject_teachers=subject_teachers)

@login_required
def add_subject():
    if request.method == "POST":
        subject_name = request.form.get("subject_name")
        teacher_ids = request.form.getlist("teacher_ids")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject_name,))
            subject_id = cursor.lastrowid
            for tid in teacher_ids:
                cursor.execute("INSERT INTO subject_teachers (subject_id, teacher_id) VALUES (?, ?)", (subject_id, tid))
            conn.commit()
            flash("تمت إضافة المادة وربطها بالمعلمين بنجاح", "success")
        except Exception as e:
            conn.rollback()
            flash(f"حدث خطأ: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("subjects_page"))

@login_required
def edit_subject(subject_id):
    conn = get_db_connection()
    subject = conn.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if not subject:
        conn.close()
        flash("المادة غير موجودة", "danger")
        return redirect(url_for("subjects_page"))

    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    current_teacher_ids = [t['teacher_id'] for t in conn.execute(
        "SELECT teacher_id FROM subject_teachers WHERE subject_id = ?", (subject_id,)
    ).fetchall()]

    if request.method == "POST":
        subject_name = request.form.get("subject_name")
        teacher_ids = request.form.getlist("teacher_ids")

        if subject_name and teacher_ids:
            conn.execute("UPDATE subjects SET subject_name = ? WHERE id = ?", (subject_name, subject_id))
            conn.execute("DELETE FROM subject_teachers WHERE subject_id = ?", (subject_id,))
            for tid in teacher_ids:
                conn.execute("INSERT INTO subject_teachers (subject_id, teacher_id) VALUES (?, ?)", (subject_id, tid))
            conn.commit()
            conn.close()
            flash("تم تعديل المادة والمعلمين بنجاح", "success")
            return redirect(url_for("subjects_page"))
        else:
            flash("يرجى تعبئة جميع الحقول واختيار المعلمين", "warning")

    conn.close()
    return render_template("edit_subject.html", subject=subject, teachers=teachers, current_teacher_ids=current_teacher_ids)

@login_required
def delete_subject(subject_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM subject_teachers WHERE subject_id = ?", (subject_id,))
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        flash("تم حذف المادة بنجاح", "success")
    except Exception as e:
        conn.rollback()
        flash(f"حدث خطأ أثناء الحذف: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("subjects_page"))

@login_required
def remove_teacher_from_subject(st_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM subject_teachers WHERE id = ?", (st_id,))
        conn.commit()
        flash("تم إزالة المعلم من المادة", "success")
    except Exception as e:
        conn.rollback()
        flash(f"حدث خطأ أثناء الإزالة: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("subjects_page"))
