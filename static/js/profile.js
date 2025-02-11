document.addEventListener("DOMContentLoaded", function () {
    // Sidebar Toggle
    document.getElementById("menuToggle").addEventListener("click", () => {
        const sidebar = document.getElementById("sidebar");
        // Toggle sidebar width between 0 and 250px
        if (sidebar.style.width === "250px") {
            sidebar.style.width = "0"; // Close the sidebar
        } else {
            sidebar.style.width = "250px"; // Open the sidebar
        }
        console.log(sidebar.style.width); // Debugging log to check the width change
    });
});
