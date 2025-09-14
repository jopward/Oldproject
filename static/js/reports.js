document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("reportsTableBody");

    tableBody.addEventListener("click", (event) => {
        const cell = event.target;
        if (cell.classList.contains("clickable")) {
            const studentId = cell.dataset.student;
            const status = cell.dataset.status;

            fetch(`/get_attendance_details/${studentId}/${status}`)
                .then(res => res.json())
                .then(data => {
                    if (data.length === 0) {
                        alert(`لا توجد سجلات ${status.toUpperCase()}`);
                    } else {
                        if(status === "note"){
                            alert(`ملاحظة:\n` + data.join("\n"));
                        } else {
                            alert(`${status.toUpperCase()}:\n` + data.join("\n"));
                        }
                    }
                });
        }
    });
});
