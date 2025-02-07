// Handle login/register panel toggle
const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
});

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
});

// Handle Django messages and display as popups
document.addEventListener("DOMContentLoaded", function () {
    let messagesDiv = document.getElementById("django-messages");
    
    if (messagesDiv) {
        let messages = messagesDiv.getElementsByClassName("message");

        for (let i = 0; i < messages.length; i++) {
            alert(messages[i].innerText);  // Show message in an alert popup
        }
    }
});
