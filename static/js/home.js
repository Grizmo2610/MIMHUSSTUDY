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
    signinBtn.addEventListener("click", () => window.location.href = "/auth");

    // Event Logout
    logoutBtn.addEventListener("click", async () => {
        try {
            await fetch("/signout", { method: "POST", credentials: "same-origin" });
        } catch (err) {
            console.error("Logout failed:", err);
        }
        localStorage.removeItem("username");
        localStorage.removeItem("access_token");
        window.location.href = "/auth";
    });
});



document.getElementById("search-form").addEventListener("submit", async (e) => {
    e.preventDefault(); // tránh reload trang

    const searchInput = document.getElementById("search-input").value;
    const container = document.getElementById("document-list"); // div chứa danh sách
    
    // Xóa nội dung cũ trước khi hiển thị kết quả mới
    container.innerHTML = "";

    try {
        let limit = 10;
        let offset = 0; // bắt đầu từ đầu

        const response = await fetch(
            `/search?title=${encodeURIComponent(searchInput)}&limit=${limit}&offset=${offset}`
        );
        const data = await response.json();

        // Hàm hiển thị document
        const renderDocument = (doc) => {
            const docDiv = document.createElement("div");
            docDiv.classList.add("document-item", "mb-4", "p-4", "border", "rounded");

            const titleEl = document.createElement("h2");
            titleEl.textContent = doc.title;
            titleEl.style.fontSize = "1.5rem";
            titleEl.style.fontWeight = "bold";

            const updatedDate = doc.last_updated ? new Date(doc.last_updated).toLocaleDateString() : "N/A";
            const infoEl = document.createElement("p");
            infoEl.textContent = `Tác giả: ${doc.author || "N/A"}, lần cập nhật cuối: ${updatedDate}`;

            const schoolEl = document.createElement("p");
            schoolEl.textContent = `Trường: ${doc.school || "N/A"} Khoa: ${doc.faculty || "N/A"}`;

            const langEl = document.createElement("p");
            langEl.textContent = `Ngôn ngữ: ${doc.language || "N/A"} | Download count: ${doc.download_count || 0}`;

            docDiv.appendChild(titleEl);
            docDiv.appendChild(infoEl);
            docDiv.appendChild(schoolEl);
            docDiv.appendChild(langEl);

            container.appendChild(docDiv);
        };

        // Render tất cả kết quả
        data.results.forEach(renderDocument);
    } catch (err) {
        console.error(err);
        alert("Có lỗi xảy ra khi tìm kiếm!");
    }
});
