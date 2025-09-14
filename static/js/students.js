document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("addStudentForm");
    const tableBody = document.getElementById("studentsTableBody");
    const searchInput = document.getElementById("searchInput");

    // تحميل الطلاب
    function loadStudents(query = "") {
        fetch(`/get_students?search=${query}`)
            .then(res => res.json())
            .then(data => {
                tableBody.innerHTML = "";
                data.forEach(student => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${student.student_name}</td>
                        <td>${student.class_name || ""}</td>
                        <td>${student.section || ""}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-btn" data-id="${student.id}">تعديل</button>
                            <button class="btn btn-sm btn-danger delete-btn" data-id="${student.id}">حذف</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });

                // زر التعديل
                document.querySelectorAll(".edit-btn").forEach(btn => {
                    btn.addEventListener("click", () => {
                        const id = btn.dataset.id;
                        const newName = prompt("ادخل الاسم الجديد:");
                        if (newName) {
                            fetch(`/edit_student/${id}`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ student_name: newName })
                            }).then(() => loadStudents());
                        }
                    });
                });

                // زر الحذف
                document.querySelectorAll(".delete-btn").forEach(btn => {
                    btn.addEventListener("click", () => {
                        const id = btn.dataset.id;
                        if (confirm("هل أنت متأكد من حذف هذا الطالب؟")) {
                            fetch(`/delete_student/${id}`, { method: "POST" })
                                .then(() => loadStudents());
                        }
                    });
                });
            });
    }

    // عند الإضافة
    form.addEventListener("submit", e => {
        e.preventDefault();
        const name = document.getElementById("studentName").value;
        const className = document.getElementById("className").value;
        const section = document.getElementById("section").value;

        fetch("/add_student", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_name: name, class_name: className, section: section })
        }).then(() => {
            form.reset();
            loadStudents();
        });
    });

    // البحث
    searchInput.addEventListener("input", () => {
        loadStudents(searchInput.value);
    });

    loadStudents();
});
