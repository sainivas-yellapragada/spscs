// Toggle sidebar open/close
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

// Calendar functionality
document.addEventListener("DOMContentLoaded", function () {
  let menuToggle = document.getElementById("menuToggle");
  let sidebar = document.getElementById("sidebar");

  menuToggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
  });

  function loadCalendar() {
    const today = new Date();
    const month = today.toLocaleString("default", { month: "long" });
    document.getElementById("currentMonth").textContent = month;

    const calendarBody = document.getElementById("calendarBody");
    calendarBody.innerHTML = "";

    let startDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay();
    let totalDays = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();

    let row = document.createElement("tr");
    for (let i = 0; i < startDay; i++) {
      row.appendChild(document.createElement("td"));
    }

    for (let day = 1; day <= totalDays; day++) {
      const dayCell = document.createElement("td");
      dayCell.textContent = day;
      row.appendChild(dayCell);

      if ((startDay + day) % 7 === 0) {
        calendarBody.appendChild(row);
        row = document.createElement("tr");
      }
    }
    calendarBody.appendChild(row);

    // Highlight today
    const todayCell = calendarBody.querySelectorAll("td");
    const todayDate = today.getDate();
    todayCell.forEach((cell) => {
      if (parseInt(cell.textContent) === todayDate) {
        cell.classList.add("today");
      }
    });
  }

  loadCalendar();
});
