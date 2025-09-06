document.addEventListener("DOMContentLoaded", () => {
    const username = localStorage.getItem("username");

    if (username) {
        window.location.href = "/search";
    }
});

AOS.init();
feather.replace();

const signinBtn = document.getElementById('signin-btn');
const signupBtn = document.getElementById('signup-btn');
const signinForm = document.getElementById('signin-form');
const signupForm = document.getElementById('signup-form');

signinBtn.addEventListener('click', () => {
    signinBtn.classList.add('active');
    signupBtn.classList.remove('active');
    signinForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
});

signupBtn.addEventListener('click', () => {
    signupBtn.classList.add('active');
    signinBtn.classList.remove('active');
    signupForm.classList.remove('hidden');
    signinForm.classList.add('hidden');
});

// Toggle password visibility (chỉ dùng 1 lần)
document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function () {
        const input = this.parentElement.querySelector('input');
        const icon = this.querySelector('svg'); // feather thay <i> -> <svg>

        if (input.type === 'password') {
            input.type = 'text';
            icon.setAttribute('data-feather', 'eye-off');
        } else {
            input.type = 'password';
            icon.setAttribute('data-feather', 'eye');
        }
        feather.replace(); // re-render lại icon
    });
});

const API_BASE = "http://127.0.0.1:8000";

// Handle Sign In
signinForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
        const formData = new FormData();
        formData.append("email", email);
        formData.append("password", password);
        const res = await fetch('/signin', {
            method: "POST",
            // headers: { "Content-Type": "application/json" },
            body: formData
        });

        const data = await res.json();
        if (res.ok) {
            
            localStorage.setItem("username", data.username);
            localStorage.setItem("access_token", data.access_token);

            window.location.href = "/search";
        } else {
            alert(data.detail || "Sign in failed");
        }
    } catch (err) {
        alert("Cannot connect to server");
    }
});

// Handle Sign Up
signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("new-email").value;
    const password = document.getElementById("new-password").value;
    const confirm = document.getElementById("confirm-password").value;

    if (password !== confirm) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("password", password);
        const res = await fetch(`/signup`, {
            method: "POST",
            // headers: { "Content-Type": "application/json" },
            body: formData
        });

        const data = await res.json();
        if (res.ok) {
            alert("Account created, please sign in!");
            signinBtn.click();
        } else {
            alert(data.detail || "Sign up failed");
        }
    } catch (err) {
        alert("Cannot connect to server");
    }
});
