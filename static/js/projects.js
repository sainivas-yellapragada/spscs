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

    // Add New Project functionality
    document.getElementById("addProjectBtn").addEventListener("click", function () {
        const form = document.getElementById("newProjectForm");
        form.style.display = form.style.display === "none" ? "block" : "none";
    });

    // Team Member Search functionality
    const teamMemberInput = document.getElementById("team_members_search");
    const suggestionBox = document.getElementById("team_members_suggestions");
    const selectedMembersContainer = document.getElementById("selected_team_members");
    let selectedUsers = [];

    teamMemberInput.addEventListener("input", function () {
        const query = this.value.trim().toLowerCase();
        suggestionBox.innerHTML = ""; // Clear previous suggestions

        if (query.length === 0) {
            suggestionBox.style.display = "none";
            return;
        }

        fetch(`/api/users/`)
            .then(response => response.json())
            .then(users => {
                const filteredUsers = users.filter(user => user.username.toLowerCase().includes(query));

                if (filteredUsers.length === 0) {
                    suggestionBox.style.display = "none";
                    return;
                }

                suggestionBox.style.display = "block";
                filteredUsers.forEach(user => {
                    const suggestion = document.createElement("div");
                    suggestion.classList.add("suggestion");
                    suggestion.textContent = user.username;
                    suggestion.setAttribute("data-user-id", user.id);

                    suggestion.addEventListener("click", function () {
                        addTeamMember(user.id, user.username);
                        teamMemberInput.value = "";
                        suggestionBox.style.display = "none";
                    });

                    suggestionBox.appendChild(suggestion);
                });
            })
            .catch(error => console.error("Error fetching users:", error));
    });

    // Add selected team member
    function addTeamMember(userId, username) {
        if (Array.from(selectedMembersContainer.children).some(item => item.getAttribute("data-user-id") == userId)) {
            return; // Avoid duplicate entries
        }

        const listItem = document.createElement("div");
        listItem.classList.add("selected-member");
        listItem.setAttribute("data-user-id", userId);
        listItem.textContent = username;

        const removeBtn = document.createElement("span");
        removeBtn.classList.add("remove-member");
        removeBtn.textContent = " ×";
        removeBtn.addEventListener("click", function () {
            listItem.remove();
        });

        listItem.appendChild(removeBtn);
        selectedMembersContainer.appendChild(listItem);

        // Add hidden input to form submission
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "team_members";
        hiddenInput.value = userId;
        listItem.appendChild(hiddenInput);
    }

    // Excalidraw integration
    const excalidrawLinks = document.querySelectorAll('a[href^="https://excalidraw.com/#room="]');

    excalidrawLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();

            const excalidrawUrl = link.href;
            const projectId = link.closest("tr").querySelector("td:first-child").textContent.trim(); // Get the project ID

            // Open Excalidraw in a new tab
            const newTab = window.open(excalidrawUrl, "_blank");

            newTab.addEventListener("beforeunload", function () {
                // Save the state of the whiteboard when the tab is closed
                saveExcalidrawState(projectId, excalidrawUrl);
            });

            // Load the state of the whiteboard
            loadExcalidrawState(projectId, newTab);
        });
    });

    function saveExcalidrawState(projectId, excalidrawUrl) {
        fetch(`/projects/${projectId}/save_excalidraw_state/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify({ excalidraw_link: excalidrawUrl })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Excalidraw state saved:", data);
        })
        .catch(error => console.error("Error saving Excalidraw state:", error));
    }

    function loadExcalidrawState(projectId, tab) {
        fetch(`/projects/${projectId}/load_excalidraw_state/`)
            .then(response => response.json())
            .then(data => {
                if (data.excalidraw_link) {
                    tab.location.href = data.excalidraw_link; // Redirect to saved whiteboard URL
                }
            })
            .catch(error => console.error("Error loading Excalidraw state:", error));
    }

    // For the search functionality with multiple selections, handle the input
    const searchInput = document.getElementById("team_members_search");
    const suggestionsList = document.getElementById("suggestions");

    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim();

        if (query.length === 0) {
            suggestionsList.innerHTML = "";
            return;
        }

        fetch(`/get_users/?query=${query}`)
            .then(response => response.json())
            .then(users => {
                suggestionsList.innerHTML = "";

                users.forEach(user => {
                    const li = document.createElement("li");
                    li.textContent = user.username;
                    li.classList.add("suggestion-item");

                    li.addEventListener("click", function () {
                        if (!selectedUsers.includes(user.username)) {
                            selectedUsers.push(user.username);
                        }

                        searchInput.value = selectedUsers.join(", ");
                        suggestionsList.innerHTML = "";
                    });

                    suggestionsList.appendChild(li);
                });
            })
            .catch(error => console.error("Error fetching users:", error));
    });

    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
            suggestionsList.innerHTML = "";
        }
    });
});
