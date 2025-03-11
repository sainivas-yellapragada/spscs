console.log("home.js loaded");

// Calendar and Chart functionality
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded");

  // Toggle sidebar open/close
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  const main = document.getElementById("main");

  if (menuToggle && sidebar && main) {
    menuToggle.addEventListener("click", () => {
      if (sidebar.style.width === "250px") {
        sidebar.style.width = "0";
        main.style.marginLeft = "0";
      } else {
        sidebar.style.width = "250px";
        main.style.marginLeft = "250px";
      }
    });
  } else {
    console.error("Menu toggle, sidebar, or main element not found");
  }

  // Match Team and Project Updates height to the donut chart's bottom
  function matchSectionHeights() {
    const totalProjects = document.querySelector(".total-projects");
    const team = document.querySelector(".team");
    const projectUpdates = document.querySelector(".project-updates");
    const chartCanvas = document.getElementById("totalProjectsChart");
    const sectionHeading = totalProjects?.querySelector(".section-heading");

    if (!totalProjects || !team || !projectUpdates || !chartCanvas || !sectionHeading) {
      console.warn("One or more elements for height matching not found");
      return;
    }

    const chartHeight = chartCanvas.offsetHeight;
    const headingHeight = sectionHeading.offsetHeight;
    const padding = 40; // 20px top + 20px bottom padding from .total-projects
    const adjustedHeight = chartHeight + headingHeight + padding;

    console.log("Chart Height:", chartHeight);
    console.log("Heading Height:", headingHeight);
    console.log("Adjusted Container Height:", adjustedHeight);

    team.style.height = `${adjustedHeight}px`;
    projectUpdates.style.height = `${adjustedHeight}px`;
    totalProjects.style.height = `${adjustedHeight}px`;
  }

  // Load Calendar
  function loadCalendar() {
    const today = new Date();
    const month = today.toLocaleString("default", { month: "long" });
    const year = today.getFullYear();
    document.getElementById("currentMonth").textContent = `${month} ${year}`;

    const calendarBody = document.getElementById("calendarBody");
    calendarBody.innerHTML = "";

    let startDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay();
    let totalDays = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();

    let row = document.createElement("tr");
    for (let i = 0; i < startDay; i++) {
      row.appendChild(document.createElement("td"));
    }

    const meetings = typeof meetingsData !== "undefined" ? meetingsData : [];
    const taskDeadlines = typeof taskDeadlinesData !== "undefined" ? taskDeadlinesData : [];
    console.log("Meetings data received:", meetings);
    console.log("Task deadlines data received:", taskDeadlines);

    for (let day = 1; day <= totalDays; day++) {
      const dayCell = document.createElement("td");
      dayCell.textContent = day;

      const currentDate = `${year}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

      // Meetings
      const meeting = meetings.find((m) => m.date === currentDate);
      if (meeting) {
        console.log(`Meeting found on ${currentDate}:`, meeting);
        dayCell.classList.add("has-meeting");
        const meetingDot = document.createElement("span");
        meetingDot.classList.add("meeting-dot");
        dayCell.appendChild(meetingDot);

        const meetingTooltip = document.createElement("div");
        meetingTooltip.classList.add("tooltip", "meeting-tooltip");
        meetingTooltip.innerHTML = `Meeting at ${meeting.time}<br><a href="${meeting.link}" target="_blank">${meeting.link}</a>`;
        dayCell.appendChild(meetingTooltip);
      }

      // Task Deadlines
      const deadline = taskDeadlines.find((t) => t.end_date === currentDate);
      if (deadline) {
        console.log(`Task deadline found on ${currentDate}:`, deadline);
        dayCell.classList.add("has-deadline");
        const deadlineDot = document.createElement("span");
        deadlineDot.classList.add("deadline-dot");
        dayCell.appendChild(deadlineDot);

        const deadlineTooltip = document.createElement("div");
        deadlineTooltip.classList.add("tooltip", "deadline-tooltip");
        deadlineTooltip.innerHTML = `${deadline.title} deadline`;
        dayCell.appendChild(deadlineTooltip);
      }

      row.appendChild(dayCell);

      if ((startDay + day - 1) % 7 === 6) {
        calendarBody.appendChild(row);
        row = document.createElement("tr");
      }
    }
    if (row.children.length > 0) {
      calendarBody.appendChild(row);
    }

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
        throw new Error("Project stages data element not found in DOM");
      }
      console.log("Raw project stages data:", projectStagesData.textContent);
      const projectStages = JSON.parse(projectStagesData.textContent);
      console.log("Parsed Project Stages:", projectStages);

      const stages = ["Planning", "Design", "Building", "Testing"];
      const colors = ["#6c757d", "#fd7e14", "#28a745", "#007bff"];

      // Custom legend
      const legendContainer = document.getElementById("project-legend");
      if (!legendContainer) {
        throw new Error("Legend container not found");
      }
      legendContainer.innerHTML = ""; // Clear existing legend
      stages.forEach((stage, index) => {
        const legendItem = document.createElement("div");
        legendItem.className = "legend-item";

        const colorBox = document.createElement("div");
        colorBox.className = "legend-color";
        colorBox.style.backgroundColor = colors[index];

        const label = document.createElement("span");
        label.textContent = `${stage}: ${projectStages[stage] || 0}`; // Default to 0 if undefined

        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legendContainer.appendChild(legendItem);
      });

      const ctx = document.getElementById("totalProjectsChart").getContext("2d");
      if (!ctx) {
        throw new Error("Chart canvas context not available");
      }
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: stages,
          datasets: [
            {
              data: [
                projectStages["Planning"] || 0,
                projectStages["Design"] || 0,
                projectStages["Building"] || 0,
                projectStages["Testing"] || 0,
              ],
              backgroundColor: colors,
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false, // Use custom legend instead
            },
          },
        },
      });
    } catch (error) {
      console.error("Error loading chart:", error);
    }
  }

  // Initialize components
  loadCalendar();
  loadTotalProjectsChart();

  // Delay height matching to ensure chart is rendered
  setTimeout(matchSectionHeights, 100);
});

// Handle window resize
window.addEventListener("resize", () => {
  setTimeout(matchSectionHeights, 100); // Delay to account for resize rendering
});