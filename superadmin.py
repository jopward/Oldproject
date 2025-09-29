# superadmin.py
from flask import render_template, request, redirect, url_for, flash
from db import SessionLocal  # SQLAlchemy session
from auth import login_required

@login_required
def superadmin_schools():
    db_session = SessionLocal()
    schools = db_session.execute("""
        SELECT s.id as school_id, s.school_name, s.admin_username as school_admin,
            (SELECT COUNT(*) FROM teachers t WHERE t.school_id = s.id) as teachers,
            (SELECT COUNT(*) FROM students st WHERE st.school_id = s.id) as students
        FROM schools s
    """).fetchall()
    db_session.close()
    return render_template("superadmin_schools.html", schools=schools)


@login_required
def add_school():
    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        db_session = SessionLocal()
        try:
            db_session.execute("""
                INSERT INTO schools (school_name, admin_username, admin_password)
                VALUES (:school_name, :admin_username, :admin_password)
            """, {"school_name": school_name, "admin_username": admin_username, "admin_password": admin_password})
            db_session.commit()
            flash("✅ تمت إضافة المدرسة بنجاح", "success")
        except Exception as e:
            db_session.rollback()
            flash(f"❌ حدث خطأ: {str(e)}", "danger")
        finally:
            db_session.close()
        return redirect(url_for("superadmin_schools"))

    return render_template("add_school.html")


@login_required
def edit_school(school_id):
    db_session = SessionLocal()
    school = db_session.execute(
        "SELECT * FROM schools WHERE id=:school_id",
        {"school_id": school_id}
    ).fetchone()

    if not school:
        db_session.close()
        flash("❌ المدرسة غير موجودة", "danger")
        return redirect(url_for("superadmin_schools"))

    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        try:
            db_session.execute("""
                UPDATE schools
                SET school_name = :school_name, admin_username = :admin_username, admin_password = :admin_password
                WHERE id = :school_id
            """, {"school_name": school_name, "admin_username": admin_username, "admin_password": admin_password, "school_id": school_id})
            db_session.commit()
            flash("✅ تم تعديل المدرسة", "success")
        except Exception as e:
            db_session.rollback()
            flash(f"❌ حدث خطأ: {str(e)}", "danger")
        finally:
            db_session.close()
        return redirect(url_for("superadmin_schools"))

    db_session.close()
    return render_template("edit_school.html", school=school)


@login_required
def delete_school(school_id):
    db_session = SessionLocal()
    try:
        db_session.execute("DELETE FROM schools WHERE id=:school_id", {"school_id": school_id})
        db_session.commit()
        flash("✅ تم حذف المدرسة", "success")
    except Exception as e:
        db_session.rollback()
        flash(f"❌ حدث خطأ: {str(e)}", "danger")
    finally:
        db_session.close()
    return redirect(url_for("superadmin_schools"))
