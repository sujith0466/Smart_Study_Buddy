document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded successfully!");

    // Smooth input focus effect
    document.querySelectorAll("input").forEach(input => {
        input.addEventListener("focus", function() {
            this.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
            this.style.color = "white";
            this.style.boxShadow = "0 0 10px rgba(255, 255, 255, 0.3)";
        });

        input.addEventListener("blur", function() {
            this.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
            this.style.color = "white";
            this.style.boxShadow = "none";
        });
    });

    // Smooth button click effect
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("mousedown", function() {
            this.style.transform = "scale(0.95)";
        });
        button.addEventListener("mouseup", function() {
            this.style.transform = "scale(1)";
        });
    });

    // Password Strength Checker
    let passwordInput = document.getElementById("password");
    let strengthBar = document.getElementById("password-strength");
    let strengthText = document.getElementById("strength-text");

    if (passwordInput) {
        passwordInput.addEventListener("input", function () {
            let password = passwordInput.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[@$!%*?&]/)) strength++;

            // Update UI dynamically
            strengthBar.className = "";
            strengthBar.style.transition = "width 0.3s ease-in-out";
            
            if (strength === 0) {
                strengthBar.style.width = "0%";
                strengthText.innerHTML = "Enter a password";
                strengthBar.style.background = "#444";
            } else if (strength === 1) {
                strengthBar.style.width = "30%";
                strengthBar.style.background = "red";
                strengthBar.classList.add("weak");
                strengthText.innerHTML = "Weak";
            } else if (strength === 2 || strength === 3) {
                strengthBar.style.width = "60%";
                strengthBar.style.background = "orange";
                strengthBar.classList.add("medium");
                strengthText.innerHTML = "Medium";
            } else {
                strengthBar.style.width = "100%";
                strengthBar.style.background = "green";
                strengthBar.classList.add("strong");
                strengthText.innerHTML = "Strong";
            }
        });
    }
});
