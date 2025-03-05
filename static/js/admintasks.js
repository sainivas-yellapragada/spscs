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

    // Add New Task functionality
    document.getElementById("addProjectBtn").addEventListener("click", function () {
        const form = document.getElementById("newProjectForm");
        form.style.display = form.style.display === "none" ? "block" : "none";
    });

    // Team Member Search functionality (matching admin_notifications.js)
    const teamMemberInput = document.getElementById("team_members_search");
    const suggestionBox = document.getElementById("team_members_suggestions");
    const selectedMembersContainer = document.getElementById("selected_team_members");
    let selectedUsers = [];

    teamMemberInput.addEventListener("input", function () {
        const fullValue = this.value.trim();
        const segments = fullValue.split(',').map(s => s.trim());
        const currentSegment = segments[segments.length - 1]; // Get the last segment being typed

        if (currentSegment.length === 0) {
            suggestionBox.style.display = "none";
            return;
        }

        fetch(`/get_users/?q=${encodeURIComponent(currentSegment)}`)
            .then(response => response.json())
            .then(users => {
                suggestionBox.innerHTML = "";
                if (users.length > 0) {
                    users.forEach(user => {
                        const div = document.createElement("div");
                        div.textContent = user.username;
                        div.classList.add("suggestion"); // Use the same class for consistency
                        div.onclick = function () {
                            // Replace the current segment with the selected username and add a comma
                            segments[segments.length - 1] = user.username;
                            teamMemberInput.value = segments.join(', ') + ', ';
                            addTeamMember(user.id, user.username); // Add to selected members
                            suggestionBox.style.display = "none";
                            teamMemberInput.focus(); // Keep focus for continued typing
                        };
                        suggestionBox.appendChild(div);
                    });
                    suggestionBox.style.display = "block";
                } else {
                    suggestionBox.style.display = "none";
                }
            })
            .catch(error => console.error('Error fetching users:', error));
    });

    // Add selected team member (with hidden input for form submission)
    function addTeamMember(userId, username) {
        if (selectedUsers.includes(username)) return;

        selectedUsers.push(username);

        const listItem = document.createElement("div");
        listItem.classList.add("selected-member");
        listItem.setAttribute("data-user-id", userId);
        listItem.textContent = username;

        const removeBtn = document.createElement("span");
        removeBtn.classList.add("remove-member");
        removeBtn.textContent = " ×";
        removeBtn.addEventListener("click", function () {
            listItem.remove();
            selectedUsers = selectedUsers.filter(u => u !== username);
            // Update input to reflect removed user
            const segments = teamMemberInput.value.split(',').map(s => s.trim());
            const updatedSegments = segments.filter(s => s !== username);
            teamMemberInput.value = updatedSegments.join(', ') + (updatedSegments.length > 0 ? ', ' : '');
        });

        listItem.appendChild(removeBtn);
        selectedMembersContainer.appendChild(listItem);

        // Add hidden input for form submission
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "team_members";
        hiddenInput.value = userId;
        listItem.appendChild(hiddenInput);
    }

    // Hide suggestions when clicking outside
    document.addEventListener("click", function (event) {
        if (!teamMemberInput.contains(event.target) && !suggestionBox.contains(event.target)) {
            suggestionBox.style.display = "none";
        }
    });
});