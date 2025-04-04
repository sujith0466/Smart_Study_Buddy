document.getElementById("add-subject").addEventListener("click", () => {
    const container = document.getElementById("subject-container");
    const entry = document.createElement("div");
    entry.classList.add("subject-entry");

    entry.innerHTML = `
        <input type="text" name="subjects[]" placeholder="Subject Name" required>
        <input type="number" name="scores[]" placeholder="Score (%)" min="0" max="100" required>
    `;

    container.appendChild(entry);
});

document.getElementById("study-form").addEventListener("submit", () => {
    document.getElementById("loader").style.display = "flex";
});
