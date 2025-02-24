document.getElementById("menuToggle").addEventListener("click", function () {
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");

    if (sidebar.style.width === "250px") {
        sidebar.style.width = "0";
        mainContent.style.marginLeft = "10%";
    } else {
        sidebar.style.width = "250px";
        mainContent.style.marginLeft = "20%";
    }
});
