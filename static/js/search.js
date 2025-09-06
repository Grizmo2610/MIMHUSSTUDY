feather.replace();

// Check if user is logged in
const username = localStorage.getItem('username');
const authButtons = document.getElementById('auth-buttons');
const userDropdown = document.getElementById('user-dropdown');

if (username) {
    // User is logged in
    document.getElementById('username-display').textContent = username;
    userDropdown.classList.remove('hidden');

    // Logout functionality
    document.getElementById('logout-btn').addEventListener('click', function (e) {
        e.preventDefault();
        localStorage.removeItem('username');
        window.location.reload();
    });
} else {
    // User is not logged in
    authButtons.classList.remove('hidden');
}

// Search functionality
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const query = document.getElementById('search-input').value.trim();
    if (query) {
        // In a real implementation, you would call a search API here
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h3 class="text-lg font-medium text-primary-700">Search results for: ${query}</h3>
                        <p class="text-gray-600 mt-2">This is a placeholder for search results. In a real implementation, you would display actual search results here.</p>
                    </div>
                `;
        resultsContainer.classList.remove('hidden');
    }
});