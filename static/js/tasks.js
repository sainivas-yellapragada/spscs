// Sidebar Toggle Functionality
document.getElementById("menuToggle").addEventListener("click", () => {
    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
  
    if (sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");
        main.classList.remove("active");
    } else {
        sidebar.classList.add("active");
        main.classList.add("active");
    }
  });
  