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

document.getElementById("study-form").addEventListener("submit", (e) => {
    e.preventDefault();
    document.getElementById("loader").style.display = "flex";

    const formData = new FormData(document.getElementById("study-form"));
    const studyMethod = formData.get('study_method');

    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loader").style.display = "none";
        if (studyMethod === "video") {
            document.getElementById("video-recommendations").style.display = "block";
            document.getElementById("reading-recommendations").style.display = "none";
            displayRecommendations(data.videoRecommendations, 'video');
        } else {
            document.getElementById("video-recommendations").style.display = "none";
            document.getElementById("reading-recommendations").style.display = "block";
            displayRecommendations(data.readingRecommendations, 'reading');
        }
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("loader").style.display = "none";
    });
});

function displayRecommendations(recommendations, type) {
    const listId = type === 'video' ? "video-list" : "reading-list";
    const listContainer = document.getElementById(listId);
    listContainer.innerHTML = '';

    recommendations.forEach(item => {
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = item;
        link.textContent = type === 'video' ? 'Watch Video' : 'Read Article';
        link.target = '_blank';
        listItem.appendChild(link);
        listContainer.appendChild(listItem);
    });
}
