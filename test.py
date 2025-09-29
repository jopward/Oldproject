from sqlalchemy import create_engine, inspect

# ضع رابط قاعدة بيانات PostgreSQL الخاص بك
DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# تعريف الجداول والأعمدة المتوقعة
expected_schema = {
    "students": ["id", "student_name", "class_name", "section", "school_id"],
    "attendance": ["id", "student_id", "date", "status", "school_id", "teacher_id"],
    "teachers": ["id", "teacher_name", "username", "password", "school_id"],
    "schools": ["id", "school_name", "admin_username", "admin_password"],
}

schemas = inspector.get_schema_names()

for table, expected_columns in expected_schema.items():
    found = False
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        if table in tables:
            found = True
            columns = [col['name'] for col in inspector.get_columns(table, schema=schema)]
            print(f"\n✅ وجد جدول '{table}' في schema: {schema}")
            print(f"الأعمدة الموجودة: {columns}")
            missing = [col for col in expected_columns if col not in columns]
            extra = [col for col in columns if col not in expected_columns]
            if missing:
                print(f"❌ الأعمدة الناقصة: {missing}")
            if extra:
                print(f"⚠️ أعمدة إضافية: {extra}")
            if not missing:
                print("✅ جميع الأعمدة متوافقة مع المشروع")
    if not found:
        print(f"\n❌ جدول '{table}' غير موجود في أي schema")
