from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# ========================
# إعداد الاتصال بـ Neggffghvffggon PostgreSQL عبر Environment Variables
# ========================
DATABASE_URL = (
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', 5432)}/{os.environ['DB_NAME']}"
    f"?sslmode={os.environ.get('DB_SSLMODE','require')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"sslmode": "require"}
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# ========================
# تعريف الجداول (كما هي تمامًا)
# ========================

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, autoincrement=True)
    school_name = Column(Text, nullable=False)
    admin_username = Column(Text, nullable=False)
    admin_password = Column(Text, nullable=False)

    teachers = relationship("Teacher", back_populates="school", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_name = Column(Text, nullable=False)
    username = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    school = relationship("School", back_populates="teachers")
    subjects = relationship("TeacherSubject", back_populates="teacher", cascade="all, delete-orphan")
    classes = relationship("ClassTeacher", back_populates="teacher", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(Text, nullable=False)
    class_name = Column(Text)
    section = Column(Text)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    school = relationship("School", back_populates="students")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    tracking = relationship("StudentTracking", back_populates="student", cascade="all, delete-orphan")

class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(Text, nullable=False)
    section = Column(Text)
    period = Column(Text, default="صباحي")

class ClassTeacher(Base):
    __tablename__ = "class_teachers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("teacher_classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    teacher = relationship("Teacher", back_populates="classes")
    __table_args__ = (UniqueConstraint('class_id', 'teacher_id', name='uq_class_teacher'),)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(Text, nullable=False, unique=True)

class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    teacher = relationship("Teacher", back_populates="subjects")
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id', name='uq_teacher_subject'),)

class ClassSubject(Base):
    __tablename__ = "class_subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("teacher_classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint('class_id', 'subject_id', 'teacher_id', name='uq_class_subject'),)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))

    student = relationship("Student", back_populates="attendance")

class StudentTracking(Base):
    __tablename__ = "student_tracking"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("teacher_classes.id", ondelete="CASCADE"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    tracking_date = Column(Text, nullable=False)
    note = Column(Text)

    student = relationship("Student", back_populates="tracking")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    role = Column(Text, nullable=False)  # superadmin, admin, teacher

# ========================
# دوال مساعدة مع ضمان إغلاق الجلسات
# ========================

def get_db_connection():
    """ارجاع جلسة SQLAlchemy"""
    return SessionLocal()

def init_db():
    """إنشاء جميع الجداول"""
    Base.metadata.create_all(engine)

def create_superadmin(username="superadmin", password="12345"):
    session = get_db_connection()
    try:
        hashed_pw = generate_password_hash(password)
        exists = session.query(User).filter_by(username=username, role="superadmin").first()
        if exists:
            exists.password = hashed_pw
            print(f"✅ تم تحديث كلمة مرور السوبر أدمن '{username}'")
        else:
            user = User(username=username, password=hashed_pw, role="superadmin")
            session.add(user)
            print(f"✅ تم إنشاء السوبر أدمن '{username}' بكلمة مرور جديدة")
        session.commit()
    finally:
        session.close()

def add_school(school_name, admin_username, admin_password):
    session = get_db_connection()
    try:
        hashed_pw = generate_password_hash(admin_password)
        exists = session.query(School).filter_by(school_name=school_name).first()
        if exists:
            exists.admin_username = admin_username
            exists.admin_password = hashed_pw
            print(f"✅ تم تحديث بيانات المدرسة '{school_name}'")
        else:
            school = School(school_name=school_name, admin_username=admin_username, admin_password=hashed_pw)
            session.add(school)
            print(f"✅ تم إضافة المدرسة '{school_name}' بنجاح")
        session.commit()
    finally:
        session.close()

def add_default_schools():
    """إضافة ثلاث مدارس افتراضية عند التشغيل"""
    add_school("مدرسة النور", "admin_nour", "12345")
    add_school("مدرسة المستقبل", "admin_mustaqbal", "12345")
    add_school("مدرسة الابتكار", "admin_ibtikar", "12345")

# ========================
# تنفيذ عند التشغيل المباشر
# ========================
if __name__ == "__main__":
    init_db()
    create_superadmin()
    add_default_schools()
