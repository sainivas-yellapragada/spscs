const container = document.querySelector('.container');
const LoginLink = document.querySelector('.SignInLink');
const RegisterLink = document.querySelector('.SignUpLink');
const toggleButtons = document.querySelectorAll('.toggle-btn');
const loginTypeInput = document.querySelector('#login_type');
const googleLoginLink = document.querySelector('#google-login');
const githubLoginLink = document.querySelector('#github-login');

// Base URLs from the initial href attributes
const googleBaseUrl = googleLoginLink.getAttribute('href').split('?')[0];
const githubBaseUrl = githubLoginLink.getAttribute('href').split('?')[0];

// Toggle between Login and Register
RegisterLink.addEventListener('click', () => {
    container.classList.add('active');
});

LoginLink.addEventListener('click', () => {
    container.classList.remove('active');
});

// Toggle between Admin and Employee Login
toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        const loginType = button.getAttribute('data-type');
        loginTypeInput.value = loginType;

        // Update social login URLs with login_type
        googleLoginLink.href = `${googleBaseUrl}?login_type=${loginType}`;
        githubLoginLink.href = `${githubBaseUrl}?login_type=${loginType}`;

        console.log(`Set login_type to ${loginType}, Google URL: ${googleLoginLink.href}, GitHub URL: ${githubLoginLink.href}`);

        // Change color and trigger animation
        if (loginType === 'admin') {
            updatePrimaryColor('#bb00ff');
            triggerPulse();
        } else {
            updatePrimaryColor('#0099ff');
            triggerPulse();
        }
    });
});

// Functions
function updatePrimaryColor(color) {
    document.documentElement.style.setProperty('--primary-color', color);
}

function triggerPulse() {
    container.classList.add('pulse');
    document.querySelector('.login-type').classList.add('pulse');
    setTimeout(() => {
        container.classList.remove('pulse');
        document.querySelector('.login-type').classList.remove('pulse');
    }, 300);
}