from sqlalchemy import create_engine, text

# نفس رابط قاعدة البيانات تبعك
DATABASE_URL = "postgresql://neondb_owner:npg_lAVrOD02hwmK@ep-orange-dream-a71g8nd6-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"sslmode": "require"})

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT id, username, role, password FROM users WHERE username=:u AND role=:r LIMIT 1"),
        {"u": "superadmin", "r": "superadmin"}
    )
    row = result.fetchone()
    print("🔍 النتيجة الراجعة من قاعدة البيانات:")
    print(row)
    if row:
        print("✅ موجود السوبر أدمن")
    else:
        print("❌ ما في سوبر أدمن بالجدول")
