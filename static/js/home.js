console.log("home.js loaded");

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

// Calendar and Chart functionality
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded");

  let menuToggle = document.getElementById("menuToggle");
  let sidebar = document.getElementById("sidebar");

  menuToggle.addEventListener("click", function () {
    sidebar.classList.toggle("open");
  });

  // Load Calendar
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

  // Load Donut Chart for Total Projects
  function loadTotalProjectsChart() {
    try {
      const projectStagesData = document.getElementById("project-stages");
      if (!projectStagesData) {
        throw new Error("Project stages data element not found");
      }
      console.log("Raw project stages data:", projectStagesData.textContent);
      const projectStages = JSON.parse(projectStagesData.textContent);
      console.log("Parsed Project Stages:", projectStages);

      // Define stages and colors
      const stages = ["Planning", "Design", "Building", "Testing"];
      const colors = ["#6c757d", "#fd7e14", "#28a745", "#007bff"];

      // Populate custom legend
      const legendContainer = document.getElementById("project-legend");
      stages.forEach((stage, index) => {
        const legendItem = document.createElement("div");
        legendItem.className = "legend-item";

        const colorBox = document.createElement("div");
        colorBox.className = "legend-color";
        colorBox.style.backgroundColor = colors[index];

        const label = document.createElement("span");
        label.textContent = `${stage}: ${projectStages[stage]}`;

        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legendContainer.appendChild(legendItem);
      });

      const ctx = document.getElementById("totalProjectsChart").getContext("2d");
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: stages, // Keep simple labels for chart (won't be shown)
          datasets: [{
            data: [
              projectStages["Planning"],
              projectStages["Design"],
              projectStages["Building"],
              projectStages["Testing"]
            ],
            backgroundColor: colors,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false // Disable default legend
            }
          }
        }
      });
    } catch (error) {
      console.error("Error loading chart:", error);
    }
  }

  loadCalendar();
  loadTotalProjectsChart();
});