document.addEventListener("DOMContentLoaded", () => {
    const noteModal = new bootstrap.Modal(document.getElementById("noteModal"));
    const noteText = document.getElementById("noteText");
    let currentStudentId = null;
    let currentButton = null;

    // ✅ تحديث القيم عند تغيير الـ checkbox
    document.querySelectorAll(".track").forEach(cb => {
        cb.addEventListener("change", () => {
            const studentId = cb.closest("tr").dataset.student;
            const field = cb.dataset.field;
            const value = cb.checked ? 1 : 0;

            fetch("/update_tracking", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ student_id: studentId, field, value })
            });
        });
    });

    // ✅ فتح نافذة الملاحظات
    document.querySelectorAll(".note-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            currentStudentId = btn.dataset.student;
            currentButton = btn;
            noteText.value = btn.dataset.note || "";
            noteModal.show();
        });
    });

    // ✅ حفظ الملاحظة
    document.getElementById("saveNote").addEventListener("click", () => {
        fetch("/update_note", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: currentStudentId, note: noteText.value })
        })
        .then(res => res.json())
        .then(() => {
            if (noteText.value.trim() !== "") {
                currentButton.classList.remove("btn-secondary");
                currentButton.classList.add("btn-danger");
                currentButton.dataset.note = noteText.value;
            } else {
                currentButton.classList.remove("btn-danger");
                currentButton.classList.add("btn-secondary");
                currentButton.dataset.note = "";
            }
            noteModal.hide();
        });
    });
});
