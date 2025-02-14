document.addEventListener("DOMContentLoaded", function () {
    // Sidebar Toggle
    document.getElementById("menuToggle").addEventListener("click", () => {
        const sidebar = document.getElementById("sidebar");
        const main = document.getElementById("main");

        if (sidebar.style.width === "250px") {
            sidebar.style.width = "0";
            main.style.marginLeft = "0";
        } else {
            sidebar.style.width = "250px";
            main.style.marginLeft = "250px";
        }
    });
});

// Add New Project functionality
document.getElementById("addProjectBtn").addEventListener("click", function () {
    const form = document.getElementById("newProjectForm");
    form.style.display = form.style.display === "none" ? "block" : "none";
});
