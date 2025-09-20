from flask import render_template, request, redirect, url_for, flash
from db import get_db_connection
from auth import login_required

# ✅ عرض جميع المدارس
@login_required
def superadmin_schools():
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT s.id as school_id, s.school_name, s.admin_username as school_admin,
            (SELECT COUNT(*) FROM teachers t WHERE t.school_id = s.id) as teachers,
            (SELECT COUNT(*) FROM students st WHERE st.school_id = s.id) as students
        FROM schools s
    """).fetchall()
    conn.close()
    return render_template("superadmin_schools.html", schools=schools)

# ✅ إضافة مدرسة جديدة
@login_required
def add_school():
    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO schools (school_name, admin_username, admin_password)
                VALUES (?, ?, ?)
            """, (school_name, admin_username, admin_password))
            conn.commit()
            flash("✅ تمت إضافة المدرسة بنجاح", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ حدث خطأ: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("superadmin_schools"))

    return render_template("add_school.html")

# ✅ تعديل مدرسة
@login_required
def edit_school(school_id):
    conn = get_db_connection()
    school = conn.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()

    if not school:
        flash("❌ المدرسة غير موجودة", "danger")
        return redirect(url_for("superadmin_schools"))

    if request.method == "POST":
        school_name = request.form.get("school_name")
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        try:
            conn.execute("""
                UPDATE schools
                SET school_name = ?, admin_username = ?, admin_password = ?
                WHERE id = ?
            """, (school_name, admin_username, admin_password, school_id))
            conn.commit()
            flash("✅ تم تعديل المدرسة", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ حدث خطأ: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("superadmin_schools"))

    conn.close()
    return render_template("edit_school.html", school=school)

# ✅ حذف مدرسة
@login_required
def delete_school(school_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM schools WHERE id = ?", (school_id,))
        conn.commit()
        flash("✅ تم حذف المدرسة", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ حدث خطأ: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("superadmin_schools"))
