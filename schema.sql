-- ========================================
-- PostgreSQL version of your SQLite schema
-- Ordered for proper FK creation
-- ========================================

-- 1️⃣ الأب: schools
CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    school_name TEXT NOT NULL,
    admin_username TEXT NOT NULL,
    admin_password TEXT NOT NULL
);

-- 2️⃣ الأب: teachers
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    teacher_name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    school_id INTEGER NOT NULL REFERENCES schools(id)
);

-- 3️⃣ الأب: subjects
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    subject_name TEXT NOT NULL UNIQUE
);

-- 4️⃣ الأب: teacher_classes
CREATE TABLE teacher_classes (
    id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    period TEXT NOT NULL,
    school_id INTEGER
);

-- 5️⃣ الأبناء: students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    student_name TEXT NOT NULL,
    username TEXT,
    password TEXT,
    class_name TEXT,
    section TEXT,
    school_id INTEGER REFERENCES schools(id),
    class_id INTEGER REFERENCES teacher_classes(id)
);

-- 6️⃣ teacher_subjects
CREATE TABLE teacher_subjects (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE (teacher_id, subject_id)
);

-- 7️⃣ class_subjects
CREATE TABLE class_subjects (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES teacher_classes(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE (class_id, subject_id, teacher_id)
);

-- 8️⃣ attendance
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    date TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'present', 'late', 'absent'
    school_id INTEGER,
    teacher_id INTEGER
);

-- 9️⃣ student_tracking
CREATE TABLE student_tracking (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    date TEXT NOT NULL,
    homework INTEGER DEFAULT 0,
    book INTEGER DEFAULT 0,
    participation INTEGER DEFAULT 0,
    misbehavior INTEGER DEFAULT 0,
    note TEXT,
    tracking_date TEXT,
    class_id INTEGER REFERENCES teacher_classes(id),
    teacher_id INTEGER REFERENCES teachers(id),
    school_id INTEGER
);

-- 🔟 teacher_class_assignments
CREATE TABLE teacher_class_assignments (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id),
    class_id INTEGER NOT NULL REFERENCES teacher_classes(id)
);

-- 11️⃣ class_teachers
CREATE TABLE class_teachers (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES teacher_classes(id),
    teacher_id INTEGER NOT NULL REFERENCES teachers(id)
);

-- 12️⃣ subject_teachers
CREATE TABLE subject_teachers (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    teacher_id INTEGER NOT NULL REFERENCES teachers(id),
    UNIQUE(subject_id, teacher_id)
);

-- 13️⃣ users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student', 'superadmin')),
    school_id INTEGER REFERENCES schools(id)
);

-- 14️⃣ superadmins
CREATE TABLE superadmins (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
