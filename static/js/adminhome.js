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

      // Use meetingsData from template with fallback
      const meetings = typeof meetingsData !== 'undefined' ? meetingsData : [];
      console.log("Meetings data received:", meetings);

      for (let day = 1; day <= totalDays; day++) {
          const dayCell = document.createElement("td");
          dayCell.textContent = day;
          
          // Format the current date as YYYY-MM-DD
          const currentDate = `${year}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          
          // Check for meetings on this date
          const meeting = meetings.find(m => m.date === currentDate);
          if (meeting) {
              console.log(`Meeting found on ${currentDate}:`, meeting);
              dayCell.classList.add("has-meeting");
              const tooltip = document.createElement("div");
              tooltip.classList.add("tooltip");
              tooltip.innerHTML = `Meeting at ${meeting.time}<br><a href="${meeting.link}" target="_blank">${meeting.link}</a>`;
              dayCell.appendChild(tooltip);
          }

          row.appendChild(dayCell);

          if ((startDay + day - 1) % 7 === 6) { // Break row on Saturday
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