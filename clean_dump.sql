PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    username TEXT,
    password TEXT
, class_name TEXT, section TEXT, school_id INTEGER REFERENCES schools(id), class_id INTEGER REFERENCES teacher_classes(id));
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL, school_id INTEGER, teacher_id INTEGER,  -- 'present', 'late', 'absent'
    FOREIGN KEY(student_id) REFERENCES students(id)
);
CREATE TABLE student_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    homework INTEGER DEFAULT 0,
    book INTEGER DEFAULT 0,
    participation INTEGER DEFAULT 0,
    misbehavior INTEGER DEFAULT 0,
    note TEXT, tracking_date TEXT, class_id INTEGER REFERENCES teacher_classes(id), teacher_id INTEGER REFERENCES teachers(id), school_id INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id)
);
CREATE TABLE schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_name TEXT NOT NULL,
        admin_username TEXT NOT NULL,
        admin_password TEXT NOT NULL
    );
CREATE TABLE teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        school_id INTEGER NOT NULL,
        FOREIGN KEY(school_id) REFERENCES schools(id)
    );
CREATE TABLE teacher_class_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    FOREIGN KEY(teacher_id) REFERENCES teachers(id),
    FOREIGN KEY(class_id) REFERENCES teacher_classes(id)
);
CREATE TABLE teacher_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    period TEXT NOT NULL
, school_id INTEGER);
CREATE TABLE class_teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES teacher_classes(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);
CREATE TABLE subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL UNIQUE
    );
CREATE TABLE teacher_subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        UNIQUE (teacher_id, subject_id)
    );
CREATE TABLE class_subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY (class_id) REFERENCES teacher_classes(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
        UNIQUE (class_id, subject_id, teacher_id)
    );
CREATE TABLE subject_teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES subjects(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id),
    UNIQUE(subject_id, teacher_id)  -- لضمان عدم تكرار الربط
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student', 'superadmin')),
    school_id INTEGER REFERENCES schools(id)
);
CREATE TABLE superadmins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
COMMIT;
