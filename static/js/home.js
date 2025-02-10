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

// Calendar initialization (existing code)
document.addEventListener("DOMContentLoaded", () => {
const currentMonthDiv = document.getElementById("currentMonth");
const calendarBody = document.getElementById("calendarBody");

const today = new Date();
const currentMonth = today.getMonth();
const currentYear = today.getFullYear();

const monthNames = [
  "January", "February", "March", "April", "May", "June", "July",
  "August", "September", "October", "November", "December"
];

currentMonthDiv.textContent = `${monthNames[currentMonth]} ${currentYear}`;
const firstDay = new Date(currentYear, currentMonth, 1).getDay();
const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

calendarBody.innerHTML = "";
let row = document.createElement("tr");

for (let i = 0; i < firstDay; i++) {
  const cell = document.createElement("td");
  row.appendChild(cell);
}

for (let day = 1; day <= daysInMonth; day++) {
  if (row.children.length === 7) {
    calendarBody.appendChild(row);
    row = document.createElement("tr");
  }

  const cell = document.createElement("td");
  cell.textContent = day;

  if (day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
    cell.classList.add("today");
  }

  row.appendChild(cell);
}

if (row.children.length > 0) {
  calendarBody.appendChild(row);
}
});
