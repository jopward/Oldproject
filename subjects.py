# subjects.py
from flask import render_template, request, redirect, url_for, flash, session
from db import SessionLocal  # ✅ استدعاء جلسة SQLAlchemy
from auth import login_required

@login_required
def subjects_page():
    school_id = session.get("school_id")
    db_session = SessionLocal()

    # جلب المواد
    subjects = db_session.execute("SELECT * FROM subjects").fetchall()

    # جلب المعلمين ضمن المدرسة الحالية فقط
    teachers = db_session.execute(
        "SELECT * FROM teachers WHERE school_id = :school_id",
        {"school_id": school_id}
    ).fetchall()

    # جلب ربط المواد بالمعلمين ضمن المدرسة
    subject_teachers = db_session.execute("""
        SELECT st.id, s.id AS subject_id, s.subject_name, t.teacher_name
        FROM subject_teachers st
        JOIN subjects s ON st.subject_id = s.id
        JOIN teachers t ON st.teacher_id = t.id
        WHERE t.school_id = :school_id
        ORDER BY s.subject_name, t.teacher_name
    """, {"school_id": school_id}).fetchall()

    db_session.close()
    return render_template("subjects.html", subjects=subjects, teachers=teachers, subject_teachers=subject_teachers)


@login_required
def add_subject():
    if request.method == "POST":
        school_id = session.get("school_id")
        subject_name = request.form.get("subject_name")
        teacher_ids = request.form.getlist("teacher_ids")
        db_session = SessionLocal()
        try:
            result = db_session.execute(
                "INSERT INTO subjects (subject_name) VALUES (:subject_name) RETURNING id",
                {"subject_name": subject_name}
            )
            subject_id = result.fetchone()[0]

            for tid in teacher_ids:
                teacher = db_session.execute(
                    "SELECT id FROM teachers WHERE id = :teacher_id AND school_id = :school_id",
                    {"teacher_id": tid, "school_id": school_id}
                ).fetchone()
                if teacher:
                    db_session.execute(
                        "INSERT INTO subject_teachers (subject_id, teacher_id) VALUES (:subject_id, :teacher_id)",
                        {"subject_id": subject_id, "teacher_id": tid}
                    )
            db_session.commit()
            flash("تمت إضافة المادة وربطها بالمعلمين بنجاح", "success")
        except Exception as e:
            db_session.rollback()
            flash(f"حدث خطأ: {str(e)}", "danger")
        finally:
            db_session.close()
        return redirect(url_for("subjects_page"))


@login_required
def edit_subject(subject_id):
    school_id = session.get("school_id")
    db_session = SessionLocal()

    subject = db_session.execute(
        "SELECT * FROM subjects WHERE id = :subject_id",
        {"subject_id": subject_id}
    ).fetchone()

    if not subject:
        db_session.close()
        flash("المادة غير موجودة", "danger")
        return redirect(url_for("subjects_page"))

    teachers = db_session.execute(
        "SELECT * FROM teachers WHERE school_id = :school_id",
        {"school_id": school_id}
    ).fetchall()

    current_teacher_ids = [t['teacher_id'] for t in db_session.execute(
        "SELECT teacher_id FROM subject_teachers WHERE subject_id = :subject_id",
        {"subject_id": subject_id}
    ).fetchall()]

    if request.method == "POST":
        subject_name = request.form.get("subject_name")
        teacher_ids = request.form.getlist("teacher_ids")

        if subject_name and teacher_ids:
            db_session.execute(
                "UPDATE subjects SET subject_name = :subject_name WHERE id = :subject_id",
                {"subject_name": subject_name, "subject_id": subject_id}
            )
            db_session.execute(
                "DELETE FROM subject_teachers WHERE subject_id = :subject_id",
                {"subject_id": subject_id}
            )
            for tid in teacher_ids:
                teacher = db_session.execute(
                    "SELECT id FROM teachers WHERE id = :teacher_id AND school_id = :school_id",
                    {"teacher_id": tid, "school_id": school_id}
                ).fetchone()
                if teacher:
                    db_session.execute(
                        "INSERT INTO subject_teachers (subject_id, teacher_id) VALUES (:subject_id, :teacher_id)",
                        {"subject_id": subject_id, "teacher_id": tid}
                    )
            db_session.commit()
            db_session.close()
            flash("تم تعديل المادة والمعلمين بنجاح", "success")
            return redirect(url_for("subjects_page"))
        else:
            flash("يرجى تعبئة جميع الحقول واختيار المعلمين", "warning")

    db_session.close()
    return render_template("edit_subject.html", subject=subject, teachers=teachers, current_teacher_ids=current_teacher_ids)


@login_required
def delete_subject(subject_id):
    db_session = SessionLocal()
    try:
        db_session.execute(
            "DELETE FROM subject_teachers WHERE subject_id = :subject_id",
            {"subject_id": subject_id}
        )
        db_session.execute(
            "DELETE FROM subjects WHERE id = :subject_id",
            {"subject_id": subject_id}
        )
        db_session.commit()
        flash("تم حذف المادة بنجاح", "success")
    except Exception as e:
        db_session.rollback()
        flash(f"حدث خطأ أثناء الحذف: {str(e)}", "danger")
    finally:
        db_session.close()
    return redirect(url_for("subjects_page"))


@login_required
def remove_teacher_from_subject(st_id):
    db_session = SessionLocal()
    try:
        db_session.execute(
            "DELETE FROM subject_teachers WHERE id = :st_id",
            {"st_id": st_id}
        )
        db_session.commit()
        flash("تم إزالة المعلم من المادة", "success")
    except Exception as e:
        db_session.rollback()
        flash(f"حدث خطأ أثناء الإزالة: {str(e)}", "danger")
    finally:
        db_session.close()
    return redirect(url_for("subjects_page"))
