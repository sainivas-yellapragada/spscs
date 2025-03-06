// adminhome.js

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
      console.log("Loading calendar...");
      const today = new Date();
      const month = today.toLocaleString("default", { month: "long" });
      const year = today.getFullYear();
      document.getElementById("currentMonth").textContent = `${month} ${year}`;
  
      const calendarBody = document.getElementById("calendarBody");
      if (!calendarBody) {
        console.error("Calendar body not found!");
        return;
      }
      calendarBody.innerHTML = "";
  
      let startDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay();
      let totalDays = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
  
      let row = document.createElement("tr");
      for (let i = 0; i < startDay; i++) {
        row.appendChild(document.createElement("td"));
      }
  
      const meetings = typeof meetingsData !== 'undefined' ? meetingsData : [];
      const taskDeadlines = typeof taskDeadlinesData !== 'undefined' ? taskDeadlinesData : [];
      console.log("Meetings data received:", meetings);
      console.log("Task deadlines data received:", taskDeadlines);
  
      for (let day = 1; day <= totalDays; day++) {
        const dayCell = document.createElement("td");
        dayCell.textContent = day;
  
        const currentDate = `${year}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  
        // Meetings
        const meeting = meetings.find(m => m.date === currentDate);
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
        const deadline = taskDeadlines.find(t => t.end_date === currentDate);
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
  
    try {
      loadCalendar();
    } catch (error) {
      console.error("Error loading calendar:", error);
    }
  });