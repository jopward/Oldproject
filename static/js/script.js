document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll(".attendance-checkbox");

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", () => {
            const studentId = checkbox.dataset.studentId;
            const status = checkbox.dataset.status;

            // إرسال البيانات للبايثون لتحديث قاعدة البيانات
            fetch("/update_attendance", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    student_id: studentId,
                    status: status
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // إذا تم اختيار هذه الحالة، أزل الصح من الحالات الأخرى
                    if (checkbox.checked) {
                        const row = checkbox.closest("tr");
                        row.querySelectorAll(".attendance-checkbox").forEach(cb => {
                            if (cb !== checkbox) cb.checked = false;
                        });
                    }
                } else {
                    alert("حدث خطأ أثناء التحديث!");
                }
            })
            .catch(err => {
                console.error("Error:", err);
            });
        });
    });
});
