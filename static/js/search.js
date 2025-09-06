document.addEventListener("DOMContentLoaded", () => {
    feather.replace();

    const signinBtn = document.getElementById("redict-signin-btn");
    const logoutBtn = document.getElementById("redict-logout-btn");
    const usernameDisplay = document.getElementById("username-display");

    const username = localStorage.getItem("username") || "Anonymous";
    usernameDisplay.textContent = username;

    // Hiển thị nút tương ứng
    signinBtn.classList.toggle("hidden", username !== "Anonymous");
    logoutBtn.classList.toggle("hidden", username === "Anonymous");

    // Event Sign In
    signinBtn.addEventListener("click", () => window.location.href = "/");

    // Event Logout
    logoutBtn.addEventListener("click", async () => {
        try {
            await fetch("/signout", { method: "POST", credentials: "same-origin" });
        } catch (err) {
            console.error("Logout failed:", err);
        }
        localStorage.removeItem("username");
        localStorage.removeItem("access_token");
        window.location.href = "/";
    });
});
