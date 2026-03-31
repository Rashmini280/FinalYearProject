

window.deleteHistory = async function(createdAt) {
    if (!confirm("Are you sure you want to delete this record?")) return;   //delete history of users function

    try {
        const res = await fetch(`/admin/delete-history/${encodeURIComponent(createdAt)}`, {
            method: "DELETE",
            credentials: "include"
        });

        const data = await res.json(); // showing the alert message 
        alert(data.message || "Record deleted");
        loadHistory();

    } catch (err) {
        console.error("Error deleting history:", err);
        alert("Failed to delete record");
    }
};


document.addEventListener("DOMContentLoaded", () => {

    loadUsers();
    loadHistory();

});

// -----------------------------
// Load Users
// -----------------------------
async function loadUsers() {
    try {
        const res = await fetch("/admin/users", { credentials: "include" });
        const data = await res.json();

        const tbody = document.querySelector("#users-table tbody");
        tbody.innerHTML = "";

        data.users.forEach(user => {

            const row = `
            <tr>
                <td>${user[0]}</td> //users details are shown in admin page
                <td>${user[1]}</td>
                <td> 
                   <button class="delete-btn" onclick="deleteUser('${user[0]}')">Delete</button>
                </td>
                <td>
                    <a href="/admin/user-activity/${user[0]}" target="_blank" style="text-decoration: none;">
                        <button class="activity-btn">User Activity</button>   #to show the user activity
                    </a>
                </td>              
            </tr>
            `;

            tbody.innerHTML += row;
        });

    } catch (err) {
        console.error("Error loading users:", err);
    }
}

// -----------------------------
// Load History
// -----------------------------
async function loadHistory() {
    try {
        const res = await fetch("/admin/history", { credentials: "include" });
        const data = await res.json();

        const tbody = document.querySelector("#admin-history-table tbody");
        tbody.innerHTML = ""; // clear existing rows

        data.history.forEach(item => {
            const color = item.prediction === "Fake" ? "red" : "green";

            // Create table row
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${item.username}</td>
                <td>${item.input_text || "-"}</td>
                <td>${(item.ocr_text || "-").replace(/\n/g, "<br>")}</td>
                <td style="color:${color}">${item.prediction}</td>
                <td>${(item.confidence * 100).toFixed(1)}%</td>
                <td>${item.created_at}</td>
                <td></td>
            `;

            // Create Delete button safely
            const deleteTd = tr.querySelector("td:last-child");
            const btn = document.createElement("button");
            btn.textContent = "Delete";
            btn.addEventListener("click", () => deleteHistory(item.created_at));
            deleteTd.appendChild(btn);

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Error loading history:", err);
    }
}


// -----------------------------
// Delete User
// -----------------------------
async function deleteUser(username) {
    if (!confirm(`Delete user ${username}?`)) return;

    await fetch(`/admin/delete-user/${username}`, {
        method: "DELETE",
        credentials: "include"
    });

    loadUsers();
}
