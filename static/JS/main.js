document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded successfully!");

    document.querySelectorAll("input").forEach(input => {
        input.addEventListener("focus", function() {
            this.style.backgroundColor = "#eef";
        });
        input.addEventListener("blur", function() {
            this.style.backgroundColor = "white";
        });
    });

    document.querySelector("button").addEventListener("click", function() {
        this.style.transform = "scale(0.95)";
        setTimeout(() => { this.style.transform = "scale(1)"; }, 150);
    });
});
