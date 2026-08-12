// ==========================================
// College Complaint Prioritizer
// Search & Filter
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");
    const priorityFilter = document.getElementById("priorityFilter");
    const statusFilter = document.getElementById("statusFilter");

    const complaintRows = document.querySelectorAll(".complaint-row");


    // If dashboard elements don't exist,
    // stop the script safely.

    if (
        !searchInput ||
        !priorityFilter ||
        !statusFilter
    ) {
        return;
    }


    function filterComplaints() {

        const searchText =
            searchInput.value
                .toLowerCase()
                .trim();

        const selectedPriority =
            priorityFilter.value;

        const selectedStatus =
            statusFilter.value;


        complaintRows.forEach(function (row) {

            const rowText =
                row.textContent.toLowerCase();

            const rowPriority =
                row.dataset.priority;

            const rowStatus =
                row.dataset.status;


            // Search condition

            const matchesSearch =
                rowText.includes(searchText);


            // Priority condition

            const matchesPriority =
                selectedPriority === "all" ||
                rowPriority === selectedPriority;


            // Status condition

            const matchesStatus =
                selectedStatus === "all" ||
                rowStatus === selectedStatus;


            // Show / hide row

            if (
                matchesSearch &&
                matchesPriority &&
                matchesStatus
            ) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    }


    // Search while typing

    searchInput.addEventListener(
        "input",
        filterComplaints
    );


    // Priority filter

    priorityFilter.addEventListener(
        "change",
        filterComplaints
    );


    // Status filter

    statusFilter.addEventListener(
        "change",
        filterComplaints
    );


});