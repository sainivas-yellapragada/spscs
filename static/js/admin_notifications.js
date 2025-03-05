// Toggle Sidebar
document.getElementById("menuToggle").onclick = function() {
    var sidebar = document.getElementById("sidebar");
    if (sidebar.style.width === "250px") {
        sidebar.style.width = "0";
        document.getElementById("main").style.marginLeft = "0";
    } else {
        sidebar.style.width = "250px";
        document.getElementById("main").style.marginLeft = "250px";
    }
};

// Popup Functionality
const scheduleBtn = document.getElementById("scheduleMeetingBtn");
const popup = document.getElementById("schedulePopup");
const overlay = document.getElementById("popupOverlay");
const closeBtn = document.getElementById("closePopup");
const userSearch = document.getElementById("user-search");
const suggestions = document.getElementById("suggestions");

scheduleBtn.onclick = function() {
    popup.style.display = "block";
    overlay.style.display = "block";
    userSearch.value = ""; // Clear input on open
    suggestions.style.display = "none"; // Hide suggestions initially
};

closeBtn.onclick = function() {
    popup.style.display = "none";
    overlay.style.display = "none";
    suggestions.style.display = "none";
};

overlay.onclick = function() {
    popup.style.display = "none";
    overlay.style.display = "none";
    suggestions.style.display = "none";
};

// Autocomplete functionality
userSearch.oninput = function() {
    const fullValue = userSearch.value.trim();
    const segments = fullValue.split(',').map(s => s.trim());
    const currentSegment = segments[segments.length - 1]; // Get the last segment being typed

    if (currentSegment.length === 0) {
        suggestions.style.display = "none";
        return;
    }

    fetch(`/get_users/?q=${encodeURIComponent(currentSegment)}`)
        .then(response => response.json())
        .then(users => {
            suggestions.innerHTML = "";
            if (users.length > 0) {
                users.forEach(user => {
                    const div = document.createElement("div");
                    div.textContent = user.username;
                    div.onclick = function() {
                        // Replace the current segment with the selected username and add a comma
                        segments[segments.length - 1] = user.username;
                        userSearch.value = segments.join(', ') + ', ';
                        suggestions.style.display = "none";
                        userSearch.focus(); // Keep focus on input for continued typing
                    };
                    suggestions.appendChild(div);
                });
                suggestions.style.display = "block";
            } else {
                suggestions.style.display = "none";
            }
        })
        .catch(error => console.error('Error fetching users:', error));
};

// Hide suggestions when clicking outside
document.addEventListener("click", function(event) {
    if (!popup.contains(event.target) && event.target !== scheduleBtn) {
        suggestions.style.display = "none";
    }
});