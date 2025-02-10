document.addEventListener("DOMContentLoaded", function () {
    const profileForm = document.getElementById("profileForm");
    const countrySelect = document.getElementById("country");
    const phoneCodeSelect = document.getElementById("phoneCode");

    countrySelect.addEventListener("change", function () {
        let selectedCountry = this.options[this.selectedIndex];
        let phoneCode = selectedCountry.getAttribute("data-code");

        phoneCodeSelect.value = phoneCode;
    });

    profileForm.addEventListener("submit", function (event) {
        event.preventDefault();
        alert("Profile Updated Successfully!");
    });

    // Sidebar Toggle
    document.getElementById("menuToggle").addEventListener("click", () => {
        const sidebar = document.getElementById("sidebar");
        sidebar.style.width = sidebar.style.width === "250px" ? "0" : "250px";
    });
});
