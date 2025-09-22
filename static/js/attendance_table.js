document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("attendanceTable");
    if (!table) return; // إذا ما فيه جدول، لا نفعل أي شيء

    const classSelect = document.getElementById("classSelect");
    const sectionSelect = document.getElementById("sectionSelect");
    const checkboxes = table.querySelectorAll(".attendance-checkbox");

    // وظيفة الفلترة وترقيم الصفوف
    function filterTable() {
        const selectedClass = classSelect ? classSelect.value : '';
        const selectedSection = sectionSelect ? sectionSelect.value : '';
        let visibleIndex = 1; // لترقيم الصفوف المرئية فقط

        table.querySelectorAll("tbody tr").forEach(row => {
            let show = true;
            if (selectedClass && row.dataset.class !== selectedClass) show = false;
            if (selectedSection && row.dataset.section !== selectedSection) show = false;
            row.style.display = show ? "" : "none";

            // تحديث الترقيم فقط للصفوف المرئية
            if (show) {
                const numberCell = row.querySelector(".row-number");
                if (numberCell) numberCell.textContent = visibleIndex++;
            }
        });
    }

    if (classSelect) classSelect.addEventListener("change", filterTable);
    if (sectionSelect) sectionSelect.addEventListener("change", filterTable);

    // تحديث الحضور عند التغيير
    checkboxes.forEach(cb => {
        cb.addEventListener("change", () => {
            const studentId = cb.dataset.studentId;
            const status = cb.dataset.status;

            fetch("/update_attendance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ student_id: studentId, status: status })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) alert("حدث خطأ أثناء تحديث الحضور");
            });
        });
    });

    // ترقيم الصفوف عند التحميل الأول
    filterTable();
});
