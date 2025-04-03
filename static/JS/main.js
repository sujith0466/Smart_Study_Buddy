document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded successfully!");

    // Input field focus and blur effect
    document.querySelectorAll("input").forEach(input => {
        input.addEventListener("focus", function() {
            this.style.backgroundColor = "#333";
            this.style.color = "white";
            this.style.boxShadow = "0 0 10px rgba(255, 255, 255, 0.3)";
        });

        input.addEventListener("blur", function() {
            this.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
            this.style.color = "white";
            this.style.boxShadow = "none";
        });
    });

    // Button click animation
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("mousedown", function() {
            this.style.transform = "scale(0.95)";
        });
        button.addEventListener("mouseup", function() {
            this.style.transform = "scale(1)";
        });
    });

    // Password Strength Indicator
    const passwordInput = document.getElementById("password");
    const strengthIndicator = document.getElementById("password-strength");

    if (passwordInput && strengthIndicator) {
        passwordInput.addEventListener("input", function () {
            let strength = 0;
            const value = passwordInput.value;

            if (value.length >= 8) strength++;
            if (/[A-Z]/.test(value)) strength++;
            if (/[0-9]/.test(value)) strength++;
            if (/[@$!%*?&#]/.test(value)) strength++;

            strengthIndicator.className = "";
            if (strength === 1) {
                strengthIndicator.classList.add("weak");
            } else if (strength === 2 || strength === 3) {
                strengthIndicator.classList.add("medium");
            } else if (strength === 4) {
                strengthIndicator.classList.add("strong");
            }
        });
    }
});
